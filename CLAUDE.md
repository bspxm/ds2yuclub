# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

羽毛球培训会员管理系统（学期制课时结算），基于 FastApiAdmin 框架构建。

**技术栈**：
- 前端：Vue3 + TypeScript + Vite + Element Plus + UnoCSS + Pinia
- 后端：FastAPI + SQLAlchemy 2.0 (async) + Pydantic 2.x + Alembic + Redis
- 数据库：MySQL 8.0 / PostgreSQL（支持异步驱动 asyncmy/asyncpg）

---

## 常用命令

### 前端（在 `frontend/` 目录下）

```bash
pnpm install                      # 安装依赖
pnpm dev                          # 启动开发服务器（热重载）
pnpm build                        # 类型检查 + 生产构建
pnpm run lint                     # ESLint + Prettier + Stylelint
pnpm run type-check               # TypeScript 类型检查
```

### 后端（在 `backend/` 目录下）

```bash
# 启动服务
python main.py run --env=dev      # 开发环境启动（带热重载）
python main.py run --env=prod     # 生产环境启动

# 数据库迁移
python main.py revision --env=dev # 生成迁移脚本
python main.py upgrade --env=dev  # 应用迁移

# 代码检查与测试
ruff check                        # Python 代码风格检查
ruff check --fix                  # 自动修复
pytest                            # 运行所有测试
pytest tests/test_main.py -v      # 运行指定测试文件
```

---

## 架构要点

### 后端插件化架构

系统采用**自动路由发现机制**，所有业务模块放在 `backend/app/plugin/` 目录下：

- 模块目录必须以 `module_` 开头（如 `module_badminton`）
- `module_xxx` 自动映射为路由前缀 `/xxx`
- 每个模块的 `controller.py` 中的 `APIRouter` 实例会被自动发现并注册

**羽毛球业务模块结构** (`module_badminton`)：
```
├── student/      # 学员管理
├── class_/       # 班级管理
├── course/       # 课程管理
├── schedule/     # 排课管理
├── purchase/     # 购买记录
├── attendance/   # 出勤管理
├── semester/     # 学期管理
├── group/        # 能力分组
├── assessment/   # 能力评估
├── tournament/   # 比赛管理
├── leave/        # 请假管理
└── auth/         # 认证
```

每个子模块遵循分层架构：`controller.py` → `service.py` → `crud.py` → `model.py` + `schema.py`

### 前端结构

- `src/views/module_badminton/` - 羽毛球业务页面组件
- `src/api/module_badminton/` - 羽毛球业务 API 调用
- `src/store/` - Pinia 状态管理
- `src/router/` - Vue Router（动态菜单从后端加载）

### 配置文件

- 后端：`backend/env/.env.dev`（开发环境，需从 `.env.dev.example` 复制并修改）
- 前端：`frontend/.env.development`（开发环境）

---

## 开发约定

### 后端

- 所有 I/O 操作使用 `async def`，数据库操作通过 `async_db_session()`
- 枚举值必须大写（如 `ACTIVE`, `COMPLETED`）
- 使用 `Annotated` 定义 FastAPI 路径/查询参数
- 返回格式：`SuccessResponse(data=...)` 或 `ErrorResponse(...)`
- 权限控制：`Depends(AuthPermission(["module:sub:action"]))`

### 前端

- Vue 函数自动导入（ref, computed, watch 等），查看 `src/types/auto-imports.d.ts`
- 组件使用 `<script setup lang="ts">`，模板优先顺序
- 路径别名：`@/` 代替 `src/`
- 使用 pnpm，不用 npm/yarn

### 时间段格式

业务中的时间段使用 JSON 格式统一存储：
```json
{"周一": ["A", "B"], "周三": ["C"]}
```
时间段编码：A=08:00-09:30, B=09:30-11:00, C=14:00-15:30, D=15:30-17:00, E=18:00-19:30

---

## Docker 部署

```bash
./deploy.sh              # 一键部署
docker compose ps        # 查看容器状态
docker compose down      # 停止服务
```

服务端口：后端 8001，前端 5180，MySQL 3306，Redis 6379