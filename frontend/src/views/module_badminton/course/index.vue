<!-- 课程管理 -->
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
        <el-form-item prop="course_name" label="课程名称">
          <el-input v-model="queryFormData.course_name" placeholder="请输入课程名称" clearable />
        </el-form-item>
        <el-form-item prop="coach_id" label="教练">
          <el-select
            v-model="queryFormData.coach_id"
            placeholder="请选择教练"
            style="width: 120px"
            clearable
            filterable
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.name || user.username"
              :value="user.id as number"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请选择状态"
            style="width: 120px"
            clearable
          >
            <el-option value="scheduled" label="已安排" />
            <el-option value="in_progress" label="进行中" />
            <el-option value="completed" label="已完成" />
            <el-option value="cancelled" label="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isExpand" prop="course_type" label="课程类型">
          <el-input v-model="queryFormData.course_type" placeholder="请输入课程类型" clearable />
        </el-form-item>
        <el-form-item v-if="isExpand" prop="start_time" label="开始时间">
          <DatePicker v-model="startTimeRange" @update:model-value="handleStartTimeRangeChange" />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:course:query']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:course:query']"
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
            课程管理
            <el-tooltip content="羽毛球课程管理">
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
                v-hasPerm="['module_badminton:course:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增课程
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:course:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_badminton:course:patch']" trigger="click">
                <el-button type="default" :disabled="selectIds.length === 0" icon="ArrowDown">
                  更多
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item icon="Check" @click="handleMoreClick('started')">
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
                  v-hasPerm="['module_badminton:course:query']"
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
          <template v-if="tableColumns.find((col) => col.prop === 'name')?.show">
            <el-table-column prop="name" label="课程名称" min-width="120" show-overflow-tooltip />
          </template>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'course_type')?.show"
            label="课程类型"
            prop="course_type"
            min-width="120"
          />
          <template v-if="tableColumns.find((col) => col.prop === 'coach')?.show">
            <el-table-column prop="coach" label="教练" min-width="100" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.coach?.name || "未分配" }}
              </template>
            </el-table-column>
          </template>
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
            v-if="tableColumns.find((col) => col.prop === 'start_time')?.show"
            label="开始时间"
            prop="start_time"
            min-width="180"
          />
          <template v-if="tableColumns.find((col) => col.prop === 'end_time')?.show">
            <el-table-column
              prop="end_time"
              label="结束时间"
              min-width="150"
              show-overflow-tooltip
            />
          </template>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'max_students')?.show"
            label="最大学员数"
            prop="max_students"
            min-width="100"
          />
          <template v-if="tableColumns.find((col) => col.prop === 'court_number')?.show">
            <el-table-column
              prop="court_number"
              label="场地号"
              min-width="80"
              show-overflow-tooltip
            />
          </template>
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
                v-hasPerm="['module_badminton:course:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:course:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:course:delete']"
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
          <ElDescriptionsItem label="课程名称" :span="2">
            {{ detailFormData.course_name }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="课程类型">
            {{ detailFormData.course_type || "未设置" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="状态">
            <el-tag :type="getStatusTagType(detailFormData.status)">
              {{ getStatusText(detailFormData.status) }}
            </el-tag>
          </ElDescriptionsItem>
          <ElDescriptionsItem label="教练">
            {{ detailFormData.coach?.name || detailFormData.instructor_name || "未分配" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="开始时间">
            {{ detailFormData.start_time }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="结束时间">
            {{ detailFormData.end_time || "未设置" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="最大学员数">
            {{ detailFormData.max_students || 0 }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="最小学员数">
            {{ detailFormData.min_students || 0 }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="场地号">
            {{ detailFormData.court_number || "未设置" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="备注" :span="2">
            {{ detailFormData.notes || "无" }}
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
          <el-form-item label="课程名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入课程名称" :maxlength="100" />
          </el-form-item>
          <el-form-item prop="course_type" label="课程类型">
            <el-select
              v-model="formData.course_type"
              placeholder="请选择课程类型"
              style="width: 100%"
            >
              <el-option value="regular" label="常规课" />
              <el-option value="private" label="私教课" />
              <el-option value="group" label="小组课" />
              <el-option value="competition" label="比赛课" />
              <el-option value="theory" label="理论课" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="(formData as any).status">
              <el-radio value="scheduled">已安排</el-radio>
              <el-radio value="in_progress">进行中</el-radio>
              <el-radio value="completed">已完成</el-radio>
              <el-radio value="cancelled">已取消</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="教练" prop="coach_id">
            <el-select
              v-model="formData.coach_id"
              placeholder="请选择教练"
              style="width: 100%"
              clearable
              filterable
            >
              <el-option
                v-for="user in userList"
                :key="user.id"
                :label="user.name || user.username"
                :value="user.id as number"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="开始时间" prop="start_time">
            <el-date-picker
              v-model="formData.start_time"
              type="datetime"
              placeholder="请选择开始时间"
              style="width: 100%"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
          <el-form-item label="结束时间" prop="end_time">
            <el-date-picker
              v-model="formData.end_time"
              type="datetime"
              placeholder="请选择结束时间"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="时长(分钟)" prop="duration">
            <el-input-number
              v-model="(formData as any).duration"
              :min="30"
              :max="240"
              :step="30"
              placeholder="请输入时长"
            />
          </el-form-item>
          <el-form-item label="最大学员数">
            <el-input
              v-model="formData.max_students"
              placeholder="请输入最大学员数"
              type="number"
            />
          </el-form-item>
          <el-form-item label="最小学员数">
            <el-input
              v-model="formData.min_students"
              placeholder="请输入最小学员数"
              type="number"
            />
          </el-form-item>
          <el-form-item label="价格">
            <el-input v-model="formData.price" placeholder="请输入价格" type="number" />
          </el-form-item>
          <el-form-item label="场地号">
            <el-input v-model="formData.court_number" placeholder="请输入场地号" :maxlength="50" />
          </el-form-item>
          <el-form-item label="所属校区">
            <el-input v-model="formData.campus" placeholder="请输入所属校区" :maxlength="100" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input
              v-model="formData.notes"
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
  name: "Course",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElNotification } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import DatePicker from "@/components/DatePicker/index.vue";
import CourseAPI from "@/api/module_badminton/course";
import type { CourseTable, CourseForm, CoursePageQuery } from "@/api/module_badminton/course";
import UserAPI, { UserInfo } from "@/api/module_system/user";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<CourseTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<CourseTable[]>([]);
const userList = ref<UserInfo[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "课程名称", show: true },
  { prop: "course_type", label: "课程类型", show: true },
  { prop: "coach", label: "教练", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "start_time", label: "开始时间", show: true },
  { prop: "end_time", label: "结束时间", show: true },
  { prop: "max_students", label: "最大学员数", show: true },
  { prop: "court_number", label: "场地号", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<Partial<CourseTable>>({
  name: "",
  course_type: "",
  start_time: "",
  end_time: "",
});
// 时间范围临时变量
const startTimeRange = ref<[Date, Date] | []>([]);

// 处理开始时间范围变化
function handleStartTimeRangeChange(range: [Date, Date]) {
  startTimeRange.value = range;
  if (range && range.length === 2) {
    queryFormData.start_time = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.start_time = undefined;
  }
}

// 分页查询参数
const queryFormData = reactive<CoursePageQuery>({
  page_no: 1,
  page_size: 10,
  course_name: undefined,
  course_type: undefined,
  status: undefined,
  start_time: undefined,
  end_time: undefined,
});

// 编辑表单
const formData = reactive<CourseForm & { id?: number }>({
  id: undefined,
  name: "",
  course_type: "regular",
  coach_id: undefined,
  campus: undefined,
  court_number: undefined,
  start_time: "",
  end_time: "",
  max_students: undefined,
  min_students: undefined,
  price: undefined,
  notes: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  course_name: [{ required: true, message: "请输入课程名称", trigger: "blur" }],
  status: [{ required: true, message: "请选择状态", trigger: "blur" }],
  start_time: [{ required: true, message: "请选择开始时间", trigger: "blur" }],
  duration: [{ required: true, message: "请输入时长", trigger: "blur" }],
});

// 获取状态标签类型
const getStatusTagType = (status?: string) => {
  switch (status) {
    case "scheduled":
      return "info";
    case "in_progress":
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
    case "scheduled":
      return "已安排";
    case "in_progress":
      return "进行中";
    case "completed":
      return "已完成";
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
    const response = await CourseAPI.getUpcomingCourses(30); // 获取30天内的课程
    pageTableData.value = response.data.data || [];
    total.value = pageTableData.value.length;
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
  // 重置时间范围选择器
  startTimeRange.value = [];
  queryFormData.start_time = undefined;
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: CourseForm & { id?: number } = {
  id: undefined,
  name: "",
  course_type: "regular",
  coach_id: undefined,
  campus: undefined,
  court_number: undefined,
  start_time: "",
  end_time: "",
  max_students: undefined,
  min_students: undefined,
  price: undefined,
  notes: undefined,
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

  if (type === "detail" && id) {
    // 详情：从当前表格数据中查找
    dialogVisible.title = "课程详情";
    const course = pageTableData.value.find((item) => item.id === id);
    if (course) {
      Object.assign(detailFormData.value, course);
    }
  } else if (type === "update" && id) {
    // 编辑：由于API不支持，暂时禁用编辑功能
    ElMessage.warning("课程编辑功能暂未实现");
    return;
  } else {
    dialogVisible.title = "新增课程";
    formData.id = undefined;
  }
  dialogVisible.visible = true;
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 保存表单数据副本（排除id）
  const { id, ...submitData } = formData;

  // 立即关闭窗口
  handleCloseDialog();

  // 显示持久化通知
  const notification = ElNotification({
    title: "创建",
    message: "后台保存中...",
    type: "info",
    duration: 0,
    position: "bottom-right",
  });

  // 在后台保存
  try {
    const res = await CourseAPI.createCourse(submitData);

    if (res.data.code === 0) {
      notification.close();
      ElNotification({
        title: "创建成功",
        message: "创建成功",
        type: "success",
        duration: 3000,
        position: "bottom-right",
      });
      loadingData();
    } else {
      notification.close();
      ElNotification({
        title: "操作失败",
        message: res.data.msg || "操作失败",
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
async function handleDelete(_ids: number[]) {
  ElMessage.warning("课程删除功能暂未实现");
}

// 批量开始/结束
async function handleMoreClick(_status: string) {
  ElMessage.warning("批量操作功能暂未实现");
}

// 列表刷新
async function handleRefresh() {
  await loadingData();
}

// 获取用户列表
const loadUserList = async () => {
  try {
    const response = await UserAPI.listUser({
      page: 1,
      page_size: 100, // API限制最大100
      status: "0", // 只获取启用状态的用户
    } as any); // 临时使用any绕过类型检查
    if (response.data?.data?.items) {
      userList.value = response.data.data.items;
    }
  } catch (error) {
    console.error("获取用户列表失败:", error);
  }
};

onMounted(() => {
  loadUserList();
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
