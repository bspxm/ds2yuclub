# FastApiAdmin - 项目上下文文档

本文档为 FastApiAdmin 项目的综合上下文指南，旨在为 iFlow CLI 提供快速上手指令和项目理解。

## 项目概述

**FastApiAdmin** 是一套完全开源、高度模块化、技术先进的现代化快速开发平台，旨在帮助开发者高效搭建高质量的企业级中后台系统。该项目采用前后端分离架构，融合 Python 后端框架 `FastAPI` 和前端主流框架 `Vue3` 实现多端统一开发。

### 核心特性
- 🔥 **现代化技术栈**: FastAPI + Vue3 + TypeScript
- ⚡ **高性能异步**: 利用 FastAPI 异步特性和 Redis 缓存优化
- 🔐 **安全可靠**: JWT + OAuth2 认证机制，RBAC 权限控制
- 🧱 **模块化设计**: 高度解耦的系统架构，便于扩展和维护
- 🌐 **全栈支持**: Web端 + 移动端(H5) + 后端一体化解决方案
- 🚀 **快速部署**: Docker 一键部署，支持生产环境快速上线
- 🤖 **AI集成**: 内置 LangChain 支持 OpenAI 和 Anthropic 模型

### 当前应用
基于 FastApiAdmin 平台开发的 **羽毛球培训会员管理系统**，实现了学员管理、班级管理、课程排班、购买记录、考勤管理、比赛管理、能力评估、分组管理等核心业务功能。系统采用学期制课时结算模式，支持固定班和自选天两种班级类型。

## 项目结构

```
FastapiAdmin/
├── backend/               # 后端工程 (FastAPI + Python)
│   ├── app/
│   │   ├── plugin/       # 插件模块目录
│   │   │   ├── module_application/  # 应用模块
│   │   │   ├── module_badminton/  # 羽毛球培训业务模块 (自动映射为 /badminton)
│   │   │   │   ├── assessment/   # 能力评估
│   │   │   │   ├── attendance/    # 出勤管理
│   │   │   │   ├── auth/          # 认证系统
│   │   │   │   ├── class_/        # 班级管理
│   │   │   │   ├── course/        # 课程管理
│   │   │   │   ├── group/         # 能力分组
│   │   │   │   ├── leave/         # 请假管理
│   │   │   │   ├── purchase/      # 购买记录
│   │   │   │   ├── schedule/      # 课程调度
│   │   │   │   ├── semester/      # 学期管理
│   │   │   │   ├── student/       # 学员管理
│   │   │   │   └── tournament/    # 比赛管理
│   │   │   ├── module_example/    # 示例模块
│   │   │   └── module_generator/  # 代码生成模块
│   │   └── ...
│   ├── env/               # 环境配置
│   ├── sql/               # 数据库SQL文件
│   ├── logs/              # 日志文件
│   ├── main.py            # 主程序入口
│   ├── requirements.txt   # Python依赖 (pip)
│   ├── pyproject.toml     # Python依赖 (uv)
│   └── .python-version    # Python版本锁定
├── frontend/             # Web前端工程 (Vue3 + Element Plus)
│   ├── src/
│   │   ├── api/          # API调用模块
│   │   ├── views/        # 页面组件
│   │   │   └── module_badminton/  # 羽毛球业务页面
│   │   │       ├── assessment/
│   │   │       ├── class/
│   │   │       ├── class-attendance/
│   │   │       ├── class-schedule/
│   │   │       ├── course/
│   │   │       ├── group/
│   │   │       ├── leave-request/
│   │   │       ├── parent/
│   │   │       ├── purchase/
│   │   │       ├── semester/
│   │   │       ├── student/
│   │   │       └── tournament/
│   │   └── ...
│   ├── .env.development.example
│   ├── .env.production.example
│   ├── package.json
│   └── pnpm-lock.yaml
├── devops/               # 部署配置 (Docker, Nginx)
├── docs/                 # 业务相关文档
│   ├── 分组循环赛.md
│   ├── 分组循环赛（纯小组赛）.md
│   ├── 定区升降赛.md
│   └── 小组单败制淘汰赛.md
├── docker-compose.yaml   # Docker编排文件
├── deploy.sh             # 一键部署脚本
├── LICENSE               # MIT开源协议
├── README.md             # 中文文档
└── README.en.md          # 英文文档
```

## 技术栈详情

