# AGENTS.md

This guide helps coding agents work effectively in this羽毛球培训会员管理系统 project.

## Project Overview

This is a full-stack badminton training management system with:
- **Frontend**: Vue3 + TypeScript + Vite + Element Plus
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic 2.x
- **Architecture**: Monorepo with separate frontend/ and backend/ directories

---

## Build/Lint/Test Commands

### Frontend (in `frontend/` directory)

**Install dependencies:**
```bash
pnpm install
```

**Development server:**
```bash
pnpm dev          # Start dev server with hot reload
pnpm prod         # Start prod server
```

**Build:**
```bash
pnpm build        # Type check + build for production
pnpm build:dev    # Build for dev environment
pnpm build:test   # Build for test environment
pnpm build:pro    # Build for prod environment
```

**Linting:**
```bash
pnpm run lint                     # Run all linters (eslint + prettier + stylelint)
pnpm run lint:eslint              # ESLint for .vue, .ts, .js files
pnpm run lint:prettier            # Prettier for code formatting
pnpm run lint:stylelint           # Stylelint for CSS/SCSS/Vue styles
```

**Type checking:**
```bash
pnpm run type-check               # Vue TypeScript type checking
pnpm run ts:check                 # TypeScript check with skipLibCheck
```

**Testing:**
No automated test framework configured for frontend currently.

### Backend (in `backend/` directory)

**Development server:**
```bash
python main.py run --env=dev      # Start dev server (default)
python main.py run --env=prod     # Start prod server
```

**Database migrations:**
```bash
python main.py revision --env=dev # Generate new migration script
python main.py upgrade --env=dev  # Apply all migrations
```

**Code quality:**
```bash
ruff check                        # Check Python code style
ruff check --fix                  # Auto-fix style issues
ruff check --watch                # Watch files and recheck
```

**Testing:**
```bash
pytest                            # Run all tests
pytest tests/test_main.py         # Run specific test file
pytest -v tests/                  # Run tests with verbose output
pytest -k test_check_health       # Run specific test by name pattern
```

**Note:** Test functions should use regular `def`, not `async def`.

---

## Code Style Guidelines

### Frontend (TypeScript/Vue3)

**Imports:**
- Auto-imported via `unplugin-auto-import`: Vue functions, VueRouter, Pinia, Element Plus components
- Manual imports needed for: custom components, utilities, types, API functions
- Import order: 1) Framework/Third-party, 2) Internal modules, 3) Relative imports
- Use `@/` alias for `src/` directory

**Formatting (Prettier):**
- Double quotes (`"`), single quotes for strings
- Semicolons required
- 2 spaces indentation (no tabs)
- Max line width: 100 characters
- Trailing commas for ES5-compatible objects/arrays
- Arrow functions always use parentheses: `(x) => x + 1`

**Vue Components:**
- Use `<script setup lang="ts">` syntax
- Define interfaces for props with `defineProps<Props>()`
- Emit events with `defineEmits<Emits>()`
- Use Composition API with `<script setup>`
- Component props must be typed with TypeScript interfaces

**TypeScript:**
- All functions must have explicit return types or inferred
- Use `interface` for object shapes, `type` for unions/primitives
- Type imports use `import type { ... }` for type-only imports
- Avoid `any` - use `unknown` or specific types

**Naming Conventions:**
- Components: PascalCase (e.g., `UserProfile.vue`, `DataTable.vue`)
- Files: kebab-case (e.g., `user-profile.vue`, `api/auth.ts`)
- Variables/functions: camelCase (e.g., `getUserInfo()`, `isLoading`)
- Constants: SCREAMING_SNAKE_CASE (e.g., `API_BASE_URL`)
- Pinia stores: camelCase with `.store.ts` suffix (e.g., `user.store.ts`)

**Error Handling:**
- Use try-catch for async operations in API calls
- Centralized error handling in `src/utils/request.ts` interceptors
- Show user-friendly messages via `ElMessage.error()`
- Never expose stack traces to users

**State Management (Pinia):**
- Stores located in `src/store/modules/`
- Export hook function: `export function useXxxStoreHook() { return useXxxStore(store); }`
- Persist stores with `persist: true` option
- Use actions for async operations, getters for derived state

