# 锦标赛模式 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 CHAMPIONSHIP 赛制（锦标赛模式），组合小组循环赛 + 交叉淘汰赛为完整赛制。

**Architecture:** 在现有 tournament 模块内扩展，新增枚举值、model 字段、service 方法、controller 端点和前端组件。复用现有小组赛生成、淘汰赛对阵、比分录入等逻辑。

**Tech Stack:** Python/FastAPI/SQLAlchemy/Alembic (后端), Vue3/TypeScript/Element Plus (前端)

---

## File Structure

| Action | File | Responsibility |
|--------|------|---------------|
| Modify | `backend/app/plugin/module_badminton/enums.py` | 新增 CHAMPIONSHIP 枚举值 |
| Modify | `backend/app/plugin/module_badminton/tournament/model.py` | 新增 advance_count, advance_top_n 字段 |
| Modify | `backend/app/plugin/module_badminton/tournament/schema.py` | 新增两个参数到 Create/Update/Out Schema |
| Modify | `backend/app/plugin/module_badminton/tournament/service.py` | 新增锦标赛创建校验、比赛生成、晋级方法，扩展排名计算 |
| Modify | `backend/app/plugin/module_badminton/tournament/controller.py` | 新增 2 个锦标赛端点，更新 types 端点 |
| Create | `backend/alembic/versions/xxxx_add_championship_fields.py` | 数据库迁移 |
| Modify | `frontend/src/api/module_badminton/tournament.ts` | 新增 advance_count, advance_top_n 字段和锦标赛 API |
| Modify | `frontend/src/views/module_badminton/tournament/index.vue` | 创建表单增加锦标赛选项和参数，管理弹窗增加锦标赛 tab |
| Modify | `frontend/src/views/module_badminton/tournament/components/ScoreDialog.vue` | 移除5局上限 |
| Modify | `frontend/src/views/module_badminton/tournament/components/GroupStageView.vue` | 锦标赛模式下隐藏平局列 |

---

### Task 1: 后端枚举 + Model + Schema 扩展

**Files:**
- Modify: `backend/app/plugin/module_badminton/enums.py`
- Modify: `backend/app/plugin/module_badminton/tournament/model.py`
- Modify: `backend/app/plugin/module_badminton/tournament/schema.py`

- [ ] **Step 1: 在 TournamentTypeEnum 中新增 CHAMPIONSHIP**

文件 `backend/app/plugin/module_badminton/enums.py`，在 `SINGLE_ELIMINATION` 行后添加：

```python
class TournamentTypeEnum(enum.Enum):
    """赛事类型枚举（对应4种赛制）"""

    ROUND_ROBIN = "ROUND_ROBIN"  # 分组循环赛（带淘汰赛）
    PURE_GROUP = "PURE_GROUP"  # 纯小组赛
    PROMOTION_RELEGATION = "PROMOTION_RELEGATION"  # 定区升降赛
    SINGLE_ELIMINATION = "SINGLE_ELIMINATION"  # 小组单败制淘汰赛
    CHAMPIONSHIP = "CHAMPIONSHIP"  # 锦标赛（分组循环 + 交叉淘汰）
```

- [ ] **Step 2: 在 TournamentModel 中新增两个字段**

文件 `backend/app/plugin/module_badminton/tournament/model.py`，在 `points_per_game` 字段后、`description` 字段前添加：

```python
    # 锦标赛专属参数
    advance_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="淘汰赛晋级总人数"
    )
    advance_top_n: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True, comment="每组前N名晋级"
    )
```

- [ ] **Step 3: 在 Schema 中新增两个字段和校验**

文件 `backend/app/plugin/module_badminton/tournament/schema.py`：

3a. `TournamentCreateSchema` 新增字段（在 `location` 字段后）：

```python
    advance_count: Optional[int] = Field(None, description="淘汰赛晋级总人数")
    advance_top_n: Optional[int] = Field(None, description="每组前N名晋级")
```

3b. 在 `TournamentCreateSchema` 类中添加校验方法：

