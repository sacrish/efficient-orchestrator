# Minimal Task and Report Contract

Use when spawning. Adapt the brief to the actual task without copying every explanation. The main agent fills it in; do not ask the user for internal scheduling information.

Each new worker must correspond to a validated confirmed instance in the [allocation protocol](allocation-ui.md). Map that instance to its runtime agent ID and preserve the execution ledger so repeated submissions cannot create duplicate workers. The form collects user choices; the task brief below remains the main agent's responsibility.

## Task brief

```text
Role and objective: one independently verifiable result.
Context: established facts, necessary paths/symbols/interfaces, user constraints, and repository rules.
Scope: relevant read scope; allowed write paths, or explicitly read-only.
Dependencies and ownership: prerequisites, shared interfaces, other owners, and existing changes to preserve.
Acceptance: observable completion criteria and necessary verification.
Stop: return when complete; report out-of-scope dependencies, missing permission, or material uncertainty without expanding scope.
Report: use the format below; provide a concise summary and paths to full deliverables.
Constraints: do not spawn descendants; respect authorization; do not create a Git commit unless the user explicitly requested one in this conversation.
```

Resolve the user's model name to a confident catalog identity or clarify ambiguity before spawning. Configure the real model ID, provider route, and reasoning with supported tool parameters, not just brief text. Honor explicit effort; if omitted and no fixed preference applies, select task-appropriate effort automatically. Add time, token, or tool-call budgets only when the user supplies them or the task warrants them. Treat only enforceable controls as hard limits. Near a budget limit, return current artifacts and unfinished work rather than claiming completion.

Preserve the full configured model ID, including routing prefixes. Absence from a descriptive model list alone does not justify refusing the selection. Follow the compatibility procedure in [Model and reasoning selection](model-selection.md), prefer the first bounded assignment over a separate probe, and report actual errors without replacing the user's selected model silently.

If a subagent cannot access parent paths, provide the smallest accessible materials. For long repository rules, give their locations and essential constraints rather than inheriting the whole chat for one rule.

For a temporary role, state its descriptive name and the specific requirement not covered by predefined roles. Define its bounded responsibility, deliverable, and acceptance criteria in this brief, and obtain the user's model choice for that particular role before spawning. The role exists only for the current task and related follow-ups.

## Completion report

```text
Status: done | partial | blocked
Deliverable: findings or change summary; artifact/changed-file paths, with symbols or line numbers where needed.
Verification: checks actually run and their results; omitted checks and reasons.
Risks/blockers: unresolved issues and required input, or none.
```

Use this one default report format. Omit lengthy reasoning, full logs, and repeated diffs. Keep important findings and artifact paths when results are large; brevity must not hide failures or truncate required deliverables.

Role-specific evidence:

- Explorer: answer the precise question with paths, symbols, or call relationships. For negative results, state the search scope instead of claiming repository-wide absence.
- Designer: provide the assigned inspectable design brief, assets, or bounded implementation aligned with requirements and the existing design. Make the visual direction, relevant layout/interaction/motion decisions, and handoff to implementation clear without duplicating other owners' work. A text proposal alone is not visual acceptance.
- Coder: list actual changed files, behavior changes, and verification. Do not fix adjacent issues outside the assigned write scope.
- Reviewer: give severity, location, trigger/impact, and evidence for each actionable issue. State when none were found and identify the review scope. Label speculation.
- Tester: report actual commands/cases, outcomes, and coverage limits. A failed check is a valid finding; never weaken assertions or ignore failures to make results pass.
- Orchestrator: return the needed requirements, tradeoffs, interfaces, or dependency decisions. Do not duplicate the main agent's coordination or redistribute the entire task.

## Receiving and integrating work

1. Inspect relevant deliverables against acceptance criteria; distinguish subagent conclusions from verified facts.
2. Review shared changes directly. For isolated workspaces, review before integrating through the actual supported mechanism. Avoid duplicate patches and overwriting user changes.
3. Check behavior affected by integration, reusing completed checks that remain applicable.
4. Send only specific gaps and new evidence to the original agent rather than restarting the task.

## Partitioning examples

| Task | Appropriate scheduling |
| --- | --- |
| One copy change in a known component | Edit and check locally; no subagent model question. |
| A new visual experience with original art direction, substantial UI, or reactive motion | Include a Coder for substantive development and explicitly assess Designer for a useful design/asset/UI assignment. Agree interfaces and give the main agent integration and acceptance work. Explain any applicable local-execution exception. |
| Two modules with agreed interfaces and disjoint files | Use two Coders if beneficial; the main agent owns integration files and final validation. |
| A bounded nontrivial implementation that is expensive on the parent model | Assign at least one Coder, preferring a cheaper reliable model when supported and justified; include handoff, review, and latency even when execution is sequential. |
| A multi-level browser platformer with physics, scene mechanisms, and progress | Include a Coder owning the engine or another substantive implementation scope; assess Designer separately. The main agent defines interfaces, integrates, and accepts gameplay. |
| Cross-module bug without a known entry point or reproduction | Handle immediate blockers locally. Assign an independent hypothesis to one Explorer if useful; do not have everyone scan the repository. |
| Authorization-boundary change | Implement with Coder; use independent Reviewer assurance when valuable and Tester coverage of allowed/denied paths, respecting dependencies. |
| Low-risk change with valid verification | Check the deliverable and finish; do not add roles for completeness. |

## Evaluating the skill when requested

For a meaningful comparison, use comparable small, medium, and independently partitionable large tasks under the same requirements and quality gates. Record total parent/subagent tokens (including retries), cached and uncached effective cost where available, elapsed time, agent count, repeated reads, checks, and defects. Control model/runtime differences or disclose them. A faster parallel run does not prove lower token usage; lower cost does not prove equal quality. Do not run benchmarks as part of ordinary task completion or claim improvements without measurements.
