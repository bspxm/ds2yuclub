<template>
  <div class="group-stage-view">
    <!-- 对阵矩阵 -->
    <div class="matrix-section">
      <h3 class="section-title">对阵矩阵</h3>
      <div class="matrix-table-wrapper">
        <table class="matrix-table">
          <thead>
            <tr>
              <th class="corner-cell"></th>
              <th v-for="(col, idx) in data.matrix" :key="idx" class="header-cell">
                {{ col.student_name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIdx) in data.matrix" :key="rowIdx">
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
                    <span class="detail-score" v-if="result.detail_score">{{ result.detail_score }}</span>
                    <span class="result-text">{{ result.win ? '胜' : result.draw ? '平' : '负' }}</span>
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
      <el-table :data="data.rankings" stripe>
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
        <el-table-column label="胜负赛" width="100" align="center">
          <template #default="{ row }">
            {{ row.wins }}-{{ row.losses }}<span v-if="row.draws > 0" class="draw-count">({{ row.draws }}平)</span>
          </template>
        </el-table-column>
        <el-table-column label="胜负局" width="80" align="center">
          <template #default="{ row }">
            {{ row.sets_won }}-{{ row.sets_lost }}
          </template>
        </el-table-column>
        <el-table-column label="胜负分" min-width="100" align="center">
          <template #default="{ row }">
            {{ row.points_scored }}-{{ row.points_conceded }}
          </template>
        </el-table-column>
        <el-table-column label="净胜分" width="80" align="center">
          <template #default="{ row }">
            <span :class="row.points_scored - row.points_conceded > 0 ? 'positive' : 'negative'">
              {{ row.points_scored - row.points_conceded > 0 ? '+' : '' }}
              {{ row.points_scored - row.points_conceded }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 赛程列表 -->
    <div class="schedule-section">
      <h3 class="section-title">赛程</h3>
      <el-table :data="data.schedule" stripe>
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
            <span class="detail-score-list" v-if="row.sets && row.sets.length > 0">
              <span v-for="(set, idx) in row.sets" :key="idx" class="set-score">
                {{ set.player1 }}:{{ set.player2 }}
              </span>
            </span>
            <span v-else class="no-score">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small"
              @click="$emit('recordScore', row)"
            >
              {{ row.completed ? '修改' : '录入' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
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

interface GroupStageData {
  matrix: MatrixRow[];
  rankings: Ranking[];
  schedule: ScheduleItem[];
}

const props = defineProps<{
  data: GroupStageData;
}>();

const emit = defineEmits<{
  (e: 'recordScore', match: ScheduleItem): void;
}>();

function getResultClass(result: MatrixResult | null): string {
  if (!result) return 'empty';
  if (result.win) return 'win-cell';
  if (result.draw) return 'draw-cell';
  return 'loss-cell';
}

function getWinnerClass(match: ScheduleItem, player: number): string {
  if (!match.completed) return '';
  const [p1Score, p2Score] = match.score.split(':').map(Number);
  if (player === 1 && p1Score > p2Score) return 'winner';
  if (player === 2 && p2Score > p1Score) return 'winner';
  return '';
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return '-';
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}
</script>

<style scoped>
.group-stage-view {
  padding: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
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
  border: 1px solid #ebeef5;
  padding: 12px 8px;
  text-align: center;
  min-width: 80px;
}

.matrix-table th {
  background-color: #f5f7fa;
  font-weight: bold;
}

.corner-cell {
  background-color: #f5f7fa;
}

.header-cell {
  writing-mode: horizontal-tb;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-header {
  background-color: #f5f7fa;
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
  background-color: #f0f9ff;
}

.loss-cell {
  background-color: #fef0f0;
}

.draw-cell {
  background-color: #fdf6ec;
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
  color: #67c23a;
}

.score.loss {
  color: #f56c6c;
}

.score.draw {
  color: #e6a23c;
}

.detail-score {
  font-size: 11px;
  color: #606266;
  font-weight: normal;
  line-height: 1.2;
}

.result-text {
  font-size: 12px;
  color: #909399;
}

.draw-count {
  font-size: 11px;
  color: #e6a23c;
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
  color: #606266;
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.no-score {
  color: #c0c4cc;
}

.diagonal {
  color: #c0c4cc;
}

.pending {
  color: #c0c4cc;
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
  background-color: #ffd700;
  color: #fff;
}

.rank-2 {
  background-color: #c0c0c0;
  color: #fff;
}

.rank-3 {
  background-color: #cd7f32;
  color: #fff;
}

.player-name {
  font-weight: 500;
}

.positive {
  color: #67c23a;
  font-weight: bold;
}

.negative {
  color: #f56c6c;
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
  color: #67c23a;
  font-weight: bold;
}

.match-players .vs {
  color: #909399;
  font-size: 12px;
}

.match-score {
  font-weight: bold;
}

.match-score.completed {
  color: #409eff;
}

.match-score.pending {
  color: #c0c4cc;
}
</style>
