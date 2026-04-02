<template>
  <div class="bracket-view" :class="viewType">
    <div class="bracket-container">
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
              completed: match.status === 'completed',
              clickable: match.status !== 'completed',
            }"
            @click="emit('matchClick', match)"
          >
            <div class="player" :class="{ winner: isWinner(match, match.player1?.id) }">
              <span class="player-name">{{ match.player1?.name || "TBD" }}</span>
              <span v-if="match.status === 'completed'" class="score">
                {{ match.scores?.[0]?.player1 || "-" }}
              </span>
            </div>
            <div class="divider"></div>
            <div class="player" :class="{ winner: isWinner(match, match.player2?.id) }">
              <span class="player-name">{{ match.player2?.name || "TBD" }}</span>
              <span v-if="match.status === 'completed'" class="score">
                {{ match.scores?.[0]?.player2 || "-" }}
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

function isWinner(match: Match, playerId: number): boolean {
  return match.winner_id === playerId;
}
</script>

<style scoped>
.bracket-view {
  width: 100%;
  overflow-x: auto;
  padding: 16px;
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
  text-align: center;
  font-weight: bold;
  color: #333;
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.round-matches {
  display: flex;
  flex-direction: column;
  gap: 16px;
  justify-content: space-around;
  flex: 1;
}

.match-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  min-width: 180px;
  transition: all 0.2s;
}

.match-card.clickable {
  cursor: pointer;
}

.match-card.clickable:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.match-card.completed {
  background: #fafafa;
}

.player {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.player.winner {
  background: #f0f9ff;
}

.player-name {
  font-size: 14px;
  color: #333;
}

.score {
  font-weight: bold;
  color: #409eff;
}

.divider {
  height: 1px;
  background: #e4e7ed;
}
</style>
