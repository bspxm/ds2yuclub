<!-- 赛事管理 - 重构版 -->
<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <div v-show="visible" class="search-container">
      <el-form
        ref="queryFormRef"
        :model="queryFormData"
        label-suffix=":"
        :inline="true"
        @submit.prevent="handleQuery"
      >
        <el-form-item prop="name" label="赛事名称">
          <el-input v-model="queryFormData.name" placeholder="请输入赛事名称" clearable />
        </el-form-item>
        <el-form-item prop="tournament_type" label="赛制">
          <el-select
            v-model="queryFormData.tournament_type"
            placeholder="请选择赛制"
            style="width: 150px"
            clearable
          >
            <el-option value="ROUND_ROBIN" label="分组循环赛" />
            <el-option value="PURE_GROUP" label="纯小组赛" />
            <el-option value="PROMOTION_RELEGATION" label="定区升降赛" />
            <el-option value="SINGLE_ELIMINATION" label="单败制淘汰赛" />
            <el-option value="CHAMPIONSHIP" label="锦标赛" />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请选择状态"
            style="width: 120px"
            clearable
          >
            <el-option value="planned" label="计划中" />
            <el-option value="ongoing" label="进行中" />
            <el-option value="completed" label="已结束" />
            <el-option value="cancelled" label="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:tournament:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:tournament:list']"
            icon="refresh"
            @click="handleResetQuery"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            赛事管理
            <el-tooltip content="羽毛球赛事管理 - 支持创建比赛、配置参赛队员、生成对阵、录入比分">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
          </span>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:tournament:create']"
                type="primary"
                icon="plus"
                @click="handleAdd"
              >
                新增赛事
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:tournament:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleBatchDelete"
              >
                批量删除
              </el-button>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        ref="dataTableRef"
        v-loading="loading"
        :data="tournamentList"
        border
        highlight-current-row
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="name" label="赛事名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="tournament_type" label="赛制" width="120">
          <template #default="{ row }">
            <el-tag>{{ getFormatLabel(row.tournament_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="location" label="比赛地点" width="120" show-overflow-tooltip />
        <el-table-column prop="participant_count" label="参赛人数" width="100" align="center" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              v-hasPerm="['module_badminton:tournament:list']"
              type="primary"
              link
              icon="view"
              @click="handleManage(row)"
            >
              管理
            </el-button>
            <el-button
              v-hasPerm="['module_badminton:tournament:update']"
              type="primary"
              link
              icon="edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_badminton:tournament:delete']"
              type="danger"
              link
              icon="delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryFormData.page_no"
          v-model:page-size="queryFormData.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 赛事管理对话框 -->
    <el-dialog
      v-model="manageDialogVisible"
      :title="`赛事管理 - ${currentTournament?.name || ''}`"
      width="95%"
      top="5vh"
      destroy-on-close
    >
      <div v-if="currentTournament" class="tournament-manager">
        <!-- 标签页 -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <!-- 参赛队员管理 -->
          <el-tab-pane label="参赛队员" name="participants">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" icon="plus" @click="handleAddParticipant">
                  添加参赛队员
                </el-button>
                <el-button
                  type="success"
                  icon="refresh"
                  :disabled="participants.length < 2"
                  @click="handleGenerateMatches"
                >
                  生成对阵表
                </el-button>
              </div>
              <el-table :data="participants" border>
                <el-table-column prop="seed_rank" label="种子排名" width="90" align="center">
                  <template #default="{ row }">
                    <el-tag v-if="row.seed_rank" type="warning">{{ row.seed_rank }}</el-tag>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="student_name" label="姓名" width="100" />
                <el-table-column prop="age" label="年龄" width="70" align="center" />
                <el-table-column prop="group_name" label="组别" width="100" />
                <el-table-column prop="level" label="水平" width="90" />
                <el-table-column prop="matches_played" label="比赛场次" width="90" align="center" />
                <el-table-column prop="wins" label="胜" width="60" align="center" />
                <el-table-column prop="losses" label="负" width="60" align="center" />
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button type="primary" link @click="handleSetSeed(row)">设置种子</el-button>
                    <el-button type="danger" link @click="handleRemoveParticipant(row)">
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- 羽球在线风格小组赛 -->
          <el-tab-pane v-if="isGroupStageTournament" label="小组赛" name="groupStage">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" icon="refresh" @click="loadGroupStageData">
                  刷新
                </el-button>
              </div>
              <GroupStageView
                v-if="groupStageData?.groups"
                :groups="groupStageData.groups"
                :tournament-type="currentTournament?.tournament_type"
                @record-score="handleGroupStageScore"
              />
              <el-empty v-else description="暂无小组赛数据" />
            </div>
          </el-tab-pane>

          <!-- 单败淘汰赛 -->
          <el-tab-pane v-if="isKnockoutTournament" label="淘汰赛" name="knockout">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" icon="refresh" @click="loadKnockoutData">刷新</el-button>
                <el-button
                  v-if="!knockoutData"
                  type="success"
                  icon="trophy"
                  @click="generateKnockout"
                >
                  生成对阵表
                </el-button>
              </div>
              <KnockoutBracketView
                v-if="knockoutData && knockoutData.matches && knockoutData.matches.length > 0"
                :matches="knockoutData.matches"
                @match-click="handleKnockoutMatchClick"
              />
              <el-empty v-else description="暂无淘汰赛数据，请先生成对阵表" />
            </div>
          </el-tab-pane>

          <!-- 锦标赛淘汰赛（小组赛后生成） -->
          <el-tab-pane v-if="isChampionshipTournament" label="淘汰赛" name="championshipKnockout">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" icon="refresh" @click="loadChampionshipStatus">
                  刷新状态
                </el-button>
                <el-button
                  v-if="
                    championshipStatus?.group_stage?.is_completed &&
                    !championshipStatus?.knockout?.is_generated
                  "
                  type="success"
                  icon="trophy"
                  @click="handleGenerateChampionshipKnockout"
                >
                  生成淘汰赛对阵
                </el-button>
              </div>

              <!-- 状态概览 -->
              <el-descriptions
                v-if="championshipStatus"
                :column="2"
                border
                style="margin-bottom: 16px"
              >
                <el-descriptions-item label="小组赛进度">
                  {{ championshipStatus.group_stage.completed }}/{{
                    championshipStatus.group_stage.total
                  }}
                  <el-tag
                    v-if="championshipStatus.group_stage.is_completed"
                    type="success"
                    size="small"
                  >
                    已完成
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="淘汰赛">
                  <el-tag v-if="!championshipStatus.knockout.is_generated" type="info" size="small">
                    未生成
                  </el-tag>
                  <el-tag
                    v-else-if="championshipStatus.knockout.is_completed"
                    type="success"
                    size="small"
                  >
                    已完成
                  </el-tag>
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
              <el-alert
                v-else-if="championshipStatus && !championshipStatus.group_stage.is_completed"
                title="小组赛尚未全部完成，请先完成所有小组赛再生成淘汰赛对阵"
                type="warning"
                :closable="false"
                show-icon
              />
              <el-empty v-else description="请点击上方按钮生成淘汰赛对阵" />
            </div>
          </el-tab-pane>

          <!-- 对阵卡片 -->
          <el-tab-pane label="对阵" name="matches">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" icon="refresh" @click="loadMatches">刷新</el-button>
              </div>
              <CardView :matches="matches" @match-click="handleMatchClick" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 添加/编辑赛事对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="赛事名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入赛事名称" />
        </el-form-item>
        <el-form-item label="赛制" prop="tournament_type">
          <el-select
            v-model="formData.tournament_type"
            placeholder="请选择赛制"
            style="width: 100%"
          >
            <el-option value="ROUND_ROBIN" label="分组循环赛（带淘汰赛）" />
            <el-option value="PURE_GROUP" label="纯小组赛" />
            <el-option value="PROMOTION_RELEGATION" label="定区升降赛" />
            <el-option value="SINGLE_ELIMINATION" label="单败制淘汰赛" />
            <el-option value="CHAMPIONSHIP" label="锦标赛（分组循环+交叉淘汰）" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="formData.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="formData.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="比赛地点" prop="location">
          <el-input v-model="formData.location" placeholder="请输入比赛地点" />
        </el-form-item>
        <el-form-item v-if="formData.tournament_type !== 'CHAMPIONSHIP'" label="每组人数" prop="group_size">
          <el-input-number v-model="formData.group_size" :min="2" :max="8" />
        </el-form-item>
        <!-- 锦标赛专属参数 -->
        <template v-if="formData.tournament_type === 'CHAMPIONSHIP'">
          <el-form-item label="晋级人数" prop="advance_count">
            <el-select
              v-model="formData.advance_count"
              placeholder="选择淘汰赛晋级人数"
              style="width: 100%"
            >
              <el-option :value="4" label="4人" />
              <el-option :value="8" label="8人" />
              <el-option :value="16" label="16人" />
              <el-option :value="32" label="32人" />
            </el-select>
          </el-form-item>
          <el-form-item label="前几晋级" prop="advance_top_n">
            <el-input-number
              v-model="formData.advance_top_n"
              :min="1"
              :max="formData.group_size ? formData.group_size - 1 : 7"
            />
          </el-form-item>
          <el-form-item label="赛事信息">
            <div class="championship-info">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="分组数">
                  {{
                    formData.advance_count && formData.advance_top_n
                      ? formData.advance_count / formData.advance_top_n
                      : "-"
                  }}
                </el-descriptions-item>
                <el-descriptions-item label="最低参赛人数">
                  {{
                    formData.advance_count && formData.advance_top_n
                      ? (formData.advance_count / formData.advance_top_n) * 3
                      : "-"
                  }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-form-item>
        </template>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 参赛队员选择对话框 -->
    <ParticipantSelect
      v-model:visible="participantSelectVisible"
      :tournament-id="currentTournament?.id || 0"
      :existing-participants="participants.map((p) => p.student_id)"
      :max-participants="
        (currentTournament?.num_groups || 1) * (currentTournament?.group_size || 4)
      "
      :group-size="currentTournament?.group_size || 4"
      @submit="handleParticipantSubmit"
    />

    <!-- 比分录入对话框 -->
    <ScoreDialog
      v-model:visible="scoreDialogVisible"
      :match="selectedMatch"
      @submit="handleScoreSubmit"
    />

    <!-- 种子排名设置对话框 -->
    <el-dialog v-model="seedDialogVisible" title="设置种子排名" width="300px">
      <el-form>
        <el-form-item label="种子排名">
          <el-input-number v-model="seedRank" :min="1" :max="participants.length" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="seedDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSeedSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled } from "@element-plus/icons-vue";
import TournamentAPI, { TournamentAPIExtended } from "@/api/module_badminton/tournament";
import type {
  TournamentTable,
  TournamentForm,
  TournamentMatch,
  TournamentParticipant,
} from "@/api/module_badminton/tournament";

// 组件导入
import CardView from "./components/CardView.vue";
import ParticipantSelect from "./components/ParticipantSelect.vue";
import ScoreDialog from "./components/ScoreDialog.vue";
import GroupStageView from "./components/GroupStageView.vue";
import KnockoutBracketView from "./components/KnockoutBracketView.vue";

// 搜索区域显示控制
const visible = ref(true);

// 查询表单
const queryFormRef = ref();
const queryFormData = reactive({
  page_no: 1,
  page_size: 10,
  name: "",
  tournament_type: "",
  status: "",
});

// 数据列表
const loading = ref(false);
const tournamentList = ref<TournamentTable[]>([]);
const total = ref(0);
const selectIds = ref<number[]>([]);

// 对话框
const dialogVisible = ref(false);
const dialogTitle = ref("");
const formRef = ref();

// 日期格式化函数
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

const formData = reactive<TournamentForm>({
  name: "",
  tournament_type: "ROUND_ROBIN", // 默认：分组循环赛（大写）
  start_date: formatDate(new Date()),
  end_date: formatDate(new Date()),
  location: "",
  num_groups: 4,
  group_size: 4,
  description: "",
  advance_count: undefined as number | undefined,
  advance_top_n: undefined as number | undefined,
});

const rules = {
  name: [{ required: true, message: "请输入赛事名称", trigger: "blur" }],
  tournament_type: [{ required: true, message: "请选择赛制", trigger: "change" }],
  start_date: [{ required: true, message: "请选择开始日期", trigger: "change" }],
  end_date: [{ required: true, message: "请选择结束日期", trigger: "change" }],
};

// 赛事管理
const manageDialogVisible = ref(false);
const currentTournament = ref<TournamentTable | null>(null);
const activeTab = ref("participants");
const participants = ref<TournamentParticipant[]>([]);
const matches = ref<TournamentMatch[]>([]);
const groupStageData = ref<any>(null);
const knockoutData = ref<any>(null);
const championshipStatus = ref<any>(null);

// 计算属性：判断是否为小组赛赛制
const isGroupStageTournament = computed(() => {
  const type = currentTournament.value?.tournament_type?.toUpperCase();
  return type === "ROUND_ROBIN" || type === "PURE_GROUP" || type === "CHAMPIONSHIP";
});

// 计算属性：判断是否为锦标赛赛制
const isChampionshipTournament = computed(() => {
  const type = currentTournament.value?.tournament_type?.toUpperCase();
  return type === "CHAMPIONSHIP";
});

// 计算属性：判断是否为淘汰赛赛制
const isKnockoutTournament = computed(() => {
  const type = currentTournament.value?.tournament_type?.toUpperCase();
  return type === "SINGLE_ELIMINATION";
});

// 参赛队员选择
const participantSelectVisible = ref(false);

// 比分录入
const scoreDialogVisible = ref(false);
const selectedMatch = ref<TournamentMatch | null>(null);

// 种子排名设置
const seedDialogVisible = ref(false);
const seedRank = ref(1);
const selectedParticipant = ref<TournamentParticipant | null>(null);

// 加载赛事列表
async function loadingData() {
  loading.value = true;
  try {
    const res = await TournamentAPI.getTournamentList(queryFormData);
    const items = res.data?.data || [];
    tournamentList.value = items;
    total.value = items.length;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 查询
function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  handleQuery();
}

// 分页
function handleSizeChange(size: number) {
  queryFormData.page_size = size;
  loadingData();
}

function handleCurrentChange(page: number) {
  queryFormData.page_no = page;
  loadingData();
}

// 选择
function handleSelectionChange(selection: TournamentTable[]) {
  selectIds.value = selection.map((item) => item.id);
}

// 新增
function handleAdd() {
  dialogTitle.value = "新增赛事";
  resetForm();
  dialogVisible.value = true;
}

// 编辑
function handleEdit(row: TournamentTable) {
  dialogTitle.value = "编辑赛事";
  Object.assign(formData, row);
  dialogVisible.value = true;
}

// 删除
function handleDelete(row: TournamentTable) {
  ElMessageBox.confirm(`确认删除赛事"${row.name}"?`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await TournamentAPI.deleteTournament([row.id]);
        ElMessage.success("删除成功");
        loadingData();
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {});
}

// 批量删除
function handleBatchDelete() {
  ElMessageBox.confirm(`确认删除选中的${selectIds.value.length}个赛事?`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await TournamentAPI.deleteTournament(selectIds.value);
        ElMessage.success("删除成功");
        loadingData();
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {});
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value?.validate();
    loading.value = true;

    // 确保日期格式为 YYYY-MM-DD
    const submitData = {
      ...formData,
      start_date:
        typeof formData.start_date === "string"
          ? formData.start_date
          : formatDate(new Date(formData.start_date)),
      end_date:
        typeof formData.end_date === "string"
          ? formData.end_date
          : formatDate(new Date(formData.end_date)),
    };

    if (formData.id) {
      await TournamentAPI.updateTournament(formData.id, submitData);
      ElMessage.success("更新成功");
    } else {
      await TournamentAPI.createTournament(submitData);
      ElMessage.success("创建成功");
    }

    dialogVisible.value = false;
    loadingData();
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 重置表单
function resetForm() {
  formRef.value?.resetFields();
  Object.assign(formData, {
    id: undefined,
    name: "",
    tournament_type: "ROUND_ROBIN",
    start_date: formatDate(new Date()),
    end_date: formatDate(new Date()),
    location: "",
    num_groups: 4,
    group_size: 4,
    description: "",
    advance_count: undefined,
    advance_top_n: undefined,
  });
}

// 赛事管理
async function handleManage(row: TournamentTable) {
  currentTournament.value = row;
  manageDialogVisible.value = true;
  activeTab.value = "participants";
  championshipStatus.value = null;
  knockoutData.value = null;
  await loadParticipants();
}

// 加载参赛队员
async function loadParticipants() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.getParticipants(currentTournament.value.id);
    participants.value = res.data?.data || [];
  } catch (error) {
    console.error(error);
  }
}

// 加载对阵
async function loadMatches() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.getMatches(currentTournament.value.id);
    console.log("对阵API原始响应:", res);
    console.log("对阵API data.data:", res.data?.data);
    matches.value = res.data?.data || [];
    console.log("最终对阵数据:", matches.value, "数量:", matches.value.length);
  } catch (error) {
    console.error("加载对阵失败:", error);
  }
}

// 添加参赛队员
function handleAddParticipant() {
  participantSelectVisible.value = true;
}

// 提交参赛队员
async function handleParticipantSubmit(selectedParticipants: any[]) {
  if (!currentTournament.value) return;
  try {
    const studentIds = selectedParticipants.map((p) => p.student_id);
    await TournamentAPIExtended.batchAddParticipants(currentTournament.value.id, studentIds);
    ElMessage.success("添加成功");
    await loadParticipants();
  } catch (error) {
    console.error(error);
  }
}

// 移除参赛队员
async function handleRemoveParticipant(row: TournamentParticipant) {
  if (!currentTournament.value) return;
  try {
    await TournamentAPIExtended.removeParticipant(currentTournament.value.id, row.id);
    ElMessage.success("移除成功");
    await loadParticipants();
  } catch (error) {
    console.error(error);
  }
}

// 设置种子排名
function handleSetSeed(row: TournamentParticipant) {
  selectedParticipant.value = row;
  seedRank.value = row.seed_rank || 1;
  seedDialogVisible.value = true;
}

// 提交种子排名
async function handleSeedSubmit() {
  if (!currentTournament.value || !selectedParticipant.value) return;
  try {
    await TournamentAPIExtended.updateParticipant(
      currentTournament.value.id,
      selectedParticipant.value.id,
      seedRank.value
    );
    ElMessage.success("设置成功");
    seedDialogVisible.value = false;
    await loadParticipants();
  } catch (error) {
    console.error(error);
  }
}

// 生成对阵表
async function handleGenerateMatches() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.generateMatches(currentTournament.value.id, true);
    // 使用生成的对阵更新本地数据
    matches.value = res.data?.data || [];
    ElMessage.success("对阵表生成成功");
    activeTab.value = "matches";
    // 同时从服务器加载最新对阵，确保数据一致
    await loadMatches();
  } catch (error) {
    console.error(error);
  }
}

