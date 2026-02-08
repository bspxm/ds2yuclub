<!-- 能力分组管理 -->
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
        <el-form-item prop="name" label="分组名称">
          <el-input v-model="queryFormData.name" placeholder="请输入分组名称" clearable />
        </el-form-item>
        <el-form-item prop="coach_id" label="教练">
          <el-select
            v-model="queryFormData.coach_id"
            placeholder="请选择教练"
            style="width: 200px"
            clearable
            filterable
          >
            <el-option
              v-for="coach in coachOptions"
              :key="coach.id"
              :label="coach.name"
              :value="coach.id"
            />
          </el-select>
        </el-form-item>
        <!-- 查询、重置按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:group:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:group:list']"
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
            学员能力分组管理
            <el-tooltip content="学员能力分组管理">
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
                v-hasPerm="['module_badminton:group:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增分组
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:group:delete']"
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
                  v-hasPerm="['module_badminton:group:list']"
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
            label="分组名称"
            prop="name"
            min-width="150"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'description')?.show"
            label="备注"
            prop="description"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'coach_count')?.show"
            label="教练数量"
            prop="coach_count"
            min-width="100"
            align="center"
          >
            <template #default="scope">
              <el-tag type="primary">{{ scope.row.coach_count || 0 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'student_count')?.show"
            label="学员数量"
            prop="student_count"
            min-width="100"
            align="center"
          >
            <template #default="scope">
              <el-tag type="success">{{ scope.row.student_count || 0 }}</el-tag>
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
                v-hasPerm="['module_badminton:group:list']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:group:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:group:delete']"
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
      width="1200px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <div v-loading="dialogLoading" :element-loading-text="loadingText">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="分组名称" :span="2">
              {{ detailFormData.name }}
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">
              {{ detailFormData.description || "无" }}
            </el-descriptions-item>
            <el-descriptions-item label="教练数量">
              {{ detailFormData.coach_count || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="学员数量">
              {{ detailFormData.student_count || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="教练列表" :span="2">
              <el-tag
                v-for="coach in detailFormData.coaches"
                :key="coach.id"
                type="primary"
                style="margin-right: 5px; margin-bottom: 5px"
              >
                {{ coach.name }}
              </el-tag>
              <span v-if="!detailFormData.coaches || detailFormData.coaches.length === 0">无</span>
            </el-descriptions-item>
            <el-descriptions-item label="学员列表" :span="2">
              <el-tag
                v-for="student in detailFormData.students"
                :key="student.id"
                type="success"
                style="margin-right: 5px; margin-bottom: 5px"
              >
                {{ student.name }}
              </el-tag>
              <span v-if="!detailFormData.students || detailFormData.students.length === 0">
                无
              </span>
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
          </el-descriptions>
        </div>
      </template>

      <!-- 新增、编辑表单 -->
      <template v-else>
        <div v-loading="dialogLoading" :element-loading-text="loadingText">
          <el-row :gutter="20">
            <!-- 左侧：学员选择 -->
            <el-col :span="8">
              <el-card shadow="never">
                <template #header>
                  <div style="display: flex; justify-content: space-between; align-items: center">
                    <span>选择学员（{{ formData.student_ids.length }} 人）</span>
                    <el-tag type="info" size="small">
                      已选择 {{ formData.student_ids.length }} 人
                    </el-tag>
                  </div>
                </template>

                <!-- 筛选区域 -->
                <div style="margin-bottom: 15px">
                  <el-input
                    v-model="studentSearch"
                    placeholder="搜索：姓名、手机号或年龄（如：张三、138...、8岁）"
                    clearable
                    style="width: 100%; margin-bottom: 10px"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                  <el-row :gutter="10">
                    <el-col :span="12">
                      <el-select
                        v-model="groupFilter"
                        placeholder="筛选组别"
                        clearable
                        style="width: 100%"
                      >
                        <el-option label="全部组别" value="" />
                        <el-option label="未设置" value="__none__" />
                        <el-option
                          v-for="group in uniqueGroups"
                          :key="group"
                          :label="group"
                          :value="group"
                        />
                      </el-select>
                    </el-col>
                    <el-col :span="12">
                      <el-select
                        v-model="levelFilter"
                        placeholder="筛选水平"
                        clearable
                        style="width: 100%"
                      >
                        <el-option label="全部水平" value="" />
                        <el-option
                          v-for="level in uniqueLevels"
                          :key="level"
                          :label="level"
                          :value="level"
                        />
                      </el-select>
                    </el-col>
                  </el-row>
                </div>

                <!-- 学员列表 -->
                <div style="height: 450px; overflow-y: auto">
                  <el-checkbox-group v-model="formData.student_ids">
                    <div
                      v-for="student in filteredStudents"
                      :key="student.id"
                      style="padding: 8px; border-bottom: 1px solid #f0f0f0"
                    >
                      <el-checkbox :label="student.id">
                        <span style="margin-left: 8px">
                          {{ student.name }}:{{ calculateAge(student.birth_date) }}岁:{{
                            student.level || "未设置"
                          }}:{{ student.group_name || "未设置" }}
                          <span style="color: #909399; font-size: 12px; margin-left: 8px">
                            {{ student.mobile || "无手机号" }}
                          </span>
                        </span>
                      </el-checkbox>
                    </div>
                  </el-checkbox-group>
                  <el-empty v-if="filteredStudents.length === 0" description="暂无学员" />
                </div>
              </el-card>
            </el-col>

            <!-- 右侧：分组信息 -->
            <el-col :span="16">
              <el-card shadow="never">
                <template #header>
                  <span>分组信息</span>
                </template>

                <el-form
                  ref="dataFormRef"
                  :model="formData"
                  :rules="rules"
                  label-suffix=":"
                  label-width="100px"
                  label-position="right"
                >
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item label="分组名称" prop="name">
                        <el-input
                          v-model="formData.name"
                          placeholder="请输入分组名称"
                          maxlength="64"
                          show-word-limit
                        />
                      </el-form-item>
                    </el-col>

                    <el-col :span="24">
                      <el-form-item label="教练" prop="coach_ids">
                        <el-select
                          v-model="formData.coach_ids"
                          multiple
                          filterable
                          placeholder="请选择教练"
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
                    </el-col>

                    <el-col :span="24">
                      <el-form-item label="备注" prop="description">
                        <el-input
                          v-model="formData.description"
                          type="textarea"
                          placeholder="请输入备注"
                          :rows="8"
                          maxlength="500"
                          show-word-limit
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>
              </el-card>
            </el-col>
          </el-row>
        </div>
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
  name: "AbilityGroup",
  inheritAttrs: false,
});

import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled, Search } from "@element-plus/icons-vue";
import GroupAPI, { GroupTable, GroupForm, GroupPageQuery } from "@/api/module_badminton/group";
import UserAPI from "@/api/module_system/user";
import StudentAPI from "@/api/module_badminton/student";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const loading = ref(false);
const dialogLoading = ref(false);

// 分页表单
const pageTableData = ref<GroupTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "分组名称", show: true },
  { prop: "description", label: "备注", show: true },
  { prop: "coach_count", label: "教练数量", show: true },
  { prop: "student_count", label: "学员数量", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<GroupTable>({});

// 分页查询参数
const queryFormData = reactive<GroupPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  coach_id: undefined,
});