```python
    @model_validator(mode="after")
    def validate_championship_params(self) -> "TournamentCreateSchema":
        """校验锦标赛模式参数"""
        if self.tournament_type and self.tournament_type.value == "CHAMPIONSHIP":
            if self.advance_count is None or self.advance_top_n is None:
                raise ValueError("锦标赛模式必须填写晋级人数和前几晋级参数")
            if self.advance_count < 4:
                raise ValueError("晋级人数不能少于4")
            if self.advance_top_n < 1:
                raise ValueError("前几晋级不能少于1")
            if self.advance_count % self.advance_top_n != 0:
                raise ValueError("晋级人数必须能被前几晋级整除")
            # 检查 advance_count 是 2 的幂次
            if self.advance_count & (self.advance_count - 1) != 0:
                raise ValueError("晋级人数必须为2的幂次（4, 8, 16, 32）")
            if self.group_size and self.advance_top_n >= self.group_size:
                raise ValueError("前几晋级必须小于每组人数")
            # 自动计算分组数
            self.num_groups = self.advance_count // self.advance_top_n
        return self
```

注意：`model_validator` 需要额外导入 `model_validator`（已在文件中导入）。

- [ ] **Step 4: 运行 ruff check 验证语法**

Run: `cd /home/filter/myproject/ds2yuclub/backend && ruff check app/plugin/module_badminton/enums.py app/plugin/module_badminton/tournament/model.py app/plugin/module_badminton/tournament/schema.py`
Expected: 无错误

- [ ] **Step 5: Commit**

```bash
git add backend/app/plugin/module_badminton/enums.py backend/app/plugin/module_badminton/tournament/model.py backend/app/plugin/module_badminton/tournament/schema.py
git commit -m "feat: add CHAMPIONSHIP enum and advance_count/advance_top_n fields"
```

---

### Task 2: 数据库迁移

**Files:**
- Create: `backend/alembic/versions/xxxx_add_championship_fields.py`

- [ ] **Step 1: 生成迁移脚本**

Run: `cd /home/filter/myproject/ds2yuclub/backend && .venv/bin/python main.py revision --env=dev`
Expected: 生成新的迁移文件

- [ ] **Step 2: 检查生成的迁移脚本内容**

打开生成的迁移文件，确认包含 `add_column('advance_count')` 和 `add_column('advance_top_n')` 到 `badminton_tournament` 表。如果自动生成的脚本有误，手动修正。

- [ ] **Step 3: 执行迁移**

Run: `cd /home/filter/myproject/ds2yuclub/backend && .venv/bin/python main.py upgrade --env=dev`
Expected: 迁移成功

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "migration: add advance_count and advance_top_n to tournament table"
```

---

### Task 3: 后端 Service 扩展 - 锦标赛逻辑

**Files:**
- Modify: `backend/app/plugin/module_badminton/tournament/service.py`

- [ ] **Step 1: 在 `generate_matches_service` 中添加 CHAMPIONSHIP 分支**

在 `generate_matches_service` 方法中，找到现有的 `elif tournament.tournament_type.value in ["ROUND_ROBIN", "PURE_GROUP"]:` 分支，将其改为：

```python
        # 小组循环赛（包括 ROUND_ROBIN、PURE_GROUP 和 CHAMPIONSHIP 的第一阶段）
        elif tournament.tournament_type.value in [
            "ROUND_ROBIN",
            "PURE_GROUP",
            "CHAMPIONSHIP",
        ]:
