# 锦标赛模式设计文档

## 概述

在现有小组赛（ROUND_ROBIN/PURE_GROUP）和淘汰赛（SINGLE_ELIMINATION）的基础上，新增"锦标赛模式"（CHAMPIONSHIP），将两个阶段组合为一个完整赛制：先分组循环赛，再根据小组排名晋级到交叉淘汰赛。

## 需求

- 新增 CHAMPIONSHIP 赛制类型
- 创建赛事时增加两个参数：晋级人数（advance_count）、前几晋级（advance_top_n）
- 这两个参数决定分组数和最低参赛人数
- 两个新参数不影响已有赛制（仅 CHAMPIONSHIP 使用）
- 复用现有小组赛和淘汰赛的前后端代码
- 每组最少 3 人

## 参数说明

| 参数 | 字段 | 类型 | 含义 | 示例 |
|------|------|------|------|------|
| 晋级人数 | `advance_count` | int | 淘汰赛阶段总参赛人数 | 8 |
| 前几晋级 | `advance_top_n` | int | 每组前N名出线 | 2 |

### 推导计算

- 分组数 = `advance_count / advance_top_n`（如 8/2=4组）
- 最低参赛人数 = 分组数 × 3（每组最少3人）
- `advance_count` 必须为 2 的幂次（4, 8, 16, 32...），不足时淘汰赛用轮空补位
- `advance_top_n` 必须 ≥ 1 且 < `group_size`
- `advance_count` 必须能被 `advance_top_n` 整除

## 赛制流程

### 第一阶段：分组循环赛

1. 按现有规则将参赛者分为 N 个小组
2. 小组内每人相互对战一次（单循环）
3. 每场分数由教练录入，不确定局数，系统自动判定分高者获胜，记局数比分（大比分）高者为胜者
4. 必须打完所有小组赛场次

### 排名规则（按优先级）

1. 胜场数（降序）
2. 相互胜负关系（仅两人之间，胜者排前）
3. 净胜局数（降序）
4. 净胜分数（降序）
5. 抽签

### 第二阶段：交叉淘汰赛

1. 每组前 `advance_top_n` 名晋级
2. **交叉排位**：A组第1 vs B组第2，B组第1 vs A组第2（避免同组立即重遇）
3. 多组时轮空补位到 2 的幂次
4. 单败淘汰，胜者晋级，败者淘汰
5. 最终决出冠军

## 后端设计

### 枚举扩展

文件：`backend/app/plugin/module_badminton/enums.py`

```python
class TournamentTypeEnum(enum.Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    PURE_GROUP = "PURE_GROUP"
    PROMOTION_RELEGATION = "PROMOTION_RELEGATION"
    SINGLE_ELIMINATION = "SINGLE_ELIMINATION"
    CHAMPIONSHIP = "CHAMPIONSHIP"  # 新增
```

### Model 扩展

文件：`backend/app/plugin/module_badminton/tournament/model.py`

TournamentModel 新增两个 nullable 字段：

```python
advance_count = Column(Integer, nullable=True, comment="淘汰赛晋级总人数")
advance_top_n = Column(Integer, nullable=True, comment="每组前N名晋级")
```

仅 CHAMPIONSHIP 类型使用，其他类型这两个字段为 NULL。

### Schema 扩展

文件：`backend/app/plugin/module_badminton/tournament/schema.py`

TournamentCreateSchema 新增：

```python
advance_count: Optional[int] = None
advance_top_n: Optional[int] = None
```

新增校验：当 tournament_type == CHAMPIONSHIP 时，advance_count 和 advance_top_n 必填。

### 比分录入（复用现有逻辑）

文件：`backend/app/plugin/module_badminton/tournament/service.py`

现有 `record_score_service()` 已完全兼容锦标赛模式的比分录入需求：
- 支持任意局数录入（无固定三局两胜限制）
- 自动判定每局胜负：`player1 > player2 → winner=1`
- 自动计算大比分：赢更多局者为比赛胜者
- 状态始终 `IN_PROGRESS`，教练可继续添加局数
- **无需修改**，直接复用

### 排名计算（需扩展）

文件：`backend/app/plugin/module_badminton/tournament/service.py`

现有 `get_group_stage_data_service()` 的排名算法需为 CHAMPIONSHIP 模式做调整：

| 对比项 | 现有逻辑 | 锦标赛逻辑 |
|--------|----------|-----------|
| 排序依据 | total_points(胜1/平0.5) → 净胜局 → 净胜分 | 胜场数 → 相互胜负关系 → 净胜局数 → 净胜分数 |
| 积分概念 | 有（胜1分/平0.5分） | 无，直接用胜场数 |
| 相互胜负关系 | 未实现 | 新增：两人胜场相同时比较直接对决结果 |

实现方式：在 `get_group_stage_data_service()` 中根据 `tournament_type` 分支处理排名逻辑，CHAMPIONSHIP 使用新算法。

