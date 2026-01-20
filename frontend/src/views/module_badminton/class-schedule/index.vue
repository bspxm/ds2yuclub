<!-- 排课记录管理 -->
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
        <el-form-item prop="class_id" label="班级ID">
          <el-input-number v-model="queryFormData.class_id" placeholder="班级ID" :min="1" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item prop="schedule_status" label="排课状态">
          <el-select
            v-model="queryFormData.schedule_status"
            placeholder="排课状态"
            style="width: 120px"
            clearable
          >
            <el-option value="scheduled" label="已排课" />
            <el-option value="in_progress" label="进行中" />
            <el-option value="completed" label="已完成" />
            <el-option value="cancelled" label="已取消" />
          </el-select>
        </el-form-item>
        <!-- 查询、重置按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:class_schedule:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:class_schedule:list']"
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
            排课记录管理
            <el-tooltip content="班级课程安排记录管理">
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
                v-hasPerm="['module_badminton:class_schedule:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增排课记录
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:class_schedule:delete']"
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
                  v-hasPerm="['module_badminton:class_schedule:list']"
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
        <el-table-column label="班级" prop="class.name" min-width="120" />
        <el-table-column label="排课日期" prop="schedule_date" min-width="120" />
        <el-table-column label="开始时间" prop="start_time" min-width="100" />
        <el-table-column label="结束时间" prop="end_time" min-width="100" />
        <el-table-column label="地点" prop="location" min-width="120" />
        <el-table-column label="教练" prop="coach.name" min-width="100" />
        <el-table-column label="排课状态" prop="schedule_status" min-width="90">
          <template #default="scope">
            <el-tag :type="scope.row.schedule_status === 'scheduled' ? 'info' : scope.row.schedule_status === 'in_progress' ? 'success' : scope.row.schedule_status === 'completed' ? 'warning' : 'danger'">
              {{ scope.row.schedule_status === 'scheduled' ? '已排课' : scope.row.schedule_status === 'in_progress' ? '进行中' : scope.row.schedule_status === 'completed' ? '已完成' : '已取消' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="出勤人数" prop="attendance_count" min-width="90" />
        <el-table-column label="创建时间" prop="created_time" min-width="180" />
        <el-table-column fixed="right" label="操作" align="center" min-width="180">
          <template #default="scope">
            <el-button
              v-hasPerm="['module_badminton:class_schedule:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_badminton:class_schedule:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_badminton:class_schedule:delete']"
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
      width="700px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="班级" :span="2">
            {{ detailFormData.class?.name || detailFormData.class_id }}
          </el-descriptions-item>
          <el-descriptions-item label="排课日期">
            {{ detailFormData.schedule_date }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ detailFormData.start_time }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ detailFormData.end_time }}
          </el-descriptions-item>
          <el-descriptions-item label="时长">
            {{ detailFormData.duration_minutes }}分钟
          </el-descriptions-item>
          <el-descriptions-item label="地点">
            {{ detailFormData.location || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="教练">
            {{ detailFormData.coach?.name || '未指定' }}
          </el-descriptions-item>
          <el-descriptions-item label="排课状态">
            <el-tag :type="detailFormData.schedule_status === 'scheduled' ? 'info' : detailFormData.schedule_status === 'in_progress' ? 'success' : detailFormData.schedule_status === 'completed' ? 'warning' : 'danger'">
              {{ detailFormData.schedule_status === 'scheduled' ? '已排课' : detailFormData.schedule_status === 'in_progress' ? '进行中' : detailFormData.schedule_status === 'completed' ? '已完成' : '已取消' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实际开始时间">
            {{ detailFormData.actual_start_time || '未记录' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际结束时间">
            {{ detailFormData.actual_end_time || '未记录' }}
          </el-descriptions-item>
          <el-descriptions-item label="出勤人数">
            {{ detailFormData.attendance_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="缺勤人数">
            {{ detailFormData.absent_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="请假人数">
            {{ detailFormData.leave_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detailFormData.notes || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ detailFormData.created_by?.name || '系统' }}
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
              <el-form-item label="班级ID" prop="class_id">
                <el-input-number v-model="formData.class_id" :min="1" placeholder="班级ID" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="排课日期" prop="schedule_date">
                <el-date-picker
                  v-model="formData.schedule_date"
                  type="date"
                  placeholder="请选择排课日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="开始时间" prop="start_time">
                <el-time-picker
                  v-model="formData.start_time"
                  placeholder="请选择开始时间"
                  style="width: 100%"
                  value-format="HH:mm:ss"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束时间">
                <el-time-picker
                  v-model="formData.end_time"
                  placeholder="请选择结束时间"
                  style="width: 100%"
                  value-format="HH:mm:ss"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="时长(分钟)">
                <el-input-number v-model="formData.duration_minutes" :min="30" :max="240" :step="15" placeholder="时长" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="地点">
                <el-input v-model="formData.location" placeholder="请输入上课地点" :maxlength="128" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="教练ID">
                <el-input-number v-model="formData.coach_id" :min="1" placeholder="教练ID" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="排课状态" prop="schedule_status">
                <el-select v-model="formData.schedule_status" placeholder="请选择排课状态" style="width: 100%">
                  <el-option value="scheduled" label="已排课" />
                  <el-option value="in_progress" label="进行中" />
                  <el-option value="completed" label="已完成" />
                  <el-option value="cancelled" label="已取消" />
                </el-select>
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
  name: "ClassSchedule",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled } from "@element-plus/icons-vue";
import ClassScheduleAPI, { ClassScheduleTable, ClassScheduleForm, ClassSchedulePageQuery } from "@/api/module_badminton/class-schedule";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<ClassScheduleTable[]>([]);
const loading = ref(false);

// 分页表单
const pageTableData = ref<ClassScheduleTable[]>([]);

// 详情表单
const detailFormData = ref<ClassScheduleTable>({});

// 分页查询参数
const queryFormData = reactive<ClassSchedulePageQuery>({
  page_no: 1,
  page_size: 10,
  class_id: undefined,
  schedule_date_start: undefined,
  schedule_date_end: undefined,
  schedule_status: undefined,
});

// 编辑表单
const formData = reactive<ClassScheduleForm>({
  id: undefined,
  class_id: undefined,
  schedule_date: "",
  start_time: "",
  end_time: "",
  duration_minutes: 90,
  location: "",
  coach_id: undefined,
  schedule_status: "scheduled",
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
  class_id: [{ required: true, message: "请输入班级ID", trigger: "blur" }],
  schedule_date: [{ required: true, message: "请选择排课日期", trigger: "blur" }],
  start_time: [{ required: true, message: "请选择开始时间", trigger: "blur" }],
  schedule_status: [{ required: true, message: "请选择排课状态", trigger: "blur" }],
});

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await ClassScheduleAPI.getClassScheduleList(queryFormData);
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
const initialFormData: ClassScheduleForm = {
  id: undefined,
  class_id: undefined,
  schedule_date: "",
  start_time: "",
  end_time: "",
  duration_minutes: 90,
  location: "",
  coach_id: undefined,
  schedule_status: "scheduled",
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
    const response = await ClassScheduleAPI.getClassScheduleDetail(id);
    if (type === "detail") {
      dialogVisible.title = "排课记录详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改排课记录";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增排课记录";
  }
  dialogVisible.visible = true;
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;
  
  await dataFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return;
    
    try {
      if (dialogVisible.type === "create") {
        await ClassScheduleAPI.createClassSchedule(formData);
        ElMessage.success("创建成功");
      } else if (dialogVisible.type === "update") {
        await ClassScheduleAPI.updateClassSchedule(formData.id!, formData);
        ElMessage.success("更新成功");
      }
      dialogVisible.visible = false;
      loadingData();
    } catch (error: any) {
      console.error(error);
    }
  });
}

// 删除
async function handleDelete(ids: number[]) {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${ids.length} 条记录吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    
    await ClassScheduleAPI.deleteClassSchedule(ids);
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