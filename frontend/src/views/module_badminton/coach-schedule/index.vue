<!-- 教练排课视图 -->
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
        <el-form-item prop="coach_id" label="教练">
          <!-- 管理员：显示可选择的下拉框 -->
          <el-select
            v-if="isAdmin"
            v-model="queryFormData.coach_id"
            placeholder="请选择教练"
            style="width: 200px"
            filterable
            clearable
            @change="handleCoachChange"
          >
            <el-option
              v-for="coach in coachList"
              :key="coach.id"
              :label="coach.name"
              :value="coach.id"
            />
          </el-select>
          <!-- 非管理员：显示只读的文本标签 -->
          <div v-else class="coach-name-display">
            {{ currentUser.name || currentUser.username }}
          </div>
        </el-form-item>
        <el-form-item prop="schedule_date" label="日期">
          <el-date-picker
            v-model="queryFormData.schedule_date"
            type="date"
            placeholder="请选择日期"
            style="width: 150px"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            @change="handleDateChange"
          />
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
            @click="handleRefresh"
          >
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            教练排课视图
            <el-tooltip content="按时间段分组展示教练的排课安排">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
          </span>
          <div class="header-actions">
            <el-tag type="primary" size="large">
              {{ formatDateDisplay(queryFormData.schedule_date) }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
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
          </el-row>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading && (!scheduleData || scheduleData.time_slots.length === 0)" class="empty-container">
        <el-empty description="暂无排课安排" :image-size="120">
          <el-button type="primary" @click="handleQuery">刷新数据</el-button>
        </el-empty>
      </div>

      <!-- 排课列表（按时间段分组） -->
      <div v-else class="schedule-list">
        <el-collapse v-model="activeTimeSlots" accordion>
          <el-collapse-item
            v-for="timeSlot in scheduleData?.time_slots || []"
            :key="timeSlot.time_slot_code"
            :name="timeSlot.time_slot_code"
          >
            <template #title>
              <div class="time-slot-header">
                <div class="time-slot-info">
                  <el-tag type="primary" size="large" effect="dark">
                    {{ timeSlot.time_slot_code }} 时段
                  </el-tag>
                  <span class="time-range">{{ timeSlot.start_time }} - {{ timeSlot.end_time }}</span>
                  <el-tag type="info" size="small">
                    共 {{ timeSlot.schedules.length }} 节课
                  </el-tag>
                  <el-tag type="success" size="small">
                    总 {{ getTotalStudents(timeSlot) }} 人
                  </el-tag>
                </div>
              </div>
            </template>

            <!-- 该时间段的所有排课 -->
            <div class="schedule-cards">
              <el-card
                v-for="schedule in timeSlot.schedules"
                :key="schedule.id"
                class="schedule-card"
                shadow="hover"
              >
                <template #header>
                  <div class="schedule-card-header">
                    <div class="schedule-title">
                      <el-tag type="success">{{ schedule.class_name }}</el-tag>
                      <span v-if="schedule.location" class="location">
                        <el-icon><Location /></el-icon>
                        {{ schedule.location }}
                      </span>
                    </div>
                    <div class="schedule-status">
                      <el-tag
                        :type="
                          schedule.schedule_status === 'scheduled'
                            ? 'info'
                            : schedule.schedule_status === 'active'
                              ? 'success'
                              : schedule.schedule_status === 'completed'
                                ? 'warning'
                                : 'danger'
                        "
                        size="small"
                      >
                        {{
                          schedule.schedule_status === 'scheduled'
                            ? '已排课'
                            : schedule.schedule_status === 'active'
                              ? '进行中'
                              : schedule.schedule_status === 'completed'
                                ? '已完成'
                                : '已取消'
                        }}
                      </el-tag>
                    </div>
                  </div>
                </template>

                <!-- 课程主题 -->
                <div v-if="schedule.topic" class="schedule-topic">
                  <strong>主题：</strong>{{ schedule.topic }}
                </div>

                <!-- 内容摘要 -->
                <div v-if="schedule.content_summary" class="schedule-summary">
                  <strong>内容：</strong>{{ schedule.content_summary }}
                </div>

                <!-- 备注 -->
                <div v-if="schedule.notes" class="schedule-notes">
                  <el-icon><InfoFilled /></el-icon>
                  {{ schedule.notes }}
                </div>

                <!-- 学员列表 -->
                <div class="students-section">
                  <div class="students-header">
                    <strong>学员列表</strong>
                    <el-tag type="info" size="small">
                      {{ schedule.student_count }} 人
                    </el-tag>
                    <el-tag v-if="schedule.attendance_count !== undefined" type="success" size="small">
                      已到 {{ schedule.attendance_count }} 人
                    </el-tag>
                  </div>
                  <el-table
                    :data="schedule.students"
                    size="small"
                    border
                    style="margin-top: 10px"
                  >
                    <el-table-column label="姓名" prop="student_name" min-width="100" />
                    <el-table-column label="英文名" prop="english_name" min-width="80" />
                    <el-table-column label="水平" prop="level" min-width="80">
                      <template #default="{ row }">
                        <el-tag size="small" type="warning">{{ row.level || '-' }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="分组" prop="group_name" min-width="80">
                      <template #default="{ row }">
                        <el-tag size="small" type="primary">{{ row.group_name || '-' }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="出勤" min-width="60" align="center">
                      <template #default="{ row }">
                        <el-tag
                          :type="row.has_attended ? 'success' : 'info'"
                          size="small"
                        >
                          {{ row.has_attended ? '已到' : '未到' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-card>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "CoachSchedule",
  inheritAttrs: false,
});

import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { QuestionFilled, Location, InfoFilled } from "@element-plus/icons-vue";
import CoachScheduleAPI, {
  CoachScheduleGroupedData,
  CoachTimeSlotGroup,
  CoachScheduleItem,
} from "@/api/module_badminton/coach-schedule";
import UserAPI from "@/api/module_system/user";
import { useUserStore } from "@/store";

const visible = ref(true);
const queryFormRef = ref();
const loading = ref(false);

// 用户信息
const userStore = useUserStore();
const currentUser = computed(() => userStore.getBasicInfo);

// 是否为教练（角色名称包含"教练"的用户）
const isCoach = computed(() => {
  const roles = currentUser.value.roles || [];
  return roles.some((role: any) => role.name && role.name.includes('教练'));
});

// 是否为管理员（不是教练的用户）
const isAdmin = computed(() => {
  return !isCoach.value;
});

// 教练列表
const coachList = ref<any[]>([]);

// 排课数据
const scheduleData = ref<CoachScheduleGroupedData | null>(null);

// 激活的时间段（用于折叠面板）
const activeTimeSlots = ref<string[]>([]);

// 查询表单
const queryFormData = reactive({
  coach_id: undefined as number | undefined,
  schedule_date: new Date().toISOString().split('T')[0], // 默认今天
});

// 加载教练列表
async function loadCoaches() {
  // 非管理员不加载教练列表
  if (!isAdmin.value) {
    return;
  }

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

// 加载排课数据
async function loadScheduleData() {
  if (!queryFormData.coach_id || !queryFormData.schedule_date) {
    scheduleData.value = null;
    return;
  }

  loading.value = true;
  try {
    const response = await CoachScheduleAPI.getCoachScheduleByDate({
      coach_id: queryFormData.coach_id,
      schedule_date: queryFormData.schedule_date,
    });

    scheduleData.value = response.data.data;

    // 默认展开第一个时间段
    if (scheduleData.value?.time_slots.length > 0) {
      activeTimeSlots.value = [scheduleData.value.time_slots[0].time_slot_code];
    }
  } catch (error: any) {
    console.error("加载排课数据失败:", error);
    ElMessage.error(`加载排课数据失败: ${error.response?.data?.msg || error.message}`);
    scheduleData.value = null;
  } finally {
    loading.value = false;
  }
}

// 教练切换处理
function handleCoachChange() {
  if (queryFormData.coach_id) {
    loadScheduleData();
  }
}

// 查询
function handleQuery() {
  loadScheduleData();
}

// 刷新
function handleRefresh() {
  loadScheduleData();
}

// 日期变化
function handleDateChange() {
  loadScheduleData();
}

// 计算时间段的总人数
function getTotalStudents(timeSlot: CoachTimeSlotGroup): number {
  return timeSlot.schedules.reduce((total, schedule) => {
    return total + (schedule.student_count || 0);
  }, 0);
}

// 格式化日期显示
function formatDateDisplay(dateStr: string): string {
  if (!dateStr) return '请选择日期';
  try {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return '今天';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return '昨天';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return '明天';
    } else {
      const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      const dayOfWeek = days[date.getDay()];
      const month = date.getMonth() + 1;
      const day = date.getDate();
      return `${month}月${day}日 ${dayOfWeek}`;
    }
  } catch {
    return dateStr;
  }
}

// 禁用日期（禁用未来日期）
function disabledDate(time: Date) {
  const date = new Date(time);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date > today;
}

// 页面加载时初始化
onMounted(async () => {
  // 加载教练列表
  await loadCoaches();

  // 如果是教练，自动选择当前用户
  if (!isAdmin.value && currentUser.value.id) {
    queryFormData.coach_id = currentUser.value.id;
  } else if (coachList.value.length > 0) {
    // 如果是管理员，默认选择第一个教练
    queryFormData.coach_id = coachList.value[0].id;
  }

  // 加载排课数据
  loadScheduleData();
});
</script>

<style scoped>
.data-table {
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 40px 0;
}

.empty-container {
  padding: 60px 0;
  text-align: center;
}

.schedule-list {
  padding: 10px 0;
}

.time-slot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.time-slot-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-range {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.schedule-cards {
  padding: 15px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.schedule-card {
  margin-bottom: 0;
}

.schedule-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.schedule-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.schedule-status {
  display: flex;
  align-items: center;
}

.schedule-topic {
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
}

.schedule-summary {
  margin-bottom: 10px;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.schedule-notes {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #606266;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.students-section {
  margin-top: 15px;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.students-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

/* 折叠面板样式优化 */
:deep(.el-collapse-item__header) {
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 12px 16px;
  margin-bottom: 10px;
  color: var(--el-text-color-primary);
}

:deep(.el-collapse-item__header:hover) {
  background-color: var(--el-fill-color);
}

:deep(.el-collapse-item__wrap) {
  border-radius: 4px;
  border: none;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 10px;
}

/* 教练名称显示样式（非管理员） */
.coach-name-display {
  width: 200px;
  padding: 8px 12px;
  background-color: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

/* 时间范围文字颜色适配 */
.time-range {
  color: var(--el-text-color-regular);
}

/* 备注区域背景色适配 */
.schedule-notes {
  background-color: var(--el-fill-color-lighter);
}

/* 学员列表上边框颜色适配 */
.students-section {
  border-top-color: var(--el-border-color-lighter);
}
</style>