### Service 扩展

文件：`backend/app/plugin/module_badminton/tournament/service.py`

1. **创建赛事校验**：
   - CHAMPIONSHIP 时 advance_count 必须为 2 的幂次
   - advance_top_n 必须 ≥ 1
   - advance_count 必须能被 advance_top_n 整除
   - 自动计算 num_groups = advance_count / advance_top_n
   - 最低参赛人数 = num_groups × 3

2. **生成比赛**：
   - 复用 `_generate_round_robin_matches()` 生成分组循环赛
   - round_type = GROUP_STAGE

3. **新增晋级方法** `_generate_championship_knockout()`：
   - 检查所有 GROUP_STAGE 比赛是否已完成
   - 按排名规则计算每组排名
   - 每组取前 advance_top_n 名
   - 交叉排位：组1第1 vs 组2第2，组2第1 vs 组1第2...
   - 调用 KnockoutService.generate_bracket() 生成淘汰赛对阵
   - round_type = KNOCKOUT

### 新增 API 端点

文件：`backend/app/plugin/module_badminton/tournament/controller.py`

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/{tournament_id}/championship/generate-knockout` | 小组赛结束后生成淘汰赛对阵 |
| GET | `/{tournament_id}/championship/status` | 获取锦标赛两阶段状态概览 |

### 数据库迁移

需要新增 Alembic migration 为 badminton_tournament 表添加 advance_count 和 advance_top_n 两个 nullable 列。

## 前端设计

### API 类型扩展

文件：`frontend/src/api/module_badminton/tournament.ts`

TournamentForm 接口新增：

```typescript
advance_count?: number
advance_top_n?: number
```

### 创建表单扩展

文件：`frontend/src/views/module_badminton/tournament/index.vue`

- 赛制下拉新增「锦标赛」选项（CHAMPIONSHIP）
- 选择锦标赛时显示两个新参数输入框：
  - 晋级人数（advance_count）：下拉选择 4/8/16/32
  - 前几晋级（advance_top_n）：数字输入，≥ 1
- 自动计算并显示：分组数、最低参赛人数
- 校验：advance_top_n < advance_count

### 管理弹窗扩展

锦标赛模式下显示三个 tab：
- **小组赛**：复用 GroupStageView.vue
- **淘汰赛**：复用 KnockoutBracketView.vue（小组赛完成前显示提示 + 禁用）
- **对阵总览**：复用 CardView.vue

小组赛全部完成后，淘汰赛 tab 出现「生成淘汰赛对阵」按钮，调用新接口生成。

### 比分录入（复用现有组件）

文件：`frontend/src/views/module_badminton/tournament/components/ScoreDialog.vue`

现有 ScoreDialog 已兼容锦标赛模式：
- 支持动态添加/删除局数
- 自动计算每局胜负和大比分
- 自动判定胜者
- **唯一调整**：移除 `addSet()` 中 `scores.value.length < 5` 的局数上限限制（锦标赛模式不限局数）

### 小组赛排名展示（需调整）

文件：`frontend/src/views/module_badminton/tournament/components/GroupStageView.vue`

锦标赛模式下排名列表的列头和排序依据需调整：

| 对比项 | 现有显示 | 锦标赛显示 |
|--------|----------|-----------|
| 排名依据列 | "总分"（含平局0.5分） | "胜场"（纯胜场数） |
| 排序 | 总分 → 净胜局 → 净胜分 | 胜场 → 相互胜负 → 净胜局 → 净胜分 |

实现方式：通过 prop 或 tournament_type 判断，切换显示列和排序。

## 代码复用策略

| 功能 | 复用来源 | 说明 |
|------|----------|------|
| 小组赛生成 | service.py `_generate_round_robin_matches()` | 直接复用 |
| 小组赛展示 | GroupStageView.vue | 直接复用 |
| 淘汰赛生成 | knockout_service.py `generate_bracket()` | 传入晋级选手列表 |
| 淘汰赛展示 | KnockoutBracketView.vue | 直接复用 |
| 比分录入 | ScoreDialog.vue + service.py `record_score_service()` | 直接复用（移除5局上限） |
| 排名计算 | service.py `get_group_stage_data_service()` | 需扩展：锦标赛用不同排名算法 |
| 排名展示 | GroupStageView.vue | 需扩展：锦标赛模式下调整列头和排序 |
| 新增逻辑 | service.py 新方法 | 交叉排位 + 晋级编排 |

## 约束与校验

- advance_count 必须为 2 的幂次（4, 8, 16, 32）
- advance_top_n 必须 ≥ 1 且 < group_size
- advance_count 必须能被 advance_top_n 整除
- 每组最少 3 人
- 最低参赛人数 = (advance_count / advance_top_n) × 3
- 这两个参数仅对 CHAMPIONSHIP 类型生效，其他类型忽略
