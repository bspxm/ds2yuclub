<template>
  <div class="parent-student-page">
    <van-loading v-if="loading" size="24px" class="loading-center" />

    <template v-else-if="students.length === 0">
      <van-empty v-if="matchLoading" description="检测中..." />
      <template v-else-if="matchedStudents.length > 0">
        <van-cell-group inset title="发现以下学员与您的手机号匹配">
          <van-cell v-for="m in matchedStudents" :key="m.id">
            <template #title>{{ m.name }}</template>
            <template #label>{{ m.level || "未评估" }} · {{ m.group_name || "未分组" }}</template>
            <template #value>
              <van-button
                size="small"
                type="primary"
                :loading="bindLoading === m.id"
                @click="onBind(m.id)"
              >
                绑定
              </van-button>
            </template>
          </van-cell>
        </van-cell-group>
      </template>
      <van-empty v-else description="暂无关联学员，且未找到手机号匹配的学员" />
      <div style="padding: 24px 16px">
        <van-button round block type="danger" @click="onLogout">退出登录</van-button>
      </div>
    </template>

    <template v-else>
      <!-- 学员切换 -->
      <van-sticky>
        <van-tabs v-model:active="activeIndex" @change="onStudentChange">
          <van-tab v-for="s in students" :key="s.student.id" :title="s.student.name" />
        </van-tabs>
      </van-sticky>

      <div v-if="student" class="content">
        <!-- 基本信息卡片 -->
        <van-cell-group inset title="基本信息">
          <van-cell title="姓名" :value="student.name" />
          <van-cell title="英文名" :value="student.english_name || '无'" />
          <van-cell title="技术水平" :value="student.level || '未评估'" />
          <van-cell title="组别" :value="student.group_name || '未分组'" />
        </van-cell-group>

        <!-- 考勤概览 -->
        <van-cell-group inset title="考勤情况">
          <van-row class="att-stats">
            <van-col span="8" class="att-stat-item">
              <div class="stat-value">{{ attendanceStats.total }}</div>
              <div class="stat-label">总出勤</div>
            </van-col>
            <van-col span="8" class="att-stat-item">
              <div class="stat-value text-green">{{ attendanceStats.present }}</div>
              <div class="stat-label">已出勤</div>
            </van-col>
            <van-col span="8" class="att-stat-item">
              <div class="stat-value text-orange">{{ attendanceStats.monthly }}</div>
              <div class="stat-label">本月</div>
            </van-col>
          </van-row>
          <van-cell
            v-for="c in recentCourses"
            :key="c.id"
            :title="c.class_name || '课程'"
            :label="c.schedule_date"
          >
            <template #value>
              <van-tag :type="attendanceTagType(c.attendance_status)" size="small">
                {{ attendanceText(c.attendance_status) }}
              </van-tag>
            </template>
          </van-cell>
          <van-empty
            v-if="recentCourses.length === 0"
            :description="attLoading ? '加载中...' : '暂无课程记录'"
          />
        </van-cell-group>

        <!-- 赛事信息 -->
        <van-cell-group inset title="赛事信息">
          <van-cell v-for="t in activeTournaments" :key="t.id" @click="onTournamentClick(t)">
            <template #title>
              <span>{{ t.tournament_name }}</span>
              <van-tag
                :type="tournamentTagType(t.tournament_status)"
                size="small"
                style="margin-left: 6px"
              >
                {{ tournamentStatusText(t.tournament_status) }}
              </van-tag>
            </template>
            <template #label>
              {{ t.start_date }}~{{ t.end_date }}
              <span v-if="t.final_rank" style="margin-left: 8px; color: var(--van-orange)">
                第{{ t.final_rank }}名
              </span>
            </template>
            <template #value>
              <span v-if="t.matches_played > 0" class="record-text">
                {{ t.matches_won }}W / {{ t.matches_lost }}L
              </span>
            </template>
          </van-cell>
          <van-empty v-if="activeTournaments.length === 0" description="暂无进行中的赛事" />
          <van-cell title="查看历史赛事" is-link @click="goHistory" />
        </van-cell-group>

        <!-- 能力评估 -->
        <van-cell-group inset title="学员评价">
          <template v-if="latestAssessment">
            <div ref="radarRef" class="radar-chart-inline" />
            <van-cell title="综合评分">
              <template #value>
                <span class="score-badge">
                  {{ (latestAssessment.overall_score ?? 0).toFixed(1) }}
                </span>
                <span class="text-muted" style="margin-left: 6px">
                  {{ formatDate(latestAssessment.assessment_date) }}
                </span>
              </template>
            </van-cell>
            <van-cell
              v-for="(h, i) in assessmentHistory"
              :key="i"
              is-link
              :title="`第${assessmentHistory.length - i}次`"
              @click="openHistory(i)"
            >
              <template #label>{{ formatDate(h.assessment_date) }}</template>
              <template #value>
                <span class="score-badge-sm">{{ (h.overall_score ?? 0).toFixed(1) }}</span>
              </template>
            </van-cell>
          </template>
          <van-cell v-else title="暂无评估数据" />
        </van-cell-group>
      </div>

      <div style="padding: 24px 16px">
        <van-button round block type="danger" @click="onLogout">退出登录</van-button>
      </div>
    </template>

    <!-- 赛事详情弹窗 -->
    <van-action-sheet
      v-model:show="showTournamentDetail"
      :title="selectedTournament?.tournament_name"
    >
      <div v-if="selectedTournament" class="tournament-detail">
        <van-cell-group>
          <van-cell
            title="状态"
            :value="tournamentStatusText(selectedTournament.tournament_status)"
          />
          <van-cell
            title="日期"
            :value="`${selectedTournament.start_date} ~ ${selectedTournament.end_date}`"
          />
          <van-cell
            v-if="selectedTournament.final_rank"
            title="最终排名"
            :value="`第${selectedTournament.final_rank}名`"
          />
          <van-cell title="参赛场次" :value="selectedTournament.matches_played" />
          <van-cell
            title="胜/负"
            :value="`${selectedTournament.matches_won} / ${selectedTournament.matches_lost}`"
          />
        </van-cell-group>
      </div>
    </van-action-sheet>

    <!-- 历史评估查看器 -->
    <van-action-sheet v-model:show="showHistoryViewer" title="历史评估">
      <div v-if="viewingAssessment" class="history-viewer">
        <div ref="historyRadarRef" class="radar-chart-inline" />
        <div class="history-nav">
          <van-button
            :disabled="historyIndex >= assessmentHistory.length - 1"
            icon="arrow-left"
            size="small"
            @click="historyNav(-1)"
          />
          <span class="history-nav-title">
            第{{ assessmentHistory.length - historyIndex }}次评估
            <span class="text-muted">({{ formatDate(viewingAssessment.assessment_date) }})</span>
          </span>
          <van-button
            :disabled="historyIndex <= 0"
            icon="arrow-right"
            size="small"
            @click="historyNav(1)"
          />
        </div>
        <div class="history-score">
          综合评分:
          <span class="score-badge">{{ (viewingAssessment.overall_score ?? 0).toFixed(1) }}</span>
        </div>
      </div>
    </van-action-sheet>

    <!-- 退出登录确认 -->
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
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from "vue";
import { showToast } from "vant";
import { useUserStore } from "@/store";
import router from "@/router";
import * as echarts from "echarts/core";
import { RadarChart } from "echarts/charts";
import { TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import ParentStudentAPI from "@/api/module_badminton/parent-student";

echarts.use([RadarChart, TooltipComponent, CanvasRenderer]);

interface StudentDisplay {
  id: number;
  name: string;
  english_name?: string;
  level?: string;
  group_name?: string;
}

const loading = ref(false);
const attLoading = ref(false);
const matchLoading = ref(false);
const students = ref<any[]>([]);
const activeIndex = ref(0);
const student = ref<StudentDisplay | null>(null);
const attendanceStats = ref({ total: 0, present: 0, monthly: 0 });
const recentCourses = ref<any[]>([]);
const tournaments = ref<any[]>([]);
const latestAssessment = ref<any>(null);
const assessmentHistory = ref<any[]>([]);
const activeTournaments = computed(() =>
  tournaments.value.filter((t: any) => t.tournament_status === "ACTIVE")
);
const showTournamentDetail = ref(false);
const selectedTournament = ref<any>(null);
const showLogoutDialog = ref(false);
const matchedStudents = ref<any[]>([]);
const bindLoading = ref<number | null>(null);
const radarRef = ref<HTMLElement | null>(null);
let radarInstance: echarts.ECharts | null = null;
const showHistoryViewer = ref(false);
const historyIndex = ref(0);
const historyRadarRef = ref<HTMLElement | null>(null);
let historyRadarInstance: echarts.ECharts | null = null;

const viewingAssessment = computed(() => {
  if (historyIndex.value < 0 || historyIndex.value >= assessmentHistory.value.length) return null;
  return assessmentHistory.value[historyIndex.value];
});

const dimensions = [
  { key: "technique", label: "技术" },
  { key: "footwork", label: "步伐" },
  { key: "tactics", label: "战术" },
  { key: "power", label: "力量" },
  { key: "speed", label: "速度" },
  { key: "stamina", label: "耐力" },
  { key: "offense", label: "进攻" },
  { key: "defense", label: "防守" },
  { key: "mental", label: "心理" },
];

function initRadar() {
  if (!radarRef.value || !latestAssessment.value) return;
  if (radarInstance) radarInstance.dispose();
  radarInstance = echarts.init(radarRef.value);
  const indicators = dimensions.map((d) => ({
    name: d.label,
    max: 5,
  }));
  const value = dimensions.map((d) => latestAssessment.value[d.key] ?? 0);
  radarInstance.setOption({
    radar: {
      indicator: indicators,
      center: ["50%", "50%"],
      radius: "70%",
      axisName: { color: "#333", fontSize: 11 },
      splitArea: { areaStyle: { color: ["rgba(245,158,11,0.02)", "rgba(245,158,11,0.06)"] } },
    },
    series: [
      {
        type: "radar",
        data: [
          {
            value,
            name: "能力评估",
            areaStyle: { color: "rgba(245,158,11,0.2)" },
            lineStyle: { color: "#f59e0b", width: 2 },
            itemStyle: { color: "#f59e0b" },
          },
        ],
      },
    ],
  });
}

watch(latestAssessment, (val) => {
  if (val) {
    nextTick(() => setTimeout(() => initRadar(), 50));
  }
});

onBeforeUnmount(() => {
  radarInstance?.dispose();
  historyRadarInstance?.dispose();
});

function formatDate(d: string) {
  if (!d) return "";
  return d.split("T")[0];
}

function attendanceTagType(status: string) {
  const map: Record<string, string> = { PRESENT: "success", ABSENT: "danger", LEAVE: "warning" };
  return map[status] || "default";
}

function attendanceText(status: string) {
  const map: Record<string, string> = { PRESENT: "已出勤", ABSENT: "缺勤", LEAVE: "请假" };
  return map[status] || "未记录";
}

function tournamentStatusText(status: string) {
  const map: Record<string, string> = { DRAFT: "草稿", ACTIVE: "进行中", COMPLETED: "已结束" };
  return map[status] || status;
}

function tournamentTagType(status: string) {
  const map: Record<string, string> = { ACTIVE: "primary", COMPLETED: "success" };
  return map[status] || "default";
}

async function loadStudentData(sid: number) {
  attLoading.value = true;
  try {
    const [attStu, assessStu, tournStu, histStu] = await Promise.all([
      ParentStudentAPI.getMyStudentAttendances(sid).catch(() => ({ data: { data: [] } })),
      ParentStudentAPI.getMyStudentLatestAssessment(sid).catch(() => ({ data: { data: null } })),
      ParentStudentAPI.getMyStudentTournaments(sid).catch(() => ({ data: { data: [] } })),
      ParentStudentAPI.getMyStudentAssessmentHistory(sid).catch(() => ({ data: { data: [] } })),
    ]);

    const attList = attStu.data.data || [];
    const now = new Date();
    attendanceStats.value = {
      total: attList.length,
      present: attList.filter((a: any) => a.attendance_status === "PRESENT").length,
      monthly: attList.filter((a: any) => {
        const d = new Date(a.attendance_date);
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
      }).length,
    };
    recentCourses.value = attList.slice(-5).reverse();
    latestAssessment.value = assessStu.data.data;
    assessmentHistory.value = histStu.data.data || [];
    tournaments.value = tournStu.data.data || [];
  } catch {
    showToast("加载数据失败");
  } finally {
    attLoading.value = false;
  }
}

function onStudentChange() {
  const rel = students.value[activeIndex.value];
  if (!rel) return;
  const s = rel.student;
  student.value = {
    id: s.id,
    name: s.name || "",
    english_name: s.english_name,
    level: s.level,
    group_name: s.group_name,
  };
  loadStudentData(s.id);
}

function goHistory() {
  const sid = student.value?.id;
  if (sid) {
    router.push(`/m/badminton/parent/tournament-history?student_id=${sid}`);
  }
}

function onTournamentClick(t: any) {
  selectedTournament.value = t;
  showTournamentDetail.value = true;
}

async function onBind(studentId: number) {
  bindLoading.value = studentId;
  try {
    await ParentStudentAPI.selfBind(studentId);
    showToast("绑定成功");
    matchedStudents.value = matchedStudents.value.filter((m) => m.id !== studentId);
    if (students.value.length === 0) {
      await loadStudentList();
    }
  } catch {
    showToast("绑定失败，请稍后重试");
  } finally {
    bindLoading.value = null;
  }
}

async function loadStudentList() {
  try {
    const res = await ParentStudentAPI.getMyStudents();
    students.value = res.data.data || [];
    if (students.value.length > 0) {
      const rel = students.value[0];
      const s = rel.student;
      student.value = {
        id: s.id,
        name: s.name || "",
        english_name: s.english_name,
        level: s.level,
        group_name: s.group_name,
      };
      await loadStudentData(s.id);
    }
  } catch {
    showToast("加载学员信息失败");
  }
}

async function checkMatchByMobile() {
  matchLoading.value = true;
  try {
    const res = await ParentStudentAPI.matchByMobile();
    matchedStudents.value = res.data.data || [];
  } catch {
    matchedStudents.value = [];
  } finally {
    matchLoading.value = false;
  }
}

function openHistory(index: number) {
  historyIndex.value = index;
  showHistoryViewer.value = true;
  nextTick(() => setTimeout(() => initHistoryRadar(), 80));
}

function historyNav(dir: number) {
  const next = historyIndex.value - dir;
  if (next < 0 || next >= assessmentHistory.value.length) return;
  historyIndex.value = next;
  nextTick(() => setTimeout(() => initHistoryRadar(), 80));
}

function initHistoryRadar() {
  if (!historyRadarRef.value || !viewingAssessment.value) return;
  if (historyRadarInstance) historyRadarInstance.dispose();
  historyRadarInstance = echarts.init(historyRadarRef.value);
  const indicators = dimensions.map((d) => ({ name: d.label, max: 5 }));
  const value = dimensions.map((d) => viewingAssessment.value[d.key] ?? 0);
  historyRadarInstance.setOption({
    radar: {
      indicator: indicators,
      center: ["50%", "50%"],
      radius: "70%",
      axisName: { color: "#333", fontSize: 11 },
      splitArea: { areaStyle: { color: ["rgba(245,158,11,0.02)", "rgba(245,158,11,0.06)"] } },
    },
    series: [
      {
        type: "radar",
        data: [
          {
            value,
            areaStyle: { color: "rgba(245,158,11,0.2)" },
            lineStyle: { color: "#f59e0b", width: 2 },
            itemStyle: { color: "#f59e0b" },
          },
        ],
      },
    ],
  });
}

function onLogout() {
  showLogoutDialog.value = true;
}

async function confirmLogout() {
  showLogoutDialog.value = false;
  const userStore = useUserStore();
  await userStore.logout();
  router.replace("/login");
}

onMounted(async () => {
  loading.value = true;
  try {
    const res = await ParentStudentAPI.getMyStudents();
    const relations = res.data.data || [];
    students.value = relations;

    if (relations.length > 0) {
      const rel = relations[0];
      const s = rel.student;
      student.value = {
        id: s.id,
        name: s.name || "",
        english_name: s.english_name,
        level: s.level,
        group_name: s.group_name,
      };
      await loadStudentData(s.id);
    } else {
      checkMatchByMobile();
    }
  } catch {
    showToast("加载学员信息失败");
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.parent-student-page {
  min-height: 100vh;
  padding-bottom: 24px;
}

.loading-center {
  margin-top: 60px;
  display: flex;
  justify-content: center;
}

.content {
  padding: 12px 0;
}

.att-stats {
  padding: 16px 0;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--van-text-color);
}

.stat-label {
  margin-top: 4px;
  font-size: 12px;
  color: var(--van-text-color-2);
}

.text-green {
  color: var(--van-green);
}

.text-orange {
  color: var(--van-orange);
}

.score-badge {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 8px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: var(--van-primary-color);
  border-radius: 10px;
}

.score-badge-sm {
  display: inline-block;
  padding: 1px 6px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: var(--van-primary-color);
  border-radius: 8px;
}

.record-text {
  font-size: 12px;
  color: var(--van-text-color-2);
}

.radar-chart-inline {
  width: 100%;
  height: 260px;
  margin: 8px 0;
}

.text-muted {
  color: var(--van-text-color-2);
  font-size: 12px;
}

.tournament-detail {
  padding: 16px;
}

.history-viewer {
  padding: 16px;
}

.history-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 12px 0;
}

.history-nav-title {
  font-size: 14px;
  font-weight: 500;
}

.history-score {
  text-align: center;
  margin-top: 8px;
  font-size: 15px;
}

.logout-body {
  text-align: center;
  padding: 30px 24px 20px;
}

.logout-icon {
  font-size: 44px;
  color: var(--van-orange);
}

.logout-title {
  margin-top: 12px;
  font-size: 17px;
  font-weight: 600;
}

.logout-desc {
  margin-top: 8px;
  font-size: 14px;
  color: var(--van-text-color-2);
}

.logout-footer {
  padding: 0 24px 24px;
}

.logout-dialog {
  width: 300px;
}
</style>
