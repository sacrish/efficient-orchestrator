"""Exercise allocation identity, freshness, submission, and rendering boundaries."""

import copy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("allocation_widget", Path(__file__).resolve().parents[1] / "scripts" / "allocation_widget.py")
widget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(widget)


class AllocationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {"models": [
            {"slug": "fast", "display_name": "Fast", "supported_reasoning_levels": [{"effort": "low"}], "default_reasoning_level": "low"},
            {"slug": "vendor/model", "display_name": "Vendor model", "supported_reasoning_levels": [{"effort": "high"}, {"effort": "max"}], "default_reasoning_level": "high"}
        ]}
        self.plan = {"batch_id": "batch-a", "agents": [
            {"id": "coder-1", "role": "Coder", "task": "Implement module A", "recommended_model": "fast"},
            {"id": "coder-2", "role": "Coder", "task": "Implement module B", "recommended_model": "vendor/model"}
        ]}
        self.snapshot = widget.build_snapshot(self.plan, self.catalog)

    def response(self):
        result = {k: self.snapshot[k] for k in ("protocol", "batch_id", "fingerprint", "demo")}
        models = {m["key"]: m for m in self.snapshot["models"]}
        result["allocations"] = []
        for agent in self.snapshot["agents"]:
            model = models[agent["recommended_model"]]
            result["allocations"].append({"agent_id": agent["id"], "role": agent["role"],
                "model_key": model["key"], "model_id": model["id"], "provider_route": model["route"],
                "reasoning_effort": model["default_effort"]})
        return result

    def test_multiple_instances_of_same_role_keep_distinct_models(self):
        selected = widget.validate_response(self.snapshot, self.response())
        self.assertEqual([a["model_id"] for a in selected["allocations"]], ["fast", "vendor/model"])

    def test_stale_batch_and_changed_scope_are_rejected(self):
        for field in ("batch_id", "fingerprint"):
            with self.subTest(field=field):
                response = self.response()
                response[field] = "stale"
                with self.assertRaises(ValueError):
                    widget.validate_response(self.snapshot, response)
        changed = copy.deepcopy(self.snapshot)
        changed["agents"][0]["task"] = "A different task"
        with self.assertRaises(ValueError):
            widget.validate_response(changed, self.response())

    def test_unknown_duplicate_missing_and_wrong_role_are_rejected(self):
        bad_responses = []
        for field, value in (("agent_id", "unknown"), ("role", "Designer"), ("model_id", "other"), ("provider_route", "other"), ("reasoning_effort", "medium")):
            response = self.response()
            response["allocations"][0][field] = value
            bad_responses.append(response)
        duplicate = self.response()
        duplicate["allocations"][1] = duplicate["allocations"][0]
        bad_responses.extend([duplicate, {**self.response(), "allocations": []}])
        for response in bad_responses:
            with self.subTest(response=response), self.assertRaises(ValueError):
                widget.validate_response(self.snapshot, response)

    def test_same_id_on_different_routes_requires_exact_identity(self):
        catalog = copy.deepcopy(self.catalog)
        other = {**catalog["models"][0], "provider_route": "second"}
        catalog["models"].append(other)
        with self.assertRaises(ValueError):
            widget.build_snapshot(self.plan, catalog)
        plan = copy.deepcopy(self.plan)
        plan["agents"][0]["recommended_model"] = widget.canonical(["second", "fast"])
        self.assertEqual(widget.build_snapshot(plan, catalog)["agents"][0]["recommended_model"], plan["agents"][0]["recommended_model"])

    def test_hidden_and_explicitly_nonselectable_models_are_not_offered(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["models"][0]["visibility"] = "hide"
        self.assertEqual([m["id"] for m in widget.catalog_models(catalog)], ["vendor/model"])

    def test_receipts_are_idempotent_and_catalog_is_rechecked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot_path, response_path = root / "batch.json", root / "response.json"
            snapshot_path.write_text(widget.canonical(self.snapshot), encoding="utf-8")
            response_path.write_text(widget.canonical(self.response()), encoding="utf-8")
            self.assertEqual(widget.confirm(snapshot_path, response_path, self.catalog)["status"], "confirmed")
            self.assertEqual(widget.confirm(snapshot_path, response_path, self.catalog)["status"], "already_confirmed")
            changed = self.response()
            changed["allocations"][1]["reasoning_effort"] = "max"
            response_path.write_text(widget.canonical(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                widget.confirm(snapshot_path, response_path, self.catalog)
            with self.assertRaises(ValueError):
                widget.confirm(snapshot_path, response_path, {"models": self.catalog["models"][:1]})

    def test_demo_confirmation_cannot_be_mistaken_for_execution(self):
        self.plan["demo"] = True
        self.snapshot = widget.build_snapshot(self.plan, self.catalog)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "batch.json").write_text(widget.canonical(self.snapshot), encoding="utf-8")
            (root / "response.json").write_text(widget.canonical(self.response()), encoding="utf-8")
            self.assertEqual(widget.confirm(root / "batch.json", root / "response.json", self.catalog)["status"], "demo_confirmed")
            self.assertEqual(widget.confirm(root / "batch.json", root / "response.json", self.catalog)["status"], "demo_confirmed")

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for the JavaScript syntax check")
    def test_runtime_javascript_parses(self):
        source = (Path(__file__).resolve().parents[1] / "assets" / "allocation-widget.html").read_text(encoding="utf-8")
        script = source.split("<script>", 1)[1].split("</script>", 1)[0]
        checked = subprocess.run([shutil.which("node"), "--check"], input=script, text=True, capture_output=True, encoding="utf-8")
        self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_catalog_text_cannot_inject_markup(self):
        class Tags(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = []

            def handle_starttag(self, tag, attrs):
                self.tags.append(tag)

        self.plan["agents"][0]["task"] = '</script><img src=x onerror="evil()">'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "allocation.html"
            widget.render(self.plan, self.catalog, output)
            parser = Tags()
            parser.feed(output.read_text(encoding="utf-8"))
            self.assertNotIn("img", parser.tags)
            with self.assertRaises(ValueError):
                widget.render(self.plan, self.catalog, output)


if __name__ == "__main__":
    unittest.main()