```

这样 CHAMPIONSHIP 类型复用 `_generate_round_robin_matches()` 生成小组赛。

- [ ] **Step 2: 新增 `_generate_championship_knockout` 方法**

在 `TournamentMatchService` 类中添加新方法：

```python
    @classmethod
    async def _generate_championship_knockout(
        cls, tournament_id: int, auth: AuthSchema
    ) -> dict:
        """锦标赛模式：根据小组赛排名生成淘汰赛对阵"""
        from sqlalchemy import text

        # 1. 获取赛事信息
        tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
        if not tournament:
            raise CustomException(msg="赛事不存在")
        if tournament.tournament_type.value != "CHAMPIONSHIP":
            raise CustomException(msg="仅锦标赛模式支持此操作")

        advance_count = tournament.advance_count
        advance_top_n = tournament.advance_top_n
        if not advance_count or not advance_top_n:
            raise CustomException(msg="锦标赛参数缺失")

        # 2. 检查所有小组赛是否已完成
        incomplete_sql = text("""
            SELECT COUNT(*) as cnt
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'GROUP_STAGE'
            AND status != 'COMPLETED'
        """)
        result = await auth.db.execute(
            incomplete_sql, {"tournament_id": tournament_id}
        )
        incomplete_count = result.scalar()
        if incomplete_count and incomplete_count > 0:
            raise CustomException(
                msg=f"还有 {incomplete_count} 场小组赛未完成，请先完成所有小组赛"
            )

        # 3. 获取小组赛排名数据
        group_stage_data = await cls.get_group_stage_data_service(
            tournament_id, None, auth
        )

        if not group_stage_data.get("groups"):
            raise CustomException(msg="小组赛数据为空")

        # 4. 收集晋级选手（交叉排位）
        advancing_participants = []  # 按淘汰赛种子顺序排列

        groups = group_stage_data["groups"]
        num_groups = len(groups)

        for rank_idx in range(advance_top_n):
            # 收集各组第 (rank_idx+1) 名
            group_winners = []
            for group_data in groups:
                rankings = group_data["data"]["rankings"]
                if rank_idx < len(rankings):
                    group_winners.append(rankings[rank_idx])
            advancing_participants.extend(group_winners)

        # 5. 交叉排位：确保相邻名次来自不同组
        # 简单策略：第1名列表和第2名列表交替排列
        # 对于 top_n=2 的情况：A1, B1, C1, D1, A2, B2, C2, D2
        # 淘汰赛对阵 1v8(A1 vs D2), 2v7(B1 vs C2), 3v6(C1 vs B2), 4v7(D1 vs A2)
        # 这天然实现了交叉排位

        # 6. 获取晋级选手的 participant ID
        participant_ids = [p["participant_id"] for p in advancing_participants]

        if len(participant_ids) < 2:
            raise CustomException(msg="晋级人数不足")

        # 7. 删除已有的淘汰赛对阵（如果有）
        await auth.db.execute(
            text(
                "DELETE FROM badminton_tournament_match WHERE tournament_id = :tid AND round_type = 'KNOCKOUT'"
            ),
            {"tid": tournament_id},
        )
        await auth.db.flush()

        # 8. 调用 KnockoutService 生成淘汰赛对阵
        result = await KnockoutService.generate_bracket(
            tournament_id=tournament_id,
            participant_ids=participant_ids,
            auth=auth,
        )

        return {
            "advancing_participants": advancing_participants,
            "total_advancing": len(participant_ids),
            "knockout_matches": result.get("matches", []),
            "total_rounds": result.get("total_rounds", 0),
        }
```

- [ ] **Step 3: 新增 `get_championship_status` 方法**

在 `TournamentMatchService` 类中添加：

```python
    @classmethod
    async def get_championship_status(
        cls, tournament_id: int, auth: AuthSchema
    ) -> dict:
        """获取锦标赛两阶段状态概览"""
        from sqlalchemy import text

        # 小组赛统计
        group_sql = text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed,
                COUNT(*) FILTER (WHERE status IN ('SCHEDULED', 'IN_PROGRESS')) as remaining
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'GROUP_STAGE'
        """)
        group_result = await auth.db.execute(
            group_sql, {"tournament_id": tournament_id}
        )
        group_row = group_result.fetchone()

        # 淘汰赛统计
        knockout_sql = text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed,
                COUNT(*) FILTER (WHERE status IN ('SCHEDULED', 'IN_PROGRESS')) as remaining
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'KNOCKOUT'
        """)
        knockout_result = await auth.db.execute(
            knockout_sql, {"tournament_id": tournament_id}
        )
        knockout_row = knockout_result.fetchone()

        group_total = group_row.total if group_row else 0
        group_completed = group_row.completed if group_row else 0
        knockout_total = knockout_row.total if knockout_row else 0
        knockout_completed = knockout_row.completed if knockout_row else 0

        return {
            "group_stage": {
                "total": group_total,
                "completed": group_completed,
                "remaining": (group_total or 0) - (group_completed or 0),
                "is_completed": group_total > 0 and group_completed == group_total,
            },
            "knockout": {
                "total": knockout_total,
                "completed": knockout_completed,
                "remaining": (knockout_total or 0) - (knockout_completed or 0),
                "is_generated": knockout_total > 0,
                "is_completed": knockout_total > 0 and knockout_completed == knockout_total,
            },
        }
