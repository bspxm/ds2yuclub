<!-- 学期管理 -->
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
        <el-form-item prop="name" label="学期名称">
          <el-input v-model="queryFormData.name" placeholder="请输入学期名称" clearable />
        </el-form-item>
        <el-form-item prop="semester_type" label="学期类型">
          <el-select
            v-model="queryFormData.semester_type"
            placeholder="请选择学期类型"
            style="width: 120px"
            clearable
          >
            <el-option value="regular" label="常规学期" />
            <el-option value="wintersummer" label="寒暑假" />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="学期状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请选择学期状态"
            style="width: 120px"
            clearable
          >
            <el-option value="active" label="进行中" />
            <el-option value="completed" label="已结束" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isExpand" prop="start_date" label="开始日期范围">
          <DatePicker
            v-model="startDateRange"
            type="daterange"
            @update:model-value="handleStartDateRangeChange"
          />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:semester:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:semester:list']"
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
            学期管理
            <el-tooltip content="学期信息管理">
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
                v-hasPerm="['module_badminton:semester:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增学期
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:semester:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
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
                  v-hasPerm="['module_badminton:semester:list']"
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
            label="学期名称"
            prop="name"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'semester_type')?.show"
            label="学期类型"
            prop="semester_type"
            min-width="100"
          >
            <template #default="scope">
              <el-tag :type="scope.row.semester_type === 'regular' ? 'primary' : 'warning'">
                {{ scope.row.semester_type === "regular" ? "常规学期" : "寒暑假" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'start_date')?.show"
            label="开始日期"
            prop="start_date"
            min-width="180"
          >
            <template #default="scope">
              {{ formatDateTime(scope.row.start_date) }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'end_date')?.show"
            label="结束日期"
            prop="end_date"
            min-width="180"
          >
            <template #default="scope">
              {{ formatDateTime(scope.row.end_date) }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'week_count')?.show"
            label="总周数"
            prop="week_count"
            min-width="90"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'status')?.show"
            label="状态"
            prop="status"
            min-width="90"
          >
            <template #default="scope">
              <el-tag :type="(statusTypeMap[scope.row.status || ''] || 'info') as any">
                {{ statusMap[scope.row.status || ""] || scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
            label="创建时间"
            prop="created_time"
            min-width="180"
          >
            <template #default="scope">
              {{ formatDateTime(scope.row.created_time) }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'operation')?.show"
            fixed="right"
            label="操作"
            align="center"
            min-width="180"
          >
            <template #default="scope">
              <el-button
                v-hasPerm="['module_badminton:semester:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:semester:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:semester:delete']"
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
          <el-descriptions-item label="学期名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="学期类型">
            <el-tag :type="detailFormData.semester_type === 'regular' ? 'primary' : 'warning'">
              {{ detailFormData.semester_type === "regular" ? "常规学期" : "寒暑假" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="学期状态">
            <el-tag :type="(statusTypeMap[detailFormData.status || ''] || 'info') as any">
              {{ statusMap[detailFormData.status || ""] || detailFormData.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ formatDateTime(detailFormData.start_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期">
            {{ formatDateTime(detailFormData.end_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="总周数">
            {{ detailFormData.week_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ detailFormData.created_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="更新人">
            {{ detailFormData.updated_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(detailFormData.created_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(detailFormData.updated_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detailFormData.description || "无" }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="120px"
          label-position="right"
        >
          <el-row :gutter="20">
            <!-- 第一行：学期名称、学期类型 -->
            <el-col :span="12">
              <el-form-item label="学期名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入学期名称" :maxlength="64" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="学期类型" prop="semester_type">
                <el-select
                  v-model="formData.semester_type"
                  placeholder="请选择学期类型"
                  style="width: 100%"
                >
                  <el-option value="regular" label="常规学期" />
                  <el-option value="wintersummer" label="寒暑假" />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- 第二行：开始日期、结束日期 -->
            <el-col :span="12">
              <el-form-item label="开始日期" prop="start_date">
                <el-date-picker
                  v-model="formData.start_date"
                  type="date"
                  placeholder="请选择开始日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期" prop="end_date">
                <el-date-picker
                  v-model="formData.end_date"
                  type="date"
                  placeholder="请选择结束日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>

            <!-- 第三行：总周数、学期状态 -->
            <el-col :span="12">
              <el-form-item label="总周数">
                <el-input-number
                  v-model="formData.week_count"
                  :min="1"
                  :max="52"
                  placeholder="总周数"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="学期状态" prop="status">
                <el-select
                  v-model="formData.status"
                  placeholder="请选择学期状态"
                  style="width: 100%"
                >
                  <el-option value="active" label="进行中" />
                  <el-option value="completed" label="已结束" />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- 第四行：备注（跨两列） -->
            <el-col :span="24">
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
            </el-col>
          </el-row>
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
  name: "Semester",
  inheritAttrs: false,
});

import { ref, reactive, onMounted, watch } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";

// 时间格式化函数（精确到秒）
function formatDateTime(timestamp: any): string {
  if (!timestamp) return "";
  if (typeof timestamp === "string") {
    // 处理 ISO 8601 格式的时间字符串（如：2026-01-20T23:49:12.804965）
    // 去掉微秒部分（.后的内容）
    const cleanTimestamp = timestamp.replace(/\.\d+$/, "");
    const date = new Date(cleanTimestamp);
    if (isNaN(date.getTime())) {
      return timestamp; // 如果解析失败，返回原字符串
    }
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  }
  const date = new Date(timestamp);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

// 状态显示映射（与后端 SemesterStatusEnum 保持一致）
const statusMap: Record<string, string> = {
  active: "进行中",
  completed: "已结束",
};

const statusTypeMap: Record<string, string> = {
  active: "success",
  completed: "warning",
};
import DatePicker from "@/components/DatePicker/index.vue";
import SemesterAPI, {
  SemesterTable,
  SemesterForm,
  SemesterPageQuery,
} from "@/api/module_badminton/semester";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<SemesterTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<SemesterTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "学期名称", show: true },
  { prop: "semester_type", label: "学期类型", show: true },
  { prop: "start_date", label: "开始日期", show: true },
  { prop: "end_date", label: "结束日期", show: true },
  { prop: "week_count", label: "总周数", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<SemesterTable>({});
// 日期范围临时变量
const startDateRange = ref<[Date, Date] | []>([]);

// 处理开始日期范围变化
function handleStartDateRangeChange(range: [Date, Date]) {
  startDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.start_date_start = formatToDateTime(range[0]);
    queryFormData.start_date_end = formatToDateTime(range[1]);
  } else {
    queryFormData.start_date_start = undefined;
    queryFormData.start_date_end = undefined;
  }
}

// 分页查询参数
const queryFormData = reactive<SemesterPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  semester_type: undefined,
  status: undefined,
  start_date_start: undefined,
  start_date_end: undefined,
});

// 编辑表单
const formData = reactive<SemesterForm>({
  id: undefined,
  name: "",
  semester_type: "regular",
  start_date: "",
  end_date: "",
  week_count: 16,
  status: "active",
  description: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 计算自然周数（从开始日期所在周的周一到结束日期所在周的周日）
function calculateNaturalWeeks(startDate: string, endDate: string): number {
  const start = new Date(startDate);
  const end = new Date(endDate);

  // 获取开始日期所在周的周一
  const startDay = start.getDay(); // 0=周日, 1=周一...
  const daysToMonday = startDay === 0 ? 6 : startDay - 1;
  const monday = new Date(start);
  monday.setDate(start.getDate() - daysToMonday);
  monday.setHours(0, 0, 0, 0);

  // 获取结束日期所在周的周日
  const endDay = end.getDay();
  const daysToSunday = endDay === 0 ? 0 : 7 - endDay;
  const sunday = new Date(end);
  sunday.setDate(end.getDate() + daysToSunday);
  sunday.setHours(0, 0, 0, 0);

  const diffTime = sunday.getTime() - monday.getTime();
  const diffDays = diffTime / (1000 * 60 * 60 * 24);

  return Math.floor(diffDays / 7) + 1;
}

// 监听日期变化，自动计算总周数（仅在新建时）
watch(
  () => [formData.start_date, formData.end_date],
  ([start, end]) => {
    if (dialogVisible.type === "create" && start && end) {
      formData.week_count = calculateNaturalWeeks(start as string, end as string);
    }
  }
);

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入学期名称", trigger: "blur" }],
  semester_type: [{ required: true, message: "请选择学期类型", trigger: "blur" }],
  start_date: [{ required: true, message: "请选择开始日期", trigger: "blur" }],
  end_date: [{ required: true, message: "请选择结束日期", trigger: "blur" }],
  status: [{ required: true, message: "请选择学期状态", trigger: "blur" }],
});

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await SemesterAPI.getSemesterList(queryFormData);
    pageTableData.value = response.data.data.items;
    total.value = response.data.data.total;
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
  queryFormData.start_date_start = undefined;
  queryFormData.start_date_end = undefined;
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: SemesterForm = {
  id: undefined,
  name: "",
  semester_type: "regular",
  start_date: "",
  end_date: "",
  week_count: 16,
  status: "active",
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
    const response = await SemesterAPI.getSemesterDetail(id);
    if (type === "detail") {
      dialogVisible.title = "学期详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改学期";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增学期";
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
  const operationType = dialogVisible.type;
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
      res = await SemesterAPI.createSemester(submitData);
    } else if (operationType === "update" && updateId) {
      res = await SemesterAPI.updateSemester(updateId, submitData);
    }

    if (!res) {
      throw new Error("操作失败：未获取到响应");
    }

    if (res.data.code === 0) {
      notification.close();
      ElNotification({
        title: operationType === "create" ? "创建成功" : "更新成功",
        message: operationType === "create" ? "创建成功" : "更新成功",
        type: "success",
        duration: 3000,
        position: "bottom-right",
      });
      loadingData();
    } else {
      notification.close();
      ElNotification({
        title: "操作失败",
        message: res!.data.msg || "操作失败",
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

// 删除
async function handleDelete(ids: number[]) {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${ids.length} 条记录吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await SemesterAPI.deleteSemester(ids);
    ElMessage.success("删除成功");
    loadingData();
    selectIds.value = [];
  } catch (error: any) {
    if (error !== "cancel") {
      console.error(error);
    }
  }
}

// 刷新
async function handleRefresh() {
  loadingData();
}

// 页面加载时获取数据
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
  display: flex;
  flex: 1;
  flex-direction: column;
  overflow: hidden;
}

.data-table__content {
  flex: 1;
}
</style>