### 后端技术栈 (backend/)
- **Python版本**: 3.10 (由 `.python-version` 文件指定)
- **框架**: FastAPI 0.115.2 + Uvicorn 0.30.6
- **数据库 ORM**: SQLAlchemy 2.0.45
  - MySQL: asyncmy 0.2.9 (异步), PyMySQL 1.1.2 (同步)
  - PostgreSQL: asyncpg 0.30.0 (异步), psycopg2-binary 2.9.10 (同步)
  - SQLite: aiosqlite 0.17.0 (异步)
- **缓存**: Redis 7.1.0
- **任务调度**: APScheduler 3.11.0
- **认证授权**: PyJWT 2.9.0, OAuth2
- **数据验证**: Pydantic 2.0+
- **数据库迁移**: Alembic 1.15.1
- **日志系统**: loguru 0.7.3
- **API限流**: fastapi-limiter 0.1.6
- **AI集成**: langchain 1.2.0 (支持 OpenAI, Anthropic)
- **包管理器**: 支持 pip (requirements.txt) 和 uv (pyproject.toml + uv.lock)
- **镜像源**: 清华大学镜像 (pypi.tuna.tsinghua.edu.cn/simple)

### 前端技术栈 (frontend/)
- **框架**: Vue 3.5.17 + TypeScript 5.8.3
- **构建工具**: Vite 6.3.5
- **UI组件库**: Element Plus 2.10.4
- **状态管理**: Pinia 3.0.3
- **路由**: Vue Router 4.5.1
- **HTTP客户端**: Axios 1.10.0
- **CSS框架**: UnoCSS 66.2.3
- **代码规范**: ESLint 9.32.0, Prettier 3.6.2, Stylelint 16.25.0
- **包管理**: pnpm 9.15.3 (配置了淘宝镜像 registry=https://registry.npmmirror.com)

## 环境要求

| 组件 | 版本要求 |
|------|----------|
| Python | = 3.10 (由项目指定) |
| Node.js | ≥ 18.0 (实际要求 >= 20.0) |
| npm | ≥ 10.0.0 |
| pnpm | ≥ 8.1.0 |
| MySQL | ≥ 8.0 |
| Redis | ≥ 6.0 |
| Docker | 最新版本 |
| Docker Compose | 最新版本 |

## 快速开始

### 1. 环境配置

```bash
# 克隆项目 (如果尚未克隆)
git clone https://gitee.com/tao__tao/FastapiAdmin.git
cd FastapiAdmin
```

### 2. 后端配置与启动

```bash
# 进入后端目录
cd backend

# 配置环境变量
cp env/.env.dev.example env/.env.dev
cp env/.env.prod.example env/.env.prod

# 编辑 .env.dev 文件，修改数据库和Redis配置
# DATABASE_HOST, DATABASE_PASSWORD, REDIS_HOST 等

# 安装依赖 (两种方式可选)
# 方式一：使用 pip (传统方式)
pip3 install -r requirements.txt

# 方式二：使用 uv (推荐，速度更快)
# 如果没有 uv，先安装: pip install uv
uv pip install -r requirements.txt
# 或者直接使用 pyproject.toml
uv pip install .

# 启动开发服务器
python main.py run --env=dev

# 或使用特定环境
python main.py run --env=prod
```

**后端管理命令**:
```bash
# 生成数据库迁移文件
python main.py revision --env=dev

# 应用数据库迁移
python main.py upgrade --env=dev

# 查看帮助
python main.py --help
```

### 3. 前端配置与启动

```bash
# 进入前端目录
cd frontend

# 配置环境变量
cp .env.development.example .env.development
cp .env.production.example .env.production

# 编辑 .env.development 文件，修改API代理地址
# VITE_API_BASE_URL, VITE_APP_PORT 等

# 安装依赖 (使用pnpm，已配置淘宝镜像加速)
pnpm install

# 启动开发服务器
pnpm run dev

# 构建生产版本
pnpm run build
```

**前端常用命令**:
```bash
# 代码检查
pnpm run lint

# 类型检查
pnpm run type-check

# 代码格式化
pnpm run lint:format

# 预览生产构建
pnpm run preview
```

## Docker 部署

### 一键部署脚本

```bash
# 赋予执行权限
chmod +x deploy.sh

# 完整部署
./deploy.sh

# 仅停止容器
./deploy.sh --stop

# 仅启动容器
./deploy.sh --start

# 查看容器日志
./deploy.sh --logs
```

### Docker Compose 手动部署

```bash
# 构建并启动所有服务
docker compose up -d --build

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 服务访问地址

| 服务 | 本地访问地址 | 容器内端口 |
|------|--------------|------------|
| 后端API | http://127.0.0.1:8771 | 8771 |
| Swagger文档 | http://127.0.0.1:8771/api/v1/docs | - |
| ReDoc文档 | http://127.0.0.1:8771/api/v1/redoc | - |
| 前端开发服务器 | http://127.0.0.1:5180 | 5180 |
| 前端生产构建 | http://localhost/web | 80 |
| MySQL | localhost:3306 | 3306 |
| Redis | localhost:6379 | 6379 |

## 开发约定与架构

### 后端插件化架构

项目采用**插件化架构设计**，二次开发应在 `backend/app/plugin/` 目录下进行：

```
backend/app/plugin/
├── module_application/  # 应用模块 (自动映射为 /application)
├── module_badminton/   # 羽毛球培训业务模块 (自动映射为 /badminton)
│   ├── assessment/       # 能力评估模块
│   │   ├── controller.py
│   │   ├── model.py
│   │   ├── schema.py
│   │   ├── service.py
│   │   └── crud.py
│   ├── attendance/        # 出勤管理模块
│   ├── auth/             # 认证系统模块
│   ├── class_/            # 班级管理模块
│   ├── course/            # 课程管理模块
│   ├── group/             # 能力分组模块
│   ├── leave/             # 请假管理模块
│   ├── purchase/          # 购买记录模块
│   ├── schedule/          # 课程调度模块
│   ├── semester/          # 学期管理模块
│   ├── student/           # 学员管理模块
│   └── tournament/        # 比赛管理模块
├── module_example/      # 示例模块 (自动映射为 /example)
├── module_generator/    # 代码生成模块 (自动映射为 /generator)
└── init_app.py         # 插件初始化文件
```

**自动路由注册规则**:
1. 控制器文件必须命名为 `controller.py`
2. 路由自动映射：`module_xxx` → `/xxx`
3. 支持多个 `APIRouter` 实例
4. 自动处理路由去重

### 羽毛球业务模块功能

羽毛球培训管理系统包含以下核心功能模块：

| 模块 | 功能描述 |
|------|----------|
| **学员管理** | 学员档案、家长关联、能力评估记录（9项能力评分） |
| **班级管理** | 班级创建、状态管理、时间段配置、学期关联、固定班/自选天 |
| **课程管理** | 课程信息、报班管理、课程调度 |
| **购买记录** | 购买记录创建、批量创建、时间段选择（A-E五个时间段）、课时包/单次课支持 |
| **学期管理** | 学期创建、状态管理、学期类型（常规/夏季/冬季/冬夏令营） |
| **课程调度** | 课程排班、时间表管理、V2版本支持多时间段排课 |
| **出勤管理** | 出勤记录、考勤统计、自动扣减课时 |
| **请假管理** | 请假申请、审批流程 |
| **能力评估** | 9项能力评分：手法、步法、战术、力量、速度、体能、进攻、防守、心理 |
| **比赛管理** | 赛事创建、分组循环赛、定区升降赛、小组单败制淘汰赛 |
| **能力分组** | 学员分组管理、教练分配、学员分组 |
| **认证系统** | 用户名登录、手机号登录（已支持） |

### 关键功能特性

#### 排课管理 V2 (Class Schedule V2)
**新增功能**:
- 支持学期选择和日期选择
- 左侧显示可用学员列表（基于时间段配置筛选）
- 右侧表单包含：班级、教练、时间段、排课状态
- 时间段支持多选（A-E五个时间段可选多个）
- 学员支持多选
- 自动为选中学员创建考勤记录
- 自动扣减学员课时
- 弹窗宽度优化为 1400px

**技术实现**:
- `ClassScheduleCreateV2Schema`: V2版本创建Schema，支持 `time_slot_ids: list[int]`
- `ClassScheduleOutSchema`: 响应Schema，直接继承 `BaseSchema` 和 `UserBySchema`，与数据库模型 `ClassScheduleModel` 字段完全匹配
- `get_available_students_service`: 根据时间段筛选可用学员
- `create_v2_service`: 为每个时间段创建排课记录和考勤记录
- 前端使用 Element Plus 多选下拉框和复选框组

**重要修复 (2026-01-30)**:
- 修复了 `ClassScheduleOutSchema` 的 Pydantic 验证错误
- 原问题：Schema 继承自 `ClassScheduleCreateV2Schema`，导致期望 `class_ids` (列表)、`time_slot_ids` (列表)、`semester_id`、`student_ids` 等字段
- 解决方案：重构 `ClassScheduleOutSchema` 直接继承 `BaseSchema` 和 `UserBySchema`，定义与数据库模型匹配的字段（`class_id`、`time_slot_id` 等）

#### 购买记录时间段选择
**功能特点**:
- 单个新增和批量新增都支持时间段选择
- 时间段按星期分组显示（周一到周日）
- 固定班自动全选所有时间段，用户不可修改
- 自选天需要手动选择，根据每周课次进行验证
- 时间段配置存储在班级的 `time_slots_json` 字段中

**时间段定义**:
- A: 08:00-09:30 (90分钟)
- B: 09:30-11:00 (90分钟)
- C: 14:00-15:30 (90分钟)
- D: 15:30-17:00 (90分钟)
- E: 18:00-19:30 (90分钟)

#### 能力分组系统
**功能描述**:
- 学员分组管理（AbilityGroupModel）
- 教练-分组多对多关系（GroupCoachModel）
- 学员-分组多对多关系（GroupStudentModel）
- 支持分组创建、编辑、删除
- 支持教练和学员的分组分配

**技术特点**:
- 使用 SQLAlchemy 的 relationship 实现多对多关系
- 支持分组描述和备注
- 级联删除和更新

### 代码生成器

项目内置代码生成器，可根据数据库表结构自动生成前后端CRUD代码：

1. 登录系统 (admin/123456)
2. 进入"代码生成"模块
3. 导入表结构并配置参数
4. 生成代码并下载/写入项目

### 权限控制系统

- **RBAC模型**: 基于角色的访问控制
- **JWT认证**: 访问令牌和刷新令牌机制
- **操作日志**: 自动记录用户操作
- **API限流**: 防止恶意请求

## 配置文件说明

### 后端配置 (backend/app/config/setting.py)

关键配置项:
```python
# 数据库配置
DATABASE_TYPE = 'mysql'  # mysql/postgres/sqlite
DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'your_password'
DATABASE_NAME = 'fastapiadmin'

# Redis配置
REDIS_ENABLE = True
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB_NAME = 1

# JWT配置
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 86400  # 1天
REFRESH_TOKEN_EXPIRE_MINUTES = 604800  # 7天
```

### 前端配置 (frontend/.env.development)

```env
# 开发环境配置
VITE_APP_PORT=5180
VITE_APP_BASE_API=/api/v1
VITE_API_BASE_URL=http://127.0.0.1:8771
```

## 包管理器说明

### 后端包管理
项目同时支持两种包管理方式：
1. **传统方式**: `requirements.txt` + `pip`
2. **现代方式**: `pyproject.toml` + `uv` (推荐)
   - 使用 `uv pip install .` 安装依赖
   - `uv.lock` 确保依赖版本一致性
   - 配置了清华镜像源加速下载

### 前端包管理
- 使用 `pnpm` 作为包管理器
- 配置了淘宝镜像 (`registry=https://registry.npmmirror.com`)
- 锁定文件: `pnpm-lock.yaml`

## 测试与质量保证

### 后端测试
```bash
# 运行测试 (需要先配置测试环境)
cd backend
pytest tests/
```

### 前端代码质量
```bash
cd frontend

# ESLint检查
pnpm run lint:eslint

# 类型检查
pnpm run type-check

# Stylelint检查
pnpm run lint:style

# Prettier格式化
pnpm run lint:prettier
```

## 数据库迁移

### 创建迁移
```bash
cd backend
python main.py revision --env=dev
```

### 应用迁移
```bash
python main.py upgrade --env=dev
```

### 迁移文件位置
```
backend/app/alembic/versions/
```

## 常见问题与解决

### 1. 数据库连接失败
- 检查 `backend/env/.env.dev` 中的数据库配置
- 确认MySQL服务已启动且可访问
- 验证用户名和密码正确性

### 2. Redis连接失败
- 检查Redis服务是否运行: `redis-cli ping`
- 验证 `backend/env/.env.dev` 中的Redis配置
- 确认Redis密码是否正确

### 3. 前端代理配置错误
- 检查 `frontend/.env.development` 中的 `VITE_API_BASE_URL`
- 确认后端服务正在运行且端口正确
- 查看浏览器开发者工具中的网络请求

### 4. 依赖安装失败
- **后端**: 使用正确的Python版本 (3.10)
  - 使用 `uv` 可加速安装: `uv pip install -r requirements.txt`
  - 如遇网络问题，检查镜像源配置
- **前端**: 使用pnpm而非npm安装前端依赖
  - 清除缓存后重试: `pnpm clean:cache`
  - 检查 `.npmrc` 中的镜像配置

### 5. Docker容器启动失败
- 检查端口是否被占用
- 查看容器日志: `docker compose logs backend`
- 验证Dockerfile和docker-compose配置

### 6. uv 命令未找到
- 安装 uv: `pip install uv`
- 或直接使用 pip: `pip install -r requirements.txt`

### 7. 路由冲突问题
- 确保 `/class-schedules/available-students` 端点定义在 `/class-schedules/{id}` 端点之前
- 避免动态路由参数与静态路由冲突

## 开发工作流

### 1. 功能开发流程
```bash
# 1. 创建数据库表设计
# 2. 使用代码生成器生成基础CRUD代码
# 3. 在 plugin/ 目录下完善业务逻辑
# 4. 编写前端页面和API调用
# 5. 测试功能完整性
# 6. 提交代码并创建Pull Request
```

### 2. Git提交规范
项目使用Commitizen规范提交消息:
```bash
# 使用交互式提交
pnpm run commit

# 或手动遵循规范
git commit -m "feat(模块): 添加新功能"
```

**提交类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

## 监控与维护

### 系统监控
- **服务器监控**: CPU、内存、磁盘使用情况
- **缓存监控**: Redis状态和命中率
- **在线用户**: 实时查看在线用户信息
- **操作日志**: 用户行为审计追踪

### 日志查看
```bash
# 查看后端日志
cd backend
tail -f logs/fastapi.log

# 查看Docker容器日志
docker compose logs -f backend

# 查看Nginx访问日志
docker compose logs -f nginx
```

## 扩展与定制

### 添加新模块
1. 在 `backend/app/plugin/` 下创建 `module_你的模块名` 目录
2. 按照插件架构规范创建 controller、model、schema、service、crud 文件
3. 系统会自动发现并注册路由

### 自定义中间件
1. 在 `backend/app/core/middlewares.py` 中添加新中间件
2. 在 `backend/app/config/setting.py` 的 `MIDDLEWARE_LIST` 中添加引用
3. 重启服务生效

### 自定义异常处理
1. 在 `backend/app/core/exceptions.py` 中定义新异常类
2. 在 `handle_exception` 函数中注册异常处理器
3. 在业务代码中抛出自定义异常

## 性能优化建议

### 数据库优化
- 合理使用索引
- 避免N+1查询问题
- 使用连接池配置优化

### 缓存策略
- 热点数据缓存到Redis
- 设置合理的缓存过期时间
- 使用缓存击穿保护机制

### API优化
- 使用分页查询大数据集
- 压缩响应数据 (Gzip已默认启用)
- 实施API限流防止滥用

## 安全最佳实践

1. **生产环境配置**:
   - 修改默认的JWT密钥
   - 使用强密码策略
   - 启用HTTPS

2. **访问控制**:
   - 遵循最小权限原则
   - 定期审计用户权限
   - 记录所有敏感操作

3. **输入验证**:
   - 对所有用户输入进行验证
   - 使用Pydantic模型进行数据验证
   - 防止SQL注入和XSS攻击
   
## 开发规范

### 代码修改
除非特别要求，否则不要修改项目的基础代码。

### 模块存放位置
后端模块：backend/app/plugin
前端视图：frontend/src/views
前端API：frontend/src/api

### 模块命名
统一格式：module_模块名称

### 环境管理
后端调试使用 uv 虚拟环境，不要直接在系统 Python 环境运行，会报错或缺组件。虚拟环境才有完整的组件，如缺少组件，请告知，自行安装到虚拟环境内。

### 测试脚本
测试临时使用的脚本，用完后要记得清理。

### 数据库配置
数据库配置信息位于 backend/env/.env.dev，已加入 .gitignore，可能看不到，但使用操作系统的 ls 命令可以查看。
## 贡献指南

1. Fork项目仓库
2. 创建功能分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -m 'Add some feature'`
4. 推送到分支: `git push origin feature/your-feature`
5. 提交Pull Request

## 获取帮助

- **官方文档**: https://service.fastapiadmin.com
- **GitHub仓库**: https://github.com/1014TaoTao/FastapiAdmin
- **Gitee仓库**: https://gitee.com/tao__tao/FastapiAdmin
- **问题反馈**: 在仓库Issues中提交问题

---

*本文档最后更新: 2026-01-30*  
*对应项目版本: FastApiAdmin v2.2.0*  
*检测到项目变更: 排课管理V2、时间段多选、弹窗宽度优化、购买记录时间段选择、能力分组系统、ClassScheduleOutSchema 修复*