// 监听标签页切换
function handleTabChange(tabName: string) {
  console.log("标签页切换:", tabName);
  if (tabName === "matches") {
    loadMatches();
  } else if (tabName === "groupStage") {
    loadGroupStageData();
  } else if (tabName === "knockout") {
    loadKnockoutData();
  } else if (tabName === "championshipKnockout") {
    loadChampionshipStatus();
  }
}

// 加载小组赛数据
async function loadGroupStageData() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.getGroupStageData(currentTournament.value.id);
    groupStageData.value = res.data?.data || null;
    console.log("小组赛数据:", groupStageData.value);
  } catch (error) {
    console.error("加载小组赛数据失败:", error);
  }
}

// 加载淘汰赛数据
async function loadKnockoutData() {
  if (!currentTournament.value) return;
  try {
    const res = await TournamentAPIExtended.getKnockoutData(currentTournament.value.id);
    knockoutData.value = res.data?.data || null;
    console.log("淘汰赛数据:", knockoutData.value);
  } catch (error) {
    console.error("加载淘汰赛数据失败:", error);
  }
}

// 生成淘汰赛对阵表
async function generateKnockout() {
  if (!currentTournament.value) return;
  try {
    const participantIds = participants.value.map((p) => p.id);
    if (participantIds.length < 2) {
      ElMessage.warning("参赛人数不足，无法生成淘汰赛");
      return;
    }
    const res = await TournamentAPIExtended.generateKnockout(
      currentTournament.value.id,
      participantIds
    );
    knockoutData.value = res.data?.data || null;
    ElMessage.success("淘汰赛对阵表生成成功");
  } catch (error) {
    console.error(error);
    ElMessage.error("生成淘汰赛对阵表失败");
  }
}

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
    await TournamentAPIExtended.generateChampionshipKnockout(
      currentTournament.value.id
    );
    ElMessage.success("锦标赛淘汰赛对阵生成成功");
    await loadChampionshipStatus();
  } catch (error: any) {
    console.error(error);
    ElMessage.error(error?.response?.data?.msg || "生成淘汰赛对阵失败");
  }
}

