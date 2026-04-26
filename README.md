# 羽毛球培训会员管理系统

<div align="center">
  <p align="center">
    <img src="https://gitee.com/tao__tao/FastDocs/raw/main/src/public/logo.png" width="150" height="150" alt="logo" />
  </p>
  <h1>羽毛球培训会员管理系统</h1>
  <h3>基于 FastApiAdmin 框架的学期制课时结算系统</h3>
  <p>技术先进、功能完善的羽毛球培训管理解决方案</p>
</div>

## 项目介绍

本系统是一套**羽毛球培训会员管理系统**，基于 **FastApiAdmin** 框架构建，采用前后端分离架构，实现学期制课时结算功能。系统支持学员管理、班级管理、课程排课、购买记录、出勤管理、能力评估、比赛管理等核心功能。

> **设计目标**：为羽毛球培训机构提供数字化管理解决方案，提高运营效率，优化会员体验。

## 技术栈

| 类型 | 技术选型 | 描述 |
|------|----------|------|
| **后端框架** | FastAPI / SQLAlchemy 2.0 / Pydantic 2.x | 高性能异步框架，强制类型约束 |
| **前端框架** | Vue3 / Vite5 / TypeScript / Pinia | 现代前端开发技术栈 |
| **UI组件** | Element Plus / UnoCSS | 企业级UI组件库 |
| **数据库** | MySQL 8.0 / PostgreSQL | 关系型数据库支持 |
| **缓存** | Redis | 高性能缓存 |
| **ORM** | SQLAlchemy 2.0 (async) | 异步ORM库 |
| **迁移工具** | Alembic | 数据库版本管理 |

## 功能模块

| 模块 | 功能 | 描述 |
|------|------|------|
| 📚 **学员管理** | 学员档案、等级管理 | 学员信息管理、能力等级划分 |
| 🏫 **班级管理** | 班级创建、排班设置 | 固定天/自选天班级设置 |
| 📅 **课程管理** | 课程表、教练分配 | 课程安排、教练管理 |
| 📆 **排课管理** | 课程调度、时间段管理 | V2版本排课功能 |
| 💰 **购买记录** | 课时购买、套餐管理 | 学期制课时购买与结算 |
| ✅ **出勤管理** | 签到签退、出勤统计 | 学员上课签到管理 |
| 📖 **学期管理** | 学期设置、周期管理 | 学期时间设置 |
| 👥 **能力分组** | 分组管理、教练分配 | 学员能力分组 |
| 📊 **能力评估** | 九维评估、历史记录 | 技术、步法、战术等多维度评估 |
| 🏆 **比赛管理** | 赛事管理、积分排名 | 赛事组织、淘汰赛/循环赛 |
| 📝 **请假管理** | 请假申请、审批流程 | 学员请假申请与审批 |

## 工程结构

```
ds2yuclub/
├─ backend/                    # 后端工程
│  └─ app/plugin/
│     └─ module_badminton/    # 羽毛球业务模块
│        ├─ student/          # 学员管理
│        ├─ team/             # 班级管理
│        ├─ course/           # 课程管理
│        ├─ schedule/         # 排课管理
│        ├─ purchase/         # 购买记录
│        ├─ attendance/       # 出勤管理
│        ├─ semester/         # 学期管理
│        ├─ group/            # 能力分组
│        ├─ assessment/       # 能力评估
│        ├─ tournament/       # 比赛管理
│        └─ leave/           # 请假管理
├─ frontend/                   # 前端工程
│  └─ src/
│     ├─ views/module_badminton/  # 业务页面组件
│     ├─ api/module_badminton/    # API调用
│     └─ store/modules/           # Pinia状态管理
├─ docs/                      # 项目文档
└─ docker-compose.yaml        # Docker编排
```

## 快速开始

### 环境要求

| 类型 | 版本要求 |
|------|----------|
| Python | ≥ 3.10 |
| Node.js | ≥ 20.0 |
| PostgreSQL | ≥ 13.0 |
| Redis | ≥ 6.0 |

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env/.env.dev.example env/.env.dev
# 编辑 env/.env.dev 配置数据库和Redis连接

# 启动服务
python main.py run --env=dev

# 数据库迁移
python main.py revision --env=dev  # 生成迁移
python main.py upgrade --env=dev   # 应用迁移
```

**数据库配置说明**（参考 `backend/env/.env.dev`）：

| 配置项 | 说明 |
|--------|------|
| DATABASE_TYPE | 数据库类型，支持 `mysql`、`postgres` |
| DATABASE_HOST | 数据库服务器地址 |
| DATABASE_PORT | 数据库端口（PostgreSQL默认5432） |
| DATABASE_NAME | 数据库名称 |

**Redis配置说明**：

| 配置项 | 说明 |
|--------|------|
| REDIS_HOST | Redis服务器地址 |
| REDIS_PORT | Redis端口（默认6379） |

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 配置环境变量
cp .env.development.example .env.development
# 编辑 .env.development 配置接口地址

# 启动开发服务器
pnpm dev

# 类型检查
pnpm run type-check

# 构建生产版本
pnpm build
```

### 访问地址

- 前端地址：http://localhost:5180
- 后端API：http://localhost:8771
- API文档：http://localhost:8771/docs

## 核心功能说明

### 时间段格式

系统中时间段使用统一的JSON格式存储：

```json
{
  "周一": ["A", "B"],
  "周三": ["C"],
  "周五": ["D", "E"]
}
```

时间段编码对照：
- A: 08:00-09:30
- B: 09:30-11:00
- C: 14:00-15:30
- D: 15:30-17:00
- E: 18:00-19:30

### 能力评估维度

系统采用九维能力评估体系：
1. 技术能力 (technique)
2. 步法移动 (footwork)
3. 战术意识 (tactics)
4. 力量 (power)
5. 速度 (speed)
6. 耐力 (stamina)
7. 进攻能力 (offense)
8. 防守能力 (defense)
9. 心理素质 (mental)

### 班级类型

- **固定天班级**：每周固定日期上课
- **自选天班级**：学员可选择上课日期

## 开发指南

### 后端开发

采用插件化架构，业务模块位于 `backend/app/plugin/module_badminton/`：

```
module_badminton/
├─ controller.py    # 控制器（路由定义）
├─ service.py       # 业务逻辑层
├─ crud.py          # 数据访问层
├─ model.py         # ORM模型
├─ schema.py        # Pydantic验证模型
└─ enums.py         # 枚举定义
```

### 前端开发

页面组件位于 `frontend/src/views/module_badminton/`：
- 使用 Vue3 Composition API
- TypeScript 类型安全
- Element Plus 组件库
- Pinia 状态管理

### API规范

- RESTful API 设计
- JWT 认证
- 统一响应格式：`{ code, msg, data }`
- 权限控制基于 RBAC 模型

## Docker 部署

```bash
# 一键部署
./deploy.sh

# 查看容器状态
docker compose ps

# 查看日志
docker logs -f <容器名>

# 停止服务
docker compose down
```

## 项目文档

- [AGENTS.md](./AGENTS.md) - AI助手开发指南
- [CLAUDE.md](./CLAUDE.md) - Claude Code 配置
- [单个新增购买记录时间段选择功能说明.md](./单个新增购买记录时间段选择功能说明.md)
- [时间段选择功能测试说明.md](./时间段选择功能测试说明.md)

## 许可证

本项目基于 MIT 许可证开源。

## 致谢

- [FastApiAdmin](https://github.com/1014TaoTao/FastApiAdmin) - 基础框架
- [Vue3](https://cn.vuejs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Element Plus](https://element-plus.org/) - UI组件库
