<!-- 能力评估管理 -->
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
        <el-form-item prop="student_id" label="学员">
          <el-select
            v-model="queryFormData.student_id"
            placeholder="选择学员"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="student in studentOptions"
              :key="student.id"
              :label="student.name"
              :value="student.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isExpand" prop="assessment_date_start" label="评估日期范围">
          <DatePicker
            v-model="assessmentDateRange"
            type="daterange"
            @update:model-value="handleAssessmentDateRangeChange"
          />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:assessment:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:assessment:list']"
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
            能力评估管理
            <el-tooltip content="学员能力评估管理，包含9个维度评分">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
          </span>
        </div>
      </template>

      <!-- 提示信息 -->
      <div class="mb-4">
        <el-alert type="info" show-icon>
          能力评估包含9个维度：技术、步法、战术、力量、速度、耐力、进攻、防守、心理，每项评分1-5分
        </el-alert>
      </div>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:assessment:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新建评估
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:assessment:delete']"
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
                  v-hasPerm="['module_badminton:assessment:list']"
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
          <el-table-column prop="student_name" label="学员姓名" min-width="120">
            <template #default="{ row }">
              {{ row.student?.name || "未知" }}
            </template>
          </el-table-column>
          <el-table-column prop="assessment_date" label="评估日期" min-width="120" />
          <el-table-column label="技术" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.technique" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="步法" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.footwork" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="战术" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.tactics" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="力量" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.power" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="速度" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.speed" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="耐力" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.stamina" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="进攻" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.offense" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="防守" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.defense" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column label="心理" min-width="100">
            <template #default="{ row }">
              <el-rate v-model="row.mental" disabled show-score :max="5" />
            </template>
          </el-table-column>
          <el-table-column prop="overall_score" label="综合评分" min-width="120">
            <template #default="{ row }">
              <el-progress :percentage="row.overall_score * 20" :format="formatScore" />
            </template>
          </el-table-column>
          <el-table-column label="评估人" min-width="120">
            <template #default="{ row }">
              {{ row.coach?.name || row.created_by?.name || "系统" }}
            </template>
          </el-table-column>
          <el-table-column prop="created_time" label="创建时间" min-width="180" />
          <el-table-column fixed="right" label="操作" align="center" min-width="180">
            <template #default="{ row }">
              <el-button
                v-hasPerm="['module_badminton:assessment:update']"
                type="primary"
                link
                size="small"
                icon="edit"
                @click="handleOpenDialog('update', row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:assessment:delete']"
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
            placeholder="选择学员"
            filterable
            style="width: 100%"
            :disabled="!!formData.id"
          >
            <el-option
              v-for="student in studentOptions"
              :key="student.id"
              :label="student.name"
              :value="student.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="评估日期" prop="assessment_date">
          <el-date-picker
            v-model="formData.assessment_date"
            type="date"
            placeholder="选择评估日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="教练">
          <el-select
            v-model="formData.coach_id"
            placeholder="选择教练（可选）"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="coach in coachOptions"
              :key="coach.id"
              :label="coach.name"
              :value="coach.id"
            />
          </el-select>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12" v-for="dimension in assessmentDimensions" :key="dimension.key">
            <el-form-item :label="dimension.label" :prop="dimension.key">
              <el-rate
                v-model="formData[dimension.key]"
                :max="5"
                :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                show-score
                text-color="#ff9900"
                score-template="{value}分"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="教练评语" prop="comments">
          <el-input
            v-model="formData.comments"
            type="textarea"
            :rows="3"
            placeholder="请输入教练评语（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
          <el-button @click="handleCloseDialog">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "BadmintonAssessment",
  inheritAttrs: false,
});

import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown } from "@element-plus/icons-vue";
import AssessmentAPI, { type AssessmentForm, type AssessmentTable, type AssessmentPageQuery } from "@/api/module_badminton/assessment";
import StudentAPI, { type StudentTable } from "@/api/module_badminton/student";
import UserAPI, { type UserInfo } from "@/api/module_system/user";
import { useUserStoreHook } from "@/store/modules/user.store";

const queryFormRef = ref<FormInstance>();
const dataFormRef = ref<FormInstance>();
const tableRef = ref();
const selectIds = ref<number[]>([]);
const loading = ref(false);
const submitting = ref(false);

const visible = ref(true);
const isExpand = ref(false);
const isExpandable = ref(false);

// 分页表单
const pageTableData = ref<AssessmentTable[]>([]);
const total = ref(0);

// 分页查询参数
const queryFormData = reactive<AssessmentPageQuery>({
  page_no: 1,
  page_size: 10,
  student_id: undefined,
  assessment_date_start: undefined,
  assessment_date_end: undefined,
});

