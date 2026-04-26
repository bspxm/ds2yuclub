<template>
  <div class="attendance-page">
    <van-cell-group inset>
      <van-cell
        title="选择日期"
        :label="formatDate(selectedDate)"
        is-link
        @click="showDatePicker = true"
      />
    </van-cell-group>

    <van-loading v-if="loading" size="24px" class="loading" />

    <template v-else-if="schedules.length === 0">
      <van-empty description="当天无排课" />
    </template>

    <template v-else>
      <div v-for="schedule in schedules" :key="schedule.id" class="schedule-card">
        <van-cell-group inset>
          <van-cell>
            <template #title>
              <span class="class-name">{{ schedule.class_name }}</span>
              <van-tag v-if="schedule.location" plain type="primary">
                {{ schedule.location }}
              </van-tag>
            </template>
            <template #label>
              <span>{{ schedule.time_range }}</span>
              <span v-if="schedule.attendance_count !== undefined" class="attendance-count">
                已签到 {{ schedule.attendance_count }}/{{ schedule.students.length }}
              </span>
            </template>
          </van-cell>
        </van-cell-group>

        <div class="student-list">
          <div
            v-for="student in schedule.students"
            :key="student.student_id"
            class="student-row"
            :class="{ absent: getAttendanceStatus(student) === 'ABSENT' }"
          >
            <div class="student-info">
              <span class="name">{{ student.student_name }}</span>
              <span v-if="student.level" class="level">{{ student.level }}</span>
            </div>
            <div class="status-buttons">
              <van-button
                :type="getAttendanceStatus(student) === 'PRESENT' ? 'success' : 'default'"
                size="small"
                round
                @click="setStudentStatus(schedule.id, student.student_id, 'PRESENT')"
              >
                出勤
              </van-button>
              <van-button
                :type="getAttendanceStatus(student) === 'ABSENT' ? 'danger' : 'default'"
                size="small"
                round
                @click="setStudentStatus(schedule.id, student.student_id, 'ABSENT')"
              >
                缺勤
              </van-button>
              <van-button
                :type="getAttendanceStatus(student) === 'LEAVE' ? 'warning' : 'default'"
                size="small"
                round
                @click="setStudentStatus(schedule.id, student.student_id, 'LEAVE')"
              >
                请假
              </van-button>
            </div>
          </div>
        </div>

        <div style="padding: 8px 16px 16px">
          <van-button
            type="primary"
            block
            round
            :loading="saving === schedule.id"
            @click="handleSave(schedule)"
          >
            保存
          </van-button>
        </div>
      </div>
    </template>

    <van-action-sheet v-model:show="showDatePicker" title="选择日期">
      <van-date-picker
        :min-date="minDate"
        :max-date="maxDate"
        :default-date="defaultDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { showToast } from "vant";
import { useUserStore } from "@/store";
import CoachScheduleAPI from "@/api/module_badminton/coach-schedule";
import ClassAttendanceAPI from "@/api/module_badminton/class-attendance";

const userStore = useUserStore();
const currentUser = computed(() => userStore.getBasicInfo);

const selectedDate = ref(new Date());
const showDatePicker = ref(false);
const loading = ref(false);
const saving = ref<number | null>(null);

const minDate = new Date(2020, 0, 1);
const maxDate = new Date();
const defaultDate = new Date();

interface ScheduleDisplay {
  id: number;
  class_id: number;
  class_name: string;
  location?: string;
  time_range: string;
  student_count: number;
  attendance_count?: number;
  start_time: string;
  end_time: string;
  students: StudentDisplay[];
}

interface StudentDisplay {
  student_id: number;
  student_name: string;
  english_name?: string;
  level?: string;
  has_attended?: boolean;
  attendance_status?: string;
}

const schedules = ref<ScheduleDisplay[]>([]);
const statusMap = ref<Record<string, Record<number, string>>>({});

function formatDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function getScheduleKey(scheduleId: number): string {
  return `schedule_${scheduleId}`;
}

function getAttendanceStatus(student: StudentDisplay): string {
  const map = statusMap.value[getScheduleKey(0)];
  if (map && map[student.student_id]) {
    return map[student.student_id];
  }
  if (student.attendance_status) {
    return student.attendance_status;
  }
  return "";
}