// 编辑表单
const formData = reactive<GroupForm>({
  id: undefined,
  name: undefined,
  description: undefined,
  coach_ids: [],
  student_ids: [],
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入分组名称", trigger: "blur" }],
});

// 教练选项
const coachOptions = ref<Array<{ id: number; name: string }>>([]);

// 学员选项
const studentOptions = ref<
  Array<{
    id: number;
    name: string;
    birth_date?: string;
    level?: string;
    group_name?: string;
    mobile?: string;
  }>
>([]);

// 学员搜索和筛选
const studentSearch = ref("");
const groupFilter = ref("");
const levelFilter = ref("");

// 计算属性：筛选后的学员列表
const filteredStudents = computed(() => {
  let filtered = studentOptions.value;
  console.log("filteredStudents计算, studentOptions.value:", studentOptions.value.length, "条");

  // 搜索过滤
  if (studentSearch.value) {
    const searchLower = studentSearch.value.toLowerCase();
    filtered = filtered.filter((student) => {
      const name = student.name?.toLowerCase() || "";
      const mobile = student.mobile?.toLowerCase() || "";
      const age = student.birth_date ? `${calculateAge(student.birth_date)}岁` : "";
      const level = student.level?.toLowerCase() || "";
      const groupName = student.group_name?.toLowerCase() || "";

      return (
        name.includes(searchLower) ||
        mobile.includes(searchLower) ||
        age.includes(searchLower) ||
        level.includes(searchLower) ||
        groupName.includes(searchLower)
      );
    });
  }

  // 组别过滤
  if (groupFilter.value) {
    if (groupFilter.value === "__none__") {
      // 筛选未设置组别的学员
      filtered = filtered.filter((student) => !student.group_name || student.group_name === "");
    } else {
      // 筛选指定组别的学员
      filtered = filtered.filter((student) => student.group_name === groupFilter.value);
    }
  }

  // 水平过滤
  if (levelFilter.value) {
    filtered = filtered.filter((student) => student.level === levelFilter.value);
  }

  console.log("filteredStudents结果:", filtered.length, "条");
  return filtered;
});

