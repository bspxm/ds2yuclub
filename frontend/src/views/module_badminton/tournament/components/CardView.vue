<template>
  <div class="card-view">
    <div class="cards-grid">
      <div
        v-for="match in matches"
        :key="match.id"
        class="match-card"
        :class="{ completed: isCompleted(match.status) }"
        @click="emit('matchClick', match)"
      >
        <div class="card-header">
          <span class="round-tag">{{ getRoundText(match.round_type) }}</span>
          <span class="match-num">第{{ match.match_number }}场</span>
        </div>

        <div class="card-content">
          <!-- 第一行：对阵双方名字 -->
          <div class="players-row">
            <span :class="['player-name', { winner: isWinner(match, match.player1?.id) }]">
              {{ match.player1?.name || "TBD" }}
            </span>
            <span class="vs">VS</span>
            <span :class="['player-name', { winner: isWinner(match, match.player2?.id) }]">
              {{ match.player2?.name || "TBD" }}
            </span>
          </div>

          <!-- 第二行：局分 -->
          <div class="sets-score" v-if="match.scores && match.scores.length > 0">
            <span class="sets-text">{{ getSetsScore(match) }}</span>
          </div>
          <div class="sets-score pending" v-else>
            <span class="sets-text">-</span>
          </div>

          <!-- 第三行：详细比分 -->
          <div class="detail-score" v-if="match.scores && match.scores.length > 0">
            <span class="detail-text">{{ getDetailScore(match) }}</span>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="matches.length === 0" description="暂无比赛数据" />
  </div>
</template>

<script setup lang="ts">
interface Match {
  id: number;
  round_number: number;
  match_number: number;
  round_type: string;
  status: string;
  player1: { id: number; name: string } | null;
  player2: { id: number; name: string } | null;
  scores?: { player1: number; player2: number; winner?: number }[];
  winner_id?: number;
}

defineProps<{
  matches: Match[];
}>();

const emit = defineEmits<{
  (e: "matchClick", match: Match): void;
}>();



function getSetsScore(match: Match): string {
  if (!match.scores || match.scores.length === 0) return "-";

  let p1Wins = 0;
  let p2Wins = 0;

  for (const set of match.scores) {
    if (set.player1 > set.player2) {
      p1Wins++;
    } else if (set.player2 > set.player1) {
      p2Wins++;
    }
  }

  return `${p1Wins}:${p2Wins}`;
}

function getDetailScore(match: Match): string {
  if (!match.scores || match.scores.length === 0) return "";

  return match.scores.map(s => `${s.player1}:${s.player2}`).join(", ");
}

function getRoundText(roundType: string): string {
  const map: Record<string, string> = {
    GROUP_STAGE: "小组赛",
    KNOCKOUT: "淘汰赛",
    PROMOTION_RELEGATION: "升降赛",
    group_stage: "小组赛",
    knockout: "淘汰赛",
    promotion_relegation: "升降赛",
  };
  return map[roundType] || roundType;
}

function isWinner(match: Match, playerId: number | undefined): boolean {
  if (playerId === undefined) return false;
  return match.winner_id === playerId;
}

function isCompleted(status: string): boolean {
  return status === "COMPLETED" || status === "completed";
}
</script>

<style scoped>
.card-view {
  padding: 16px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.match-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.match-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.match-card.completed {
  background: #fafafa;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.round-tag {
  font-size: 12px;
  color: #409eff;
  font-weight: bold;
}

.match-num {
  font-size: 11px;
  color: #909399;
}

.card-content {
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 第一行：对阵双方名字 */
.players-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.player-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.player-name.winner {
  color: #67c23a;
  font-weight: bold;
}

.vs {
  font-size: 11px;
  color: #c0c4cc;
  font-weight: normal;
  flex-shrink: 0;
}

/* 第二行：局分 */
.sets-score {
  text-align: center;
  padding: 6px 0;
  background: #f5f7fa;
  border-radius: 4px;
}

.sets-score.pending {
  background: #f5f7fa;
}

.sets-text {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

/* 第三行：详细比分 */
.detail-score {
  text-align: center;
  padding-top: 4px;
}

.detail-text {
  font-size: 12px;
  color: #909399;
  letter-spacing: 0.5px;
}
</style>
