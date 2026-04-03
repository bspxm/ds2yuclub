<!-- 赛事管理 -->
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
        <el-form-item prop="format" label="赛制">
          <el-select
            v-model="queryFormData.format"
            placeholder="请选择赛制"
            style="width: 150px"
            clearable
          >
            <el-option value="group_cycle" label="分组循环赛" />
            <el-option value="pure_group" label="纯小组赛" />
            <el-option value="fixed_zone_promotion" label="定区升降赛" />
            <el-option value="single_elimination" label="小组单败制淘汰赛" />
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
        <el-form-item v-if="isExpand" prop="location" label="比赛地点">
          <el-input v-model="queryFormData.location" placeholder="请输入比赛地点" clearable />
        </el-form-item>
        <el-form-item v-if="isExpand" prop="start_date" label="开始日期">
          <DatePicker v-model="startDateRange" @update:model-value="handleStartDateRangeChange" />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:tournament:query']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:tournament:query']"
            icon="refresh"
            @click="handleResetQuery"
          >
            重置
          </el-button>
          <!-- 展开/收起 -->
          <template v-if="isExpandable">
            <el-link class="ml-3" type="primary" underline="never" @click="isExpand = !isExpand">
              {{ isExpand ? "收起" : "展开" }}
              <el-icon>
                <template v-if="isExpand">
                  <ArrowUp />
                </template>
                <template v-else>
                  <ArrowDown />
                </template>
              </el-icon>
            </el-link>
          </template>
        </el-form-item>
      </el-form>
    </div>

    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            赛事管理
            <el-tooltip content="羽毛球赛事管理">
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
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
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
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_badminton:tournament:patch']" trigger="click">
                <el-button type="default" :disabled="selectIds.length === 0" icon="ArrowDown">
                  更多
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item icon="Check" @click="handleMoreClick('ongoing')">
                      批量开始
                    </el-dropdown-item>
                    <el-dropdown-item icon="CircleClose" @click="handleMoreClick('completed')">
                      批量结束
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="搜索显示/隐藏">
                <el-button
                  v-hasPerm="['*:*:*']"
                  type="info"
                  icon="search"
                  circle
                  @click="visible = !visible"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button
                  v-hasPerm="['module_badminton:tournament:query']"
                  type="primary"
                  icon="refresh"
                  circle
                  @click="handleRefresh"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-popover placement="bottom" trigger="click">
                <template #reference>
                  <el-button type="danger" icon="operation" circle></el-button>
                </template>
                <el-scrollbar max-height="350px">
                  <template v-for="column in tableColumns" :key="column.prop">
                    <el-checkbox v-if="column.prop" v-model="column.show" :label="column.label" />
                  </template>
                </el-scrollbar>
              </el-popover>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 表格区域 -->
      <div class="data-table__content-wrapper">
        <el-table
          ref="tableRef"
          v-loading="loading"
          :data="pageTableData"
          highlight-current-row
          class="data-table__content"
          border
          stripe
          @selection-change="handleSelectionChange"
        >
          <template #empty>
            <el-empty :image-size="80" description="暂无数据" />
          </template>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'selection')?.show"
            type="selection"
            min-width="55"
            align="center"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'index')?.show"
            fixed
            label="序号"
            min-width="60"
          >
            <template #default="scope">
              {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'name')?.show"
            label="赛事名称"
            prop="name"
            min-width="150"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'format')?.show"
            label="赛制"
            prop="format"
            min-width="120"
          >
            <template #default="scope">
              <el-tag>
                {{ getFormatText(scope.row.format) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'status')?.show"
            label="状态"
            prop="status"
            min-width="100"
          >
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'start_date')?.show"
            label="开始日期"
            prop="start_date"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'end_date')?.show"
            label="结束日期"
            prop="end_date"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'location')?.show"
            label="比赛地点"
            prop="location"
            min-width="150"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'participant_count')?.show"
            label="参赛人数"
            prop="participant_count"
            min-width="100"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
            label="创建时间"
            prop="created_time"
            min-width="180"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'operation')?.show"
            fixed="right"
            label="操作"
            align="center"
            min-width="180"
          >
            <template #default="scope">
              <el-button
                v-hasPerm="['module_badminton:tournament:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:tournament:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:tournament:delete']"
                type="danger"
                size="small"
                link
                icon="delete"
                @click="handleDelete([scope.row.id])"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页区域 -->
      <template #footer>
        <pagination
          v-model:total="total"
          v-model:page="queryFormData.page_no"
          v-model:limit="queryFormData.page_size"
          @pagination="loadingData"
        />
      </template>
    </el-card>

    <!-- 弹窗区域 -->
    <el-dialog
      v-model="dialogVisible.visible"
      :title="dialogVisible.title"
      width="800px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="2" border>
          <ElDescriptionsItem label="赛事名称" :span="2">
            {{ detailFormData.name }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="赛制">
            <el-tag>
              {{ getFormatText(detailFormData.format) }}
            </el-tag>
          </ElDescriptionsItem>
          <ElDescriptionsItem label="状态">
            <el-tag :type="getStatusTagType(detailFormData.status)">
              {{ getStatusText(detailFormData.status) }}
            </el-tag>
          </ElDescriptionsItem>
          <ElDescriptionsItem label="开始日期">
            {{ detailFormData.start_date }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="结束日期">
            {{ detailFormData.end_date }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="比赛地点">
            {{ detailFormData.location || "未设置" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="参赛人数">
            {{ detailFormData.participant_count || 0 }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="规则说明" :span="2">
            {{ detailFormData.rules_description || "无" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="备注" :span="2">
            {{ detailFormData.description || "无" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="创建人">
            {{ detailFormData.created_by?.name || "系统" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="更新人">
            {{ detailFormData.updated_by?.name || "系统" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="创建时间">
            {{ detailFormData.created_time }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="更新时间">
            {{ detailFormData.updated_time }}
          </ElDescriptionsItem>
        </el-descriptions>
      </template>
      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="auto"
          label-position="right"
          inline
        >
          <el-form-item label="赛事名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入赛事名称" :maxlength="100" />
          </el-form-item>
          <el-form-item label="赛制" prop="format">
            <el-select v-model="formData.format" placeholder="请选择赛制">
              <el-option value="group_cycle" label="分组循环赛" />
              <el-option value="pure_group" label="纯小组赛" />
              <el-option value="fixed_zone_promotion" label="定区升降赛" />
              <el-option value="single_elimination" label="小组单败制淘汰赛" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="formData.status">
              <el-radio value="planned">计划中</el-radio>
              <el-radio value="ongoing">进行中</el-radio>
              <el-radio value="completed">已结束</el-radio>
              <el-radio value="cancelled">已取消</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="开始日期" prop="start_date">
            <el-date-picker
              v-model="formData.start_date"
              type="date"
              placeholder="请选择开始日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker
              v-model="formData.end_date"
              type="date"
              placeholder="请选择结束日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="比赛地点">
            <el-input v-model="formData.location" placeholder="请输入比赛地点" :maxlength="200" />
          </el-form-item>
          <el-form-item label="规则说明">
            <el-input
              v-model="formData.rules_description"
              :rows="3"
              :maxlength="500"
              show-word-limit
              type="textarea"
              placeholder="请输入规则说明"
            />
          </el-form-item>
          <el-form-item label="备注">
            <el-input
              v-model="formData.description"
              :rows="3"
              :maxlength="500"
              show-word-limit
              type="textarea"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button v-if="dialogVisible.type !== 'detail'" type="primary" @click="handleSubmit">
            确定
          </el-button>
          <el-button v-else type="primary" @click="handleCloseDialog">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Tournament",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import DatePicker from "@/components/DatePicker/index.vue";
import TournamentAPI, {
  TournamentTable,
  TournamentForm,
  TournamentPageQuery,
} from "@/api/module_badminton/tournament";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<TournamentTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<TournamentTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "赛事名称", show: true },
  { prop: "format", label: "赛制", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "start_date", label: "开始日期", show: true },
  { prop: "end_date", label: "结束日期", show: true },
  { prop: "location", label: "比赛地点", show: true },
  { prop: "participant_count", label: "参赛人数", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<Partial<TournamentTable>>({});
// 日期范围临时变量
const startDateRange = ref<[Date, Date] | []>([]);

// 处理开始日期范围变化
function handleStartDateRangeChange(range: [Date, Date]) {
  startDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.start_date = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.start_date = undefined;
  }
}

// 分页查询参数
const queryFormData = reactive<TournamentPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  format: undefined,
  status: undefined,
  location: undefined,
  start_date: undefined,
  end_date: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<TournamentForm>({
  id: undefined,
  name: "",
  format: "group_cycle",
  status: "planned",
  start_date: "",
  end_date: undefined,
  location: undefined,
  rules_description: undefined,
  description: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入赛事名称", trigger: "blur" }],
  format: [{ required: true, message: "请选择赛制", trigger: "blur" }],
  status: [{ required: true, message: "请选择状态", trigger: "blur" }],
  start_date: [{ required: true, message: "请选择开始日期", trigger: "blur" }],
});

// 获取赛制文本
const getFormatText = (format?: string) => {
  switch (format) {
    case "group_cycle":
      return "分组循环赛";
    case "pure_group":
      return "纯小组赛";
    case "fixed_zone_promotion":
      return "定区升降赛";
    case "single_elimination":
      return "小组单败制淘汰赛";
    default:
      return format || "未知";
  }
};

// 获取状态标签类型
const getStatusTagType = (status?: string) => {
  switch (status) {
    case "planned":
      return "info";
    case "ongoing":
      return "warning";
    case "completed":
      return "success";
    case "cancelled":
      return "danger";
    default:
      return "info";
  }
};

// 获取状态文本
const getStatusText = (status?: string) => {
  switch (status) {
    case "planned":
      return "计划中";
    case "ongoing":
      return "进行中";
    case "completed":
      return "已结束";
    case "cancelled":
      return "已取消";
    default:
      return "未知";
  }
};

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await TournamentAPI.getTournamentList(queryFormData);
    pageTableData.value = response.data.data.items || [];
    total.value = response.data.data.total || 0;
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 查询（重置页码后获取数据）
async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 重置查询
async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  // 重置日期范围选择器
  startDateRange.value = [];
  queryFormData.start_date = undefined;
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: TournamentForm = {
  id: undefined,
  name: "",
  format: "group_cycle",
  status: "planned",
  start_date: "",
  end_date: undefined,
  location: undefined,
  rules_description: undefined,
  description: undefined,
};

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
}

// 行复选框选中项变化
async function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
  selectionRows.value = selection;
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

// 打开弹窗
async function handleOpenDialog(type: "create" | "update" | "detail", id?: number) {
  // 每次打开弹窗前先重置表单
  resetForm();
  dialogVisible.type = type;
  if (id) {
    const response = await TournamentAPI.getTournamentDetail(id);
    if (type === "detail") {
      dialogVisible.title = "赛事详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改赛事";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增赛事";
    formData.id = undefined;
  }
  dialogVisible.visible = true;
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 保存表单数据副本
  const submitData = { ...formData };
  delete submitData.id;

  // 保存操作类型和ID
  const operationType = formData.id ? "update" : "create";
  const updateId = formData.id;

  // 立即关闭窗口
  handleCloseDialog();

  // 显示持久化通知
  const notification = ElNotification({
    title: operationType === "create" ? "创建" : "更新",
    message: "后台保存中...",
    type: "info",
    duration: 0,
    position: "bottom-right",
  });

  // 在后台保存
  try {
    let res;
    if (operationType === "create") {
      res = await TournamentAPI.createTournament(submitData);
    } else if (operationType === "update" && updateId) {
      res = await TournamentAPI.updateTournament(updateId, submitData);
    }

    if (res && res.data.code === 0) {
      notification.close();
      ElNotification({
        title: operationType === "create" ? "创建成功" : "更新成功",
        message: operationType === "create" ? "创建成功" : "更新成功",
        type: "success",
        duration: 3000,
        position: "bottom-right",
      });
      handleResetQuery();
    } else {
      notification.close();
      ElNotification({
        title: "操作失败",
        message: res?.data?.msg || "操作失败",
        type: "error",
        duration: 3000,
        position: "bottom-right",
      });
    }
  } catch (error: any) {
    console.error("提交失败:", error);
    notification.close();
    ElNotification({
      title: "提交失败",
      message: "网络错误或服务器异常",
      type: "error",
      duration: 3000,
      position: "bottom-right",
    });
  }
}

// 删除、批量删除
async function handleDelete(ids: number[]) {
  ElMessageBox.confirm("确认删除该赛事数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await TournamentAPI.deleteTournament(ids);
        handleResetQuery();
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 批量开始/结束
async function handleMoreClick(status: string) {
  if (selectIds.value.length) {
    ElMessageBox.confirm(`确认${status === "ongoing" ? "开始" : "结束"}该赛事?`, "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(async () => {
        try {
          loading.value = true;
          await TournamentAPI.batchSetTournamentStatus({ ids: selectIds.value, status });
          handleResetQuery();
        } catch (error: any) {
          console.error(error);
        } finally {
          loading.value = false;
        }
      })
      .catch(() => {
        ElMessageBox.close();
      });
  }
}

// 列表刷新
async function handleRefresh() {
  await loadingData();
}

onMounted(() => {
  loadingData();
});
</script>

<style scoped>
/* 使表格容器使用flex布局自动填充剩余空间 */
.data-table {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.data-table__content-wrapper {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.data-table__content {
  flex: 1;
}
</style>