// 计算属性：唯一的组别列表
const uniqueGroups = computed(() => {
  const groups = new Set<string>();
  studentOptions.value.forEach((student) => {
    if (student.group_name) {
      groups.add(student.group_name);
    }
  });
  return Array.from(groups).sort();
});

// 计算属性：唯一的水平列表
const uniqueLevels = computed(() => {
  const levels = new Set<string>();
  studentOptions.value.forEach((student) => {
    if (student.level) {
      levels.add(student.level);
    }
  });
  return Array.from(levels).sort();
});

// 计算年龄
const calculateAge = (birthDate: string) => {
  if (!birthDate) return 0;
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
};

// 格式化时间（精确到秒）
const formatDateTime = (dateTime: string | null | undefined) => {
  if (!dateTime) return "";
  try {
    const date = new Date(dateTime);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    console.error("时间格式化失败:", error);
    return dateTime;
  }
};

// 加载数据
const loadingData = async () => {
  loading.value = true;
  try {
    const res = await GroupAPI.getGroupList(queryFormData);
    if (res.data.success) {
      pageTableData.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    }
  } catch (error) {
    console.error("加载分组列表失败:", error);
  } finally {
    loading.value = false;
  }
};

// 查询
const handleQuery = () => {
  queryFormData.page_no = 1;
  loadingData();
};

// 重置查询
const handleResetQuery = () => {
  queryFormData.name = undefined;
  queryFormData.coach_id = undefined;
  handleQuery();
};

// 刷新
const handleRefresh = () => {
  loadingData();
};

// 选择变化
const handleSelectionChange = (selection: GroupTable[]) => {
  selectIds.value = selection.map((item) => item.id);
};

// 打开弹窗
const handleOpenDialog = async (type: "create" | "update" | "detail", id?: number) => {
  dialogVisible.type = type;
  dialogVisible.visible = true;

  if (type === "create") {
    dialogVisible.title = "新增分组";
    dialogLoading.value = false;
    resetForm();
  } else if (type === "update" && id) {
    dialogVisible.title = "编辑分组";
    dialogLoading.value = true;
    await loadGroupDetail(id);
  } else if (type === "detail" && id) {
    dialogVisible.title = "分组详情";
    dialogLoading.value = true;
    await loadGroupDetail(id);
  }

  // 加载教练选项
  await loadCoachOptions();

  // 加载学员选项
  await loadStudentOptions();
};

// 加载分组详情
const loadGroupDetail = async (id: number) => {
  try {
    const res = await GroupAPI.getGroupDetail(id);
    if (res.data.success) {
      const data = res.data.data;

      if (dialogVisible.type === "detail") {
        detailFormData.value = data;
      } else {
        formData.id = data.id;
        formData.name = data.name;
        formData.description = data.description;
        formData.coach_ids = data.coaches?.map((c) => c.id) || [];
        formData.student_ids = data.students?.map((s) => s.id) || [];
      }
    }
  } catch (error) {
    console.error("加载分组详情失败:", error);
    ElMessage.error("加载分组详情失败");
  } finally {
    dialogLoading.value = false;
  }
};

