---
name: efficient-orchestrator
description: Coordinate tasks with cost-aware subagent delegation, role-specific model and reasoning choices, and risk-proportionate verification. Use when bounded implementation, parallel work, focused exploration, or independent review can improve efficiency or quality. Handle simple tasks directly.
---

# Efficient Multi-Agent Orchestration

Meet the user's quality and timing requirements while minimizing unnecessary total tokens, cost, waiting, and rework. The main agent is the default executor. Applying this skill authorizes bounded delegation within the current task; it does not expand permission to change files, perform external actions, or create commits.

Keep skill files in English. Communicate with the user in their preferred language unless they request otherwise.

## 1. Decide whether delegation pays off

Use existing context and a little targeted inspection to establish the objective, acceptance criteria, dependencies, and the main agent's immediate next action before spawning.

- Complete simple questions, localized edits, and work covered by one search or an existing command directly.
- Identify at least one substantial benefit: lower effective model cost, reduced latency through independent parallel work, isolation of distracting context, or independent assurance for a material risk. Compare it with startup, context transfer, coordination, waiting, integration, review, and likely retries.
- Distinguish these benefits. A cheaper model can reduce cost even in sequential work if the runtime permits it and the handoff pays off. Parallel agents using the same model do not inherently reduce tokens or fees. Keep short, immediately blocking work local instead of handing it off and waiting.
- Partition by independently verifiable responsibility. Keep closely related small edits together and reuse established findings rather than repeating repository-wide exploration.
- Scale progressively: no agents without a clear benefit; one for a bounded workstream; two for independent workstreams; additional agents only when new evidence justifies them. Complexity and risk matter more than file count.

A short internal rationale per delegation is sufficient. Do not produce a numeric budget or lengthy plan unless it helps the task.

## 2. Select roles as needed

Roles describe responsibilities, not necessarily built-in `agent_type` values. Use supported runtime types or specify the role in the task brief; never invent parameters.

| Role | Responsibility and deliverable | Default boundary |
| --- | --- | --- |
| Orchestrator | Requirements, architectural decisions, scheduling, integration, and acceptance | The main agent owns this role. Delegate only bounded complex analysis; final decisions remain local. |
| Explorer | Targeted search, file/symbol location, call or data flow tracing | Read-only. Return locations and evidence; stop when the question is answered. |
| Designer | Visual direction, layout, interaction, and design deliverables | Explicitly evaluate for substantial visual work as described below. Preserve the established design baseline; distinguish proposals from assets or implementation. |
| Coder | Features, routine fixes, and scoped refactoring | Change only the assigned write scope; return changed paths and relevant verification. |
| Reviewer | Correctness, code quality, and security risks relevant to the change | Read-only by default. Report actionable findings with evidence; do not manufacture issues or rewrite code. |
| Tester | Test design, necessary test implementation, and regression checks | Specify whether test-file edits are allowed. Report commands, results, coverage, and gaps. |

These roles are not a mandatory pipeline. Skip exploration when locations are known and handle small implementation and validation locally.

### Evaluate visual work before assigning implementation

- Explicitly assess Designer when the task involves a new visual direction, original art/assets, a substantial UI design, or meaningful animation and reactive visual feedback. Do this during initial planning, before committing the visual implementation to the main agent or a Coder.
- Prefer a Designer subagent when there is an independently useful design deliverable and the expected quality, parallelism, or focus benefit outweighs coordination. Bound the assignment to a design brief, asset set, or specific UI/visual implementation with clear ownership. Other agents can continue independent work; the main agent retains integration and final visual acceptance.
- Small changes to an established design can stay local. For substantial visual work kept local, briefly explain the concrete reason, such as no useful independent workstream or disproportionate handoff cost. This is a scheduling explanation, not an additional user approval gate. Assigning all UI to the main agent alone does not establish that Designer was evaluated.

### Temporary roles

When a subtask has specific requirements that the predefined roles cannot adequately cover, the main agent may define a temporary role for that subtask. Give it a descriptive name, explain the unmet requirement, and specify its responsibility, scope, deliverable, and acceptance criteria. Apply the same delegation benefit check before creating it.

Before launching a temporary role, present its purpose and let the user choose its model. A model already specified by the user for that particular temporary role counts as a choice; otherwise ask, even if a general all-role automatic preference exists. The user may explicitly choose automatic selection for this role. Do not inherit another role's model preference. Keep the role and its model choice scoped to this task, reuse them for related follow-ups, and retire the role when the task ends without adding it to permanent role definitions.

## 3. Select a model and reasoning effort for each role

Apply this gate only to a subagent about to be created. The main agent acting as Orchestrator does not trigger subagent selection or imply that its own model changed.

Before the first actual delegation, read [Model and reasoning selection](references/model-selection.md) and maintain a compact role-to-choice record in the current conversation.

