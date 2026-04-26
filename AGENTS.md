# AGENTS.md

Badminton training management system (羽毛球培训会员管理系统). Monorepo: `frontend/` + `backend/`.

## Modification Restrictions

Only modify files under these paths without asking:

**Frontend:**
- `frontend/src/api/module_badminton/`
- `frontend/src/views/module_badminton/`

**Backend:**
- `backend/app/plugin/module_badminton/`

**Menu SQL:**
- `backend/sql/postgres/menu/`

Modifying any other file requires explicit user approval first (e.g. `router/index.ts`, `permission.store.ts`, `layouts/`, `composables/`, `store/`, config files, etc.).

## Commands

### Frontend (`frontend/`, pnpm only)

```bash
pnpm install                 # install deps
pnpm dev                     # Vite dev server on :5180
pnpm build                   # vue-tsc --noEmit + vite build
pnpm run ts:check            # vue-tsc --noEmit --skipLibCheck
pnpm run lint                # eslint → prettier → stylelint (in sequence)
```
No frontend tests.

### Backend (`backend/`, uv + .venv)

```bash
.venv/bin/python main.py run --env=dev       # dev server on :8771 (hot reload)
.venv/bin/python main.py revision --env=dev  # generate Alembic migration
.venv/bin/python main.py upgrade --env=dev   # apply migrations
ruff check                                    # lint (global install)
ruff check --fix                              # auto-fix
pytest                                        # tests (use sync `def`, never `async def`)
```
Config: copy `backend/env/.env.dev.example` → `backend/env/.env.dev`.

## Architecture

### Backend: Plugin Auto-Discovery

Routes auto-discovered by `app/core/discover.py`. It scans `app/plugin/module_*/` directories — `module_xxx` maps to route prefix `/xxx` (e.g. `module_badminton` → `/badminton`). Any `controller.py` with an `APIRouter` instance is auto-registered. **No manual router registration needed.**

Each module dir: `model.py` → `schema.py` → `crud.py` (extends `CRUDBase`) → `service.py` → `controller.py`.

Modules: `assessment`, `attendance`, `auth`, `course`, `group`, `leave`, `purchase`, `schedule`, `semester`, `student`, `team`, `tournament`.  
Shared: `enums.py`, `cache_utils.py`, `response.py`.

### Frontend: Dynamic Menus

Most routes come from DB `sys_menu` table via `permission.store.ts`. Static routes (login, 401/404/500, home, and `/m/` mobile) live in `src/router/index.ts`.

Menu/permission SQL: `backend/sql/postgres/menu/sync_badminton_menu.sql`. Runs as DELETE+INSERT — not idempotent UPSERT.

- Views: `src/views/module_badminton/`
- API clients: `src/api/module_badminton/`
- Auto-imports (vue, @vueuse/core, pinia, vue-router, Element Plus) — see `src/types/auto-imports.d.ts`
- Vant 4 auto-imported for mobile pages — VantResolver in `vite.config.ts`
- Pinia stores: `src/store/modules/`

### Mobile Pages (`/m/badminton/`)

Static routes (not from DB), use Vant 4 and `layouts/mobile.vue`.

| Prefix | Pages |
|--------|-------|
| `/m/badminton/coach/` | `home`, `attendance`, `schedule`, `tournament-list`, `tournament-matches`, `match-score`, `assessment-compose` |
| `/m/badminton/parent/` | `student`, `tournament`, `h2h` |

Role-based redirect in `plugins/permission.ts`: non-superuser + role `PARENTS` → `/m/badminton/parent/student`, else → `/m/badminton/coach/home`.

## Key Conventions

- **Enum values UPPERCASE** in PostgreSQL (`ACTIVE`, `COMPLETED`)
- **Time slots** as JSON: `{"周一": ["A", "B"]}`. Codes: A=08:00-09:30, B=09:30-11:00, C=14:00-15:30, D=15:30-17:00, E=18:00-19:30. Used in `team.time_slots_json`, `purchase.selected_time_slots`, `schedule.time_slots_json`.
- **Chinese** for user-facing text, English for code
- **No comments** on self-explanatory code
- Vue: `<script setup lang="ts">`, path alias `@/` → `src/`
- Backend `ModelMixin` provides `description` field (not `notes`)
- Permissions: `module_badminton:<module>:<action>` (e.g. `module_badminton:team:list`)
- `ClassAttendanceModel` lacks a `notes` field — uses `coach_comments` / `parent_comments` instead


### 输出语言
- 所有输出必须使用中文（思考过程、分析、回答）

## Ports

- Frontend dev: 5180
- Backend API: 8771
- API docs: http://localhost:8771/docs

## Docker

```bash
./deploy.sh        # one-command deploy
docker compose ps
docker compose down
```

## Adding a New Backend Module

```bash
mkdir backend/app/plugin/module_badminton/{name}/
# model.py → schema.py → crud.py → service.py → controller.py
```
Add model import to `module_badminton/__init__.py`, then:
```bash
.venv/bin/python main.py revision --env=dev
.venv/bin/python main.py upgrade --env=dev
```
Add menu + permissions entries to `sync_badminton_menu.sql`.

## Adding a New Frontend Feature

1. API client in `src/api/module_badminton/`
2. View in `src/views/module_badminton/`
3. Add menu/permission rows to `sync_badminton_menu.sql` (for PC dynamic routes) or add static route in `src/router/index.ts` (for `/m/` mobile routes).
