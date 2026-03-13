---
name: 操控编程工具
description: Use this skill whenever the user wants work to be carried out through Cursor-backed workflows and expects Cursor to do the actual analysis. This includes real repo work and Cursor-local inspection tasks. Critical rule: once this skill is invoked, the current operator model should not do the substantive analysis itself. It should route the task to Cursor, pass scope and constraints, and then review and summarize Cursor's result. If the task should be answered directly without Cursor, do not use this skill.
---

# 操控编程工具

This skill helps Claude use Cursor correctly.

The key rule is simple:

- If this skill triggers, Cursor must do the substantive analysis
- The current operator model may decide whether to use the skill, set constraints, and summarize results
- The current operator model must not trigger the skill and then do the real work itself

## When to use this skill

Use this skill when most of the value should come from Cursor working inside the user's local environment, for example:

- Multi-file edits
- Refactors with follow-up verification
- Feature implementation
- Bug fixes that require reading or changing multiple files
- Tasks that benefit from IDE context, file graph awareness, or running commands in the workspace
- Requests to inspect Cursor-local facts such as available models, known projects, login status, or CLI capabilities, when the user wants Cursor to check them on-machine

## When not to use this skill

If the task should be answered directly, do not invoke this skill at all. Usually skip it when the user mainly wants:

- An explanation of code
- A design discussion without implementation
- A tiny one-line answer
- Pure planning with no code changes yet

## Operating model

Always think in this split:

- Operator model: decide whether this skill is appropriate, define scope, set constraints, review outcomes
- Cursor: analyze the repo or local Cursor state, inspect files, edit code, run build/test commands, gather facts

If this skill is invoked, do not just say "I'll use Cursor." Give Cursor a crisp, executable brief and let Cursor do the actual investigation.

If the request should be answered without Cursor, skip this skill and help directly.

## Hard boundary

Once this skill is invoked, the operator model must **not**:

- inspect the repo itself and then merely ask Cursor to implement
- inspect local Cursor state itself and then merely rephrase the answer
- solve the task from generic reasoning while pretending Cursor was involved

Once this skill is invoked, the operator model may:

- identify the user goal
- write a bounded brief
- specify repo, directory, scope, and constraints
- ask for validation
- summarize Cursor's returned results for the user

## Workflow

### 1. Decide whether the skill should trigger

Ask yourself:

- Should Cursor perform the real analysis here?
- Is the user asking for on-machine repo work or Cursor-local inspection?
- If I answer directly, would that violate the user's expectation that Cursor should do the work?

If the answer is yes, invoke this skill and route the task to Cursor.

If the answer is no, do not use this skill. Help directly instead.

### 2. Do only routing analysis

Before calling `delegate_to_cursor` or the equivalent Cursor path, the operator model should do only enough thinking to route well:

- The user goal
- The likely files or subsystems involved
- The desired constraints
- What success looks like

Do not do the substantive repo investigation yourself. This routing analysis exists only so the delegated task is sharp rather than vague.

### 3. Write a strong delegation brief

When you delegate, package the request so Cursor can execute without guessing.

Include these ingredients whenever relevant:

- Goal: what to implement, fix, or refactor
- Scope: repo, directory, or subsystem
- Constraints: avoid unrelated changes, preserve behavior, no commit unless asked
- Validation: compile, test, or smoke-check if appropriate
- Deliverable: what Cursor should report back

Good delegation tasks are concrete and bounded.

Bad:

```text
Please handle this in Cursor.
```

Good:

```text
Implement the requested bug fix in the current repo.
- Investigate the failing behavior in the session runner path
- Make the minimum safe code changes
- Avoid unrelated edits
- Run the relevant compile or test command if available
- Return a concise summary of changed files, validation run, and any remaining risk
```

### 4. Prefer one coherent delegation over many tiny ones

If the task is a single coherent coding unit, send one well-structured delegation request.

Only split into multiple delegations when there are clearly separable phases, such as:

- first investigate, then implement
- first refactor backend, then adjust frontend wiring

### 5. For Cursor-local inspection, still delegate

When the user asks about Cursor models, projects, login state, or similar local facts, Cursor should perform the inspection.

Ask Cursor to check the most direct local source first, such as:

- `cursor-agent models`
- `cursor-agent status` or related CLI commands
- `~/.local/bin/cursor-agent` if `cursor-agent` is not on PATH
- local Cursor config/state files such as `~/.cursor/ide_state.json`
- local Cursor project directories such as `~/.cursor/projects`

The operator model should not gather these facts itself once the skill has triggered.

### 6. Review the result instead of parroting it

When Cursor returns:

- Distill the important outcome
- Surface changed areas, validation, and risks
- Mention if the result appears incomplete or if a follow-up delegation is needed

The operator model remains accountable for the final answer, but Cursor owns the analysis path.

## Default delegation template

Use this shape when you need to build a `task` payload:

```text
Work in the current repository and complete this coding task:

<goal>

Constraints:
- Keep changes focused
- Avoid unrelated edits
- Do not commit unless explicitly requested

Validation:
- Run the most relevant compile/test/smoke check if practical

Return:
- What you changed
- Which files were touched
- What validation you ran
- Any remaining caveats
```

If the environment supports passing `cwd`, provide it when the target directory matters.

## Response style

When delegation is appropriate:

- Be decisive
- Delegate with a concrete brief and let Cursor perform the analysis
- After the result returns, summarize the outcome rather than exposing raw internal chatter

When delegation is not appropriate:

- Say so implicitly by just helping directly
- Do not mention the skill or `delegate_to_cursor` unless it adds value

## Examples

**Example 1: should delegate**

User:

```text
在当前项目里给 settings 页面加一个“导出配置”按钮，并把 Electron 主进程打通，最后跑一下编译。
```

Desired behavior:

- Recognize that this is a real multi-file implementation task
- Use `delegate_to_cursor`
- Provide a bounded brief mentioning UI + Electron wiring + compile verification
- Let Cursor do both investigation and implementation rather than pre-analyzing it locally

**Example 2: should delegate**

User:

```text
帮我修一下这个 runner 在 continue 模式下偶发丢 session 的问题，尽量最小改动，修完告诉我风险点。
```

Desired behavior:

- Recognize bug-fix plus repo investigation
- Delegate with constraints about minimal change and risk reporting
- Let Cursor perform the bug investigation itself

**Example 3: should not delegate**

User:

```text
解释一下 `runClaude()` 这段代码的大致流程。
```

Desired behavior:

- Answer directly
- Do not use this skill because the user wants explanation, not execution

**Example 4: should delegate Cursor-local inspection**

User:

```text
看下 cursor 都有哪些项目和模型
```

Desired behavior:

- Recognize this is a local Cursor inspection request
- Use Cursor to check Cursor CLI and local Cursor state
- Return the actual project/model information found on the machine
- Do not let the operator model do the inspection itself
