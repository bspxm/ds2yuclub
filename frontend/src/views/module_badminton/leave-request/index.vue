<!-- 请假管理 -->
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
        <el-form-item prop="student_name" label="学员姓名">
          <el-input v-model="queryFormData.student_name" placeholder="请输入学员姓名" clearable />
        </el-form-item>
        <el-form-item prop="course_name" label="课程名称">
          <el-input v-model="queryFormData.course_name" placeholder="请输入课程名称" clearable />
        </el-form-item>
        <el-form-item prop="status" label="请假状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请假状态"
            style="width: 120px"
            clearable
          >
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isExpand" prop="leave_date_start" label="请假日期范围">
          <DatePicker
            v-model="leaveDateRange"
            type="daterange"
            @update:model-value="handleLeaveDateRangeChange"
          />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:leave:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:leave:list']"
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
            请假管理
            <el-tooltip content="学员请假申请管理">
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
                v-hasPerm="['module_badminton:leave:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增请假
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:leave:delete']"
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
                  v-hasPerm="['module_badminton:leave:list']"
                  type="primary"
                  icon="refresh"
                  circle
                  @click="handleRefresh"
                />
              </el-tooltip>
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
          <el-table-column type="selection" min-width="55" align="center" />
          <el-table-column fixed label="序号" min-width="60">
            <template #default="scope">
              {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="student_name" label="学员姓名" min-width="120" />
          <el-table-column prop="course_name" label="课程名称" min-width="150" />
          <el-table-column prop="leave_date" label="请假日期" min-width="120" />
          <el-table-column prop="reason" label="请假原因" min-width="200" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="approver_name" label="审批人" min-width="120" />
          <el-table-column prop="approved_time" label="审批时间" min-width="180" />
          <el-table-column prop="created_time" label="创建时间" min-width="180" />
          <el-table-column fixed="right" label="操作" align="center" min-width="260">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'pending'"
                v-hasPerm="['module_badminton:leave:approve']"
                type="success"
                link
                size="small"
                icon="check"
                @click="handleApprove()"
              >
                批准
              </el-button>
              <el-button
                v-if="row.status === 'pending'"
                v-hasPerm="['module_badminton:leave:approve']"
                type="danger"
                link
                size="small"
                icon="close"
                @click="handleReject()"
              >
                拒绝
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:leave:update']"
                type="primary"
                link
                size="small"
                icon="edit"
                @click="handleOpenDialog('update', row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:leave:delete']"
                type="danger"
                link
                size="small"
                icon="delete"
                @click="handleDelete([row.id])"
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
      <el-form
        ref="dataFormRef"
        :model="formData"
        :rules="rules"
        label-suffix=":"
        label-width="auto"
        label-position="right"
      >
        <el-form-item label="学员" prop="student_id">
          <el-select
            v-model="formData.student_id"
            placeholder="请选择学员"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="student in studentOptions"
              :key="student.value"
              :label="student.label"
              :value="student.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select
            v-model="formData.course_id"
            placeholder="请选择课程"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="course in courseOptions"
              :key="course.value"
              :label="course.label"
              :value="course.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="请假日期" prop="leave_date">
          <el-date-picker
            v-model="formData.leave_date"
            type="date"
            placeholder="请选择请假日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="请假原因" prop="reason">
          <el-input
            v-model="formData.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入请假原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="handleSubmit">确定</el-button>
          <el-button @click="handleCloseDialog">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "BadmintonLeaveRequest",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown } from "@element-plus/icons-vue";

const queryFormRef = ref<FormInstance>();
const dataFormRef = ref<FormInstance>();
const tableRef = ref();
const selectIds = ref<number[]>([]);
const loading = ref(false);

const visible = ref(true);
const isExpand = ref(false);
const isExpandable = ref(false);

// 分页表单
const pageTableData = ref<any[]>([]);
const total = ref(0);

// 分页查询参数
const queryFormData = reactive({
  page_no: 1,
  page_size: 10,
  student_name: undefined as string | undefined,
  course_name: undefined as string | undefined,
  status: undefined as string | undefined,
  leave_date_range: undefined as any,
});

// 编辑表单
const formData = reactive({
  id: undefined as number | undefined,
  student_id: undefined as string | undefined,
  course_id: undefined as string | undefined,
  leave_date: undefined as string | undefined,
  reason: undefined as string | undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update",
});

// 学员选项
const studentOptions = ref<Array<{ value: string; label: string }>>([]);
// 课程选项
const courseOptions = ref<Array<{ value: string; label: string }>>([]);

// 日期范围临时变量
const leaveDateRange = ref<[Date, Date] | []>([]);

// 表单验证规则
const rules: FormRules = {
  student_id: [{ required: true, message: "请选择学员", trigger: "blur" }],
  course_id: [{ required: true, message: "请选择课程", trigger: "blur" }],
  leave_date: [{ required: true, message: "请选择请假日期", trigger: "blur" }],
  reason: [
    { required: true, message: "请输入请假原因", trigger: "blur" },
    { min: 2, max: 500, message: "长度 2 到 500 个字符", trigger: "blur" },
  ],
};

