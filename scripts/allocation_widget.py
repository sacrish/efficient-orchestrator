"""Build allocation forms and validate user-submitted choices. Standard library only."""

import argparse
import hashlib
import json
from pathlib import Path
import uuid


PROTOCOL = "efficient-orchestrator.allocation.v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(snapshot):
    content = {k: v for k, v in snapshot.items() if k != "fingerprint"}
    return hashlib.sha256(canonical(content).encode("utf-8")).hexdigest()


def required_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value


def catalog_models(catalog):
    models = {}
    for entry in catalog["models"]:
        if entry.get("visibility") in ("hide", "hidden") or entry.get("selectable") is False:
            continue
        model_id = required_text(entry.get("slug", entry.get("id")), "model ID")
        route = required_text(entry.get("provider_route") or entry.get("model_provider") or "inherited", "provider route")
        key = canonical([route, model_id])
        raw_efforts = entry.get("supported_reasoning_levels", entry.get("efforts", []))
        efforts = list(dict.fromkeys(
            required_text(e.get("effort") if isinstance(e, dict) else e, "effort")
            for e in raw_efforts
        ))
        default = entry.get("default_reasoning_level", entry.get("default_effort"))
        if default is not None and default not in efforts:
            raise ValueError(f"Unsupported default effort for {model_id}")
        model = {"key": key, "id": model_id, "route": route,
                 "label": entry.get("display_name") or model_id,
                 "efforts": efforts, "default_effort": default}
        if key in models and models[key] != model:
            raise ValueError(f"Conflicting catalog metadata for {model_id}")
        models[key] = model
    if not models:
        raise ValueError("The catalog has no eligible models")
    return list(models.values())


def resolve_model(models, value):
    matches = [m for m in models if m["key"] == value or m["id"] == value]
    if len(matches) != 1:
        raise ValueError(f"Expected one model identity for {value!r}; found {len(matches)}")
    return matches[0]


def build_snapshot(plan, catalog):
    models = catalog_models(catalog)
    agents, seen = [], set()
    for entry in plan["agents"]:
        agent_id = required_text(entry["id"], "agent ID")
        if agent_id in seen:
            raise ValueError(f"Duplicate agent ID: {agent_id}")
        seen.add(agent_id)
        model = resolve_model(models, entry["recommended_model"])
        effort = entry.get("recommended_effort", model["default_effort"])
        if effort is not None and effort not in model["efforts"]:
            raise ValueError(f"Unsupported recommended effort for {agent_id}")
        recommendations = {}
        for identity, value in entry.get("effort_by_model", {}).items():
            candidate = resolve_model(models, identity)
            if value is not None and value not in candidate["efforts"]:
                raise ValueError(f"Unsupported alternative effort for {agent_id}")
            recommendations[candidate["key"]] = value
        recommendations[model["key"]] = effort
        agents.append({"id": agent_id, "role": required_text(entry["role"], "role"),
                       "task": required_text(entry["task"], "task"),
                       "recommended_model": model["key"],
                       "effort_by_model": recommendations})
    if not agents:
        raise ValueError("An allocation batch must contain at least one agent")
    labels = plan.get("labels", {})
    if not isinstance(labels, dict) or any(not isinstance(v, str) for v in labels.values()):
        raise ValueError("labels must contain text values")
    if len(labels.get("confirmTitle", "")) > 250:
        raise ValueError("The host confirmation title must not exceed 250 characters")
    demo = plan.get("demo", False)
    if not isinstance(demo, bool):
        raise ValueError("demo must be boolean")
    snapshot = {"protocol": PROTOCOL, "batch_id": plan.get("batch_id") or uuid.uuid4().hex,
                "title": plan.get("title", "Subagent allocation"), "demo": demo,
                "models": models, "agents": agents, "labels": labels}
    required_text(snapshot["batch_id"], "batch ID")
    required_text(snapshot["title"], "title")
    snapshot["fingerprint"] = fingerprint(snapshot)
    return snapshot


