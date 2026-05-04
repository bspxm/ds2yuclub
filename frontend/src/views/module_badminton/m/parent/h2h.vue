<template>
  <div class="h2h-page">
    <van-loading v-if="loading" size="24px" class="loading" />

    <template v-else-if="data">
      <div class="summary-card">
        <div class="summary-student">{{ studentName }}</div>
        <div class="summary-stats">
          <span class="stat-item">
            <span class="stat-value">{{ data.total_matches }}</span>
            <span class="stat-label">总场次</span>
          </span>
          <span class="stat-item">
            <span class="stat-value win">{{ data.wins }}</span>
            <span class="stat-label">胜</span>
          </span>
          <span class="stat-item">
            <span class="stat-value loss">{{ data.losses }}</span>
            <span class="stat-label">负</span>
          </span>
          <span class="stat-item">
            <span class="stat-value" :class="winRateClass">{{ winRate }}%</span>
            <span class="stat-label">胜率</span>
          </span>
        </div>
      </div>

      <div v-if="data.records.length === 0" class="empty-state">
        <van-icon name="records" size="48" class="empty-icon" />
        <p>暂无对战记录</p>
      </div>

      <div v-else class="filter-bar">
        <van-search v-model="searchQuery" shape="round" placeholder="搜索对手姓名" clearable />
      </div>

      <div v-if="opponentsWithRecords.length === 0 && data.records.length > 0" class="empty-state">
        <p>未找到匹配的对手</p>
      </div>

      <div
        v-for="opponent in opponentsWithRecords"
        v-else
        :key="opponent.name"
        class="opponent-group"
      >
        <div class="opponent-header">
          <span class="opponent-name">VS {{ opponent.name }}</span>
          <span class="opponent-record" :class="opponent.recordClass">{{ opponent.record }}</span>
        </div>
        <div v-for="r in opponent.records" :key="r.match_id" class="match-card">
          <div class="match-tournament">{{ r.tournament_name }}</div>
          <div class="match-players">
            <span :class="{ highlight: r.player1?.name === studentName }">
              {{ r.player1?.name || "选手1" }}
            </span>
            <span class="vs-text">VS</span>
            <span :class="{ highlight: r.player2?.name === studentName }">
              {{ r.player2?.name || "选手2" }}
            </span>
          </div>
          <div v-if="r.scores?.sets" class="match-scores">
            <span v-for="(s, i) in r.scores.sets" :key="i" class="score-pill">
              {{ s.player1 }}:{{ s.player2 }}
            </span>
          </div>
          <div class="match-meta">
            <span v-if="r.winner_id" class="match-winner" :class="winnerClass(r, studentName)">
              {{ winnerLabel(r, studentName) }}
            </span>
            <span class="match-date">{{ formatDate(r.match_date) }}</span>
          </div>
        </div>
      </div>
    </template>

    <van-empty v-else description="加载失败" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { showToast } from "vant";
import ParentStudentAPI from "@/api/module_badminton/parent-student";
import { TournamentAPIExtended } from "@/api/module_badminton/tournament";

const route = useRoute();

const loading = ref(true);
const data = ref<any>(null);
const studentName = ref("");
const searchQuery = ref("");

const winRate = computed(() => {
  if (!data.value || data.value.total_matches === 0) return 0;
  return Math.round((data.value.wins / data.value.total_matches) * 100);
});

const winRateClass = computed(() => {
  const r = winRate.value;
  if (r >= 60) return "win";
  if (r <= 30) return "loss";
  return "";
});

const opponentsWithRecords = computed(() => {
  if (!data.value) return [];
  const map = new Map<string, any[]>();
  for (const r of data.value.records) {
    const name = r.opponent_name || "未知";
    if (!map.has(name)) map.set(name, []);
    map.get(name)!.push(r);
  }
  const q = searchQuery.value.trim().toLowerCase();
  const result: any[] = [];
  for (const [name, records] of map) {
    if (q && !name.toLowerCase().includes(q)) continue;
    const wins = records.filter(
      (r: any) =>
        (r.player1?.name === studentName.value && r.winner_id === r.player1?.id) ||
        (r.player2?.name === studentName.value && r.winner_id === r.player2?.id)
    ).length;
    const total = records.length;
    const losses = total - wins;
    let recordClass = "";
    if (wins > losses) recordClass = "positive";
    else if (losses > wins) recordClass = "negative";
    result.push({
      name,
      records,
      record: `${wins}胜 ${losses}负`,
      recordClass,
    });
  }
  result.sort((a, b) => a.name.localeCompare(b.name, "zh"));
  return result;
});