function setStudentStatus(scheduleId: number, studentId: number, status: string) {
  if (!statusMap.value[getScheduleKey(scheduleId)]) {
    statusMap.value[getScheduleKey(scheduleId)] = {};
  }
  statusMap.value[getScheduleKey(scheduleId)][studentId] = status;
}

function onDateConfirm({ selectedValues }: { selectedValues: number[] }) {
  const [year, month, day] = selectedValues;
  selectedDate.value = new Date(year, month - 1, day);
  showDatePicker.value = false;
  loadData();
}

async function loadData() {
  const coachId = currentUser.value.id;
  if (!coachId) {
    showToast("未获取到教练信息");
    return;
  }

  loading.value = true;
  try {
    const dateStr = formatDate(selectedDate.value);
    const res = await CoachScheduleAPI.getCoachScheduleByDate({
      coach_id: coachId,
      schedule_date: dateStr,
    });

    const data = res.data.data;
    if (!data?.time_slots) {
      schedules.value = [];
      return;
    }

    const result: ScheduleDisplay[] = [];
    statusMap.value = {};

    for (const slot of data.time_slots) {
      for (const s of slot.schedules) {
        const students: StudentDisplay[] = (s.students || []).map((stu: any) => ({
          student_id: stu.student_id,
          student_name: stu.student_name,
          english_name: stu.english_name,
          level: stu.level,
          has_attended: stu.has_attended,
          attendance_status: stu.attendance_status || (stu.has_attended ? "PRESENT" : ""),
        }));

        result.push({
          id: s.id,
          class_id: s.class_id,
          class_name: s.class_name,
          location: s.location,
          time_range: `${slot.start_time}-${slot.end_time}`,
          student_count: s.student_count,
          attendance_count: s.attendance_count,
          start_time: slot.start_time,
          end_time: slot.end_time,
          students,
        });
      }
    }

    schedules.value = result;
  } catch (e: any) {
    showToast(e.response?.data?.msg || "加载失败");
  } finally {
    loading.value = false;
  }
}

async function handleSave(schedule: ScheduleDisplay) {
  saving.value = schedule.id;
  try {
    const dateStr = formatDate(selectedDate.value);
    const scheduleMap = statusMap.value[getScheduleKey(schedule.id)] || {};

    for (const student of schedule.students) {
      const status = scheduleMap[student.student_id] || (student.has_attended ? "PRESENT" : "");

      if (!status) continue;

      if (student.has_attended) {
        const res = await ClassAttendanceAPI.getClassAttendanceList({
          schedule_id: schedule.id,
          student_id: student.student_id,
          page_no: 1,
          page_size: 1,
        });
        const items = res.data.data?.items || [];
        if (items.length > 0 && items[0].id) {
          await ClassAttendanceAPI.updateClassAttendance(items[0].id, {
            attendance_status: status,
            attendance_date: dateStr,
          });
        }
      } else {
        await ClassAttendanceAPI.createClassAttendance({
          student_id: student.student_id,
          class_id: schedule.class_id,
          schedule_id: schedule.id,
          attendance_date: dateStr,
          attendance_status: status,
        });
      }
    }

    showToast("保存成功");
    await loadData();
  } catch (e: any) {
    showToast(e.response?.data?.msg || "保存失败");
  } finally {
    saving.value = null;
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.attendance-page {
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.schedule-card {
  margin-top: 12px;
}

.class-name {
  margin-right: 8px;
  font-weight: 600;
}

.attendance-count {
  margin-left: 12px;
  font-size: 12px;
  color: var(--mobile-text-muted);
}

.student-list {
  margin: 0 16px;
  overflow: hidden;
  border: 1px solid var(--mobile-border);
  border-radius: 8px;
}

.student-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--mobile-border-light);
}

.student-row:last-child {
  border-bottom: none;
}

.student-row.absent {
  background: var(--mobile-red-bg);
}

.student-info {
  display: flex;
  gap: 6px;
  align-items: center;
}

.name {
  font-size: 14px;
  font-weight: 500;
  color: var(--mobile-text-primary);
}

.level {
  padding: 1px 6px;
  font-size: 11px;
  color: var(--mobile-text-muted);
  background: var(--mobile-gray-bg);
  border-radius: 4px;
}

.status-buttons {
  display: flex;
  gap: 6px;
}
</style>