**Styling:**
- Use UnoCSS utilities or Element Plus components
- Custom styles in `<style lang="scss" scoped>`
- Global variables imported from `@/styles/variables.scss`
- SCSS structure: follow BEM naming for custom classes

### Backend (Python/FastAPI)

**Architecture Pattern:**
```
module_*/
├── controller.py    # HTTP request handlers (API routes)
├── service.py       # Business logic layer
├── crud.py          # Database access layer
├── model.py         # SQLAlchemy ORM models
├── schema.py        # Pydantic models for validation
└── param.py         # Request parameter models
```

**Imports:**
- Standard library imports first
- Third-party imports second (FastAPI, SQLAlchemy, etc.)
- Local application imports last
- Group with blank lines between sections
- Use absolute imports: `from app.module_name import ...`

**Type Hints:**
- All function parameters must have type hints
- Return types required for all functions
- Use `from typing import ...` for generic types
- Use `Annotated` for FastAPI path/query/body parameters

**Naming Conventions:**
- Classes: PascalCase (e.g., `UserService`, `StudentModel`)
- Functions/methods: snake_case (e.g., `get_user_info()`, `create_student()`)
- Variables: snake_case (e.g., `user_id`, `is_active`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- File names: snake_case (e.g., `student_service.py`, `user_model.py`)

**Error Handling:**
- Use FastAPI's built-in exception handling
- Define custom exceptions in `app/common/exceptions.py`
- Use Pydantic's validation decorators for input validation
- Return standardized responses via `app/common/response.py`
- Log errors using loguru logger

**Async/Await:**
- Use `async def` for all I/O operations (database, HTTP, file I/O)
- Database operations with SQLAlchemy async session
- Use `await` for async operations (not for CPU-bound tasks)
- Never use `def` for test functions (use `def`, not `async def`)

**Database:**
- Use SQLAlchemy 2.0 async ORM
- Models define table structure and relationships
- CRUD operations in separate `crud.py` files
- Use Alembic for migrations - never modify schema directly
- All database access through CRUD layer (no SQL in controllers)

**API Design:**
- RESTful conventions (GET/POST/PUT/DELETE)
- Path parameters: `/{item_id}`
- Query parameters: `?page=1&size=10`
- Pydantic schemas for request/response validation
- Return consistent response structure: `{code, msg, data}`

**Logging:**
- Use `loguru` logger (configured in `app/core/logger.py`)
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR
- Include context in logs (user_id, action, etc.)

---

## Common Patterns

### Adding a New Feature

**Frontend:**
1. Create API client in `frontend/src/api/`
2. Create component in `frontend/src/views/` or `frontend/src/components/`
3. Add routing in `frontend/src/router/`
4. Create store if needed in `frontend/src/store/modules/`

**Backend:**
1. Create model in `backend/app/api/v1/module_*/model.py`
2. Create schema/param in `backend/app/api/v1/module_*/schema.py`
3. Create CRUD in `backend/app/api/v1/module_*/crud.py`
4. Create service in `backend/app/api/v1/module_*/service.py`
5. Create controller in `backend/app/api/v1/module_*/controller.py`
6. Generate and run database migration

### Code Review Checklist

- [ ] TypeScript/Python type hints complete
- [ ] Error handling in place
- [ ] No `any` types or bare `except` clauses
- [ ] Linting passes (`pnpm run lint` or `ruff check`)
- [ ] Type checking passes (`pnpm run type-check`)
- [ ] Tests added and passing
- [ ] Naming conventions followed
- [ ] Comments only for complex logic (not basic stuff)

---

## Important Notes

- **Never commit secrets** (.env, credentials, etc.)
- **Always run migrations** after model changes
- **Backend async functions**: use `await` for DB/API calls, not for CPU work
- **Frontend auto-imports**: Vue/Element Plus functions auto-imported, check `src/types/auto-imports.d.ts`
- **No comments needed** for self-explanatory code
- **Use Chinese** for user-facing text, English for code
- **Frontend uses pnpm** - not npm or yarn
- **Backend uses uv** for dependency management (uvx/uv sync)