function formatDate(d: string | null) {
  if (!d) return "—";
  return d.split("T")[0];
}

function winnerClass(r: any, student: string) {
  const studentWon =
    (r.player1?.name === student && r.winner_id === r.player1?.id) ||
    (r.player2?.name === student && r.winner_id === r.player2?.id);
  return studentWon ? "win-text" : "lose-text";
}

function winnerLabel(r: any, student: string) {
  const studentWon =
    (r.player1?.name === student && r.winner_id === r.player1?.id) ||
    (r.player2?.name === student && r.winner_id === r.player2?.id);
  return studentWon ? "胜" : "负";
}

onMounted(async () => {
  const studentId = Number(route.query.student_id);
  if (!studentId) {
    loading.value = false;
    return;
  }
  try {
    const [detailRes, h2hRes] = await Promise.all([
      ParentStudentAPI.getMyStudents(),
      TournamentAPIExtended.getAllH2H(studentId),
    ]);
    const relations = detailRes.data.data || [];
    const match = relations.find((r: any) => r.student.id === studentId);
    studentName.value = match?.student?.name || `学员${studentId}`;
    data.value = h2hRes.data.data;
  } catch (e) {
    console.error("H2H load failed", e);
    showToast("加载失败");
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.h2h-page {
  min-height: 100vh;
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.summary-card {
  margin: 12px 16px;
  padding: 20px 16px;
  background: var(--mobile-card-bg);
  border-radius: 12px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}

.summary-student {
  font-size: 18px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 14px;
}

.summary-stats {
  display: flex;
  gap: 0;
  text-align: center;
}

.stat-item {
  flex: 1;
  border-right: 1px solid var(--mobile-border);
}

.stat-item:last-child {
  border-right: none;
}

.stat-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: var(--mobile-text-primary);
}

.stat-value.win {
  color: var(--mobile-green);
}

.stat-value.loss {
  color: var(--mobile-red);
}

.stat-label {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: var(--mobile-text-muted);
}

.empty-state {
  padding: 60px 0;
  text-align: center;
  color: var(--mobile-text-muted);
}

.empty-icon {
  margin-bottom: 12px;
  color: var(--mobile-text-muted);
  opacity: 0.4;
}

.opponent-group {
  margin: 0 16px 16px;
}

.opponent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  margin-bottom: 8px;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}

.opponent-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.opponent-record {
  font-size: 12px;
  font-weight: 500;
}

.opponent-record.positive {
  color: var(--mobile-green);
}

.opponent-record.negative {
  color: var(--mobile-red);
}

.filter-bar {
  margin: 0 12px 8px;
}

.filter-bar :deep(.van-search) {
  padding: 0;
}

.match-card {
  padding: 12px 14px;
  margin-bottom: 6px;
  background: var(--mobile-card-bg);
  border-radius: 8px;
  box-shadow: 0 1px 3px var(--mobile-shimmer);
}

.match-tournament {
  font-size: 12px;
  font-weight: 500;
  color: var(--mobile-text-muted);
  margin-bottom: 6px;
}

.match-players {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: var(--mobile-text-primary);
}

.match-players .highlight {
  font-weight: 700;
}

.vs-text {
  font-size: 11px;
  color: var(--mobile-text-muted);
}

.match-scores {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-top: 8px;
}

.score-pill {
  padding: 2px 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  background: var(--mobile-gray-bg);
  border-radius: 4px;
}

.match-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.match-winner {
  font-size: 12px;
  font-weight: 600;
}

.match-winner.win-text {
  color: var(--mobile-green);
}

.match-winner.lose-text {
  color: var(--mobile-red);
}

.match-date {
  font-size: 11px;
  color: var(--mobile-text-muted);
}
</style>
