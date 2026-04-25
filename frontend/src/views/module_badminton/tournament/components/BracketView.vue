<template>
  <div class="bracket-view" :class="viewType">
    <div v-if="matches.length === 0" class="empty-state">
      <el-empty description="暂无对阵数据，请先生成对阵表" />
    </div>
    <div v-else class="bracket-container">
      <div v-for="[roundNum, roundMatches] in rounds" :key="roundNum" class="round">
        <div class="round-header">
          {{ getRoundName(roundNum, roundMatches.length) }}
        </div>
        <div class="round-matches">
          <div
            v-for="match in roundMatches"
            :key="match.id"
            class="match-card"
            :class="{
              completed: isCompleted(match.status),
              clickable: !isCompleted(match.status),
            }"
            @click="emit('matchClick', match)"
          >
            <div class="player" :class="{ winner: isWinner(match, match.player1?.id) }">
              <span class="player-name">{{ match.player1?.name || "TBD" }}</span>
              <span v-if="match.scores && match.scores.length > 0" class="score">
                {{ getSetScores(match) }}
              </span>
            </div>
            <div class="divider"></div>
            <div class="player" :class="{ winner: isWinner(match, match.player2?.id) }">
              <span class="player-name">{{ match.player2?.name || "TBD" }}</span>
              <span v-if="match.scores && match.scores.length > 0" class="score">
                {{ getSetScores(match) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Match {
  id: number;
  round_number: number;
  match_number: number;
  round_type: string;
  status: string;
  player1: { id: number; name: string } | null;
  player2: { id: number; name: string } | null;
  scores?: { player1: number; player2: number }[];
  winner_id?: number;
}

interface BracketViewProps {
  matches: Match[];
  viewType?: "tree" | "compact";
}

const props = withDefaults(defineProps<BracketViewProps>(), {
  viewType: "compact",
});

const emit = defineEmits<{
  (e: "matchClick", match: Match): void;
}>();

const rounds = computed(() => {
  const roundMap = new Map<number, Match[]>();
  for (const match of props.matches) {
    const existing = roundMap.get(match.round_number) || [];
    existing.push(match);
    roundMap.set(match.round_number, existing);
  }
  return Array.from(roundMap.entries()).sort((a, b) => a[0] - b[0]);
});

function getRoundName(roundNum: number, matchCount: number): string {
  if (matchCount === 1 && rounds.value.length === 1) {
    return "决赛";
  }
  if (matchCount === 1) {
    return "决赛";
  }
  if (roundNum === 1) {
    return "小组赛";
  }
  const names = ["", "", "半决赛", "三四名", "决赛"];
  return names[roundNum] || `第${roundNum}轮`;
}

function isWinner(match: Match, playerId: number | undefined): boolean {
  if (playerId === undefined) return false;
  return match.winner_id === playerId;
}

function isCompleted(status: string): boolean {
  return status === "COMPLETED" || status === "completed";
}

function getSetScores(match: Match): string {
  if (!match.scores || match.scores.length === 0) return "";
  return match.scores.map((s) => `${s.player1}:${s.player2}`).join(" ");
}
</script>

<style scoped>
.bracket-view {
  width: 100%;
  padding: 16px;
  overflow-x: auto;
}

.empty-state {
  padding: 40px;
}

.bracket-container {
  display: flex;
  gap: 32px;
  min-width: min-content;
}

.round {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.round-header {
  padding: 8px 16px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  text-align: center;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.round-matches {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 16px;
  justify-content: space-around;
}

.match-card {
  min-width: 180px;
  overflow: hidden;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  transition: all 0.2s;
}

.match-card.clickable {
  cursor: pointer;
}

.match-card.clickable:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.dark .match-card.clickable:hover {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.match-card.completed {
  background: var(--el-fill-color-light);
}

.player {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}

.player.winner {
  background: var(--el-color-primary-light-9);
}

.player-name {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.score {
  font-weight: bold;
  color: var(--el-color-primary);
}

.divider {
  height: 1px;
  background: var(--el-border-color);
}
</style>
