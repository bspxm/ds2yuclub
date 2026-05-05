<template>
  <div class="attendance-page">
    <div class="date-header">{{ formatDate(selectedDate) }}</div>

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
            :class="{ absent: getAttendanceStatus(schedule.id, student) === 'absent' }"
          >
            <div class="student-info">
              <span class="name">{{ student.student_name }}</span>
              <span v-if="student.level" class="level">{{ student.level }}</span>
            </div>
            <div class="status-buttons">
              <van-button
                :type="
                  getAttendanceStatus(schedule.id, student) === 'present' ? 'success' : 'default'
                "
                size="small"
                round
                @click="setStudentStatus(schedule.id, student.student_id, 'present')"
              >
                出勤
              </van-button>
              <van-button
                :type="
                  getAttendanceStatus(schedule.id, student) === 'absent' ? 'danger' : 'default'
                "
                size="small"
                round
                @click="setStudentStatus(schedule.id, student.student_id, 'absent')"
              >
                缺勤
              </van-button>
              <van-button
                :type="
                  getAttendanceStatus(schedule.id, student) === 'leave' ? 'warning' : 'default'
                "
                size="small"
                round
                @click="setStudentStatus(schedule.id, student.student_id, 'leave')"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { showToast } from "vant";
import { useUserStore } from "@/store";
import CoachScheduleAPI from "@/api/module_badminton/coach-schedule";
import ClassAttendanceAPI from "@/api/module_badminton/class-attendance";

const route = useRoute();
const userStore = useUserStore();
const currentUser = computed(() => userStore.getBasicInfo);

function parseDateParam(dateStr: string | string[] | undefined): Date {
  if (typeof dateStr === "string" && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    const [y, m, d] = dateStr.split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  return new Date();
}

const selectedDate = ref(parseDateParam(route.query.date));
const loading = ref(false);
const saving = ref<number | null>(null);

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

function getAttendanceStatus(scheduleId: number, student: StudentDisplay): string {
  const map = statusMap.value[getScheduleKey(scheduleId)];
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
          attendance_status: stu.attendance_status || (stu.has_attended ? "present" : ""),
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

    // 1. 一次性查出该排课的所有现有考勤记录
    const res = await ClassAttendanceAPI.getClassAttendanceList({
      schedule_id: schedule.id,
      page_no: 1,
      page_size: 100,
    });
    const existingItems = res.data.data?.items || [];
    const existingMap = new Map<number, number>(); // student_id -> attendance_id
    for (const item of existingItems) {
      if (item.student_id && item.id) {
        existingMap.set(item.student_id, item.id);
      }
    }

    // 2. 并行执行所有创建/更新
    const promises: Promise<any>[] = [];
    for (const student of schedule.students) {
      const status = scheduleMap[student.student_id] || (student.has_attended ? "present" : "");
      if (!status) continue;

      const attendanceId = existingMap.get(student.student_id);
      if (attendanceId) {
        promises.push(
          ClassAttendanceAPI.updateClassAttendance(attendanceId, {
            attendance_status: status,
            attendance_date: dateStr,
          })
        );
      } else {
        promises.push(
          ClassAttendanceAPI.createClassAttendance({
            student_id: student.student_id,
            class_id: schedule.class_id,
            schedule_id: schedule.id,
            attendance_date: dateStr,
            attendance_status: status,
          })
        );
      }
    }

    await Promise.all(promises);
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

.date-header {
  padding: 16px 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
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
