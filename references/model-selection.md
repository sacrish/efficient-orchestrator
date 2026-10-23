# Per-Role Model and Reasoning Selection

Read when preparing the first delegation, changing model/reasoning settings, or resolving a user model name. Catalogs, access, and pricing change; do not maintain a permanent role-to-model-name table.

## 1. Establish the candidate set

Inspect the current subagent tool's schema, model/provider selection mechanisms, explicit restrictions, and reasoning controls. Discover the current instance's configured model catalog through supported interfaces or the catalog referenced by its configuration. Inspect only necessary model metadata; do not expose API keys, authentication headers, or unrelated settings. Consult the configured catalog rather than assuming a separate official-model cache is the complete instance catalog.

For user selection, include configured OpenAI and third-party API models without a vendor restriction. Distinguish configured, explicitly restricted, and actually verified. Picker visibility, an API model-list entry, or parent access alone does not prove subagent access. A model list in descriptive tool text is not necessarily an exhaustive allowlist. Treat omission as unverified unless an explicit schema enum, governing instruction, enforced allowlist, or actual runtime rejection establishes otherwise. Respect explicit restrictions; do not bypass them. Label uncertainty without presenting it as a proven inability to call the model.

Record each relevant display name, real model ID, provider/route identifier, aliases, and supported/default reasoning values when available. Resolve identity within the configured route; the same model ID on different providers may represent distinct choices. Reuse fresh session evidence rather than spawning multiple probe agents merely to test availability.

Read these official sources as needed, reusing a concise verified summary within the conversation instead of browsing all pages for every role:

- [Codex / Work models and access](https://learn.chatgpt.com/docs/models)
- [Subagent model and reasoning configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex / Work plans and usage](https://learn.chatgpt.com/docs/pricing)
- Use [API pricing](https://developers.openai.com/api/docs/pricing) only for API-billed comparisons.

For third-party selections, use configured metadata and that provider's official documentation when capability or pricing checks are needed. If documentation is inaccessible, use available runtime evidence and disclose the uncertainty. Do not claim an absolute cheapest model, equate API rates with subscription usage, or invent fees. No price lookup is required merely to honor an explicit supported choice.

## 2. Resolve names to configured model identities

Use the latest applicable user choice, not a permanent list of aliases:

1. Prefer an exact real ID with its specified provider/route. If it identifies one configured route, resolve it directly.
2. Otherwise match display names or established aliases. Normalize case, surrounding whitespace, and harmless separator differences only where equivalence is clear. Preserve version numbers, model-family distinctions, and provider qualifiers.
3. When one identity is confidently supported by the catalog evidence, use its real ID without asking for an additional confirmation. Briefly show the resolved display name/ID and route when helpful; confirmation is not a new approval gate.
4. If multiple distinct IDs or routes plausibly match, ask the user to choose. Show the differentiating version/provider and exact ID. Do not pick the newest, cheapest, most popular, or first entry, or assume one because another is currently unavailable. Duplicate catalog records for the same ID and route are not distinct choices.
5. If no confident match exists, show relevant nearby candidates and ask. Do not fabricate an ID, infer a version from a name, or route a request to a different provider.

A friendly name can legitimately differ from its ID: use the catalog mapping rather than deriving an API ID from the name. For example, use a configured Flash entry's recorded ID even if its display name contains a newer version label absent from that ID. Treat this as a resolution rule, not evidence that the model is callable.

## 3. Collect model and optional reasoning choices

Use the [allocation UI protocol](allocation-ui.md) to collect model and effort choices for each planned worker instance in a confirmed batch. Prefer linked dropdowns in supported inline clients, preselect recommendations, and show eligible configured models without requiring typed IDs. Preserve role preferences as recommendation inputs; a confirmed per-instance choice applies to that assignment and does not silently rewrite a global role preference.

For a client without a working inline submission channel, use available structured user-input questions, or ask in a reply. Offer relevant configured names and automatic selection, collect optional effort, and obtain explicit confirmation of the batch. Explain verified versus unverified choices only when it affects the decision. A submitted complete selection can itself confirm the batch; do not ask for the same confirmation twice.

For a temporary role, first explain its specific purpose and why the predefined roles do not cover it. Obtain a choice for that particular role before launch, even when a general all-role automatic preference exists. An existing user instruction naming a model for that particular temporary role satisfies the gate. Offer supported models and the option to explicitly delegate selection to the agent. Do not reuse a different role's preference. Scope the record to the current task and preserve it for follow-ups and context compaction until that task ends.

Fallback question structure:

> This is the first use of Reviewer, to check this change's permission boundaries. Choose Automatic (recommended), candidate A, or candidate B, or name another configured model. Optionally specify a supported reasoning effort; otherwise I will choose it for this task.

Replace candidate labels with real catalog names in the actual question. Give one task-specific recommendation reason; automatic selection may show the intended model. Avoid unrelated catalog entries. When Coder and Tester are both needed now, collect their choices together; ask about other roles when needed.

Record model choice and effort choice independently. If the user answers with a model alone, resolve it and automatically choose effort unless an earlier fixed effort preference still applies. Do not ask again just because effort was omitted. If only effort is supplied and the model still lacks an applicable choice, keep the model question pending; silence never authorizes automatic model selection.

| User input or state | Action |
| --- | --- |
| A specific model | `fixed`: honor it; do not silently replace it for cost reasons. |
| "Automatic", "no preference", "you decide", or a valid submitted answer explicitly leaving the model unspecified | `auto`: select the model. |
| An earlier all-role automatic instruction or an applicable role-specific choice | Use it to seed recommendations. A new worker instance still requires batch confirmation unless the user explicitly waived it. For a temporary role, require a choice explicitly covering that role. |
| No reply, an asynchronous question still pending, or an unsubmitted default | `pending`: do not launch that role; continue independent work. |
| "Use a different model" without a replacement | Request a new selection with supported candidates and automatic selection. |
| "Switch Coder to [model]" or "Make Coder automatic" | Update and verify the supplied choice without asking redundantly. |

If an ambiguous answer affects selection, keep it pending. A choice covers later calls of the same role within its lifetime. The latest applicable user instruction wins: later per-role choices can override an all-role choice, and later all-role instructions can update earlier per-role choices after the temporary role's initial selection gate has been satisfied.

## 4. Optimize automatic model choices subject to quality

Among candidates capable of the task and its tools, input modalities, and context, compare expected total completion cost and latency. Include parent/subagent input, reasoning/output, context transfers, coordination, review, retries, and tool/compute costs. Token volume and effective pricing are separate metrics; neither output length nor unit price alone determines value.

Prefer capable, runtime-supported official OpenAI models by default. Include configured third-party models in automatic comparison when the user explicitly authorizes that scope; a fixed third-party choice needs no automatic-selection authorization. If the default candidate set cannot meet the task, explain the gap and request a viable choice or expanded scope rather than silently switching providers.

### Default preferences for predefined roles

Apply these preferences only when model selection is automatic and authorized. They are capability and cost preferences, not fixed model IDs or proof that a model is suitable. Use the current candidate set, task requirements, and evidence; do not override a user-fixed choice.

| Role | Default model preference | When to increase capability |
| --- | --- | --- |
| Orchestrator | Keep ordinary coordination in the main agent without changing its model. For justified delegated architectural analysis, prefer strong reasoning, judgment, and broad context handling. | Ambiguous requirements, interacting constraints, architectural decisions, or costly downstream mistakes. Do not create a second coordinator for routine scheduling. |
| Explorer | Prefer the lowest-cost reliable, fast model for bounded search, symbol location, extraction, and factual summaries. | Complex cross-module flow, competing root-cause hypotheses, or semantic analysis that exceeds mechanical retrieval. Use direct tools instead when they already suffice. |
| Designer | Prefer a model with demonstrated visual/design judgment and the input/tool capabilities required by the deliverable. A balanced model can adapt established designs; original direction and cohesive visual systems may justify a stronger model. | Original art direction, complex interaction/motion, visual ambiguity, or observed quality gaps. Image inspection requires suitable visual input; text-only specification work does not automatically require it. |
| Coder | Prefer a cost-efficient balanced model with reliable coding, tool use, and relevant validation. Lightweight models can handle clear mechanical edits. | Complex integration, concurrency, subtle state changes, architecture, or repeated correctness failures. |
| Reviewer | Prefer strong correctness and risk judgment for substantive independent review. A balanced model can cover a narrow, routine review with clear invariants. | Authorization, security, data integrity, subtle regressions, or important uncertain assumptions. Do not create an independent reviewer for low-risk changes without a benefit. |
| Tester | Prefer a lightweight reliable model for running established checks and summarizing failures; use a balanced model to design and implement meaningful tests. | Complex behavioral contracts, asynchronous/nondeterministic cases, failure-path design, or high-impact coverage gaps. |

Automatic selection requires a role-aware decision, not blanket inheritance of the parent's model or maximum reasoning effort. Inherit only when that model fits the task and expected total cost, or when a runtime constraint makes inheritance the viable option; explain a constraint when it affects the user's choice. Resolve the actual supported model and effort through the existing selection rules. If the tool requires explicit named-model authorization for an override, obtain it rather than ignoring the restriction.

For a temporary role, derive the same kind of preference from its specific deliverable after its user selection gate is satisfied. Prefer the least costly reliable capability level that meets acceptance; do not assume a specialized role always needs a flagship model.

Difficulty may vary within one role. Automatic preferences may produce new recommendations without a separate model-name question, but a new or changed assignment still follows the batch-confirmation gate. Honor the actual confirmed identity and effort during execution. For an observed capability gap, collect a replacement selection or specific automatic-recovery authorization rather than silently upgrading a confirmed assignment.

## 5. Resolve reasoning effort independently

- Honor an explicit effort for the selected model. Resolve localized UI labels or aliases to actual parameter values using the instance metadata or provider documentation; do not assume labels map identically across models. Clarify an ambiguous request when its meaning is not established by context.
- With no new effort specified, preserve an applicable earlier fixed preference. Otherwise use `auto` effort without a separate blocking question. A fixed model can use automatic effort, and an automatic model preference can retain a fixed effort where compatible.
- In automatic mode, select the effort most suitable for task complexity, risk, likely rework, latency, and the selected model's guidance. Clear searches and mechanical edits usually need less reasoning than complex diagnosis or high-risk review. Start with an appropriate model default and adjust when justified; neither maximum nor minimum is a universal default.
- Use only the intersection of the model/provider's supported values and runtime controls. Identical level names do not guarantee equal behavior across models. On a model change, revalidate fixed effort compatibility; reselect automatic effort for the new model/task.
- If explicit effort is unsupported or the runtime cannot apply it, explain the limit and ask whether to use a supported value or automatic effort while preserving the model choice. Do not silently downgrade, ignore the request, or declare the model unavailable because one effort value is invalid.
- For a model without configurable effort, omit the unsupported parameter and record `not_configurable` in automatic mode. If the user explicitly requested effort, ask how to proceed. Do not invent controls for models exposing a different reasoning mechanism.
- Inspect omission semantics: if the runtime inherits parent effort, omission may not mean the selected model's default. Pass the resolved supported value when needed, or disclose inability to enforce the choice. Verify reported settings when available; never claim an automatically selected effort was applied solely because it appeared in the task prompt.

## 6. Establish compatibility through bounded actual calls

After the role's model selection gate is satisfied:

1. Check explicit constraints. If a real schema restriction or governing instruction excludes the selected identity, report that specific limit. A missing entry in descriptive text is insufficient evidence. Do not invent alternate parameters or evade a restriction.
2. If the call accepts a model string and no explicit restriction excludes the configured choice, pass its exact resolved ID, including any gateway/vendor prefix, and the supported reasoning value. Do not strip the prefix, replace the ID with its display name, or silently inherit a default model.
3. Prefer using the first bounded real assignment to establish compatibility. If uncertainty makes that assignment costly or risky, use one minimal probe that returns a short readiness message without tool calls, file access, writes, or descendants. Use the selected role/model rather than creating a different role solely to probe it, and reuse that agent for the assignment when follow-ups are supported. Do not require a probe for every role or task.
4. Separate spawn acceptance from successful completion. When model metadata or execution records are available, verify the recorded model and reasoning to detect a fallback. A successful text-only probe establishes that scope; it does not prove complex tool compatibility or a gateway's downstream vendor identity.
5. Cache the result and its scope for the same runtime, model route, and settings within this conversation. Recheck only after relevant changes or contradictory failures. Keep user preference gates per role even when compatibility evidence is shared.
6. If an actual call fails, classify its stage and concrete error before retrying or requesting a new model. Do not describe a model as runtime-rejected when no invocation occurred.

## 7. Apply selections and retain their evidence

This is a conceptual conversation record, not global runtime configuration. Track only used roles and actual worker instances. Task-owned allocation snapshots and receipts support confirmation; do not create long-term preference files:

```text
role: Coder
allocation_batch: confirmed batch ID
allocation_instance: worker ID, distinct from its role
model_mode: auto | fixed
requested_model: exact user choice, or empty in auto mode
resolved_model: actual model identifier for this call
provider_route: configured route identifier, or verified inherited route
reasoning_mode: auto | fixed
requested_reasoning: exact user effort choice, or empty in auto mode
resolved_reasoning: supported parameter value, verified default, or not_configurable
status: selected | pending | needs_reselection
runtime_support: unverified | spawn_accepted | completed | explicitly_rejected
evidence: brief runtime, official-source, and actual-call evidence
```

- Before launching, check the role record and real tool schema. Apply the resolved ID, provider route, and reasoning through supported parameters covered by the user's choices. If a tool requires an explicit named-model request to override inheritance, ask for that choice rather than bypassing the restriction through this skill.
- A catalog route is not a tool parameter. An inherited provider, including one named `openai`, can represent a gateway routing multiple vendors by model ID. Provider inheritance or its label alone is insufficient to reject a third-party model. Use its registered routing ID through the existing model parameter when permitted; do not invent a provider field. If an actual call proves a required separate route unavailable, explain that specific routing failure.
- Verify reported model/route/effort metadata when available. If requested settings are unsupported, explain the specific limit and offer supported choices or local execution. Keep the affected choice pending; do not silently substitute an inherited model.
- Do not switch the parent's model, change global settings, or create separate chats to simulate subagents. Before reuse, check the agent's identity and effort against the current choices; use a replacement with a minimal handoff when the runtime cannot apply a necessary change to an existing agent.
- Preserve both preferences, resolved identities, automatic-selection scope, unavailability evidence, and unanswered questions through context compaction. Do not assume choices carry into a new conversation.

## 8. Separate selection problems from execution failures

| Situation | Action |
| --- | --- |
| A configured model is absent from descriptive tool examples or an official-model cache | Keep it unverified; apply the bounded-call procedure unless an explicit restriction excludes it. Do not request a replacement solely for this absence. |
| A user-fixed model is excluded by an explicit constraint or an actual call establishes inaccessibility, retirement, or a clear model-unavailable error | Record the constraint or exact error, mark `needs_reselection`, and ask again. Do not replace that role's model before selection. |
| An automatically recommended model is explicitly unavailable | Remove it from recommendations and propose a viable replacement. Changing a confirmed assignment requires confirmation or explicit recovery authorization; if no candidate remains, explain the limit. |
| An ambiguous model name or provider route | Ask for the specific identity before launch; do not treat it as model unavailability. |
| An unsupported reasoning level or parameter | Keep the selected model. Correct automatic settings within supported controls; ask before replacing or omitting a user-fixed effort. |
| Authentication, rate limits, quota, network timeouts, tool/test failures, or poor output | Diagnose the specific cause rather than claiming a vendor/model whitelist restriction. Use bounded recovery, narrower scope, or local takeover. Temporary congestion must not cause repeated model-selection prompts. |

Complete required reselection before another call of the affected role. Update records on user-requested changes so old-model agents are not reused accidentally. Coordinate stopping/completion and handoff of running work; never leave two owners writing the same scope.
