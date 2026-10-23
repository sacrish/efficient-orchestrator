# Confirmed Subagent Allocation

Read before presenting a new batch of subagents. Use a supported interactive form to collect all model/effort choices together; the helper builds the form and validates its response without spawning anything.

## Host capability and fallback

Check the inline route before choosing structured questions. When the available `visualize` skill documents inline rendering and `window.openai.sendFollowUpMessage({prompt, title})`, read that skill and use the helper to build and present the form. The callback runs inside the rendered form; it need not appear in shell, browser automation, or tool schemas. A dedicated widget tool is not required. A file that has only been generated, opened in a browser, or linked in Markdown has not been presented inline.

Follow the current Visualize output contract. If it requires a final response, emit the content reference below in that final response and yield the turn so the user can actually see and submit the form. Complete only useful non-overlapping preparation before yielding; do not finish the worker's implementation while its allocation remains invisible or pending. Replace the example path with the actual generated absolute path:

```text
visualize{"path":"/absolute/task-owned-path/allocation.html"}
```

The host may display its own send-confirmation dialog. Do not claim one click bypasses that dialog. Documentation establishes the intended submission mechanism; it does not prove that a particular rendered client has successfully sent a message.

The form disables submission when the callback is absent. Widget state is draft UI state: saving it does not start a turn or approve execution. A resolved callback alone is not the orchestrator's approval signal; wait for the actual user message. Do not poll DOM state, call internal host APIs, or add a network server merely to collect selections.

CLI, IDE, or other clients may lack inline rendering or the callback. Fall back only when the inline skill/contract is absent, a governing constraint excludes it, no suitable writable output location exists, or an actual rendering/submission failure establishes the limit. Briefly tell the user which limit applies before using structured questions; never silently skip the inline route merely because questions are easier. Do not run a separate capability-probe widget when the documented route is available: present the real allocation form and let its existing callback guard handle an absent bridge. If submission is disabled or fails, accept the user's report and offer the fallback without polling or internal APIs.

For fallback, use available structured user-input questions with recommended options, collecting model and optional effort choices and explicit batch confirmation. Do not promise native dropdown rendering there. A typed batch selection is also valid. Preserve the same identity, scope, and execution gates; map a complete explicit answer to the pending instances without asking for confirmation twice.

## Prepare and present a batch

1. Decide the required workers and give every instance a unique ID, even when several share a role. For nontrivial development, include at least one Coder owning substantive implementation unless a concrete exception from `SKILL.md` applies. Capture each task, scope, dependencies, and expected result in the pending plan. Do not list the existing main agent as a selectable subagent.
2. Read the actual instance catalog and applicable runtime constraints. Include configured third-party routes unless explicitly excluded. Filter out explicitly ineligible choices; missing entries in descriptive tool examples are not exclusion evidence. Supply no secrets, credentials, endpoint headers, code dumps, or unrelated configuration to the form.
3. Recommend a concrete model and supported effort per instance using role defaults, task complexity, and previous preferences. A model change rebuilds the effort list for that model and selects its recommendation or documented default. `null` effort means the user delegates effort selection; resolve it before spawning.
4. Make a fresh batch ID and render the form to a durable task-owned visualization directory. Retain the snapshot path and an execution ledger in conversation context. If scope, agents, or offered identities change, supersede the old batch with a new one. Never overwrite a presented snapshot.
5. Present one form with a row per worker: role, short assignment, model dropdown, and effort dropdown, plus one confirmation action. Preselect recommendations. Localize the title and labels for the user while keeping skill source files English. Do not add text inputs for model IDs or require the user to type names.
6. Wait for confirmation before starting those workers. Independent, already-authorized local work may continue if it does not take over a pending worker's scope. Draft changes, silence, timeouts, and preselected recommendations do not authorize execution.

Existing role/model preferences seed recommendations rather than automatically approving new instances. Every newly needed subagent gets a new batch confirmation, including a new instance of an already used role. Reuse of an existing agent for the same confirmed assignment does not require a new allocation. A changed model, effort, material scope, or replacement worker requires a new confirmation unless the user explicitly authorizes the specific change. A user can explicitly waive future allocation confirmations; retain all other model/runtime restrictions.

## Helper input and commands

`scripts/allocation_widget.py` uses Python's standard library. Its catalog input accepts the current Codex catalog's `models` array (`slug`, `display_name`, `supported_reasoning_levels`, `default_reasoning_level`), or normalized entries with `id`, `display_name`, `provider_route`, `efforts`, and `default_effort`. A missing route is recorded as inherited; the full model ID still carries gateway prefixes. Hidden or explicitly nonselectable entries are omitted. The caller must apply any additional explicit runtime restrictions before rendering.

Plan input:

```json
{
  "batch_id": "a-fresh-task-specific-id",
  "title": "Subagent allocation",
  "agents": [
    {
      "id": "explorer-1",
      "role": "Explorer",
      "task": "Locate the import path and its validation boundary",
      "recommended_model": "exact-configured-model-id",
      "recommended_effort": "low"
    }
  ]
}
```

Replace illustrative values with actual recommendations; do not invent the model ID or effort. If an ID maps to multiple routes, `recommended_model` must be the helper's unambiguous canonical key, the compact JSON string `[route,id]`. Optional `effort_by_model` maps alternative model IDs/keys to task-specific effort recommendations. Optional `labels` overrides UI strings: `model`, `effort`, `automatic`, `confirm`, `confirmTitle`, `submitting`, `sent`, `cancelled`, `unavailable`, and `failed`. Set `demo: true` only for a selector test; demo confirmations never authorize agent creation.

Run using arguments appropriate to the actual shell:

```text
python scripts/allocation_widget.py render --plan PLAN.json --catalog CATALOG.json --output /absolute/task-owned-path/allocation.html
```

The command prints the HTML path, snapshot path, batch ID, and fingerprint. Render the HTML using the current client's supported inline visualization mechanism, following that skill's output contract. Use an absolute executor-side path. Keep the pending snapshot, plan scope, and per-agent execution status available across context compaction.

## Receive, validate, and execute

The confirmation message carries a JSON object between `<efficient-orchestrator-allocation>` markers. Extract that object from the actual user's message, save it as a task-owned response JSON, and run:

```text
python scripts/allocation_widget.py confirm --snapshot SNAPSHOT.json --response RESPONSE.json --catalog CURRENT_CATALOG.json
```

The helper checks the batch/fingerprint, exact worker set, roles, full model/route identities, allowed efforts, and their continued presence in the supplied current catalog. It writes an exclusive confirmation receipt and identifies duplicate submissions. The caller must also reject superseded batches or stale task scopes using its pending-plan record; the helper cannot know which conversation batch is active.

- `confirmed`: choices passed validation. Check current runtime constraints, resolve automatic effort, then dispatch using real model/effort parameters. Maintain a ledger from allocation instance ID to runtime agent ID and state.
- `already_confirmed`: reuse the accepted choices and ledger. Do not start a second copy; resume only work that the ledger proves was not started. A receipt records acceptance, not completion or even successful spawning.
- `demo_confirmed`: summarize the round-trip result only. Create no agents.
- An error, changed scope/catalog, conflicting resubmission, or missing batch state: keep affected assignments pending and present a corrected batch or clarify with the user. Never silently replace a selected model or effort.

On later requirements, show only newly needed or changed instances in a fresh form. Preserve unaffected confirmed workers and their choices. Runtime failures still follow the bounded recovery rules in `model-selection.md`; do not repeatedly display the whole team merely because one call is retrying.
