<template>
  <div class="card-view">
    <div class="cards-grid">
      <div
        v-for="match in matches"
        :key="match.id"
        class="match-card"
        :class="{ completed: match.status === 'completed' }"
        @click="emit('matchClick', match)"
      >
        <div class="card-header">
          <span class="round-tag">{{ getRoundText(match.round_type) }}</span>
          <span class="match-num">第{{ match.match_number }}场</span>
        </div>

        <div class="players">
          <div class="player-row" :class="{ winner: isWinner(match, match.player1?.id) }">
            <span class="player-name">{{ match.player1?.name || "TBD" }}</span>
            <span v-if="match.status === 'completed'" class="score">
              {{ match.scores?.[0]?.player1 || "-" }}
            </span>
          </div>
          <div class="vs-divider">
            <span class="vs">VS</span>
          </div>
          <div class="player-row" :class="{ winner: isWinner(match, match.player2?.id) }">
            <span class="player-name">{{ match.player2?.name || "TBD" }}</span>
            <span v-if="match.status === 'completed'" class="score">
              {{ match.scores?.[0]?.player2 || "-" }}
            </span>
          </div>
        </div>

        <div v-if="match.scores && match.scores.length > 1" class="score-detail">
          {{ getScoreText(match) }}
        </div>

        <div class="card-footer">
          <el-tag
            :type="
              match.status === 'completed'
                ? 'success'
                : match.status === 'active'
                  ? 'warning'
                  : 'info'
            "
            size="small"
          >
            {{
              match.status === "completed"
                ? "已完成"
                : match.status === "active"
                  ? "进行中"
                  : "待开始"
            }}
          </el-tag>
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
  scores?: { player1: number; player2: number }[];
  winner_id?: number;
}

defineProps<{
  matches: Match[];
}>();

const emit = defineEmits<{
  (e: "matchClick", match: Match): void;
}>();

function getScoreText(match: Match): string {
  if (!match.scores || match.scores.length === 0) {
    return "";
  }
  return match.scores.map((s) => `${s.player1}:${s.player2}`).join(" ");
}

function getRoundText(roundType: string): string {
  const map: Record<string, string> = {
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
</script>

<style scoped>
.card-view {
  padding: 16px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.round-tag {
  font-size: 12px;
  color: #409eff;
  font-weight: bold;
}

.match-num {
  font-size: 12px;
  color: #999;
}

.players {
  padding: 16px;
}

.player-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.player-row.winner {
  background: #f0f9ff;
  margin: 0 -16px;
  padding: 8px 16px;
}

.player-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.score {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.vs-divider {
  text-align: center;
  padding: 4px 0;
}

.vs {
  color: #c0c4cc;
  font-size: 12px;
}

.score-detail {
  text-align: center;
  padding: 8px 16px;
  background: #fafafa;
  font-size: 12px;
  color: #666;
  border-top: 1px solid #eee;
}

.card-footer {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}
</style>