```

- [ ] **Step 4: 运行 ruff check 验证**

Run: `cd /home/filter/myproject/ds2yuclub/backend && ruff check app/plugin/module_badminton/tournament/service.py`
Expected: 无错误

- [ ] **Step 5: Commit**

```bash
git add backend/app/plugin/module_badminton/tournament/service.py
git commit -m "feat: add championship knockout generation and status service methods"
```

---

### Task 4: 后端 Controller 扩展 - 新增端点

**Files:**
- Modify: `backend/app/plugin/module_badminton/tournament/controller.py`

- [ ] **Step 1: 在 `get_tournament_types` 中新增锦标赛类型**

找到 `get_tournament_types` 函数中的 `types` 列表，在最后一个类型（`SINGLE_ELIMINATION`）后添加：

```python
        {
            "value": "CHAMPIONSHIP",
            "label": "锦标赛",
            "description": "分组循环赛 + 交叉淘汰赛，先小组循环后淘汰争夺冠军",
        },
```

- [ ] **Step 2: 新增两个锦标赛端点**

在 `record_knockout_score` 端点之后、`get_tournament_types` 端点之前添加：

```python
@TournamentRouter.post(
    "/{tournament_id}/championship/generate-knockout",
    summary="生成锦标赛淘汰赛",
    description="小组赛结束后，根据排名生成交叉淘汰赛对阵",
)
async def generate_championship_knockout(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    """生成锦标赛淘汰赛对阵"""
    result = await TournamentMatchService._generate_championship_knockout(
        tournament_id, auth
    )
    return SuccessResponse(data=result, msg="锦标赛淘汰赛对阵生成成功")


@TournamentRouter.get(
    "/{tournament_id}/championship/status",
    summary="获取锦标赛状态",
    description="获取锦标赛两阶段（小组赛/淘汰赛）状态概览",
)
async def get_championship_status(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """获取锦标赛状态"""
    result = await TournamentMatchService.get_championship_status(
        tournament_id, auth
    )
    return SuccessResponse(data=result, msg="锦标赛状态获取成功")
```

- [ ] **Step 3: 运行 ruff check**

Run: `cd /home/filter/myproject/ds2yuclub/backend && ruff check app/plugin/module_badminton/tournament/controller.py`
Expected: 无错误

- [ ] **Step 4: Commit**

```bash
git add backend/app/plugin/module_badminton/tournament/controller.py
git commit -m "feat: add championship controller endpoints and tournament type"
```

---

### Task 5: 后端排名计算扩展 - 锦标赛无平局排名

**Files:**
- Modify: `backend/app/plugin/module_badminton/tournament/service.py`

- [ ] **Step 1: 在 `get_group_stage_data_service` 中添加锦标赛排名分支**

找到 `get_group_stage_data_service` 方法中计算 `rankings` 的部分（在 `# 按总分、胜负局差、胜负分差排序` 注释处）。在排名计算之后，需要根据赛事类型选择不同排序方式。

先在方法开头获取赛事类型（在现有的 groups_sql 之前添加）：

```python
        # 获取赛事类型
        tournament_sql = text("""
            SELECT tournament_type FROM badminton_tournament WHERE id = :tid
        """)
        t_result = await auth.db.execute(tournament_sql, {"tid": tournament_id})
        t_row = t_result.fetchone()
        tournament_type = t_row["tournament_type"] if t_row else None
```

然后将现有的排序代码：

```python
            # 按总分、胜负局差、胜负分差排序
            rankings.sort(
                key=lambda x: (
                    -x["total_points"],
                    -(x["sets_won"] - x["sets_lost"]),
                    -(x["points_scored"] - x["points_conceded"]),
                )
            )
```

替换为：

```python
            if tournament_type == "CHAMPIONSHIP":
                # 锦标赛排名：胜场数 → 净胜局数 → 净胜分数
                # 无平局概念
                rankings.sort(
                    key=lambda x: (
                        -x["wins"],
                        -(x["sets_won"] - x["sets_lost"]),
                        -(x["points_scored"] - x["points_conceded"]),
                    )
                )
            else:
                # 其他赛制排名：总分 → 净胜局 → 净胜分
                rankings.sort(
                    key=lambda x: (
                        -x["total_points"],
                        -(x["sets_won"] - x["sets_lost"]),
                        -(x["points_scored"] - x["points_conceded"]),
                    )
                )
```

- [ ] **Step 2: 运行 ruff check**

Run: `cd /home/filter/myproject/ds2yuclub/backend && ruff check app/plugin/module_badminton/tournament/service.py`
Expected: 无错误

- [ ] **Step 3: Commit**

```bash
git add backend/app/plugin/module_badminton/tournament/service.py
git commit -m "feat: add championship-specific ranking (no draws, wins-first)"
```

---

### Task 6: 后端测试

**Files:**
- Test: `backend/tests/`

- [ ] **Step 1: 启动后端确认无启动错误**

Run: `cd /home/filter/myproject/ds2yuclub/backend && .venv/bin/python -c "from app.plugin.module_badminton.tournament.controller import TournamentRouter; print('Controller import OK')"`
Expected: `Controller import OK`

- [ ] **Step 2: 确认枚举加载正常**

Run: `cd /home/filter/myproject/ds2yuclub/backend && .venv/bin/python -c "from app.plugin.module_badminton.enums import TournamentTypeEnum; print([e.value for e in TournamentTypeEnum])"`
Expected: 包含 `CHAMPIONSHIP`

- [ ] **Step 3: 确认 Schema 校验生效**

Run: `cd /home/filter/myproject/ds2yuclub/backend && .venv/bin/python -c "
from app.plugin.module_badminton.tournament.schema import TournamentCreateSchema
from app.plugin.module_badminton.enums import TournamentTypeEnum

# 应该成功
s = TournamentCreateSchema(
    name='测试锦标赛',
    tournament_type=TournamentTypeEnum.CHAMPIONSHIP,
    start_date='2026-05-01',
    end_date='2026-05-03',
    advance_count=8,
    advance_top_n=2,
    group_size=4,
)
print(f'OK: num_groups={s.num_groups}')

# 应该失败 - 晋级人数不是2的幂次
try:
    TournamentCreateSchema(
        name='测试',
        tournament_type=TournamentTypeEnum.CHAMPIONSHIP,
        start_date='2026-05-01',
        end_date='2026-05-03',
        advance_count=6,
        advance_top_n=2,
    )
    print('FAIL: 应该报错')
except Exception as e:
    print(f'OK: 校验生效 - {e}')
"`
Expected: `OK: num_groups=4` 和 `OK: 校验生效`

---

### Task 7: 前端 API 类型扩展

**Files:**
- Modify: `frontend/src/api/module_badminton/tournament.ts`

- [ ] **Step 1: 在 `TournamentTable` 接口中新增字段**

找到 `TournamentTable` 接口，在 `points_per_game` 后添加：

```typescript
  advance_count?: number;
  advance_top_n?: number;
```

- [ ] **Step 2: 在 `TournamentForm` 接口中新增字段**

找到 `TournamentForm` 接口，在 `points_per_game` 后添加：

```typescript
  advance_count?: number;
  advance_top_n?: number;
```

- [ ] **Step 3: 新增锦标赛 API 方法**

在 `TournamentAPIExtended` 对象中添加（在 `recordKnockoutScore` 方法之后）：

```typescript
  // 生成锦标赛淘汰赛（从小组赛晋级）
  generateChampionshipKnockout(tournamentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/championship/generate-knockout`,
      method: "post",
    });
  },

  // 获取锦标赛状态概览
  getChampionshipStatus(tournamentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/championship/status`,
      method: "get",
    });
  },
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/module_badminton/tournament.ts
git commit -m "feat: add championship API types and endpoints"
```

---

### Task 8: 前端创建表单扩展

**Files:**
- Modify: `frontend/src/views/module_badminton/tournament/index.vue`

- [ ] **Step 1: 在搜索区域赛制下拉中新增锦标赛选项**

找到查询表单中赛制下拉的 `<el-select>`，在 `SINGLE_ELIMINATION` 选项后添加：

```html
            <el-option value="CHAMPIONSHIP" label="锦标赛" />
```

- [ ] **Step 2: 在创建/编辑表单中新增锦标赛选项和参数**

2a. 找到创建/编辑对话框中赛制下拉的 `<el-select>`，在 `SINGLE_ELIMINATION` 选项后添加：

```html
            <el-option value="CHAMPIONSHIP" label="锦标赛（分组循环+交叉淘汰）" />
```

2b. 在 `group_size` 表单项之后、`description` 表单项之前，添加锦标赛参数区域（仅锦标赛模式显示）：

```html
        <!-- 锦标赛专属参数 -->
        <template v-if="formData.tournament_type === 'CHAMPIONSHIP'">
          <el-form-item label="晋级人数" prop="advance_count">
            <el-select v-model="formData.advance_count" placeholder="选择淘汰赛晋级人数" style="width: 100%">
              <el-option :value="4" label="4人" />
              <el-option :value="8" label="8人" />
              <el-option :value="16" label="16人" />
              <el-option :value="32" label="32人" />
            </el-select>
          </el-form-item>
          <el-form-item label="前几晋级" prop="advance_top_n">
            <el-input-number v-model="formData.advance_top_n" :min="1" :max="formData.group_size ? formData.group_size - 1 : 7" />
          </el-form-item>
          <el-form-item label="赛事信息">
            <div class="championship-info">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="分组数">
                  {{ formData.advance_count && formData.advance_top_n ? formData.advance_count / formData.advance_top_n : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="最低参赛人数">
                  {{ formData.advance_count && formData.advance_top_n ? (formData.advance_count / formData.advance_top_n) * 3 : '-' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-form-item>
        </template>
```

2c. 在 `<style scoped>` 中添加样式：

```css
.championship-info {
  width: 100%;
}
```

- [ ] **Step 3: 更新 `formData` reactive 和 `resetForm` 中的默认值**

在 `formData` reactive 对象中添加（在 `description` 之后）：

```typescript
  advance_count: undefined as number | undefined,
  advance_top_n: undefined as number | undefined,
```

在 `resetForm` 函数的 `Object.assign(formData, {...})` 中添加：

```typescript
    advance_count: undefined,
    advance_top_n: undefined,
```

- [ ] **Step 4: 更新 `getFormatLabel` 函数**

在 `getFormatLabel` 函数的 map 对象中添加：

```typescript
    CHAMPIONSHIP: "锦标赛",
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/module_badminton/tournament/index.vue
git commit -m "feat: add championship option to tournament create form"
```

---

### Task 9: 前端管理弹窗扩展 - 锦标赛 Tab

**Files:**
- Modify: `frontend/src/views/module_badminton/tournament/index.vue`

- [ ] **Step 1: 更新计算属性以支持锦标赛**

将 `isGroupStageTournament` 改为：

```typescript
const isGroupStageTournament = computed(() => {
  const type = currentTournament.value?.tournament_type?.toUpperCase();
  return type === "ROUND_ROBIN" || type === "PURE_GROUP" || type === "CHAMPIONSHIP";
});
```

新增 `isChampionshipTournament` 计算属性（在 `isKnockoutTournament` 之后）：

```typescript
const isChampionshipTournament = computed(() => {
  const type = currentTournament.value?.tournament_type?.toUpperCase();
  return type === "CHAMPIONSHIP";
});
```

新增锦标赛状态响应式变量（在其他 ref 附近）：

```typescript
const championshipStatus = ref<any>(null);
```

- [ ] **Step 2: 在管理弹窗的 tabs 中添加锦标赛淘汰赛 tab**

找到管理弹窗中现有的 `<!-- 单败淘汰赛 -->` `<el-tab-pane>`，在其之后添加：

```html
          <!-- 锦标赛淘汰赛（小组赛后生成） -->
          <el-tab-pane v-if="isChampionshipTournament" label="淘汰赛" name="championshipKnockout">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" icon="refresh" @click="loadChampionshipStatus">刷新状态</el-button>
                <el-button
                  v-if="championshipStatus?.group_stage?.is_completed && !championshipStatus?.knockout?.is_generated"
                  type="success"
                  icon="trophy"
                  @click="handleGenerateChampionshipKnockout"
                >
                  生成淘汰赛对阵
                </el-button>
              </div>

              <!-- 状态概览 -->
              <el-descriptions v-if="championshipStatus" :column="2" border style="margin-bottom: 16px">
                <el-descriptions-item label="小组赛进度">
                  {{ championshipStatus.group_stage.completed }}/{{ championshipStatus.group_stage.total }}
                  <el-tag v-if="championshipStatus.group_stage.is_completed" type="success" size="small">已完成</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="淘汰赛">
                  <el-tag v-if="!championshipStatus.knockout.is_generated" type="info" size="small">未生成</el-tag>
                  <el-tag v-else-if="championshipStatus.knockout.is_completed" type="success" size="small">已完成</el-tag>
                  <el-tag v-else type="warning" size="small">进行中</el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <template v-if="championshipStatus?.knockout?.is_generated">
                <KnockoutBracketView
                  v-if="knockoutData && knockoutData.matches && knockoutData.matches.length > 0"
                  :matches="knockoutData.matches"
                  @match-click="handleKnockoutMatchClick"
                />
                <el-empty v-else description="加载淘汰赛数据..." />
              </template>
              <el-alert v-else-if="championshipStatus && !championshipStatus.group_stage.is_completed"
                title="小组赛尚未全部完成，请先完成所有小组赛再生成淘汰赛对阵"
                type="warning"
                :closable="false"
                show-icon
              />
              <el-empty v-else description="请点击上方按钮生成淘汰赛对阵" />
            </div>
          </el-tab-pane>
```

- [ ] **Step 3: 添加锦标赛相关方法**

在 `generateKnockout` 函数之后添加：

```typescript
// 加载锦标赛状态
async function loadChampionshipStatus() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.getChampionshipStatus(currentTournament.value.id);
    championshipStatus.value = res.data?.data || null;
    // 如果淘汰赛已生成，同时加载淘汰赛数据
    if (championshipStatus.value?.knockout?.is_generated) {
      await loadKnockoutData();
    }
  } catch (error) {
    console.error("加载锦标赛状态失败:", error);
  }
}

// 生成锦标赛淘汰赛对阵
async function handleGenerateChampionshipKnockout() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.generateChampionshipKnockout(
      currentTournament.value.id
    );
    ElMessage.success("锦标赛淘汰赛对阵生成成功");
    await loadChampionshipStatus();
  } catch (error: any) {
    console.error(error);
    ElMessage.error(error?.response?.data?.msg || "生成淘汰赛对阵失败");
  }
}
```

- [ ] **Step 4: 更新 `handleTabChange` 函数**

在 `handleTabChange` 函数中添加锦标赛 tab 的分支：

```typescript
  } else if (tabName === "championshipKnockout") {
    loadChampionshipStatus();
  }
```

- [ ] **Step 5: 更新 `handleManage` 函数**

在 `handleManage` 函数中，设置 `activeTab` 之后添加状态重置：

```typescript
async function handleManage(row: TournamentTable) {
  currentTournament.value = row;
  manageDialogVisible.value = true;
  activeTab.value = "participants";
  championshipStatus.value = null;  // 重置锦标赛状态
  knockoutData.value = null;  // 重置淘汰赛数据
  await loadParticipants();
}
```

- [ ] **Step 6: 更新比分提交逻辑**

在 `handleScoreSubmit` 函数中，找到 `activeTab.value === 'knockout'` 条件，在其后添加锦标赛淘汰赛的处理：

将：
```typescript
    if (activeTab.value === 'knockout' && data.winnerId) {
```

改为：
```typescript
    if ((activeTab.value === 'knockout' || activeTab.value === 'championshipKnockout') && data.winnerId) {
```

并在后续的刷新逻辑中，如果是锦标赛淘汰赛，也刷新锦标赛状态：

在 `await loadKnockoutData();` 之后添加：
```typescript
      if (activeTab.value === 'championshipKnockout') {
        await loadChampionshipStatus();
      }
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/module_badminton/tournament/index.vue
git commit -m "feat: add championship knockout tab with status and bracket generation"
```

---

### Task 10: 前端 ScoreDialog 移除局数上限

**Files:**
- Modify: `frontend/src/views/module_badminton/tournament/components/ScoreDialog.vue`

- [ ] **Step 1: 移除5局上限**

找到 `addSet` 函数：

```typescript
function addSet() {
  if (scores.value.length < 5) {
    scores.value.push({ player1: 0, player2: 0 });
  }
}
```

改为：

```typescript
function addSet() {
  scores.value.push({ player1: 0, player2: 0 });
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/module_badminton/tournament/components/ScoreDialog.vue
git commit -m "feat: remove 5-set limit in score dialog for flexible scoring"
```

---

### Task 11: 前端 GroupStageView 锦标赛模式适配

**Files:**
- Modify: `frontend/src/views/module_badminton/tournament/components/GroupStageView.vue`

- [ ] **Step 1: 添加 `tournamentType` prop**

在组件的 props 定义中添加 `tournamentType`：

找到 `defineProps` 或 props 定义处，添加：

```typescript
tournamentType?: string;
```

（需要查看组件实际的 props 定义方式来适配）

- [ ] **Step 2: 在排名表中隐藏平局列（锦标赛模式）**

找到排名表格中显示"平局"或"draws"的列，添加 `v-if` 条件：

```html
<el-table-column v-if="tournamentType !== 'CHAMPIONSHIP'" ... />
```

（需要查看组件实际的表格列定义来适配，找到 draws 相关列）

- [ ] **Step 3: 更新调用方传入 prop**

在 `index.vue` 中，找到 `<GroupStageView` 组件的使用处，添加 `tournament-type` prop：

```html
              <GroupStageView
                v-if="groupStageData?.groups"
                :groups="groupStageData.groups"
                :tournament-type="currentTournament?.tournament_type"
                @record-score="handleGroupStageScore"
              />
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/module_badminton/tournament/components/GroupStageView.vue frontend/src/views/module_badminton/tournament/index.vue
git commit -m "feat: hide draws column in championship mode group stage view"
```

---

### Task 12: 集成测试

**Files:**
- 无新文件，使用现有工具

- [ ] **Step 1: 启动后端确认无错误**

Run: `cd /home/filter/myproject/ds2yuclub/backend && .venv/bin/python main.py run --env=dev`
Expected: 服务正常启动，无 import 错误

- [ ] **Step 2: 启动前端确认编译通过**

Run: `cd /home/filter/myproject/ds2yuclub/frontend && pnpm run type-check`
Expected: 无类型错误

- [ ] **Step 3: 前端 lint 检查**

Run: `cd /home/filter/myproject/ds2yuclub/frontend && pnpm run lint:eslint`
Expected: 无 ESLint 错误

- [ ] **Step 4: 后端 lint 检查**

Run: `cd /home/filter/myproject/ds2yuclub/backend && ruff check app/plugin/module_badminton/tournament/`
Expected: 无错误

- [ ] **Step 5: 使用浏览器测试完整流程**

1. 打开赛事管理页面
2. 点击"新增赛事"→ 选择"锦标赛"
3. 填写晋级人数（8）和前几晋级（2），确认分组数和最低人数自动计算
4. 提交创建 → 确认成功
5. 点击"管理"→ 添加参赛队员（至少12人）
6. 设置种子排名 → 生成对阵表
7. 在小组赛 tab 中录入比分（无平局，不限局数）
8. 完成所有小组赛后，切换到淘汰赛 tab
9. 点击"生成淘汰赛对阵"→ 确认对阵表生成成功
10. 在淘汰赛中录入比分 → 确认自动晋级正常