def validate_response(snapshot, response):
    if not isinstance(snapshot, dict) or not isinstance(response, dict):
        raise ValueError("The snapshot and response must be objects")
    if snapshot.get("fingerprint") != fingerprint(snapshot):
        raise ValueError("The saved allocation snapshot was modified")
    for field in ("protocol", "batch_id", "fingerprint", "demo"):
        if type(response.get(field)) is not type(snapshot[field]) or response[field] != snapshot[field]:
            raise ValueError(f"Stale or mismatched allocation field: {field}")
    allocations = response.get("allocations")
    if not isinstance(allocations, list) or len(allocations) != len(snapshot["agents"]):
        raise ValueError("The response must cover exactly the pending agents")
    models = {m["key"]: m for m in snapshot["models"]}
    expected = {a["id"]: a for a in snapshot["agents"]}
    chosen = {}
    for allocation in allocations:
        if not isinstance(allocation, dict):
            raise ValueError("Each allocation must be an object")
        agent_id = allocation.get("agent_id")
        if not isinstance(agent_id, str) or agent_id not in expected or agent_id in chosen:
            raise ValueError("Unknown or duplicate agent ID")
        if allocation.get("role") != expected[agent_id]["role"]:
            raise ValueError("Role mismatch")
        model_key = allocation.get("model_key")
        if not isinstance(model_key, str):
            raise ValueError("The model identity must be text")
        model = models.get(model_key)
        if model is None or allocation.get("model_id") != model["id"] or allocation.get("provider_route") != model["route"]:
            raise ValueError("Unknown or mismatched model identity")
        effort = allocation.get("reasoning_effort")
        if "reasoning_effort" not in allocation or (effort is not None and effort not in model["efforts"]):
            raise ValueError("Unsupported reasoning effort")
        chosen[agent_id] = {"agent_id": agent_id, "role": expected[agent_id]["role"],
                            "model_key": model["key"], "model_id": model["id"],
                            "provider_route": model["route"], "reasoning_effort": effort}
    return {"protocol": PROTOCOL, "batch_id": snapshot["batch_id"],
            "fingerprint": snapshot["fingerprint"], "demo": snapshot["demo"],
            "allocations": [chosen[a["id"]] for a in snapshot["agents"]]}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def render(plan, catalog, output):
    snapshot = build_snapshot(plan, catalog)
    data = canonical(snapshot).replace("<", "\\u003c").replace("&", "\\u0026")
    root_id = "allocation-" + snapshot["fingerprint"][:20]
    template = (Path(__file__).resolve().parents[1] / "assets" / "allocation-widget.html").read_text(encoding="utf-8")
    fragment = template.replace("__ROOT_ID__", root_id).replace("__ALLOCATION_DATA__", data)
    if len(fragment.encode("utf-8")) >= 1_000_000:
        raise ValueError("The allocation form exceeds the inline size limit")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path = output.with_suffix(".snapshot.json")
    if output.exists() or snapshot_path.exists():
        raise ValueError("Use a fresh output path for each allocation batch")
    output.write_text(fragment, encoding="utf-8", newline="\n")
    snapshot_path.write_text(canonical(snapshot) + "\n", encoding="utf-8", newline="\n")
    return {"batch_id": snapshot["batch_id"], "fingerprint": snapshot["fingerprint"],
            "html": str(output.resolve()), "snapshot": str(snapshot_path.resolve())}


def confirm(snapshot_path, response_path, catalog):
    snapshot = read_json(snapshot_path)
    result = validate_response(snapshot, read_json(response_path))
    current = {m["key"]: m for m in catalog_models(catalog)}
    for allocation in result["allocations"]:
        model = current.get(allocation["model_key"])
        if model is None or (allocation["reasoning_effort"] is not None and allocation["reasoning_effort"] not in model["efforts"]):
            raise ValueError("A selected model or effort is no longer in the current eligible catalog")
    receipt = Path(snapshot_path).with_suffix(".confirmed.json")
    try:
        with receipt.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical(result) + "\n")
        status = "demo_confirmed" if result["demo"] else "confirmed"
    except FileExistsError:
        if read_json(receipt) != result:
            raise ValueError("This batch was already confirmed with different choices")
        status = "demo_confirmed" if result["demo"] else "already_confirmed"
    return {"status": status, "receipt": str(receipt.resolve()), **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("render")
    create.add_argument("--plan", required=True)
    create.add_argument("--catalog", required=True)
    create.add_argument("--output", required=True)
    accept = commands.add_parser("confirm")
    accept.add_argument("--snapshot", required=True)
    accept.add_argument("--response", required=True)
    accept.add_argument("--catalog", required=True)
    args = parser.parse_args()
    try:
        result = render(read_json(args.plan), read_json(args.catalog), args.output) if args.command == "render" else confirm(args.snapshot, args.response, read_json(args.catalog))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"Allocation error: {error}\n")
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
