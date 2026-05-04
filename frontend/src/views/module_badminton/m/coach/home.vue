<template>
  <div class="coach-home">
    <div class="greeting">
      <div class="greeting-text">{{ greeting }}</div>
      <div class="date-text">{{ todayStr }}</div>
    </div>

    <van-loading v-if="loading" size="24px" class="loading" />

    <template v-else>
      <div class="today-summary">
        <div class="summary-item">
          <span class="num">{{ scheduleCount }}</span>
          <span class="label">今日课程</span>
        </div>
        <div class="summary-item">
          <span class="num">{{ totalStudents }}</span>
          <span class="label">学员</span>
        </div>
      </div>

      <div v-if="nextClass" class="next-class-card">
        <div class="card-label">下一节课</div>
        <div class="card-class">{{ nextClass.class_name }}</div>
        <div class="card-time">{{ nextClass.time_range }}</div>
        <div v-if="nextClass.location" class="card-location">{{ nextClass.location }}</div>
      </div>

      <div class="quick-actions">
        <div class="section-title">快捷操作</div>
        <div class="action-grid">
          <div class="action-item" @click="router.push('/m/badminton/coach/attendance')">
            <van-icon name="records" size="28" color="#07c160" />
            <span>点名签到</span>
          </div>
          <div class="action-item" @click="router.push('/m/badminton/coach/schedule')">
            <van-icon name="calendar-o" size="28" color="#1989fa" />
            <span>我的课表</span>
          </div>
          <div class="action-item" @click="router.push('/m/badminton/coach/tournament-list')">
            <van-icon name="flag-o" size="28" color="#ee0a24" />
            <span>比赛管理</span>
          </div>
          <div class="action-item" @click="router.push('/m/badminton/coach/assessment')">
            <van-icon name="chart-trending-o" size="28" color="#ff976a" />
            <span>能力评估</span>
          </div>
        </div>
      </div>

      <van-button round block type="danger" class="logout-btn" @click="onLogout">
        退出登录
      </van-button>
    </template>

    <van-dialog
      v-model:show="showLogoutDialog"
      title=""
      :show-confirm-button="false"
      class="logout-dialog"
    >
      <div class="logout-body">
        <van-icon name="info-o" class="logout-icon" />
        <div class="logout-title">退出登录</div>
        <div class="logout-desc">确定要退出当前账号吗？</div>
      </div>
      <div class="logout-footer">
        <van-button round block @click="showLogoutDialog = false">取消</van-button>
        <van-button round block type="danger" style="margin-top: 10px" @click="confirmLogout">
          退出
        </van-button>
      </div>
    </van-dialog>
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

const loading = ref(false);
const scheduleCount = ref(0);
const totalStudents = ref(0);
const nextClass = ref<{ class_name: string; time_range: string; location?: string } | null>(null);

function formatDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function getGreeting(): string {
  const hour = new Date().getHours();
  const name = currentUser.value.name || "";
  if (hour < 6) return `${name}，夜深了`;
  if (hour < 9) return `${name}，早上好`;
  if (hour < 12) return `${name}，上午好`;
  if (hour < 14) return `${name}，中午好`;
  if (hour < 18) return `${name}，下午好`;
  return `${name}，晚上好`;
}

const greeting = ref("");
const todayStr = ref("");
const showLogoutDialog = ref(false);

function onLogout() {
  showLogoutDialog.value = true;
}

async function confirmLogout() {
  showLogoutDialog.value = false;
  await userStore.logout();
  router.replace("/login");
}

function updateTime() {
  const now = new Date();
  const weekDays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  greeting.value = getGreeting();
  todayStr.value = `${now.getMonth() + 1}月${now.getDate()}日 ${weekDays[now.getDay()]}`;
}

async function loadData() {
  const coachId = currentUser.value.id;
  if (!coachId) return;

  loading.value = true;
  try {
    const res = await CoachScheduleAPI.getCoachScheduleByDate({
      coach_id: coachId,
      schedule_date: formatDate(new Date()),
    });
    const data = res.data.data;
    if (!data?.time_slots) {
      loading.value = false;
      return;
    }

    let count = 0;
    let students = 0;
    let earliest: { class_name: string; time_range: string; location?: string } | null = null;
    let earliestTime = "";

    for (const slot of data.time_slots) {
      for (const s of slot.schedules) {
        count++;
        students += s.student_count || 0;
        const timeRange = `${slot.start_time}-${slot.end_time}`;
        if (!earliest || slot.start_time < earliestTime) {
          earliest = { class_name: s.class_name, time_range: timeRange, location: s.location };
          earliestTime = slot.start_time;
        }
      }
    }

    scheduleCount.value = count;
    totalStudents.value = students;
    nextClass.value = earliest;
  } catch {
    // silent
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  updateTime();
  loadData();
});
</script>

<style scoped>
.coach-home {
  padding-bottom: 24px;
}

.greeting {
  padding: 24px 0 16px;
}

.greeting-text {
  font-size: 22px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.date-text {
  margin-top: 4px;
  font-size: 14px;
  color: var(--mobile-text-muted);
}

.loading {
  margin-top: 60px;
}

.today-summary {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.summary-item {
  flex: 1;
  padding: 16px;
  text-align: center;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}

.summary-item .num {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--mobile-text-primary);
}

.summary-item .label {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: var(--mobile-text-muted);
}

.next-class-card {
  padding: 16px;
  margin-bottom: 20px;
  color: #fff;
  background: var(--mobile-gradient-green);
  border-radius: 10px;
}

.card-label {
  font-size: 12px;
  opacity: 0.8;
}

.card-class {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 600;
}

.card-time {
  margin-top: 4px;
  font-size: 14px;
  opacity: 0.9;
}

.card-location {
  margin-top: 2px;
  font-size: 13px;
  opacity: 0.8;
}

.section-title {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.action-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  padding: 16px 8px;
  cursor: pointer;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}

.action-item span {
  font-size: 12px;
  color: var(--mobile-text-secondary);
}

.logout-btn {
  margin-top: 24px;
}

.logout-body {
  padding: 32px 24px 24px;
  text-align: center;
}

.logout-icon {
  font-size: 48px;
  color: var(--van-danger-color, #ee0a24);
}

.logout-title {
  margin-top: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.logout-desc {
  margin-top: 8px;
  font-size: 14px;
  color: var(--mobile-text-muted);
}

.logout-footer {
  padding: 0 24px 24px;
}

.logout-dialog {
  :deep(.van-dialog__content) {
    padding: 0;
  }
}
</style>
