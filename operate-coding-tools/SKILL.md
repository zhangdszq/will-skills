---
name: 操控编程工具
description: Use this skill whenever the user wants Claude to operate local coding tools, especially Cursor-backed workflows. This includes two common modes: (1) real coding work through `delegate_to_cursor` or an equivalent "Claude plans, Cursor edits" path, and (2) direct inspection of local Cursor state such as available models, known projects, login status, or CLI capabilities. Be proactive: if the request is about actually changing code, or about checking what Cursor can do on this machine, use this skill instead of giving a generic chat answer.
---

# 操控编程工具

This skill helps Claude operate coding tools well.

The point is not to blindly offload work. The point is to choose the right operating mode:

- Claude plans and Cursor executes when the job is real repo work
- Claude directly inspects local Cursor tooling when the user wants facts about Cursor itself

## Two operating modes

### Mode A: delegate real coding work

Delegate when most of the value comes from actual code execution inside the repo:

- Multi-file edits
- Refactors with follow-up verification
- Feature implementation
- Bug fixes that require reading or changing multiple files
- Tasks that benefit from IDE context, file graph awareness, or running commands in the workspace

Usually do **not** delegate when the user mainly wants:

- An explanation of code
- A design discussion without implementation
- A tiny one-line answer
- Pure planning with no code changes yet

### Mode B: inspect Cursor locally

Use direct local inspection when the user asks about Cursor itself, for example:

- Which models are available in Cursor
- Which local projects Cursor knows about
- Whether Cursor Agent is logged in
- What Cursor CLI commands or capabilities exist on this machine

In these cases, do **not** default to `delegate_to_cursor`. First inspect local facts through available tooling such as:

- `cursor-agent models`
- `cursor-agent status` or related CLI commands
- `~/.local/bin/cursor-agent` if `cursor-agent` is not on PATH
- local Cursor config/state files such as `~/.cursor/ide_state.json`
- local Cursor project directories such as `~/.cursor/projects`

Do not say "I can't access your local Cursor" until you have actually checked.

## Operating model

Always think in this split:

- Claude: understand intent, define scope, set constraints, review outcomes
- Cursor: perform concrete coding steps, inspect files, edit code, run build/test commands

If delegation is appropriate, do not just say "I'll use Cursor." Give Cursor a crisp, executable brief.

If the request is about Cursor's local state, Claude should gather the facts directly and answer plainly.

## Workflow

### 1. Choose the right mode

Ask yourself:

- Is this about changing code in a repo?
- Or is it about checking Cursor's local state or capabilities?
- Would delegation help, or would direct local inspection be faster and more accurate?

If it is a Cursor-state question, inspect locally and answer directly.

If it is a real coding task, continue into delegation planning.

If the answer is mostly no, do the task normally and do not force delegation.

### 2. Analyze first

Before calling `delegate_to_cursor`, briefly reason about:

- The user goal
- The likely files or subsystems involved
- The desired constraints
- What success looks like

Do not dump a long essay to the user. This analysis exists so the delegated task is sharp rather than vague.

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

### 5. Review the result instead of parroting it

When Cursor returns:

- Distill the important outcome
- Surface changed areas, validation, and risks
- Mention if the result appears incomplete or if a follow-up delegation is needed

Claude should remain accountable for the final answer.

## Local inspection workflow

When the user asks about Cursor models, projects, login state, or similar local facts:

1. Identify the exact fact being asked for
2. Check the most direct local source first
3. Prefer command output over fallback config files whenever available
4. Summarize only the useful facts back to the user

Examples:

- Models: use `cursor-agent models`; if that binary is not on PATH, try common local install locations such as `~/.local/bin/cursor-agent`
- Local projects: inspect `~/.cursor/projects` and filter out obvious temporary directories when appropriate
- Recent files or current repo context: inspect `~/.cursor/ide_state.json` if relevant

If one command hangs or fails, try a nearby alternative before giving up.

For model queries, returning only the current default model from a config file is a fallback, not the preferred answer. If a CLI model-listing command is available, use it and return the actual list.

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
- Delegate with a concrete brief
- After the result returns, summarize the outcome rather than exposing raw internal chatter

When delegation is not appropriate:

- Say so implicitly by just helping directly
- Do not mention the skill or `delegate_to_cursor` unless it adds value

When direct local inspection is appropriate:

- Be factual
- Say what you checked
- Return the actual models, projects, or status you found
- Avoid generic UI instructions unless the user explicitly asked for navigation help

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

**Example 2: should delegate**

User:

```text
帮我修一下这个 runner 在 continue 模式下偶发丢 session 的问题，尽量最小改动，修完告诉我风险点。
```

Desired behavior:

- Recognize bug-fix plus repo investigation
- Delegate with constraints about minimal change and risk reporting

**Example 3: should not delegate**

User:

```text
解释一下 `runClaude()` 这段代码的大致流程。
```

Desired behavior:

- Answer directly
- Do not delegate because the user wants explanation, not execution

**Example 4: should inspect locally, not delegate**

User:

```text
看下 cursor 都有哪些项目和模型
```

Desired behavior:

- Recognize this is a local Cursor inspection request
- Check Cursor CLI and local Cursor state
- Return the actual project/model information found on the machine
- Do not claim inability before checking
