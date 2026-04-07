<template>
  <div class="group-stage-view">
    <!-- 小组切换下拉框 -->
    <div class="group-selector">
      <el-select v-model="selectedGroup" placeholder="选择小组" size="large">
        <el-option v-for="group in groups" :key="group.id" :label="group.name" :value="group.id" />
      </el-select>
    </div>

    <!-- 对阵矩阵 -->
    <div class="matrix-section">
      <h3 class="section-title">对阵矩阵</h3>
      <div class="matrix-table-wrapper">
        <table class="matrix-table">
          <thead>
            <tr>
              <th class="corner-cell"></th>
              <th v-for="(col, idx) in currentGroupData.matrix" :key="idx" class="header-cell">
                {{ col.student_name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIdx) in currentGroupData.matrix" :key="rowIdx">
              <td class="row-header">{{ row.student_name }}</td>
              <td
                v-for="(result, colIdx) in row.results"
                :key="colIdx"
                :class="['matrix-cell', getResultClass(result)]"
              >
                <template v-if="result">
                  <div class="score-container">
                    <span :class="['score', result.win ? 'win' : result.draw ? 'draw' : 'loss']">
                      {{ result.score }}
                    </span>
                    <span v-if="result.detail_score" class="detail-score">
                      {{ result.detail_score }}
                    </span>
                    <span class="result-text">
                      {{ result.win ? "胜" : result.draw ? "平" : "负" }}
                    </span>
                  </div>
                </template>
                <template v-else-if="rowIdx === colIdx">
                  <span class="diagonal">—</span>
                </template>
                <template v-else>
                  <span class="pending">-</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 积分排名 -->
    <div class="rankings-section">
      <h3 class="section-title">积分排名</h3>
      <el-table :data="currentGroupData.rankings" stripe>
        <el-table-column type="index" label="名次" width="60" align="center">
          <template #default="{ $index }">
            <span :class="['rank-num', 'rank-' + ($index + 1)]">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="选手" min-width="120">
          <template #default="{ row }">
            <span class="player-name">{{ row.student_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_points" label="总分" width="60" align="center" />
        <el-table-column prop="matches_played" label="场数" width="60" align="center" />
        <el-table-column
          v-if="tournamentType !== 'CHAMPIONSHIP'"
          label="胜负赛"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.wins }}-{{ row.losses }}
            <span v-if="row.draws > 0" class="draw-count">({{ row.draws }}平)</span>
          </template>
        </el-table-column>
        <el-table-column v-else label="胜负" width="80" align="center">
          <template #default="{ row }">{{ row.wins }}-{{ row.losses }}</template>
        </el-table-column>
        <el-table-column label="胜负局" width="80" align="center">
          <template #default="{ row }">{{ row.sets_won }}-{{ row.sets_lost }}</template>
        </el-table-column>
        <el-table-column label="胜负分" min-width="100" align="center">
          <template #default="{ row }">{{ row.points_scored }}-{{ row.points_conceded }}</template>
        </el-table-column>
        <el-table-column label="净胜分" width="80" align="center">
          <template #default="{ row }">
            <span :class="row.points_scored - row.points_conceded > 0 ? 'positive' : 'negative'">
              {{ row.points_scored - row.points_conceded > 0 ? "+" : "" }}
              {{ row.points_scored - row.points_conceded }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 赛程列表 -->
    <div class="schedule-section">
      <h3 class="section-title">赛程</h3>
      <el-table :data="currentGroupData.schedule" stripe>
        <el-table-column label="时间" width="150">
          <template #default="{ row }">
            {{ formatTime(row.scheduled_time) }}
          </template>
        </el-table-column>
        <el-table-column label="对阵" min-width="200">
          <template #default="{ row }">
            <div class="match-players">
              <span :class="['player', getWinnerClass(row, 1)]">{{ row.player1_name }}</span>
              <span class="vs">vs</span>
              <span :class="['player', getWinnerClass(row, 2)]">{{ row.player2_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="比分" width="70" align="center">
          <template #default="{ row }">
            <span :class="['match-score', row.completed ? 'completed' : 'pending']">
              {{ row.score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="详细比分" min-width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.sets && row.sets.length > 0" class="detail-score-list">
              <span v-for="(set, idx) in row.sets" :key="idx" class="set-score">
                {{ set.player1 }}:{{ set.player2 }}
              </span>
            </span>
            <span v-else class="no-score">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="$emit('recordScore', row)">
              {{ row.completed ? "修改" : "录入" }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";

interface MatrixResult {
  win: boolean;
  draw?: boolean;
  score: string;
  detail_score?: string;
  sets?: any[];
}

interface MatrixRow {
  participant_id: number;
  student_name: string;
  results: (MatrixResult | null)[];
}

interface Ranking {
  participant_id: number;
  student_name: string;
  total_points: number;
  matches_played: number;
  wins: number;
  losses: number;
  draws: number;
  sets_won: number;
  sets_lost: number;
  points_scored: number;
  points_conceded: number;
}

interface ScheduleItem {
  match_id: number;
  player1_id: number;
  player1_name: string;
  player2_id: number;
  player2_name: string;
  score: string;
  scheduled_time: string | null;
  completed: boolean;
}

interface GroupData {
  matrix: MatrixRow[];
  rankings: Ranking[];
  schedule: ScheduleItem[];
}

interface Group {
  id: number;
  name: string;
  data: GroupData;
}

const props = defineProps<{
  groups: Group[];
  tournamentType?: string;
}>();

const emit = defineEmits<{
  (e: "recordScore", match: ScheduleItem): void;
}>();

const selectedGroup = ref<number>(0);

// 当 groups 数据加载后，自动选中第一个小组
watch(
  () => props.groups,
  (groups) => {
    if (groups.length > 0 && !groups.find((g) => g.id === selectedGroup.value)) {
      selectedGroup.value = groups[0].id;
    }
  },
  { immediate: true }
);

const currentGroupData = computed(() => {
  const group = props.groups.find((g) => g.id === selectedGroup.value);
  return group?.data || { matrix: [], rankings: [], schedule: [] };
});

function getResultClass(result: MatrixResult | null): string {
  if (!result) return "empty";
  if (result.win) return "win-cell";
  if (result.draw) return "draw-cell";
  return "loss-cell";
}

function getWinnerClass(match: ScheduleItem, player: number): string {
  if (!match.completed) return "";
  const [p1Score, p2Score] = match.score.split(":").map(Number);
  if (player === 1 && p1Score > p2Score) return "winner";
  if (player === 2 && p2Score > p1Score) return "winner";
  return "";
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return "-";
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}
</script>

<style scoped>
.group-stage-view {
  padding: 20px;
}

.group-selector {
  margin-bottom: 24px;
  text-align: center;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--el-color-primary);
}

.matrix-section,
.rankings-section,
.schedule-section {
  margin-bottom: 32px;
}

.matrix-table-wrapper {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.matrix-table th,
.matrix-table td {
  border: 1px solid var(--el-border-color-lighter);
  padding: 12px 8px;
  text-align: center;
  min-width: 80px;
}

.matrix-table th {
  background-color: var(--el-fill-color-light);
  font-weight: bold;
}

.corner-cell {
  background-color: var(--el-fill-color-light);
}

.header-cell {
  writing-mode: horizontal-tb;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-header {
  background-color: var(--el-fill-color-light);
  font-weight: bold;
  text-align: left;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.matrix-cell {
  transition: background-color 0.2s;
  padding: 8px 4px;
}

.win-cell {
  background-color: var(--el-color-primary-light-9);
}

.loss-cell {
  background-color: var(--el-color-danger-light-9);
}

.draw-cell {
  background-color: var(--el-color-warning-light-9);
}

.score-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.score {
  font-weight: bold;
  font-size: 16px;
}

.score.win {
  color: var(--el-color-success);
}

.score.loss {
  color: var(--el-color-danger);
}

.score.draw {
  color: var(--el-color-warning);
}

.detail-score {
  font-size: 11px;
  color: var(--el-text-color-regular);
  font-weight: normal;
  line-height: 1.2;
}

.result-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.draw-count {
  font-size: 11px;
  color: var(--el-color-warning);
  margin-left: 2px;
}

.detail-score-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.set-score {
  font-size: 12px;
  color: var(--el-text-color-regular);
  background-color: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 4px;
}

.no-score {
  color: var(--el-text-color-placeholder);
}

.diagonal {
  color: var(--el-text-color-placeholder);
}

.pending {
  color: var(--el-text-color-placeholder);
}

.rank-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-weight: bold;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e0e0e0 100%);
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.player-name {
  font-weight: 500;
}

.positive {
  color: var(--el-color-success);
  font-weight: bold;
}

.negative {
  color: var(--el-color-danger);
  font-weight: bold;
}

.match-players {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.match-players .player {
  font-weight: 500;
}

.match-players .player.winner {
  color: var(--el-color-success);
  font-weight: bold;
}

.match-players .vs {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.match-score {
  font-weight: bold;
}

.match-score.completed {
  color: var(--el-color-primary);
}

.match-score.pending {
  color: var(--el-text-color-placeholder);
}
</style>