// 处理淘汰赛比分录入
function handleKnockoutMatchClick(match: any) {
  selectedMatch.value = {
    id: match.id,
    player1: match.player1,
    player2: match.player2,
    scores: match.scores
      ? match.scores.split(", ").map((s: string) => {
          const [p1, p2] = s.split("-").map(Number);
          return { player1: p1, player2: p2 };
        })
      : [],
    status: match.status,
  };
  scoreDialogVisible.value = true;
}

// 处理小组赛比分录入
function handleGroupStageScore(scheduleItem: any) {
  // 转换小组赛赛程项为 TournamentMatch 格式
  selectedMatch.value = {
    id: scheduleItem.match_id,
    player1: { id: scheduleItem.player1_id, name: scheduleItem.player1_name },
    player2: { id: scheduleItem.player2_id, name: scheduleItem.player2_name },
    scores: scheduleItem.sets || [], // 传递已有的比分数据
    status: scheduleItem.completed ? "COMPLETED" : "SCHEDULED",
  } as any;
  scoreDialogVisible.value = true;
}

// 点击比赛
function handleMatchClick(match: TournamentMatch) {
  selectedMatch.value = match;
  scoreDialogVisible.value = true;
}

// 提交比分
async function handleScoreSubmit(data: { matchId: number; sets: any[]; winnerId?: number }) {
  if (!currentTournament.value) return;
  try {
    if (
      (activeTab.value === "knockout" || activeTab.value === "championshipKnockout") &&
      data.winnerId
    ) {
      // 淘汰赛且有胜者，使用淘汰赛API并自动晋级
      await TournamentAPIExtended.recordKnockoutScore(
        currentTournament.value.id,
        data.matchId,
        { sets: data.sets },
        data.winnerId
      );
      ElMessage.success("比分录入成功，胜者已晋级");
      await loadKnockoutData(); // 刷新淘汰赛数据
      if (activeTab.value === "championshipKnockout") {
        await loadChampionshipStatus();
      }
    } else {
      // 小组赛或无胜者，使用普通API
      await TournamentAPIExtended.recordScore(currentTournament.value.id, data.matchId, {
        sets: data.sets,
      });
      ElMessage.success("比分录入成功");
      await loadMatches();
      await loadGroupStageData(); // 刷新小组赛数据
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("比分录入失败");
  }
}

// 格式化
function getFormatLabel(tournamentType: string): string {
  const map: Record<string, string> = {
    // 大写格式（数据库枚举）
    ROUND_ROBIN: "分组循环赛",
    PURE_GROUP: "纯小组赛",
    PROMOTION_RELEGATION: "定区升降赛",
    SINGLE_ELIMINATION: "单败制淘汰赛",
    CHAMPIONSHIP: "锦标赛",
  };
  return map[tournamentType] || tournamentType;
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    // 大写格式（数据库视图返回）
    DRAFT: "草稿",
    REGISTRATION: "报名中",
    ACTIVE: "进行中",
    COMPLETED: "已结束",
    CANCELLED: "已取消",
    // 小写格式（兼容旧数据）
    draft: "草稿",
    registration: "报名中",
    active: "进行中",
    completed: "已结束",
    cancelled: "已取消",
  };
  return map[status] || status;
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    // 大写格式
    DRAFT: "info",
    REGISTRATION: "warning",
    ACTIVE: "success",
    COMPLETED: "success",
    CANCELLED: "danger",
    // 小写格式（兼容）
    draft: "info",
    registration: "warning",
    active: "success",
    completed: "success",
    cancelled: "danger",
  };
  return map[status] || "info";
}

function getRankType(rank: number): string {
  if (rank === 1) return "danger";
  if (rank === 2) return "warning";
  if (rank === 3) return "success";
  return "info";
}

onMounted(() => {
  loadingData();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.search-container {
  margin-bottom: 20px;
}

.data-table {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-table__toolbar {
  margin-bottom: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.tournament-manager {
  min-height: 500px;
}

.tab-content {
  padding: 16px 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.championship-info {
  width: 100%;
}
</style>