// 加载教练选项
const loadCoachOptions = async () => {
  try {
    const response = await UserAPI.listUser({ page_no: 1, page_size: 100 });
    coachOptions.value = response.data.data.items
      .filter((user: any) => {
        const isEnabled = user.status === "0";
        const hasPositions = user.positions && user.positions.length > 0;
        const isCoach =
          hasPositions &&
          user.positions.some((pos: any) => pos.name === "教练" || pos.name === "主管教练");
        return isEnabled && isCoach;
      })
      .map((user: any) => ({
        id: user.id,
        name: user.name,
      }));
  } catch (error) {
    console.error("加载教练列表失败:", error);
  }
};

// 加载学员选项
const loadStudentOptions = async () => {
  try {
    const res = await StudentAPI.getStudentList({ page_no: 1, page_size: 100 });
    console.log("学员列表响应:", res);

    if (res.data && res.data.code === 0 && res.data.data) {
      // 过滤掉禁用状态的学员（status !== '0' 表示禁用）
      studentOptions.value = (res.data.data.items || []).filter(
        (student) => student.status === "0"
      );
      console.log("学员选项:", studentOptions.value);
    } else {
      console.error("响应格式错误:", res);
    }
  } catch (error) {
    console.error("加载学员列表失败:", error);
  }
};

// 重置表单
const resetForm = () => {
  formData.id = undefined;
  formData.name = undefined;
  formData.description = undefined;
  formData.coach_ids = [];
  formData.student_ids = [];
  studentSearch.value = "";
  groupFilter.value = "";
  levelFilter.value = "";
  dataFormRef.value?.resetFields();
};

// 关闭弹窗
const handleCloseDialog = () => {
  dialogVisible.visible = false;
  resetForm();
};

// 提交
const handleSubmit = async () => {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 保存表单数据副本（用于后台提交）
  const submitData = { ...formData };
  delete submitData.id;

  // 保存操作类型和ID（在关闭窗口之前）
  const operationType = dialogVisible.type;
  const updateId = formData.id;

  // 立即关闭窗口
  handleCloseDialog();

  // 在右下角显示持久化通知
  const notification = ElNotification({
    title: operationType === "create" ? "创建分组" : "更新分组",
    message: "后台保存中...",
    type: "info",
    duration: 0, // 不自动关闭
    position: "bottom-right",
  });

  // 在后台保存数据
  try {
    let res;
    if (operationType === "create") {
      res = await GroupAPI.createGroup(submitData);
    } else if (operationType === "update" && updateId) {
      res = await GroupAPI.updateGroup(updateId, submitData);
    }

    console.log("提交响应:", res);
    if (res.data.code === 0) {
      // 关闭加载通知，显示成功通知
      notification.close();
      ElNotification({
        title: operationType === "create" ? "创建成功" : "更新成功",
        message: operationType === "create" ? "分组创建成功" : "分组更新成功",
        type: "success",
        duration: 3000,
        position: "bottom-right",
      });
      loadingData();
    } else {
      // 关闭加载通知，显示错误通知
      notification.close();
      ElNotification({
        title: "操作失败",
        message: res.data.msg || "操作失败",
        type: "error",
        duration: 3000,
        position: "bottom-right",
      });
    }
  } catch (error) {
    console.error("提交失败:", error);
    // 关闭加载通知，显示错误通知
    notification.close();
    ElNotification({
      title: "提交失败",
      message: "网络错误或服务器异常",
      type: "error",
      duration: 3000,
      position: "bottom-right",
    });
  }
};

// 删除
const handleDelete = async (ids: number[]) => {
  try {
    await ElMessageBox.confirm("确定要删除这些分组吗？删除后会清空学员的组别信息。", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    const res = await GroupAPI.deleteGroup(ids);
    if (res.data.code === 0) {
      ElMessage.success("删除成功");
      loadingData();
    } else {
      ElMessage.error(res.data.msg || "删除失败");
    }
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("删除失败:", error);
      ElMessage.error("删除失败");
    }
  }
};

// 初始化
const loadingText = computed(() => {
  if (dialogVisible.type === "update") {
    return "保存中...";
  }
  return "加载中...";
});

onMounted(() => {
  loadingData();
  loadCoachOptions();
  loadStudentOptions();
});
</script>

<style scoped lang="scss">
.app-container {
  padding: 20px;
}

.search-container {
  margin-bottom: 20px;
  padding: 20px;
  background-color: var(--el-bg-color);
  border-radius: 4px;
}

.data-table {
  margin-bottom: 20px;
}

.data-table__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.data-table__content-wrapper {
  min-height: 400px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
