# 赛事补报设计文档

## 背景

赛事已进入 ACTIVE 状态（小组赛已开打，部分比赛已有比分）后，需要补报 1-2 名学员参赛。当前系统在非 DRAFT 状态下禁止添加参赛队员。

## 需求

- 赛制：纯小组赛（PURE_GROUP）和锦标赛小组赛阶段（CHAMPIONSHIP）
- 状态：ACTIVE（已开打，部分比赛已有比分）
- 操作：在现有入口添加参赛队员，系统自动完成补报逻辑
- 分组：自动分配到当前人数最少的小组
- 比赛：只创建新人 vs 同组其他活跃成员的新比赛，已有比分不变

## 方案 A（选定）

复用 `POST /tournament/{id}/participants/batch` 接口，在 backend service 层增加 ACTIVE 状态下的补报分支。

### 后端改动

**`service.py` - `TournamentParticipantService.batch_add_service`**

当前流程：
1. 查询赛事信息 → 校验 status == DRAFT → 校验人数上限 → 逐条创建 participant

改为：
1. 查询赛事信息（带 groups 和当前成员信息）
2. 如果 `status == DRAFT` → 走原有流程
3. 如果 `status == ACTIVE` 且赛制为 `PURE_GROUP`/`CHAMPIONSHIP` → 走补报分支：
   - 查询当前所有小组及其成员数
   - 选人数最少的小组
   - 创建 participant 记录（`is_withdrawn=False`）
   - 为该 participant vs 同组所有活跃成员创建新比赛
   - 新比赛的 `round_type = 'GROUP_STAGE'`，`match_number` 接续当前组最大 match_number
   - 跳过种子排名、奇偶校验等 DRAFT 相关逻辑
4. 其他 status/赛制组合 → 抛异常"赛事已开始，不能添加参赛队员"

**`crud.py` - 新增补建比赛方法**

在 `TournamentMatchCRUD` 增加 `batch_create_late_matches_crud`：
- 入参：tournament_id, group_id, new_participant_id, existing_participant_ids[]
- 查询当前组最大 `match_number`
- 为新 participant vs 每个 existing participant 创建 match，`match_number` 递增

### 前端改动

**`index.vue` - 添加参赛队员按钮**

- 当前的显示条件：`currentTournament?.status === 'DRAFT'`
- 改为：`currentTournament?.status === 'DRAFT' || (currentTournament?.status === 'ACTIVE' && isGroupStageTournament)`

**`index.vue` - 确认弹窗**

点击添加时，如果是 ACTIVE 状态，弹确认框：
> "赛事已开始，补报学员将自动分配到人数最少的小组，并创建该学员与组内其他成员的比赛。是否继续？"

### 边界情况

- 没有小组（`groups` 为空）：先创建小组再分配
- 所有小组人数相同：分配到序号最小的小组（`group_order` 最小）
- 补报后人数超出 `group_size × num_groups`：允许（实际已有小组人数不均，放宽限制）
- 锦标赛的淘汰赛阶段：不开放补报（只允许小组赛阶段）
- 新人 vs 已退赛成员：不创建比赛（过滤 `is_withdrawn=True`）
