# Phase 5.4 Development Log

## 2026-03-18

### Context

Phase 5.3 delivered workspace runtime isolation and a frontend bootstrap gate, but did not deliver the actual bootstrap interaction loop.

The gap was structural:

- frontend had a gate card but no bootstrap chat mode
- backend had `bootstrap/start` status transition but no bootstrap runner body
- normal `/api/chat` had no strict bootstrap lifecycle ownership

### Decision

Phase 5.4 will implement bootstrap as a dedicated, strict chat-like initialization flow.

Key decision:

- bootstrap uses chat interaction
- bootstrap is not normal chat
- bootstrap is runner-owned lifecycle logic
- bootstrap completion is the only path into normal chat

### Required Correction

The earlier minimum-closure shortcut was rejected because the bootstrap initialization must follow the strict staged protocol defined by `BOOTSTRAP.md`.

Therefore the implementation direction changed from:

- single-turn bootstrap shortcut

to:

- staged runner with explicit Phase A-J coverage

### Current Work Items

1. add Phase 5.4 plan and log docs
2. implement backend bootstrap runner state machine
3. wire bootstrap route into `/api/chat`
4. switch frontend from gate-only to gate + bootstrap chat
5. add tests for pending -> running -> completed handoff

### Implemented

1. Added `runtime/bootstrap_runner.py`
2. Added a dedicated bootstrap session id: `__bootstrap__`
3. Upgraded `POST /api/workspaces/{workspace_id}/bootstrap/start`
   - now moves manifest to `running`
   - resets and seeds the bootstrap session
   - initializes bootstrap state
4. Upgraded `/api/chat`
   - normal chat now hard-blocks non-completed workspaces
   - `route=bootstrap` is handled by the bootstrap runner
   - bootstrap completion updates manifest to `completed`
   - bootstrap failure updates manifest to `failed`
5. Upgraded frontend app flow
   - `pending | failed` => gate
   - `running` => bootstrap chat
   - `completed` => normal chat
6. Fixed workspace creation UX
   - auto-generate safe `workspace_id` when the field is empty or unusable
   - surface create errors instead of silent failure

### Strict Bootstrap Flow Implemented

The runner now executes the protocol as a staged conversation:

1. Start bootstrap and seed the initialization brief
2. Collect Phase A Scope Discovery input
3. Collect Phase B asset intake input
4. Build Phase C lightweight parse handoff from uploaded asset metadata
5. Present Phase D confirmation draft plus Phase E generation plan preview
6. Require explicit user confirmation before file generation
7. Execute Phase F-H file generation
8. Update manifest via runner path
9. Return Phase J completion summary

### Generated Files

Current strict runner can generate:

- `memory/identity/workspace_scope.md`
- `memory/identity/project.md`
- `memory/identity/context_budget.md`
- conditional `lab_context.md` or `work_context.md`
- conditional timeline files
- conditional kickoff `Concept / Task / Pack` seed files

### Verification

Executed successfully:

- `python3 -m unittest ResearchAgentPrivateWorkspace/backend/tests/test_bootstrap_runner.py`
- `npm test -- --run src/app/App.test.tsx src/features/workspace/WorkspaceDialogs.test.tsx src/features/workspace/BootstrapGate.test.tsx src/features/chat/ChatPanel.test.tsx`
