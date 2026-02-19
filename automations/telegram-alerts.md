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

## Implementation Plan (v1 COMPLETE)
1. **State cache** — `kanban-board/.cache/kanban_state.json` stores last-seen board snapshot.
2. **Parser** — `kanban_utils.py` exposes `load_board` + `summarize_delta` for reuse (renderer + alerts share the same logic).
3. **Diff logic** — `summarize_delta(prev, curr)` compares column + done states and returns per-column change lists.
4. **Message builder** — `jobs_alert.py` maps columns to emoji (✅/⚒️/🕵️/📝) and narrates the change (`moved into`, `marked done`, `reopened`, etc.).
5. **Delivery script (`kanban-board/jobs_alert.py`)**
   - Usage: `./kanban-board/jobs_alert.py` (adds `--dry-run` to preview).
   - Automatically initializes cache on first run, sends Telegram DM via `openclaw message send --channel telegram --to 6308720344` afterward, then updates cache.
6. **Integration options (next):**
   - Call script at the end of every Jobs PM Agent run.
   - Optional git hook/cron to run after `KANBAN.md` commits.
7. **Future enhancements:** throttle window, richer context (links to commits), auto-tag blockers.

## Next Actions
- [ ] Factor Markdown parsing helpers into `kanban-board/kanban_utils.py` for reuse by both renderer + alert script.
- [ ] Implement `jobs_alert.py` (reads new vs cached state, sends DM via `message` tool).
- [ ] Hook script into Jobs agent runbook (`jobs-agent/README.md`).
- [ ] Optionally auto-run after successful `git push` via simple pre-push hook.
