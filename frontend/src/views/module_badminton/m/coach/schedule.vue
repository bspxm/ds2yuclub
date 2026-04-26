<template>
  <div class="schedule-page">
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
      <div v-for="slot in schedules" :key="slot.time_slot_code" class="time-slot-group">
        <div class="time-slot-header">
          <van-tag type="primary" round>{{ slot.time_slot_code }}</van-tag>
          <span class="time-range">{{ slot.start_time }} - {{ slot.end_time }}</span>
          <span class="count">{{ slot.schedules.length }}节课 · {{ totalStudents(slot) }}人</span>
        </div>

        <div
          v-for="s in slot.schedules"
          :key="s.id"
          class="schedule-card"
          @click="router.push(`/m/badminton/coach/attendance?date=${formatDate(selectedDate)}`)"
        >
          <van-cell-group inset>
            <van-cell>
              <template #title>
                <span class="class-name">{{ s.class_name }}</span>
              </template>
              <template #label>
                <span>{{ slot.start_time }}-{{ slot.end_time }}</span>
                <span v-if="s.location" class="location-label">{{ s.location }}</span>
              </template>
              <template #value>
                <van-tag
                  :type="
                    s.schedule_status === 'active'
                      ? 'success'
                      : s.schedule_status === 'completed'
                        ? 'warning'
                        : 'primary'
                  "
                >
                  {{
                    s.schedule_status === "scheduled"
                      ? "待上课"
                      : s.schedule_status === "active"
                        ? "进行中"
                        : "已结束"
                  }}
                </van-tag>
              </template>
            </van-cell>
            <van-cell v-if="s.students && s.students.length > 0">
              <template #title>
                <van-space>
                  <span
                    v-for="stu in s.students.slice(0, 8)"
                    :key="stu.student_id"
                    class="student-tag"
                  >
                    {{ stu.student_name }}
                  </span>
                  <span v-if="s.students.length > 8" class="more-students">
                    +{{ s.students.length - 8 }}
                  </span>
                </van-space>
              </template>
            </van-cell>
          </van-cell-group>
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
import { useRouter } from "vue-router";
import { useUserStore } from "@/store";
import CoachScheduleAPI from "@/api/module_badminton/coach-schedule";

const router = useRouter();
const userStore = useUserStore();
const currentUser = computed(() => userStore.getBasicInfo);

const selectedDate = ref(new Date());
const showDatePicker = ref(false);
const loading = ref(false);

const minDate = new Date(2020, 0, 1);
const maxDate = new Date();
const defaultDate = new Date();

interface TimeSlot {
  time_slot_code: string;
  time_slot_name: string;
  start_time: string;
  end_time: string;
  schedules: any[];
}

const schedules = ref<TimeSlot[]>([]);

function formatDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function totalStudents(slot: TimeSlot): number {
  return slot.schedules.reduce((sum: number, s: any) => sum + (s.student_count || 0), 0);
}

function onDateConfirm({ selectedValues }: { selectedValues: number[] }) {
  const [year, month, day] = selectedValues;
  selectedDate.value = new Date(year, month - 1, day);
  showDatePicker.value = false;
  loadData();
}

async function loadData() {
  const coachId = currentUser.value.id;
  if (!coachId) return;

  loading.value = true;
  try {
    const res = await CoachScheduleAPI.getCoachScheduleByDate({
      coach_id: coachId,
      schedule_date: formatDate(selectedDate.value),
    });
    schedules.value = res.data.data?.time_slots || [];
  } catch {
    schedules.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.schedule-page {
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.time-slot-group {
  margin-bottom: 16px;
}

.time-slot-header {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 12px 16px 8px;
  font-size: 13px;
}

.time-range {
  color: var(--mobile-text-secondary);
}

.count {
  margin-left: auto;
  font-size: 12px;
  color: var(--mobile-text-muted);
}

.schedule-card {
  margin-top: 8px;
}

.class-name {
  font-weight: 600;
}

.location-label {
  margin-left: 8px;
  font-size: 12px;
  color: var(--mobile-text-muted);
}

.student-tag {
  display: inline-block;
  padding: 2px 8px;
  margin: 2px 4px 2px 0;
  font-size: 12px;
  color: var(--mobile-text-primary);
  background: var(--mobile-blue-bg);
  border-radius: 4px;
}

.more-students {
  font-size: 12px;
  color: var(--mobile-text-muted);
}
</style>
