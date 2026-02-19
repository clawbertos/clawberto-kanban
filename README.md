# Clawberto Mission Control

Live Kanban + status board for Satya ↔️ Clawberto operations.

- `KANBAN.md`: Source of truth for every task (Backlog → In Progress → Review → Done).
- `index.html`: Simple HTML render suitable for sharing/embedding.
- Updates: Jobs (our Steve Jobs-inspired PM agent) owns this board and announces significant changes directly to Satya on Telegram.

## Update Workflow
1. Edit `KANBAN.md` (or use the Jobs agent to do it).
2. Regenerate `index.html` (right now it is hand-authored; automation script is on the backlog).
3. Commit + push.
4. Jobs sends a Telegram DM if the change is meaningful.

More polish (automation, filtering, multi-agent hooks) is coming soon.
