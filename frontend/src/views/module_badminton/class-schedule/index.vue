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
        <el-table-column label="时间段" min-width="280">
          <template #default="scope">
            <div v-if="scope.row.time_slots_json" class="time-slots-container">
              <div v-for="(dayGroup, index) in formatSelectedTimeSlots(JSON.parse(scope.row.time_slots_json))" :key="index" class="day-group">
                <span class="day-label">{{ dayGroup.day }}:</span>
                <span class="time-labels">{{ dayGroup.slots.join(', ') }}</span>
              </div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="排课类型" min-width="100">
          <template #default="scope">
            <el-tag :type="scope.row.schedule_type === 'regular' ? '' : scope.row.schedule_type === 'makeup' ? 'warning' : scope.row.schedule_type === 'extra' ? 'success' : 'info'">
              {{ getScheduleTypeName(scope.row.schedule_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="地点" prop="location" min-width="120" />
        <el-table-column label="教练" prop="coach.name" min-width="100" />
        <el-table-column label="排课状态" prop="schedule_status" min-width="90">
          <template #default="scope">
            <el-tag :type="scope.row.schedule_status === 'scheduled' ? 'info' : scope.row.schedule_status === 'active' ? 'success' : scope.row.schedule_status === 'completed' ? 'warning' : 'danger'">
                        {{ scope.row.schedule_status === 'scheduled' ? '已排课' : scope.row.schedule_status === 'active' ? '进行中' : scope.row.schedule_status === 'completed' ? '已完成' : '已取消' }}
                      </el-tag>          </template>
        </el-table-column>
        <el-table-column label="学员数" prop="student_count" min-width="80" align="center">
          <template #default="scope">
            {{ scope.row.student_count || scope.row.attendance_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="出勤人数" prop="attendance_count" min-width="90" />
        <el-table-column label="创建时间" prop="created_time" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_time) }}
          </template>
        </el-table-column>
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
      width="1400px"
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
          <el-descriptions-item label="时间段配置" :span="2">
            <span v-if="detailFormData.time_slots_json">
              {{ formatTimeSlotsJson(detailFormData.time_slots_json) }}
            </span>
            <span v-else-if="detailFormData.time_slot_code">
              {{ detailFormData.time_slot_code }}时段 ({{ detailFormData.start_time }} - {{ detailFormData.end_time }})
            </span>
            <span v-else>未设置</span>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ detailFormData.start_time || '从时间段配置获取' }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ detailFormData.end_time || '从时间段配置获取' }}
          </el-descriptions-item>
          <el-descriptions-item label="时长">
            {{ detailFormData.duration_minutes ? detailFormData.duration_minutes + '分钟' : '90分钟（从时间段配置获取）' }}
          </el-descriptions-item>
          <el-descriptions-item label="地点">
            {{ detailFormData.location || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="教练">
            {{ detailFormData.coach?.name || '未指定' }}
          </el-descriptions-item>
          <el-descriptions-item label="排课状态">
            <el-tag :type="detailFormData.schedule_status === 'scheduled' ? 'info' : detailFormData.schedule_status === 'active' ? 'success' : detailFormData.schedule_status === 'completed' ? 'warning' : 'danger'">
                      {{ detailFormData.schedule_status === 'scheduled' ? '已排课' : detailFormData.schedule_status === 'active' ? '进行中' : detailFormData.schedule_status === 'completed' ? '已完成' : '已取消' }}
                    </el-tag>          </el-descriptions-item>
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
        <!-- V2版本新增排课表单 -->
        <el-form
          ref="dataFormRef"
          :model="formDataV2"
          :rules="rulesV2"
          label-suffix=":"
          label-width="100px"
          label-position="right"
        >
          <el-row :gutter="20">
            <!-- 左侧：学员列表 -->
            <el-col :span="10">
              <el-card class="student-list-card">
                <template #header>
                  <div class="card-header">
                    <span>可用学员列表</span>
                    <el-tag size="small" type="info">已选择: {{ selectedStudentIds.length }} 人</el-tag>
                  </div>
                </template>
                
                <!-- 筛选区域 -->
                <div style="margin-bottom: 15px;">
                  <el-input
                    v-model="studentSearch"
                    placeholder="搜索学员姓名"
                    clearable
                    style="width: 100%; margin-bottom: 10px;"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                  <el-row :gutter="10">
                    <el-col :span="12">
                      <el-select v-model="groupFilter" placeholder="筛选组别" clearable style="width: 100%">
                        <el-option label="全部组别" value="" />
                        <el-option
                          v-for="group in uniqueGroups"
                          :key="group"
                          :label="group"
                          :value="group"
                        />
                      </el-select>
                    </el-col>
                    <el-col :span="12">
                      <el-select v-model="levelFilter" placeholder="筛选水平" clearable style="width: 100%">
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
                
                <div v-if="loadingStudents" class="empty-tip">
                  <el-skeleton :rows="5" animated />
                </div>
                <div v-else-if="availableStudents.length === 0" class="empty-tip">
                  <el-empty description="请选择班级、日期和时间段后查看可用学员" :image-size="80" />
                </div>
                <div v-else-if="!loadingStudents && filteredStudents.length === 0" class="empty-tip">
                  <el-empty description="没有符合条件的学员" :image-size="80" />
                </div>
                <el-checkbox-group v-else v-model="selectedStudentIds" class="student-checkbox-group">
                  <el-checkbox
                    v-for="student in filteredStudents"
                    :key="student.student_id"
                    :label="student.student_id"
                    :disabled="student.remaining_sessions <= 0"
                  >
                    <div class="student-item">
                      <div class="student-name">{{ student.student_name }}</div>
                      <div class="student-info">
                        <el-tag size="small" type="info">{{ student.birth_date ? calculateAge(student.birth_date) + '岁' : '未知年龄' }}</el-tag>
                        <el-tag size="small" type="primary">{{ student.group_name || '未分组' }}</el-tag>
                        <el-tag size="small" type="warning">{{ student.level || '未设置' }}</el-tag>
                        <el-tag size="small" :type="student.remaining_sessions > 0 ? 'success' : 'danger'">
                          剩余: {{ student.remaining_sessions }} / 总计: {{ student.total_sessions }}
                        </el-tag>
                      </div>
                    </div>
                  </el-checkbox>
                </el-checkbox-group>
              </el-card>
            </el-col>

            <!-- 右侧：排课表单 -->
            <el-col :span="14" class="right-form-container">
              <!-- 右侧表单的 loading 覆盖层 -->
              <div v-if="dialogLoading" class="form-loading-overlay">
                <el-icon class="is-loading" :size="36">
                  <Loading />
                </el-icon>
                <p class="loading-text">数据加载中...</p>
              </div>

              <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="学期" prop="semester_id">
                      <el-select
                        v-model="formDataV2.semester_id"
                        placeholder="请选择学期"
                        style="width: 100%"
                        @change="loadClasses"
                      >
                        <el-option
                          v-for="semester in semesterList"
                          :key="semester.id"
                          :label="semester.name"
                          :value="semester.id"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="排课日期" prop="schedule_date">
                      <el-date-picker
                        v-model="formDataV2.schedule_date"
                        type="date"
                        placeholder="请选择排课日期"
                        style="width: 100%"
                        value-format="YYYY-MM-DD"
                        :disabled-date="disabledDate"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="班级" prop="class_ids">
                      <el-select
                        v-model="formDataV2.class_ids"
                        placeholder="请选择班级（可多选）"
                        style="width: 100%"
                        multiple
                        :disabled="!formDataV2.semester_id"
                      >
                        <el-option
                          v-for="cls in classList"
                          :key="cls.id"
                          :label="cls.name"
                          :value="cls.id"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="时间段">
                      <el-select
                        v-model="tempTimeSlotIds"
                        placeholder="请选择时间段（可多选）"
                        style="width: 100%"
                        multiple
                        :disabled="!formDataV2.class_ids || formDataV2.class_ids.length === 0"
                      >
                        <el-option-group
                          v-for="group in groupedTimeSlots"
                          :key="group.label"
                          :label="group.label"
                        >
                          <el-option
                            v-for="slot in group.slots"
                            :key="slot.id"
                            :label="slot.name"
                            :value="slot.id"
                          />
                        </el-option-group>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="教练" prop="coach_id">
                      <el-select
                        v-model="formDataV2.coach_id"
                        placeholder="请选择教练"
                        style="width: 100%"
                        filterable
                      >
                        <el-option
                          v-for="coach in coachList"
                          :key="coach.id"
                          :label="coach.name"
                          :value="coach.id"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="排课状态" prop="schedule_status">
                      <el-select
                        v-model="formDataV2.schedule_status"
                        placeholder="请选择排课状态"
                        style="width: 100%"
                      >
                        <el-option value="scheduled" label="已排课" />
                        <el-option value="confirmed" label="已确认" />
                        <el-option value="active" label="进行中" />
                        <el-option value="completed" label="已完成" />
                        <el-option value="cancelled" label="已取消" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="地点">
                      <el-input
                        v-model="formDataV2.location"
                        placeholder="请输入上课地点"
                        :maxlength="128"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="课程主题">
                      <el-input
                        v-model="formDataV2.topic"
                        placeholder="请输入课程主题"
                        :maxlength="256"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="内容摘要">
                      <el-input
                        v-model="formDataV2.content_summary"
                        type="textarea"
                        :rows="2"
                        placeholder="请输入内容摘要"
                        :maxlength="500"
                        show-word-limit
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="备注">
                      <el-input
                        v-model="formDataV2.notes"
                        type="textarea"
                        :rows="2"
                        placeholder="请输入备注"
                        :maxlength="500"
                        show-word-limit
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
            </el-col>
          </el-row>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button v-if="dialogVisible.type !== 'detail'" type="primary" :loading="submitLoading" @click="handleSubmit">
            <template v-if="!submitLoading">
              确定
            </template>
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

import { ref, reactive, onMounted, watch, computed, nextTick } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled, Search, Loading } from "@element-plus/icons-vue";
import ClassScheduleAPI, { ClassScheduleTable, ClassSchedulePageQuery, AvailableStudentInfo, ClassScheduleCreateV2Form, TimeSlotInfo, DictDataItem } from "@/api/module_badminton/class-schedule";
import SemesterAPI from "@/api/module_badminton/semester";
import ClassAPI from "@/api/module_badminton/class";
import UserAPI from "@/api/module_system/user";

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

// 格式化时间段JSON显示
function formatTimeSlotsJson(jsonStr: string | undefined): string {
  if (!jsonStr) return '未设置';
  try {
    const timeSlots = JSON.parse(jsonStr);
    const result: string[] = [];
    for (const [day, codes] of Object.entries(timeSlots)) {
      result.push(`${day}: ${codes.join(', ')}`);
    }
    return result.join('; ');
  } catch (e) {
    return jsonStr;
  }
}

// 格式化选课时间段（参照购买记录样式）
function formatSelectedTimeSlots(timeSlots: { [key: string]: string[] } | undefined): { day: string; slots: string[] }[] {
  if (!timeSlots) return [];
  
  const result: { day: string; slots: string[] }[] = [];
  
  // 按天排序
  const dayOrder = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  
  // 遍历每天的时段
  dayOrder.forEach(day => {
    const daySlots = timeSlots[day];
    if (daySlots && Array.isArray(daySlots) && daySlots.length > 0) {
      const slots: string[] = [];
      daySlots.forEach((slotCode: string) => {
        // 从时间段列表中查找对应的时间段
        const slot = timeSlotList.value.find(s => s.code === slotCode);
        if (slot) {
          slots.push(`${slot.start_time}-${slot.end_time}`);
        } else {
          // 降级使用代码本身
          slots.push(slotCode);
        }
      });
      if (slots.length > 0) {
        result.push({ day, slots });
      }
    }
  });
  
  return result;
}

// 分页查询参数
const queryFormData = reactive<ClassSchedulePageQuery>({
  page_no: 1,
  page_size: 10,
  class_id: undefined,
  schedule_date_start: undefined,
  schedule_date_end: undefined,
  schedule_status: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" | "update" | "detail",
});

// 表单验证规则
const rulesV2 = reactive({
  semester_id: [{ required: true, message: "请选择学期", trigger: "change" }],
  schedule_date: [{ required: true, message: "请选择排课日期", trigger: "change" }],
  class_ids: [{ required: true, message: "请选择班级", trigger: "change" }],
  coach_id: [{ required: true, message: "请选择教练", trigger: "change" }],
  schedule_status: [{ required: true, message: "请选择排课状态", trigger: "change" }],
});

// ============================================================================
// V2版本新增排课功能
// ============================================================================

// V2版本表单数据
const formDataV2 = reactive<ClassScheduleCreateV2Form>({
  semester_id: undefined,
  schedule_date: "",
  class_ids: [],
  coach_id: undefined,
  time_slots: {},
  schedule_status: undefined,
  student_ids: [],
  location: "",
  topic: "",
  content_summary: "",
  notes: "",
});

// 临时存储时间段ID数组（用于前端选择）
const tempTimeSlotIds = ref<number[]>([]);

// 学期列表
const semesterList = ref<any[]>([]);

// 班级列表
const classList = ref<any[]>([]);

// 教练列表
const coachList = ref<any[]>([]);

// 可用学员列表
const availableStudents = ref<AvailableStudentInfo[]>([]);

// 学员列表加载状态
const loadingStudents = ref(false);

// 对话框加载状态（用于编辑模式的loading覆盖层）
const dialogLoading = ref(false);

// 提交按钮loading状态
const submitLoading = ref(false);

// 已选中学员ID列表
const selectedStudentIds = ref<number[]>([]);

// 编辑模式下的记录ID
const editingScheduleId = ref<number | undefined>(undefined);

// 编辑模式下是否正在初始化加载（防止 watch 重复调用 loadAvailableStudents）
const isEditingLoading = ref(false);

// 学员列表加载防抖计时器
let loadStudentsTimer: ReturnType<typeof setTimeout> | null = null;

// 学员搜索和筛选
const studentSearch = ref("");
const groupFilter = ref("");
const levelFilter = ref("");

// 计算年龄
function calculateAge(birthDate?: string): number {
  if (!birthDate) return 0;
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

// 过滤后的学员列表
const filteredStudents = computed(() => {
  return availableStudents.value.filter((student) => {
    // 姓名搜索
    let matchSearch = true;
    if (studentSearch.value) {
      matchSearch = student.student_name?.toLowerCase().includes(studentSearch.value.toLowerCase());
    }
    
    // 组别筛选
    let matchGroup = true;
    if (groupFilter.value) {
      matchGroup = student.group_name === groupFilter.value;
    }
    
    // 水平筛选
    let matchLevel = true;
    if (levelFilter.value) {
      matchLevel = student.level === levelFilter.value;
    }
    
    return matchSearch && matchGroup && matchLevel;
  });
});

// 将时间段ID列表转换为JSON格式 {"周一": ["A", "B"]}
function convertTimeSlotIdsToJson(slotIds: number[]): { [key: string]: string[] } {
  const result: { [key: string]: string[] } = {};
  
  slotIds.forEach(slotId => {
    // 查找对应的时间段信息
    const slot = timeSlotList.value.find(s => s.id === slotId);
    if (slot && slot.day && slot.code) {
      if (!result[slot.day]) {
        result[slot.day] = [];
      }
      if (!result[slot.day].includes(slot.code)) {
        result[slot.day].push(slot.code);
      }
    }
  });
  
  return result;
}

// 监听临时时间段ID变化，自动转换并更新表单数据
watch(tempTimeSlotIds, (newSlotIds) => {
  // 更新 formDataV2.time_slots
  formDataV2.time_slots = convertTimeSlotIdsToJson(newSlotIds);

  // 只在新增模式下（没有 id）清空数据，编辑模式不清空
  if (!editingScheduleId.value) {
    formDataV2.student_ids = [];
    selectedStudentIds.value = [];
    availableStudents.value = [];
  }
  // 编辑模式下不清空任何数据，保留用户的选择

  // 使用防抖加载可用学员列表（新增模式）
  if (!editingScheduleId.value) {
    if (loadStudentsTimer) {
      clearTimeout(loadStudentsTimer);
    }

    if (newSlotIds.length > 0) {
      loadStudentsTimer = setTimeout(() => {
        loadAvailableStudents();
        loadStudentsTimer = null;
      }, 500);
    }
  } else {
    // 编辑模式下：如果正在初始化加载，则不重复调用 loadAvailableStudents()
    if (isEditingLoading.value) {
      console.log('编辑模式正在初始化加载，跳过 watch 触发的 loadAvailableStudents');
      return;
    }
    // 编辑模式下用户手动更改时间段时才加载
    if (newSlotIds.length > 0) {
      loadAvailableStudents();
    }
  }
}, { deep: true });

// 获取时间段名称
function getTimeSlotName(timeSlotId: number | undefined): string {
  if (!timeSlotId) return '-';
  
  // 解析 time_slot_id：day_index * 10 + slot_id
  const dayIndex = Math.floor(timeSlotId / 10);
  const slotId = timeSlotId % 10;
  const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  
  // 从timeSlotList查找对应的时间段
  const timeSlot = timeSlotList.value.find(ts => ts.id === slotId);
  if (!timeSlot) {
    return `未知 (${timeSlotId})`;
  }
  
  return `${dayNames[dayIndex]} ${timeSlot.code} (${timeSlot.name})`;
}

// 获取排课类型名称
function getScheduleTypeName(type: string | undefined): string {
  const typeMap: Record<string, string> = {
    'regular': '常规课',
    'makeup': '补课',
    'extra': '加课',
    'cancelled': '取消课'
  };
  return type ? typeMap[type] || type : '-';
}

// 格式化日期时间
function formatDateTime(dateStr: string | undefined): string {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    // 格式化为 YYYY-MM-DD HH:mm:ss
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (e) {
    return dateStr;
  }
}

// 获取唯一的组别列表
const uniqueGroups = computed(() => {
  const groups = availableStudents.value
    .map((s) => s.group_name)
    .filter((g): g is string => !!g);
  return [...new Set(groups)].sort();
});

// 获取唯一的水平列表
const uniqueLevels = computed(() => {
  const levels = availableStudents.value
    .map((s) => s.level)
    .filter((l): l is string => !!l);
  return [...new Set(levels)].sort();
});

// 时间段列表（从字典接口获取）
const timeSlotList = ref<TimeSlotInfo[]>([]);

// 加载时间段字典数据
async function loadTimeSlotDict() {
  // 如果已经加载过，不再重复加载
  if (timeSlotList.value.length > 0) {
    return;
  }
  
  try {
    const response = await ClassScheduleAPI.getTimeSlotDict();
    const dictData = response.data.data || [];
    
    // 转换字典数据为时间段格式
    timeSlotList.value = dictData.map((item: DictDataItem) => ({
      id: item.dict_sort,
      code: item.dict_value,
      name: item.dict_label,
      start_time: item.dict_label.split('-')[0],
      end_time: item.dict_label.split('-')[1],
      duration_minutes: 90,
      day: '默认'
    }));
    
    console.log('加载时间段字典成功:', timeSlotList.value);
  } catch (error: any) {
    console.error("加载时间段字典失败:", error);
    // 失败时使用默认时间段列表
    timeSlotList.value = [
      { id: 1, code: 'A', name: '08:00-09:30', start_time: '08:00', end_time: '09:30', duration_minutes: 90, day: '默认' },
      { id: 2, code: 'B', name: '09:30-11:00', start_time: '09:30', end_time: '11:00', duration_minutes: 90, day: '默认' },
      { id: 3, code: 'C', name: '14:00-15:30', start_time: '14:00', end_time: '15:30', duration_minutes: 90, day: '默认' },
      { id: 4, code: 'D', name: '15:30-17:00', start_time: '15:30', end_time: '17:00', duration_minutes: 90, day: '默认' },
      { id: 5, code: 'E', name: '18:00-19:30', start_time: '18:00', end_time: '19:30', duration_minutes: 90, day: '默认' },
    ];
  }
}

// 加载学期列表

async function loadSemesters() {

  // 如果已经加载过，不再重复加载

  if (semesterList.value.length > 0) {

    return;

  }

  

  try {

    const response = await SemesterAPI.getSemesterList({ page_no: 1, page_size: 100 });

    semesterList.value = response.data.data.items || [];

  } catch (error: any) {

    console.error("加载学期列表失败:", error);

  }

}



// 加载班级列表（根据学期筛选）

async function loadClasses() {

  if (!formDataV2.semester_id) {

    classList.value = [];

    return;

  }

  

  try {

    const response = await ClassAPI.getClassList({

      page_no: 1,

      page_size: 100,

      semester_id: formDataV2.semester_id,

    });

    classList.value = response.data.data.items || [];

  } catch (error: any) {

    console.error("加载班级列表失败:", error);

  }

}



// 加载教练列表

async function loadCoaches() {

  // 如果已经加载过，不再重复加载

  if (coachList.value.length > 0) {

    return;

  }

  

  try {

    const response = await UserAPI.listUser({

      page_no: 1,

      page_size: 100,

    });

    coachList.value = response.data.data.items || [];

  } catch (error: any) {

    console.error("加载教练列表失败:", error);

  }

}

// 加载可用学员列表
async function loadAvailableStudents() {
  // 只在选择了班级、日期和时间段后才加载学员列表
  if (!formDataV2.semester_id || !formDataV2.schedule_date || formDataV2.class_ids.length === 0 || tempTimeSlotIds.value.length === 0) {
    availableStudents.value = [];
    // 新增模式下清空，编辑模式下保留
    if (!editingScheduleId.value) {
      selectedStudentIds.value = [];
    }
    loadingStudents.value = false;
    return;
  }
  
  // 新增模式下清空之前选择的学员ID，编辑模式下保留
  if (!editingScheduleId.value) {
    selectedStudentIds.value = [];
  }
  loadingStudents.value = true;
  
  try {
    const requestData = {
      semester_id: formDataV2.semester_id,
      schedule_date: formDataV2.schedule_date,
      time_slots: formDataV2.time_slots,
      class_ids: formDataV2.class_ids.length > 0 ? formDataV2.class_ids : undefined,
    };
    
    const response = await ClassScheduleAPI.getAvailableStudents(requestData);
    availableStudents.value = response.data.data || [];
  } catch (error: any) {
    console.error("加载可用学员列表失败:", error);
    ElMessage.error(`加载可用学员列表失败: ${error.response?.data?.msg || error.message}`);
  } finally {
    loadingStudents.value = false;
  }
}

// 加载可用时间段（根据班级和日期的星期几）
async function loadAvailableTimeSlots() {
  console.log('开始加载可用时间段:', {
    class_ids: formDataV2.class_ids,
    schedule_date: formDataV2.schedule_date
  });
  
  // 从后端获取完整的时间段列表（包含所有7天 × 10个基础时段 + 扩展时段）
  if (!formDataV2.class_ids.length || !formDataV2.schedule_date) {
    console.log('缺少班级或日期，使用字典数据');
    // 使用字典数据作为默认值
    if (timeSlotDict.value.length === 0) {
      await loadTimeSlotDict();
    }
    return;
  }
  
  try {
    // 计算星期几（0=周日，1=周一，...，6=周六）
    const date = new Date(formDataV2.schedule_date);
    const dayOfWeek = date.getDay(); // 0=周日，1=周一，...，6=周六
    console.log('计算星期几:', dayOfWeek, '(0=周日，1=周一，...，6=周六)');
    
    // 并行获取所有选定班级的时间段配置
    console.log('开始调用 API 获取时间段，班级ID:', formDataV2.class_ids);
    const timeSlotPromises = formDataV2.class_ids.map(classId => 
      ClassAPI.getAvailableTimeSlots(classId, dayOfWeek)
    );
    
    const results = await Promise.all(timeSlotPromises);
    console.log('API 返回结果:', results);
    
    // 合并所有时间段数据
    let allTimeSlots: any[] = [];
    results.forEach((response, index) => {
      console.log(`班级 ${formDataV2.class_ids[index]} 的完整响应:`, response);
      console.log(`班级 ${formDataV2.class_ids[index]} 的 data 字段:`, response.data);
      // 后端返回格式: response.data.data.time_slots
      if (response.data && response.data.data) {
        console.log(`班级 ${formDataV2.class_ids[index]} 的 data.data:`, response.data.data);
        if (response.data.data.time_slots) {
          console.log(`班级 ${formDataV2.class_ids[index]} 的 time_slots:`, response.data.data.time_slots);
          allTimeSlots = allTimeSlots.concat(response.data.data.time_slots);
        } else {
          console.warn(`班级 ${formDataV2.class_ids[index]} 没有 time_slots 字段`);
        }
      } else {
        console.warn(`班级 ${formDataV2.class_ids[index]} 没有 data.data 字段`);
      }
    });
    
    console.log('合并后的时间段数据:', allTimeSlots);
    
    // 根据选择的日期过滤出对应星期的时间段
    const dayOfWeekMap: Record<number, string> = {
      0: '周日',
      1: '周一',
      2: '周二',
      3: '周三',
      4: '周四',
      5: '周五',
      6: '周六'
    };
    const dayOfWeekName = dayOfWeekMap[dayOfWeek];
    const filteredTimeSlots = allTimeSlots.filter(slot => slot.day === dayOfWeekName);
    console.log(`过滤 ${dayOfWeekName} 的时间段，过滤前: ${allTimeSlots.length} 个，过滤后: ${filteredTimeSlots.length} 个`);
    
    // 如果没有获取到时间段，使用字典数据
    if (filteredTimeSlots.length === 0) {
      console.warn(`未获取到 ${dayOfWeekName} 的时间段数据，使用字典数据`);
      await loadTimeSlotDict();
      return;
    }
    
    // 去重时间段（按 day 和 slot_code 组合去重，避免不同班级的相同时间段代码冲突）
    const uniqueTimeSlots = new Map();
    for (const slot of filteredTimeSlots) {
      const key = `${slot.day}_${slot.slot_code}`;
      if (!uniqueTimeSlots.has(key)) {
        uniqueTimeSlots.set(key, slot);
      }
    }
    
    console.log('去重后的时间段数据:', Array.from(uniqueTimeSlots.values()));
    
    // 更新时间段列表，保留 day 字段用于分组
    timeSlotList.value = Array.from(uniqueTimeSlots.values()).map((slot: any) => ({
      id: slot.id,
      code: slot.slot_code,
      name: `${slot.day} ${slot.slot_code} ${slot.start_time}-${slot.end_time}`,
      start_time: slot.start_time,
      end_time: slot.end_time,
      duration_minutes: slot.duration_minutes,
      day: slot.day, // 保留星期几用于分组
    }));
    
    console.log('最终的时间段列表:', timeSlotList.value);
    console.log('时间段时间段数量:', timeSlotList.value.length);

    // 如果之前选择的时间段不在新列表中，清空选择
    const validIds = timeSlotList.value.map((s: any) => s.id);
    tempTimeSlotIds.value = tempTimeSlotIds.value.filter((id: number) => validIds.includes(id));
    console.log('清理后的已选时间段:', tempTimeSlotIds.value);
    
    // 如果有已选时间段，自动加载学员列表
    if (tempTimeSlotIds.value.length > 0) {
      console.log('时间段加载完成，自动加载学员列表');
      await loadAvailableStudents();
    }
  } catch (error: any) {
    console.error("加载可用时间段失败:", error);
    ElMessage.error(`加载可用时间段失败: ${error.message || error}`);
    // 加载失败时使用字典数据
    if (timeSlotList.value.length === 0) {
      await loadTimeSlotDict();
    }
  }
}

// 将时间段按星期几分组
const groupedTimeSlots = computed(() => {
  const groups: Array<{ label: string; slots: any[] }> = [];
  const groupMap = new Map<string, any[]>();
  
  timeSlotList.value.forEach((slot: any) => {
    const day = slot.day || '其他';
    if (!groupMap.has(day)) {
      groupMap.set(day, []);
    }
    groupMap.get(day)!.push(slot);
  });

  // 定义星期几排序顺序
  const dayOrder = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  
  // 将 Map 转换为数组，方便 el-option-group 使用
  const sortedGroups: Array<{ label: string; slots: any[] }> = [];
  
  // 按星期几排序
  dayOrder.forEach(day => {
    if (groupMap.has(day)) {
      const slots = groupMap.get(day)!;
      // 按时间段开始时间排序（支持新增时间段）
      slots.sort((a, b) => {
        const timeA = a.start_time || '00:00';
        const timeB = b.start_time || '00:00';
        return timeA.localeCompare(timeB);
      });
      sortedGroups.push({ label: day, slots });
    }
  });
  
  // 添加其他时间段（如果有）
  groupMap.forEach((slots, day) => {
    if (!dayOrder.includes(day)) {
      slots.sort((a, b) => {
        const timeA = a.start_time || '00:00';
        const timeB = b.start_time || '00:00';
        return timeA.localeCompare(timeB);
      });
      sortedGroups.push({ label: day, slots });
    }
  });

  return sortedGroups;
});

// 监听学期变化，自动加载班级列表
watch(() => formDataV2.semester_id, (newVal, oldVal) => {
  // 只在新增模式下（没有 id）清空数据，编辑模式不清空
  if (!editingScheduleId.value) {
    formDataV2.class_ids = [];
    tempTimeSlotIds.value = [];
    formDataV2.time_slots = {};
    formDataV2.student_ids = [];
    selectedStudentIds.value = [];
    availableStudents.value = [];
  }
  loadClasses();
});

// 监听班级和日期变化，重新加载可用时间段
watch(() => [formDataV2.class_ids, formDataV2.schedule_date], () => {
  // 清空时间段和学员选择（日期改变时，原来的时间段可能不再有效）
  tempTimeSlotIds.value = [];
  formDataV2.time_slots = {};
  formDataV2.student_ids = [];
  selectedStudentIds.value = [];
  availableStudents.value = [];
  
  // 加载可用时间段
  if (formDataV2.class_ids.length > 0 && formDataV2.schedule_date) {
    loadAvailableTimeSlots();
  }
});

// 学员选择变化
watch(selectedStudentIds, (newIds) => {
  formDataV2.student_ids = newIds;
});

// 重置V2表单
function resetFormV2() {
  dialogLoading.value = false; // 重置 loading 状态
  editingScheduleId.value = undefined; // 重置编辑ID
  isEditingLoading.value = false; // 重置编辑加载标志
  Object.assign(formDataV2, {
    semester_id: undefined,
    schedule_date: "",
    class_ids: [],
    coach_id: undefined,
    time_slots: {},
    schedule_status: undefined,
    student_ids: [],
    location: "",
    topic: "",
    content_summary: "",
    notes: "",
  });
  tempTimeSlotIds.value = [];
  selectedStudentIds.value = [];
  availableStudents.value = [];
}

// 提交V2表单
async function handleSubmitV2() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 手动验证时间段选择
  if (tempTimeSlotIds.value.length === 0) {
    ElMessage.warning("请选择时间段");
    return;
  }

  if (formDataV2.student_ids.length === 0) {
    ElMessage.warning("请至少选择一名学员");
    return;
  }

  // 保存表单数据副本
  const submitData = { ...formDataV2 };
  delete submitData.student_ids; // student_ids 会在 API 中处理

  // 保存操作类型和ID
  const operationType = "create";

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
    const res = await ClassScheduleAPI.createScheduleV2(submitData);

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

// 行复选框选中项变化
async function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
  selectionRows.value = selection;
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  dialogLoading.value = false; // 关闭对话框时重置 loading 状态
  resetFormV2();
}

// 打开弹窗
async function handleOpenDialog(type: "create" | "update" | "detail", id?: number) {
  // 每次打开弹窗前先重置表单
  resetFormV2();
  dialogVisible.type = type;
  
  if (id) {
    // 立即显示弹窗，先不填充数据
    dialogVisible.visible = true;
    if (type === "detail") {
      dialogVisible.title = "排课记录详情";
    } else if (type === "update") {
      dialogVisible.title = "加载中...";
      dialogLoading.value = true; // 开始加载时显示 loading 覆盖层
    }

    try {
      // 并行加载基础数据
      const loadPromises = [
        loadSemesters(),
        loadCoaches(),
        loadTimeSlotDict()
      ];
      await Promise.all(loadPromises);

      // 获取排课详情
      const response = await ClassScheduleAPI.getClassScheduleDetail(id);
      const data = response.data.data;

      if (type === "detail") {
        dialogVisible.title = "排课记录详情";
        Object.assign(detailFormData.value, data);
      } else if (type === "update") {
        dialogVisible.title = "修改排课记录";

        console.log('编辑模式，后端返回的排课数据:', data);
        console.log('后端返回的 student_ids:', data.student_ids);
      
      // 将后端返回的单个值转换为数组格式，以匹配表单期望的结构
      const studentIdsFromBackend = data.student_ids || [];
      
      console.log('解析后的学员IDs:', studentIdsFromBackend);
      
      // 先设置 id 字段，避免 watch 触发清空
      editingScheduleId.value = data.id;
      // 设置编辑模式初始化加载标志，防止 watch 重复调用 loadAvailableStudents
      isEditingLoading.value = true;
      
      // 使用 nextTick 确保设置 id 后再赋值其他字段
      await nextTick();
      
      // 先设置基本字段，以便后续可以加载可用时间段
      const class_id = data.class_id;
      const schedule_date = data.schedule_date || "";
      const semester_id = data.class?.semester_id || data.semester_id;
      
      Object.assign(formDataV2, {
        semester_id: semester_id,
        schedule_date: schedule_date,
        class_ids: class_id ? [class_id] : [],
        coach_id: data.coach_id,
        schedule_status: data.schedule_status || "scheduled",
        student_ids: studentIdsFromBackend,
        location: data.location || "",
        topic: data.topic || "",
        content_summary: data.content_summary || "",
        notes: data.notes || "",
      });
      
      // 同步选中学员ID到 selectedStudentIds
      selectedStudentIds.value = studentIdsFromBackend;
      
      console.log('设置 selectedStudentIds 后:', selectedStudentIds.value);
      
      // 等待 Vue 更新，确保响应式状态稳定
      await nextTick();
      
      // 并行加载班级列表和可用时间段
      const loadMorePromises = [];
      
      // 加载班级列表
      if (formDataV2.semester_id) {
        loadMorePromises.push(loadClasses());
      }
      
      // 加载可用时间段（必须在解析时间段JSON之前调用）
      if (formDataV2.class_ids.length > 0 && formDataV2.schedule_date) {
        loadMorePromises.push(loadAvailableTimeSlots());
      }
      
      await Promise.all(loadMorePromises);
      
      // 现在解析时间段JSON数据（timeSlotList.value 已包含正确的星期几信息）
      let timeSlotsData: { [key: string]: string[] } = {};
      let tempSlotIds: number[] = [];
      
      if (data.time_slots_json) {
        try {
          timeSlotsData = JSON.parse(data.time_slots_json);
        } catch (e) {
          console.error('解析时间段JSON失败:', e);
        }
      }
      
      // 将JSON格式转换为临时ID列表
      Object.entries(timeSlotsData).forEach(([day, codes]) => {
        codes.forEach((code: string) => {
          const slot = timeSlotList.value.find(s => s.day === day && s.code === code);
          if (slot) {
            tempSlotIds.push(slot.id);
          }
        });
      });
      
      // 设置时间段数据
      formDataV2.time_slots = timeSlotsData;
      tempTimeSlotIds.value = tempSlotIds;

      console.log('编辑模式解析的时间段数据:', timeSlotsData);
      console.log('编辑模式生成的临时ID列表:', tempSlotIds);

      // 手动加载学员列表（等待加载完成后再关闭 loading）
      if (tempSlotIds.length > 0) {
        await loadAvailableStudents();
      }

      // 学员列表加载完成，允许 watch 正常工作
      isEditingLoading.value = false;

      console.log('加载完成后，selectedStudentIds:', selectedStudentIds.value);
      console.log('加载完成后，availableStudents:', availableStudents.value);
    }
  } finally {
    // 无论成功还是失败，都关闭 loading
    if (type === "update") {
      dialogLoading.value = false;
    }
  }
  } else {
    // 新增模式
    dialogVisible.title = "新增排课记录";
    dialogVisible.visible = true;

    // 加载V2版本所需的数据
    await Promise.all([
      loadSemesters(),
      loadCoaches(),
      loadTimeSlotDict()
    ]);
  }
}

// 禁用日期（不在学期范围内的日期）
function disabledDate(time: Date) {
  if (!formDataV2.semester_id) {
    return false;
  }
  
  const semester = semesterList.value.find(s => s.id === formDataV2.semester_id);
  if (!semester) {
    return false;
  }
  
  const date = new Date(time);
  const startDate = new Date(semester.start_date);
  const endDate = new Date(semester.end_date);
  
  return date < startDate || date > endDate;
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 手动验证时间段选择（仅更新时需要验证）
  if (dialogVisible.type === "update") {
    if (tempTimeSlotIds.value.length === 0) {
      ElMessage.warning("请选择时间段");
      return;
    }

    if (formDataV2.student_ids.length === 0) {
      ElMessage.warning("请至少选择一名学员");
      return;
    }
  }

  // 保存表单数据副本
  const submitData = { ...formDataV2 };
  delete submitData.student_ids; // student_ids 会在 API 中处理

  // 保存操作类型和ID
  const operationType = dialogVisible.type;
  const updateId = editingScheduleId.value;

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
      res = await ClassScheduleAPI.createScheduleV2(submitData);
    } else if (operationType === "update" && updateId) {
      console.log('更新排课记录，提交的数据:', JSON.stringify(submitData));
      res = await ClassScheduleAPI.updateClassSchedule(updateId, submitData);
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
  // 并行加载基础数据（学期、教练、时间段字典）
  Promise.all([
    loadSemesters(),
    loadCoaches(),
    loadTimeSlotDict()
  ]).catch(error => {
    console.error("加载基础数据失败:", error);
  });
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

/* V2版本新增排课表单样式 */
.schedule-create-v2 {
  padding: 10px 0;
}

.student-list-card {
  height: 600px;
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.empty-tip {
  padding: 40px 0;
  text-align: center;
}

.student-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.student-checkbox-group :deep(.el-checkbox) {
  width: 100%;
  margin-right: 0;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  transition: all 0.3s;
}

.student-checkbox-group :deep(.el-checkbox:hover) {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.student-checkbox-group :deep(.el-checkbox.is-checked) {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.student-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.student-name {
  font-weight: 500;
  font-size: 14px;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 8px;
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

/* 右侧表单容器 - 相对定位 */
.right-form-container {
  position: relative;
  min-height: 400px;
}

/* 右侧表单的 loading 覆盖层 */
.form-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 100;
  border-radius: 4px;
}

.form-loading-overlay .loading-text {
  margin-top: 15px;
  font-size: 14px;
  color: #606266;
}
</style>