// 编辑表单
const formData = reactive<AssessmentForm>({
  student_id: 0,
  assessment_date: "",
  coach_id: undefined,
  technique: 3,
  footwork: 3,
  tactics: 3,
  power: 3,
  speed: 3,
  stamina: 3,
  offense: 3,
  defense: 3,
  mental: 3,
  comments: "",
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update",
});

// 学员选项
const studentOptions = ref<StudentTable[]>([]);
// 教练选项
const coachOptions = ref<any[]>([]);

// 日期范围临时变量
const assessmentDateRange = ref<[Date, Date] | []>([]);

// 表单验证规则
const rules: FormRules = {
  student_id: [{ required: true, message: "请选择学员", trigger: "blur" }],
  assessment_date: [{ required: true, message: "请选择评估日期", trigger: "blur" }],
  technique: [{ required: true, message: "请评分技术能力", trigger: "blur" }],
};

// 能力评估维度配置
const assessmentDimensions = [
  { key: "technique", label: "技术能力" },
  { key: "footwork", label: "步法移动" },
  { key: "tactics", label: "战术意识" },
  { key: "power", label: "力量" },
  { key: "speed", label: "速度" },
  { key: "stamina", label: "耐力" },
  { key: "offense", label: "进攻能力" },
  { key: "defense", label: "防守能力" },
  { key: "mental", label: "心理素质" },
];

// 对话框标题
const dialogTitle = computed(() => {
  return formData.id ? "编辑能力评估" : "新建能力评估";
});

// 格式化评分显示
const formatScore = (percentage: number) => {
  return `${(percentage / 20).toFixed(1)}分`;
};

// 处理日期范围变化
function handleAssessmentDateRangeChange(range: [Date, Date]) {
  assessmentDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.assessment_date_start = range[0];
    queryFormData.assessment_date_end = range[1];
  } else {
    queryFormData.assessment_date_start = undefined;
    queryFormData.assessment_date_end = undefined;
  }
}

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
  assessmentDateRange.value = [];
  queryFormData.assessment_date_start = undefined;
  queryFormData.assessment_date_end = undefined;
  handleQuery();
}

// 刷新
async function handleRefresh() {
  loadingData();
}

// 行复选框选中项变化
async function handleSelectionChange(selection: AssessmentTable[]) {
  selectIds.value = selection.map((item) => item.id);
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
    dialogVisible.title = "编辑能力评估";
    const row = pageTableData.value.find((item) => item.id === id);
    if (row) {
      Object.assign(formData, row);
    }
  } else {
    dialogVisible.title = "新建能力评估";
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
    student_id: 0,
    assessment_date: "",
    coach_id: useUserStoreHook().basicInfo.id || undefined,
    technique: 3,
    footwork: 3,
    tactics: 3,
    power: 3,
    speed: 3,
    stamina: 3,
    offense: 3,
    defense: 3,
    mental: 3,
    comments: "",
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
      res = await AssessmentAPI.createAssessment(submitData);
    } else if (operationType === "update" && updateId) {
      res = await AssessmentAPI.updateAssessment(updateId, submitData);
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

// 删除、批量删除
async function handleDelete(ids: number[]) {
  ElMessageBox.confirm(`确定删除选中的${ids.length}条记录吗？`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      loading.value = true;
      try {
        await AssessmentAPI.deleteAssessment(ids);
        ElMessage.success("删除成功");
        loadingData();
      } catch (error: any) {
        console.error("删除失败:", error);
        ElMessage.error("删除失败");
        loading.value = false;
      }
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 加载数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await AssessmentAPI.getAssessmentList(queryFormData);
    pageTableData.value = response.data.data.items || [];
    total.value = response.data.data.total || 0;
  } catch (error: any) {
    console.error("加载评估列表失败:", error);
    ElMessage.error("加载数据失败");
  } finally {
    loading.value = false;
  }
}

// 加载学员列表
const loadStudentOptions = async () => {
  try {
    const response = await StudentAPI.getStudentList({
      page_no: 1,
      page_size: 100,
    });
    studentOptions.value = response.data.data.items;
  } catch (error) {
    console.error("加载学员列表失败:", error);
  }
};

// 加载教练列表
const loadCoachOptions = async () => {
  try {
    const response = await UserAPI.listUser({
      page: 1,
      page_size: 100,
      status: "0", // 只获取启用状态的用户
    } as any);
    if (response.data?.data?.items) {
      coachOptions.value = response.data.data.items;
    }
  } catch (error) {
    console.error("加载教练列表失败:", error);
  }
};

onMounted(() => {
  loadStudentOptions();
  loadCoachOptions();
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