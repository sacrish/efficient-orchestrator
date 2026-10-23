# Efficient Orchestrator

A Codex skill for completing tasks with selective subagent delegation, appropriate models, and controlled coordination overhead.

The main agent handles work directly by default. It delegates when a bounded assignment can reduce cost, shorten completion time, isolate distracting context, or improve quality enough to justify the handoff. Quality and the user's timing requirements take priority over resource savings.

## When to use it

- Develop features with independent implementation workstreams.
- Investigate a large codebase through focused searches.
- Create visual experiences that benefit from dedicated design work.
- Review or test changes where independent verification adds value.

Simple questions, small edits, and work covered by a single command usually stay with the main agent. Agent count grows with useful independent work rather than following a fixed pipeline.

## Installation

Copy the following files and directories into `$CODEX_HOME/skills/efficient-orchestrator/`. When `CODEX_HOME` is unset, the default location is `~/.codex/skills/efficient-orchestrator/`, or `%USERPROFILE%\.codex\skills\efficient-orchestrator\` on Windows.

```text
efficient-orchestrator/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|   `-- allocation-widget.html
|-- scripts/
|   `-- allocation_widget.py
`-- references/
    |-- allocation-ui.md
    |-- model-selection.md
    `-- task-contract.md
```

You can copy this README alongside them for convenience. Update all listed resources together. The allocation helper uses Python 3's standard library. If the skill does not appear immediately, refresh skill discovery or restart the client.

The skill uses the host's subagent tools and configured model catalog. Configure provider access in Codex or its model gateway before selecting a third-party model.

## Quick start

Invoke the skill with your task:

```text
Use $efficient-orchestrator to add a statistics dashboard with filters,
trend charts, and export. Delegate only where it improves efficiency
or quality, and verify the completed workflow.
```

Before starting a batch of new workers, the agent presents their assignments and recommended model/effort choices for confirmation. You can also provide preferences with the initial request; these seed recommendations rather than automatically approving new instances.

### Allocation controls

In a client supporting inline visualizations and their documented follow-up callback, each planned subagent gets linked model and reasoning dropdowns. Defaults reflect the main agent's recommendations. Confirm once for the batch; the host may additionally ask you to confirm sending the selection. Execution begins only after the selection arrives in chat and passes validation.

Newly required subagents appear in a fresh allocation form; unaffected confirmed workers keep their choices. Existing workers can continue the same assignment without another allocation. Unsupported clients use structured choice questions and explicit confirmation instead of nonfunctional dropdowns. A user may explicitly waive future allocation confirmations.

### Allow automatic selection

```text
Use $efficient-orchestrator to investigate and fix the failing import flow.
Choose models and reasoning effort automatically for all predefined roles.
Prioritize low total cost while meeting the acceptance criteria.
```

Automatic model selection prefers suitable official OpenAI models by default. To include configured third-party models in that comparison, add:

```text
Include configured third-party models in automatic model selection.
```

### Specify a model or reasoning effort

```text
Use $efficient-orchestrator to build the audio analysis module.
For Coder, use DeepSeek V4.1 Flash and choose reasoning effort automatically.
For Reviewer, choose the model automatically and use high reasoning effort.
```

This example assumes the named model is configured in your instance. A friendly name is resolved to its recorded model ID. If multiple versions or providers match, the agent asks which one you mean. Explicit effort must be supported by the chosen model and runtime; otherwise the agent asks how to proceed.

Skill files are written in English. The agent communicates in your preferred language.

## Roles and automatic model preferences

| Role | Responsibility | Automatic model preference |
| --- | --- | --- |
| Orchestrator | Requirements, architecture, scheduling, integration, and acceptance | Usually the main agent; strong reasoning for justified delegated architectural analysis. |
| Explorer | Targeted searches, file/symbol location, and flow tracing | Fast, low-cost models for bounded retrieval; upgrade for difficult semantic investigation. |
| Designer | Visual direction, art/assets, layout, interaction, and motion | Models with suitable design judgment and required visual/tool capabilities. |
| Coder | Features, fixes, and scoped refactoring | Reliable, cost-efficient balanced models; lighter models for mechanical work. |
| Reviewer | Correctness, code quality, and relevant security risks | Strong judgment for substantive review; balanced models for narrow routine checks. |
| Tester | Test design, test implementation, and regression verification | Lightweight models for established checks; balanced or stronger models for complex test design. |

These preferences apply to automatic selection and adapt to task complexity. They do not override explicit user choices. Automatic selection considers the role and expected total completion cost rather than always inheriting the main agent's model.

### Visual work

New visual direction, original art, substantial UI design, and meaningful animation or reactive feedback require an explicit Designer assessment during planning. A Designer subagent is preferred when it can produce an independently useful design brief, asset set, or bounded implementation. If substantial visual work stays with the main agent, it briefly explains why. Small changes to an established design can stay local.

### Temporary roles

When the predefined roles cannot cover a specific requirement, the main agent may define a temporary role with a clear scope and deliverable. You choose its model before it starts, even if all predefined roles already use automatic selection. You may explicitly choose automatic selection for that temporary role. The role lasts for the current task and related follow-ups.

## Model selection and compatibility

- User choices can refer to any model configured in the current instance, including third-party APIs, subject to explicit runtime constraints and actual call results.
- The agent preserves exact model IDs and routing prefixes. A name omitted from descriptive tool examples is treated as unverified rather than automatically rejected.
- Where permitted, compatibility is established through the first bounded assignment. A separate minimal probe is used only when useful, and its result is reused within the conversation.
- Spawn acceptance, successful completion, and verified model settings are separate evidence. A short text response does not establish complex tool compatibility or identify a gateway's downstream vendor.
- Model and reasoning preferences are independent. Omitted effort is selected automatically unless an earlier fixed preference applies. Unsupported explicit settings are clarified rather than silently replaced.
- Choices are reused within the conversation and retained across context compaction. Silence or an unsubmitted default is not consent to automatic model selection. An unavailable user-selected model requires a new choice.

## How resource use is controlled

Delegated tasks receive a compact brief with relevant context, write boundaries, dependencies, acceptance criteria, and stopping conditions. File ownership is kept separate, shared resources are coordinated, and existing agents are reused when appropriate.

Verification follows the change's risk. The main agent reviews actual deliverables and evidence, requests focused corrections when needed, and owns final integration and acceptance. Valid checks are reused; additional agents and repeated reviews need a concrete benefit. Git commits require an explicit user request.

Parallel execution can shorten elapsed time while increasing total tokens. Lower model prices can reduce fees without reducing tokens. Savings should be reported only when measured across the complete task, including coordination, review, and retries.

## Files

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill entry point and delegation, role, scheduling, and acceptance rules. |
| [references/model-selection.md](references/model-selection.md) | Model identity resolution, role preferences, reasoning selection, compatibility checks, and recovery. |
| [references/allocation-ui.md](references/allocation-ui.md) | Confirmed allocation batches, supported host callbacks, fallback questions, and response validation. |
| [scripts/allocation_widget.py](scripts/allocation_widget.py) | Builds forms from the instance catalog and validates confirmed selections with duplicate-submission receipts. |
| [assets/allocation-widget.html](assets/allocation-widget.html) | Linked model/effort controls with recommended defaults and explicit submission. |
| [references/task-contract.md](references/task-contract.md) | Minimal assignment and completion-report formats, evidence requirements, and partitioning examples. |
| [agents/openai.yaml](agents/openai.yaml) | Display metadata for Codex. |