// 处理日期范围变化
function handleLeaveDateRangeChange(range: [Date, Date]) {
  leaveDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.leave_date_range = range;
  } else {
    queryFormData.leave_date_range = undefined;
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case "approved":
      return "success";
    case "rejected":
      return "danger";
    case "cancelled":
      return "info";
    default:
      return "warning";
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case "pending":
      return "待审批";
    case "approved":
      return "已批准";
    case "rejected":
      return "已拒绝";
    case "cancelled":
      return "已取消";
    default:
      return status;
  }
};

// 查询
async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 重置查询
async function handleResetQuery() {
  if (queryFormRef.value) {
    queryFormRef.value.resetFields();
  }
  leaveDateRange.value = [];
  queryFormData.leave_date_range = undefined;
  handleQuery();
}

// 刷新
async function handleRefresh() {
  loadingData();
}

// 行复选框选中项变化
async function handleSelectionChange(selection: any[]) {
  selectIds.value = selection.map((item: any) => item.id);
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

// 打开弹窗
async function handleOpenDialog(type: "create" | "update", id?: number) {
  dialogVisible.type = type;
  if (id) {
    dialogVisible.title = "编辑请假";
    const row = pageTableData.value.find((item) => item.id === id);
    if (row) {
      Object.assign(formData, row);
    }
  } else {
    dialogVisible.title = "新增请假";
    resetForm();
  }
  dialogVisible.visible = true;
}

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  Object.assign(formData, {
    id: undefined,
    student_id: undefined,
    course_id: undefined,
    leave_date: undefined,
    reason: undefined,
  });
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 保存表单数据副本
  const submitData = { ...formData };
  delete submitData.id;

  // 保存操作类型
  const operationType = dialogVisible.type;

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

  // 在后台保存（TODO: 调用API保存数据）
  try {
    // TODO: 替换为实际的API调用
    // let res;
    // if (operationType === "create") {
    //   res = await SomeAPI.create(submitData);
    // } else if (operationType === "update" && updateId) {
    //   res = await SomeAPI.update(updateId, submitData);
    // }

    // 模拟API调用
    await new Promise((resolve) => setTimeout(resolve, 500));

    notification.close();
    ElNotification({
      title: operationType === "create" ? "创建成功" : "更新成功",
      message: operationType === "create" ? "创建成功" : "更新成功",
      type: "success",
      duration: 3000,
      position: "bottom-right",
    });
    loadingData();
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
  ElMessageBox.confirm(`确定删除选中的${ids.length}条记录吗？`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      loading.value = true;
      // TODO: 调用API删除数据
      setTimeout(() => {
        loading.value = false;
        ElMessage.success("删除成功");
        loadingData();
      }, 500);
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 批准
async function handleApprove() {
  ElMessageBox.confirm(`确定批准该请假申请吗？`, "批准请假", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      loading.value = true;
      // TODO: 调用API批准请假
      setTimeout(() => {
        loading.value = false;
        ElMessage.success("已批准");
        loadingData();
      }, 500);
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 拒绝
async function handleReject() {
  ElMessageBox.confirm(`确定拒绝该请假申请吗？`, "拒绝请假", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      loading.value = true;
      // TODO: 调用API拒绝请假
      setTimeout(() => {
        loading.value = false;
        ElMessage.success("已拒绝");
        loadingData();
      }, 500);
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 加载数据
async function loadingData() {
  loading.value = true;
  try {
    // TODO: 调用API获取数据
    // 模拟数据
    setTimeout(() => {
      pageTableData.value = [
        {
          id: 1,
          student_name: "张三",
          course_name: "周一基础班",
          leave_date: "2026-01-20",
          reason: "生病发烧",
          status: "pending",
          approver_name: "",
          approved_time: "",
          created_time: "2026-01-18 14:30:00",
        },
        {
          id: 2,
          student_name: "李四",
          course_name: "周三提高班",
          leave_date: "2026-01-19",
          reason: "家庭事务",
          status: "approved",
          approver_name: "王教练",
          approved_time: "2026-01-18 10:15:00",
          created_time: "2026-01-17 09:20:00",
        },
      ];
      total.value = 2;
      loading.value = false;
    }, 300);
  } catch (error: any) {
    console.error(error);
    ElMessage.error("加载数据失败");
    loading.value = false;
  }
}

// 加载学员选项
async function loadStudentOptions() {
  // TODO: 调用API获取学员列表
  studentOptions.value = [
    { value: "1", label: "张三" },
    { value: "2", label: "李四" },
    { value: "3", label: "王五" },
  ];
}

// 加载课程选项
async function loadCourseOptions() {
  // TODO: 调用API获取课程列表
  courseOptions.value = [
    { value: "1", label: "周一基础班" },
    { value: "2", label: "周三提高班" },
    { value: "3", label: "周五进阶班" },
  ];
}

onMounted(() => {
  loadStudentOptions();
  loadCourseOptions();
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
