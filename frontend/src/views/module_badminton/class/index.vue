<!-- 班级管理 -->
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
        <el-form-item prop="name" label="班级名称">
          <el-input v-model="queryFormData.name" placeholder="请输入班级名称" clearable />
        </el-form-item>
        <el-form-item prop="class_type" label="班级类型">
          <el-select
            v-model="queryFormData.class_type"
            placeholder="请选择班级类型"
            style="width: 120px"
            clearable
          >
            <el-option value="fixed" label="固定天" />
            <el-option value="flexible" label="自选天" />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="班级状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请选择班级状态"
            style="width: 120px"
            clearable
          >
            <el-option value="active" label="进行中" />
            <el-option value="ended" label="已结束" />
            <el-option value="pending" label="未开始" />
          </el-select>
        </el-form-item>
        <el-form-item prop="semester_id" label="学期">
          <el-select
            v-model="queryFormData.semester_id"
            placeholder="请选择学期"
            style="width: 150px"
            clearable
            filterable
          >
            <el-option
              v-for="semester in semesterOptions"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isExpand" prop="coach_id" label="教练">
          <el-input v-model="queryFormData.coach_id" placeholder="请输入教练ID" clearable />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:class:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:class:list']"
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
            班级管理
            <el-tooltip content="班级信息管理">
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
                v-hasPerm="['module_badminton:class:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增班级
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:class:delete']"
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
                  v-hasPerm="['module_badminton:class:list']"
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
            v-if="isColumnShow('selection')"
            type="selection"
            min-width="55"
            align="center"
          />
          <el-table-column v-if="isColumnShow('index')" fixed label="序号" min-width="60">
            <template #default="scope">
              {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="isColumnShow('name')"
            label="班级名称"
            prop="name"
            min-width="120"
          />
          <el-table-column
            v-if="isColumnShow('class_type')"
            label="班级类型"
            prop="class_type"
            min-width="90"
          >
            <template #default="scope">
              <el-tag :type="scope.row.class_type === 'fixed' ? 'primary' : 'success'">
                {{ scope.row.class_type === "fixed" ? "固定天" : "自选天" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="isColumnShow('semester')"
            label="所属学期"
            prop="semester.name"
            min-width="120"
          />
          <el-table-column
            v-if="isColumnShow('coach')"
            label="教练"
            prop="coach_user.name"
            min-width="100"
          />
          <el-table-column
            v-if="isColumnShow('current_students')"
            label="当前学员"
            prop="current_students"
            min-width="90"
          >
            <template #default="scope">
              <el-tag
                :type="
                  (scope.row.current_students || 0) >= scope.row.max_students ? 'danger' : 'success'
                "
              >
                {{ scope.row.current_students || 0 }}/{{ scope.row.max_students }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnShow('class_time')" label="上课时间" min-width="300">
            <template #default="scope">
              <div v-if="scope.row.time_slots_json" class="time-slots-container">
                <div
                  v-for="(dayGroup, index) in formatTimeSlots(scope.row.time_slots_json)"
                  :key="index"
                  class="day-group"
                >
                  <span class="day-label">{{ dayGroup.day }}:</span>
                  <span class="time-labels">{{ dayGroup.slots.join(", ") }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnShow('fee_per_session')" label="总费用" min-width="100">
            <template #default="scope">
              ¥{{ ((scope.row.fee_per_session || 0) * (scope.row.total_sessions || 0)).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnShow('status')" label="状态" prop="status" min-width="90">
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.class_status === 'active'
                    ? 'success'
                    : scope.row.class_status === 'pending'
                      ? 'info'
                      : 'warning'
                "
              >
                {{
                  scope.row.class_status === "active"
                    ? "进行中"
                    : scope.row.class_status === "pending"
                      ? "未开始"
                      : "已结束"
                }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="isColumnShow('created_time')"
            label="创建时间"
            prop="created_time"
            min-width="180"
          />
          <el-table-column
            v-if="isColumnShow('operation')"
            fixed="right"
            label="操作"
            align="center"
            min-width="180"
          >
            <template #default="scope">
              <el-button
                v-hasPerm="['module_badminton:class:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:class:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:class:delete']"
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
          <el-descriptions-item label="班级名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="班级类型">
            <el-tag :type="detailFormData.class_type === 'fixed' ? 'primary' : 'success'">
              {{ detailFormData.class_type === "fixed" ? "固定天" : "自选天" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="所属学期">
            {{ detailFormData.semester?.name || "未指定" }}
          </el-descriptions-item>
          <el-descriptions-item label="班级状态">
            <el-tag
              :type="
                detailFormData.class_status === 'active'
                  ? 'success'
                  : detailFormData.class_status === 'pending'
                    ? 'info'
                    : 'warning'
              "
            >
              {{
                detailFormData.class_status === "active"
                  ? "进行中"
                  : detailFormData.class_status === "pending"
                    ? "未开始"
                    : "已结束"
              }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大学员数">
            {{ detailFormData.max_students }}
          </el-descriptions-item>
          <el-descriptions-item label="当前学员数">
            {{ detailFormData.current_students || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="每周排班" :span="2">
            <div v-if="detailFormData.weekly_schedule">{{ detailFormData.weekly_schedule }}</div>
            <div
              v-if="detailFormData.time_slots_json"
              style="white-space: pre-wrap; line-height: 1.6; margin-top: 8px"
            >
              {{ formatTimeSlots(detailFormData.time_slots_json) }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="上课地点">
            {{ detailFormData.location || "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="教练">
            {{ detailFormData.coach_user?.name || "未指定" }}
          </el-descriptions-item>
          <el-descriptions-item label="每节课费用">
            ¥{{ detailFormData.fee_per_session || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="每周课次">
            {{ detailFormData.sessions_per_week || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="总课次">
            {{ detailFormData.total_sessions || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="总费用" :span="2">
            ¥{{
              (
                (detailFormData.fee_per_session || 0) * (detailFormData.total_sessions || 0)
              ).toFixed(2)
            }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ detailFormData.created_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="更新人">
            {{ detailFormData.updated_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ detailFormData.created_time }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ detailFormData.updated_time }}
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
            <!-- 第一行：班级名称、班级类型 -->
            <el-col :span="12">
              <el-form-item label="班级名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入班级名称" :maxlength="64" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="班级类型" prop="class_type">
                <el-select
                  v-model="formData.class_type"
                  placeholder="请选择班级类型"
                  style="width: 100%"
                >
                  <el-option value="fixed" label="固定天" />
                  <el-option value="flexible" label="自选天" />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- 第二行：所属学期、最大学员数 -->
            <el-col :span="12">
              <el-form-item label="所属学期" prop="semester_id">
                <el-select
                  v-model="formData.semester_id"
                  placeholder="请选择学期"
                  style="width: 100%"
                  filterable
                >
                  <el-option
                    v-for="semester in semesterOptions"
                    :key="semester.id"
                    :label="semester.name"
                    :value="semester.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="最大学员数" prop="max_students">
                <el-input-number
                  v-model="formData.max_students"
                  :min="1"
                  :max="100"
                  placeholder="最大学员数"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>

            <!-- 第三行：每周排班（占满一整行） -->
            <el-col :span="24">
              <el-form-item label="每周排班" prop="weekly_schedule_days">
                <el-checkbox-group v-model="formData.weekly_schedule_days">
                  <el-checkbox label="周日" value="周日" />
                  <el-checkbox label="周一" value="周一" />
                  <el-checkbox label="周二" value="周二" />
                  <el-checkbox label="周三" value="周三" />
                  <el-checkbox label="周四" value="周四" />
                  <el-checkbox label="周五" value="周五" />
                  <el-checkbox label="周六" value="周六" />
                </el-checkbox-group>
              </el-form-item>
            </el-col>

            <!-- 第四行：时间段选择 -->
            <el-col :span="24">
              <el-form-item label="时间段选择">
                <div style="display: flex; flex-wrap: wrap; gap: 20px">
                  <div
                    v-for="day in sortedWeeklyScheduleDays"
                    :key="day"
                    :style="{
                      flex: 1,
                      minWidth: '200px',
                      padding: '16px',
                      borderRadius: '8px',
                      border: timeSlotsValidationError[day]
                        ? '2px solid var(--el-color-error)'
                        : '1px solid var(--el-border-color)',
                      backgroundColor: timeSlotsValidationError[day]
                        ? 'var(--el-color-error-light-9)'
                        : 'var(--el-bg-color)',
                      transition: 'all 0.3s',
                    }"
                  >
                    <div
                      style="margin-bottom: 8px; font-weight: bold; color: timeSlotsValidationError[day] ? 'var(--el-color-error)' : 'inherit';"
                    >
                      {{ day }}
                    </div>
                    <el-checkbox-group v-model="formData.time_slots[day]">
                      <el-checkbox label="A" value="A">09:00-10:30</el-checkbox>
                      <el-checkbox label="B" value="B">10:30-12:00</el-checkbox>
                      <el-checkbox label="C" value="C">15:00-16:30</el-checkbox>
                      <el-checkbox label="D" value="D">16:30-18:00</el-checkbox>
                      <el-checkbox label="E" value="E">19:30-21:00</el-checkbox>
                    </el-checkbox-group>
                  </div>
                </div>
              </el-form-item>
            </el-col>

            <!-- 第五行：主管教练、每节课费用 -->
            <el-col :span="12">
              <el-form-item label="主管教练" prop="coach_id">
                <el-select
                  v-model="formData.coach_id"
                  placeholder="请选择主管教练"
                  style="width: 100%"
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
            </el-col>
            <el-col :span="12">
              <el-form-item label="每节课费用">
                <el-input-number
                  v-model="formData.fee_per_session"
                  :min="0"
                  :step="10"
                  placeholder="每节课费用"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>

            <!-- 第六行：每周课次、总课次 -->
            <el-col :span="12">
              <el-form-item label="每周课次">
                <el-input-number
                  v-model="formData.sessions_per_week"
                  :min="1"
                  :max="7"
                  placeholder="每周课次"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="总课次">
                <el-input-number
                  v-model="formData.total_sessions"
                  :min="1"
                  :max="100"
                  placeholder="总课次"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>

            <!-- 第七行：班级状态、上课地点 -->
            <el-col :span="12">
              <el-form-item label="班级状态" prop="class_status">
                <el-select
                  v-model="formData.class_status"
                  placeholder="请选择班级状态"
                  style="width: 100%"
                >
                  <el-option value="pending" label="未开始" />
                  <el-option value="active" label="进行中" />
                  <el-option value="ended" label="已结束" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="上课地点">
                <el-input
                  v-model="formData.location"
                  placeholder="请输入上课地点"
                  :maxlength="128"
                />
              </el-form-item>
            </el-col>

            <!-- 第八行：备注（跨两列） -->
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
  name: "Class",
  inheritAttrs: false,
});

import { ref, reactive, onMounted, computed, watch } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown } from "@element-plus/icons-vue";
import DatePicker from "@/components/DatePicker/index.vue";
import ClassAPI, { ClassTable, ClassForm, ClassPageQuery } from "@/api/module_badminton/class";
import SemesterAPI from "@/api/module_badminton/semester";
import { UserAPI } from "@/api/module_system/user";
import request from "@/utils/request";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<ClassTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 时间段列表（从字典接口获取）
interface TimeSlotInfo {
  id: number;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
}

const timeSlotList = ref<TimeSlotInfo[]>([]);

// 分页表单
const pageTableData = ref<ClassTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "班级名称", show: true },
  { prop: "class_type", label: "班级类型", show: true },
  { prop: "semester", label: "所属学期", show: true },
  { prop: "coach", label: "教练", show: true },
  { prop: "current_students", label: "当前学员", show: true },
  { prop: "class_time", label: "上课时间", show: true },
  { prop: "fee_per_session", label: "总费用", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "created_time", label: "创建时间", show: false },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<ClassTable>({});

// 教练列表
const coachOptions = ref<any[]>([]);

// 学期列表
const semesterOptions = ref<any[]>([]);

// 分页查询参数
const queryFormData = reactive<ClassPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  class_type: undefined,
  semester_id: undefined,
  status: undefined,
  class_status: undefined,
  coach_id: undefined,
});

// 定义初始表单数据常量
const initialFormData: ClassForm = {
  id: undefined,
  name: "",
  class_type: "fixed",
  semester_id: undefined,
  max_students: 20,
  weekly_schedule: "",
  weekly_schedule_days: [],
  time_slots: {
    周一: [],
    周二: [],
    周三: [],
    周四: [],
    周五: [],
    周六: [],
    周日: [],
  },
  location: "",
  coach_id: undefined,
  fee_per_session: 0,
  sessions_per_week: 2,
  total_sessions: 32,
  status: "0",
  class_status: "pending",
  description: undefined,
};

// 编辑表单
const formData = reactive<ClassForm>(initialFormData);

// 计算属性：按星期顺序排序的星期列表（周日在前，强制排序）
const sortedWeeklyScheduleDays = computed(() => {
  const dayOrder = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  // 过滤出选中的星期
  const selectedDays = formData.weekly_schedule_days.filter((day) => dayOrder.includes(day));
  // 按固定顺序排序
  return selectedDays.sort((a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b));
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 时间段验证错误状态（按星期）
const timeSlotsValidationError = reactive<Record<string, boolean>>({
  周日: false,
  周一: false,
  周二: false,
  周三: false,
  周四: false,
  周五: false,
  周六: false,
});

// 自定义验证器：确保每个选中的星期都有至少一个时间段
const validateTimeSlots = (rule: any, value: any, callback: any) => {
  if (!formData.weekly_schedule_days || formData.weekly_schedule_days.length === 0) {
    // 没有选择星期，不验证时间段
    Object.keys(timeSlotsValidationError).forEach((day) => (timeSlotsValidationError[day] = false));
    callback();
    return;
  }

  // 检查每个选中的星期是否有时间段
  const emptyDays: string[] = [];
  for (const day of formData.weekly_schedule_days) {
    if (!formData.time_slots[day] || formData.time_slots[day].length === 0) {
      emptyDays.push(day);
      timeSlotsValidationError[day] = true;
    } else {
      timeSlotsValidationError[day] = false;
    }
  }

  if (emptyDays.length > 0) {
    callback(new Error(`以下星期未选择时间段：${emptyDays.join("、")}`));
  } else {
    callback();
  }
};

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入班级名称", trigger: "blur" }],
  class_type: [{ required: true, message: "请选择班级类型", trigger: "blur" }],
  semester_id: [{ required: true, message: "请选择所属学期", trigger: "blur" }],
  coach_id: [{ required: true, message: "请选择主管教练", trigger: "change" }],
  max_students: [{ required: true, message: "请输入最大学员数", trigger: "blur" }],
  class_status: [{ required: true, message: "请选择班级状态", trigger: "blur" }],
  weekly_schedule_days: [
    { required: true, message: "请选择每周排班", trigger: "change" },
    { validator: validateTimeSlots, trigger: "change" },
  ],
});

// 加载学期选项
async function loadSemesterOptions() {
  try {
    const response = await SemesterAPI.getSemesterList({ page_no: 1, page_size: 100 });
    semesterOptions.value = response.data.data.items.map((item: any) => ({
      id: item.id,
      name: item.name,
    }));
  } catch (error: any) {
    console.error(error);
  }
}

// 加载教练选项
async function loadCoachOptions() {
  try {
    const response = await UserAPI.listUser({ page_no: 1, page_size: 100 });
    console.log("用户列表响应:", response.data.data);

    // 过滤出启用状态且岗位为教练的用户
    coachOptions.value = response.data.data.items
      .filter((user: any) => {
        const isEnabled = user.status === "0";
        const hasPositions = user.positions && user.positions.length > 0;
        const isCoach =
          hasPositions &&
          user.positions.some((pos: any) => pos.name === "教练" || pos.name === "主管教练");

        console.log(
          `用户 ${user.name}: status=${user.status}, hasPositions=${hasPositions}, isCoach=${isCoach}`
        );

        return isEnabled && isCoach;
      })
      .map((user: any) => ({
        id: user.id,
        name: user.name,
      }));

    console.log("过滤后的教练列表:", coachOptions.value);
  } catch (error: any) {
    console.error("加载教练列表失败:", error);
  }
}

// 加载时间段字典数据
async function loadTimeSlotDict() {
  if (timeSlotList.value.length > 0) {
    return;
  }

  try {
    const response = await request<ApiResponse<any[]>>({
      url: "/system/dict/data/info/badminton_time_slot",
      method: "get",
    });
    const dictData = response.data.data || [];

    timeSlotList.value = dictData.map((item: any) => ({
      id: item.dict_sort,
      code: item.dict_value,
      name: item.dict_label,
      start_time: item.dict_label.split("-")[0],
      end_time: item.dict_label.split("-")[1],
    }));
  } catch (error: any) {
    console.error("加载时间段字典失败:", error);
  }
}

// 格式化时间段显示
function formatTimeSlots(timeSlotsJson: string): { day: string; slots: string[] }[] {
  if (!timeSlotsJson) return [];

  try {
    const timeSlots = JSON.parse(timeSlotsJson);
    const result: { day: string; slots: string[] }[] = [];

    // 按天排序（周日在前）
    const dayOrder = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

    // 遍历每天的时段
    dayOrder.forEach((day) => {
      const daySlots = timeSlots[day];
      if (daySlots && Array.isArray(daySlots) && daySlots.length > 0) {
        const slots: string[] = [];
        daySlots.forEach((slotCode: string) => {
          // 从时间段列表中查找对应的时间段
          const slot = timeSlotList.value.find((s) => s.code === slotCode);
          if (slot) {
            slots.push(`${slot.start_time}-${slot.end_time}`);
          }
        });
        if (slots.length > 0) {
          result.push({ day, slots });
        }
      }
    });

    return result;
  } catch (e) {
    console.error("解析时间段JSON失败:", e);
    return [];
  }
}

// 检查表格列是否显示
function isColumnShow(prop: string): boolean {
  const column = tableColumns.value.find((col: any) => col.prop === prop);
  return column?.show || false;
}

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await ClassAPI.getClassList(queryFormData);
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

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
  // 重置验证错误状态
  Object.keys(timeSlotsValidationError).forEach((day) => (timeSlotsValidationError[day] = false));
}

// 监听时间段变化，清除对应星期的验证错误
watch(
  () => formData.time_slots,
  (newTimeSlots) => {
    for (const day in newTimeSlots) {
      if (timeSlotsValidationError[day] && newTimeSlots[day] && newTimeSlots[day].length > 0) {
        timeSlotsValidationError[day] = false;
      }
    }
  },
  { deep: true }
);

// 监听星期变化，清除取消选择星期的时间段
watch(
  () => formData.weekly_schedule_days,
  (newDays, oldDays = []) => {
    // 找出被移除的星期
    const removedDays = oldDays.filter((day) => !newDays.includes(day));

    // 清除被移除星期的时间段数据
    removedDays.forEach((day) => {
      if (formData.time_slots[day]) {
        formData.time_slots[day] = [];
      }
      // 同时清除该星期的验证错误状态
      timeSlotsValidationError[day] = false;
    });
  },
  { deep: true }
);

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
    const response = await ClassAPI.getClassDetail(id);
    if (type === "detail") {
      dialogVisible.title = "班级详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改班级";
      Object.assign(formData, response.data.data);
      // 将weekly_schedule字符串解析为数组，并按周日到周六排序
      if (formData.weekly_schedule) {
        const dayOrder = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
        const days = formData.weekly_schedule.split("、");
        formData.weekly_schedule_days = days.filter((day) => dayOrder.includes(day));
      }
      // 解析time_slots_json
      if (response.data.data.time_slots_json) {
        try {
          formData.time_slots = JSON.parse(response.data.data.time_slots_json);
        } catch (e) {
          console.error("解析time_slots_json失败", e);
        }
      }
    }
  } else {
    dialogVisible.title = "新增班级";
  }
  dialogVisible.visible = true;
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 将time_slots对象转换为JSON字符串存储
  formData.time_slots_json = JSON.stringify(formData.time_slots || {});
  // 将选中的星期数组转换为逗号分隔的字符串（按固定顺序：周日、周一...周六）
  const dayOrder = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  const sortedDays = formData.weekly_schedule_days.filter((day) => dayOrder.includes(day));
  formData.weekly_schedule = sortedDays.join("、") || "";

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
      res = await ClassAPI.createClass(submitData);
    } else if (operationType === "update" && updateId) {
      res = await ClassAPI.updateClass(updateId, submitData);
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

    await ClassAPI.deleteClass(ids);
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
onMounted(async () => {
  await loadSemesterOptions();
  await loadCoachOptions();
  await loadTimeSlotDict();
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

/* 时间段显示样式 */
.time-slots-container {
  line-height: 1.8;
}

.day-group {
  display: flex;
  align-items: flex-start;
  margin-bottom: 4px;
}

.day-label {
  font-weight: 600;
  color: #606266;
  min-width: 40px;
  flex-shrink: 0;
}

.time-labels {
  color: #909399;
  font-size: 13px;
}
</style>
