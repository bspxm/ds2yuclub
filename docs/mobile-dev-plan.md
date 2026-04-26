# 羽毛球培训系统 —— 移动端开发计划

## 一、背景与目标

当前系统基于 PC 浏览器设计，在手机端体验不佳。需要在**不修改后端**的前提下，为教练和家长开发专用的手机端页面。

## 二、角色与设备

| 角色 | 设备 | 操作性质 | 路由分发 |
|------|------|----------|----------|
| 总管 | PC | 全部管理功能 | 保持现有 PC 版 |
| 教练 | 手机（强制） | 现场操作型 | 登录后自动进 `/m/badminton/coach/` |
| 家长 | 手机（强制） | 纯查看型 | 登录后自动进 `/m/badminton/parent/` |

- 家长角色已存在，角色编码 `PARENTS`，系统注册默认获得
- 教练角色由总管在后台配置

## 三、技术方案

| 项目 | 选择 |
|------|------|
| 移动端组件库 | **Vant 4**（Vue 3 移动端标准方案） |
| 项目结构 | 同项目内，与 Element Plus 共存 |
| 视图路径 | `src/views/module_badminton/m/coach/` 和 `m/parent/` |
| 路由前缀 | `/m/badminton/coach/` 和 `/m/badminton/parent/` |
| API | **全部复用**现有后端接口，不动后端一行代码 |

```
src/
├── views/module_badminton/
│   ├── assessment/          # PC版（已有）
│   ├── tournament/          # PC版（已有）
│   ├── class-attendance/    # PC版（已有）
│   ├── coach-schedule/      # PC版（已有）
│   ├── parent/              # PC版家长端（已有）
│   └── m/                   # 🆕 移动端
│       ├── coach/
│       │   ├── attendance.vue      # 点名签到
│       │   ├── schedule.vue        # 课表查看
│       │   ├── tournament.vue      # 赛事列表
│       │   ├── match-score.vue     # 比赛比分录入
│       │   └── assessment.vue      # 学员能力评估
│       └── parent/
│           ├── student.vue         # 学员学习情况
│           ├── tournament.vue      # 比赛结果查看
│           └── h2h.vue             # 学员H2H对比
```

## 四、开发范围（共 8 个页面）

### 第一阶段：教练端核心操作

**1. 点名签到** (`m/coach/attendance.vue`)
- 教练选择班级 + 日期 → 显示当天排课对应的考勤列表
- 每行：学员姓名 + 状态切换按钮（出勤/缺勤/请假）+ 提交
- 后端 API：`GET /class-schedules/team/{class_id}/upcoming` + `PUT /class-attendances/{id}`

**2. 课表查看** (`m/coach/schedule.vue`)
- 日历/日期选择 → 当天所有课程卡片（班级名、时间、场地、学员数）
- 后端 API：`GET /class-schedules/team/{class_id}/upcoming`

**3. 比赛比分录入** (`m/coach/tournament-index.vue` + `m/coach/tournament-matches.vue` + `m/coach/match-score.vue`)
- 赛事列表 → 选择赛事 → 对阵列表（按分组Tab） → 点击比赛进入比分录入
- 比分录入：两选手姓名 + 每局两个数字输入框 + "新增一局"按钮 + 确认提交
- 后端 API：`GET /tournament/active` → `GET /{tournament_id}/matches` → `PUT /{tournament_id}/matches/{match_id}/score`
- 比分数据格式：`{"sets": [{"player1": 21, "player2": 19}, ...]}`

**4. 学员能力评估** (`m/coach/assessment-compose.vue`)
- 选择学员 → 9个评分维度（技术、步伐、战术、力量、速度、耐力、进攻、防守、心理）+ 评语 → 提交
- 后端 API：`POST /assessments`
- 评估字段：`technique`, `footwork`, `tactics`, `power`, `speed`, `stamina`, `offense`, `defense`, `mental`, `comments`

### 第二阶段：家长端查看

**5. 学员学习情况** (`m/parent/student.vue`)
- 显示关联学员基本信息 + 出勤统计 + 能力评分趋势 + 最近课程
- 后端 API：`GET /class-attendances/student/{student_id}` + `GET /assessments/student/{student_id}/latest`

**6. 比赛结果** (`m/parent/tournament.vue`)
- 孩子参与的赛事列表 → 比赛结果详情
- 后端 API：复用 tournament 相关接口

**7. H2H 对比** (`m/parent/h2h.vue`)
- 选择对比学员 → 历史对战记录 + 能力评分对比
- 后端 API：`GET /tournament/h2h?student_id_1=X&student_id_2=Y`
