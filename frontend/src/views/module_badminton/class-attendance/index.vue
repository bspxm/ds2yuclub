<!-- 考勤记录管理 -->
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
        <el-form-item prop="student_id" label="学员ID">
          <el-input-number
            v-model="queryFormData.student_id"
            placeholder="学员ID"
            :min="1"
            clearable
            style="width: 120px"
          />
        </el-form-item>
        <el-form-item prop="class_id" label="班级ID">
          <el-input-number
            v-model="queryFormData.class_id"
            placeholder="班级ID"
            :min="1"
            clearable
            style="width: 120px"
          />
        </el-form-item>
        <el-form-item prop="attendance_status" label="考勤状态">
          <el-select
            v-model="queryFormData.attendance_status"
            placeholder="考勤状态"
            style="width: 120px"
            clearable
          >
            <el-option value="present" label="出勤" />
            <el-option value="absent" label="缺勤" />
            <el-option value="leave" label="请假" />
          </el-select>
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:class_attendance:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:class_attendance:list']"
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
            考勤记录管理
            <el-tooltip content="学员上课考勤记录管理">
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
                v-hasPerm="['module_badminton:class_attendance:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增考勤记录
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:class_attendance:delete']"
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
                  v-hasPerm="['module_badminton:class_attendance:list']"
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
          <el-table-column label="学员" prop="student.name" min-width="120" />
          <el-table-column label="班级" prop="class.name" min-width="120" />
          <el-table-column label="考勤日期" prop="attendance_date" min-width="120" />
          <el-table-column label="考勤状态" prop="attendance_status" min-width="90">
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.attendance_status === 'present'
                    ? 'success'
                    : scope.row.attendance_status === 'absent'
                      ? 'danger'
                      : 'warning'
                "
              >
                {{
                  scope.row.attendance_status === "present"
                    ? "出勤"
                    : scope.row.attendance_status === "absent"
                      ? "缺勤"
                      : "请假"
                }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="考勤时间" prop="attendance_time" min-width="120" />
          <el-table-column
            label="请假原因"
            prop="leave_reason"
            min-width="120"
            show-overflow-tooltip
          />
          <el-table-column label="创建时间" prop="created_time" min-width="180" />
          <el-table-column fixed="right" label="操作" align="center" min-width="180">
            <template #default="scope">
              <el-button
                v-hasPerm="['module_badminton:class_attendance:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:class_attendance:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:class_attendance:delete']"
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
      width="600px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学员" :span="2">
            {{ detailFormData.student?.name || detailFormData.student_id }}
          </el-descriptions-item>
          <el-descriptions-item label="班级">
            {{ detailFormData.class?.name || detailFormData.class_id }}
          </el-descriptions-item>
          <el-descriptions-item label="考勤日期">
            {{ detailFormData.attendance_date }}
          </el-descriptions-item>
          <el-descriptions-item label="考勤状态">
            <el-tag
              :type="
                detailFormData.attendance_status === 'present'
                  ? 'success'
                  : detailFormData.attendance_status === 'absent'
                    ? 'danger'
                    : 'warning'
              "
            >
              {{
                detailFormData.attendance_status === "present"
                  ? "出勤"
                  : detailFormData.attendance_status === "absent"
                    ? "缺勤"
                    : "请假"
              }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="考勤时间">
            {{ detailFormData.attendance_time || "未记录" }}
          </el-descriptions-item>
          <el-descriptions-item label="请假原因" :span="2">
            {{ detailFormData.leave_reason || "无" }}
          </el-descriptions-item>
          <el-descriptions-item label="补课排课ID">
            {{ detailFormData.makeup_schedule_id || "无" }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detailFormData.notes || "无" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ detailFormData.created_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ detailFormData.created_time }}
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
            <el-col :span="24">
              <el-form-item label="学员ID" prop="student_id">
                <el-input-number
                  v-model="formData.student_id"
                  :min="1"
                  placeholder="学员ID"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="班级ID" prop="class_id">
                <el-input-number
                  v-model="formData.class_id"
                  :min="1"
                  placeholder="班级ID"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="考勤日期" prop="attendance_date">
                <el-date-picker
                  v-model="formData.attendance_date"
                  type="date"
                  placeholder="请选择考勤日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="考勤状态" prop="attendance_status">
                <el-select
                  v-model="formData.attendance_status"
                  placeholder="请选择考勤状态"
                  style="width: 100%"
                >
                  <el-option value="present" label="出勤" />
                  <el-option value="absent" label="缺勤" />
                  <el-option value="leave" label="请假" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col v-if="formData.attendance_status === 'leave'" :span="24">
              <el-form-item label="请假原因">
                <el-input
                  v-model="formData.leave_reason"
                  placeholder="请输入请假原因"
                  :maxlength="200"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
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
  name: "ClassAttendance",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled } from "@element-plus/icons-vue";
import ClassAttendanceAPI, {
  ClassAttendanceTable,
  ClassAttendanceForm,
  ClassAttendancePageQuery,
} from "@/api/module_badminton/class-attendance";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<ClassAttendanceTable[]>([]);
const loading = ref(false);

// 分页表单
const pageTableData = ref<ClassAttendanceTable[]>([]);

// 详情表单
const detailFormData = ref<ClassAttendanceTable>({});

// 分页查询参数
const queryFormData = reactive<ClassAttendancePageQuery>({
  page_no: 1,
  page_size: 10,
  student_id: undefined,
  class_id: undefined,
  schedule_id: undefined,
  attendance_status: undefined,
  attendance_date_start: undefined,
  attendance_date_end: undefined,
});

// 编辑表单
const formData = reactive<ClassAttendanceForm>({
  id: undefined,
  student_id: undefined,
  class_id: undefined,
  schedule_id: undefined,
  attendance_date: "",
  attendance_status: "present",
  attendance_time: "",
  leave_reason: undefined,
  makeup_schedule_id: undefined,
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
  student_id: [{ required: true, message: "请输入学员ID", trigger: "blur" }],
  class_id: [{ required: true, message: "请输入班级ID", trigger: "blur" }],
  attendance_date: [{ required: true, message: "请选择考勤日期", trigger: "blur" }],
  attendance_status: [{ required: true, message: "请选择考勤状态", trigger: "blur" }],
});

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await ClassAttendanceAPI.getClassAttendanceList(queryFormData);
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
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: ClassAttendanceForm = {
  id: undefined,
  student_id: undefined,
  class_id: undefined,
  schedule_id: undefined,
  attendance_date: "",
  attendance_status: "present",
  attendance_time: "",
  leave_reason: undefined,
  makeup_schedule_id: undefined,
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
  if (id) {
    const response = await ClassAttendanceAPI.getClassAttendanceDetail(id);
    if (type === "detail") {
      dialogVisible.title = "考勤记录详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改考勤记录";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增考勤记录";
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
      res = await ClassAttendanceAPI.createClassAttendance(submitData);
    } else if (operationType === "update" && updateId) {
      res = await ClassAttendanceAPI.updateClassAttendance(updateId, submitData);
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

// 删除
async function handleDelete(ids: number[]) {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${ids.length} 条记录吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await ClassAttendanceAPI.deleteClassAttendance(ids);
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
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.data-table__content {
  flex: 1;
}
</style>
