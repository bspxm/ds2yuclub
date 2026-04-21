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
          <div v-if="match.scores && match.scores.length > 0" class="sets-score">
            <span class="sets-text">{{ getSetsScore(match) }}</span>
          </div>
          <div v-else class="sets-score pending">
            <span class="sets-text">-</span>
          </div>

          <!-- 第三行：详细比分 -->
          <div v-if="match.scores && match.scores.length > 0" class="detail-score">
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

  return match.scores.map((s) => `${s.player1}:${s.player2}`).join(", ");
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
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.match-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.dark .match-card:hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
}

.match-card.completed {
  background: var(--el-fill-color-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
}

.round-tag {
  font-size: 12px;
  color: var(--el-color-primary);
  font-weight: bold;
}

.match-num {
  font-size: 11px;
  color: var(--el-text-color-secondary);
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
  color: var(--el-text-color-regular);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.player-name.winner {
  color: var(--el-color-success);
  font-weight: bold;
}

.vs {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  font-weight: normal;
  flex-shrink: 0;
}

/* 第二行：局分 */
.sets-score {
  text-align: center;
  padding: 6px 0;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.sets-score.pending {
  background: var(--el-fill-color-light);
}

.sets-text {
  font-size: 20px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

/* 第三行：详细比分 */
.detail-score {
  text-align: center;
  padding-top: 4px;
}

.detail-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  letter-spacing: 0.5px;
}
</style>