- For a role without a choice, first offer concrete models and **Automatic (recommended)**. Allow selection of any model configured in the current instance, including third-party APIs, subject to actual subagent runtime support. Ask only about roles needed now; batch independent role choices when useful.
- Resolve user model names against the instance catalog to real IDs and provider routes. Use a confidently unique match without a redundant confirmation; ask when versions, providers, or aliases leave multiple plausible matches, and never invent an ID.
- A model missing from a tool description's advertised list is not automatically prohibited. When the schema accepts a model string and no explicit restriction excludes the user's configured choice, attempt its exact resolved ID through the normal subagent call. Follow the evidence-based compatibility procedure in the selection reference; do not demand a different model solely because the description omitted it.
- When the user explicitly leaves the model unspecified, chooses automatic selection, or has authorized automatic selection for all predefined roles, apply the role defaults in [Model and reasoning selection](references/model-selection.md) and choose a capable model by expected total cost. Prefer supported official OpenAI models by default; expand automatic comparison to third-party models when the user authorizes it. Automatic selection is not synonymous with inheriting the parent's model. Temporary roles require the role-specific user choice described above. Reuse an existing applicable choice without asking again.
- Offer optional reasoning effort in the same selection prompt. Honor an explicit supported choice; if omitted and no earlier fixed preference applies, automatically choose the effort most suitable for the task and selected model. Model and reasoning preferences are independent, so a fixed model can have automatic effort. Do not add a blocking question solely because effort was omitted.
- Silence, a timeout, or an unsubmitted UI default is not an automatic choice. Continue independent work while a selection is pending; do not start that role yet.
- Ask again if a user-selected model is unavailable, or if the user requests a replacement without naming one. A newly named model or an explicit switch to automatic is already a new choice.
- Reuse preferences within this conversation. Preserve choices and pending questions across context compaction. Do not assume missing records, write long-term memory, or change global configuration.

Apply the resolved model and reasoning through actual tool parameters, preserving the configured routing ID. Establish compatibility from explicit constraints and actual results, reusing fresh session evidence. Picker visibility alone does not prove support, and omission from descriptive lists alone does not prove rejection. An inherited provider may route multiple vendors through a gateway; its name alone does not establish a model's availability or upstream identity.

## 4. Delegate with a minimal contract

Use the [Task and report contract](references/task-contract.md) when spawning; the main agent fills it in. Provide only the objective, necessary facts and paths, write boundaries, dependencies, acceptance and stopping conditions, report requirements, and applicable repository/user constraints.

- Start with focused context. Inherit full history only when a short brief cannot preserve essential information.
- Prefer accessible paths, symbols, interface contracts, and small evidence excerpts to repository dumps, complete chats, long logs, or repeated copies of this skill.
- Give each write scope one owner. Agree on shared interfaces first; assign integration files to the main agent or one designated owner.
- Subagents must not spawn descendants by default. Route further decomposition through the main agent so model selection and cost decisions remain coordinated.

## 5. Schedule and control resource use

- Start with only the necessary one or two subagents. A third or further agent requires additional independent work and a clear benefit, within runtime limits, user budgets, and system capacity. These are scheduling defaults, not product limits.
- Dispatch independent work together; start dependent work only when prerequisites are established. Immediately continue non-overlapping local work instead of duplicating the delegated task.
- Reuse or resume a suitable agent for the same context, role, model/provider route, and reasoning settings when supported. Send only new facts or corrections. Recheck preferences when settings change; avoid accumulating unrelated history just to reuse an agent.
- If follow-ups or resumption are unsupported, use a concise handoff rather than replaying full history. If delegation itself is unsupported, work locally.
- Prefer completion events or bounded blocking waits when results are needed for the next step. Avoid frequent polling, repeated nudges, and unchanged status messages.
- Bound searches and logs to relevant evidence. Keep long outputs in artifacts and return summaries with paths without hiding failure details.
- Coordinate builds, browsers, databases, lockfiles, and other shared mutable resources. Serialize or isolate access when needed; disjoint file edits do not guarantee independent execution.
- Use appropriate reasoning, output, or execution budgets only when supported. Concision must preserve required deliverables, meaningful checks, and error evidence.

## 6. Accept, correct, and finish

The main agent owns final acceptance; a subagent's completion claim is not sufficient.

1. Check deliverables, scope, diffs, and evidence first. Confirm shared versus isolated workspace semantics before integrating changes, and preserve existing user work. Inspect implementations more deeply when interfaces, architecture, security, data integrity, or uncertain acceptance warrant it; avoid rereading unchanged files unnecessarily.
2. Apply verification in proportion to risk:

   | Risk | Verification direction |
   | --- | --- |
   | Low | Targeted checks and a brief inspection of affected behavior; relevant existing tests where useful. |
   | Medium | Relevant tests/type checks and integration checks for affected contracts and behavior. |
   | High | Boundary and failure cases, security/data-integrity checks, relevant regression coverage, and independent review when it adds assurance. |

   Risk follows impact, not file count. Reuse valid completed checks; repeat them when integration, new failures, or independent assurance justify it. Static checks do not prove runtime or visual behavior.
3. For visual changes, preserve design tokens/components, render in a real browser when visual acceptance matters, and inspect relevant viewports. Request targeted corrections. Changes without visual impact do not require screenshots or a separate visual reviewer.
4. For a specific gap, prefer one focused correction to the original agent with failure evidence. If it makes no progress, reassess scope, model, or local takeover. Do not repeat identical attempts or add agents without a concrete reason.
5. Keep acceptance standards intact. Use a stronger model or independent review when risk or likely rework justifies it; changes to fixed model choices still require the selection gate.
6. Close agents with no expected follow-up when supported. After cancellation, confirm the previous writer stopped before reassigning its scope. Finish when required deliverables pass acceptance; do not add ceremonial reviews afterward.

Report completed work, verification, and remaining limitations concisely. Report actual tokens or fees only when observed; do not claim a savings percentage without measurements. Explain coordination only when it affects progress or a user decision.
