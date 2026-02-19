# Telegram Alert Automations

Goal: Whenever a Kanban card changes columns (Backlog ↔ In Progress ↔ Review ↔ Done), Satya gets a concise Telegram DM from the Jobs agent summarizing the delta.

## Requirements
1. **Trigger** — Board update detected (manual edit, Jobs agent run, etc.).
2. **Delta capture** — Identify which cards changed column, their new status, and any notes.
3. **Message format** — Steve Jobs tone, ≤400 chars, with emoji headers:
   - ✅ (Done) items
   - ⚒️ (In Progress) focus + next action
   - ⚠️ blockers needing Satya
4. **Delivery** — Use OpenClaw `message` tool to DM Satya (Telegram ID 6308720344).
5. **Deduping** — Avoid sending multiple alerts for the same edit within 60 seconds.

## Architecture Sketch
```
kanban-board/KANBAN.md
      │
      ├─ (1) git diff or filesystem watcher catches change
      │
      ├─ (2) jobs_alert.py reads previous snapshot (kanban-board/.cache/state.json)
      │      and new KANBAN.md → computes column moves
      │
      ├─ (3) summary builder formats message text (Jobs tone)
      │
      └─ (4) calls OpenClaw message tool → Telegram DM
```

## Implementation Plan
1. **State cache** — store last-seen columns per card in `kanban-board/.cache/kanban_state.json`.
2. **Parser** — reuse `render_html.py` parsing logic (factor into shared module or duplicate helper) to map Markdown → cards.
3. **Diff logic** — compare previous vs current `column` and `done` state; collect events per column change.
4. **Message builder** — for each event:
   - Done → `✅ <title> done (owner).`
   - New In Progress → `⚒️ <title>: <next step/desc>.`
   - Blocker (optional tag) → `⚠️ <title> stuck — need <owner>/<ask>.`
5. **Delivery script (`jobs_alert.py`)**
   - CLI usage: `./jobs_alert.py --reason "manual update"`
   - Accept `--skip-if-stale <minutes>` to avoid spamming.
   - Calls OpenClaw messaging via subprocess (`openclaw message send ...`).
6. **Integration options**
   - After editing `KANBAN.md`, run `./jobs_alert.py` manually.
   - Embed inside Jobs PM Agent flow so every Jobs run ends by calling this script with the diff output.
7. **Future:** cron/FS watcher to auto-run on git commits.

## Next Actions
- [ ] Factor Markdown parsing helpers into `kanban-board/kanban_utils.py` for reuse by both renderer + alert script.
- [ ] Implement `jobs_alert.py` (reads new vs cached state, sends DM via `message` tool).
- [ ] Hook script into Jobs agent runbook (`jobs-agent/README.md`).
- [ ] Optionally auto-run after successful `git push` via simple pre-push hook.
