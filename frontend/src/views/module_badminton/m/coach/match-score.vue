<template>
  <div class="score-page">
    <van-loading v-if="loading" size="24px" class="loading" />

    <template v-else-if="match">
      <div class="scoreboard">
        <div class="sb-player" :class="{ 'is-winner': winnerId === match.player1?.id }">
          <div class="sb-name">{{ match.player1?.name || "待定" }}</div>
          <div class="sb-score">{{ setsWon(1) }}</div>
        </div>
        <div class="sb-vs">
          <div class="sb-vs-text">VS</div>
          <div class="sb-vs-sub">大比分</div>
        </div>
        <div class="sb-player" :class="{ 'is-winner': winnerId === match.player2?.id }">
          <div class="sb-name">{{ match.player2?.name || "待定" }}</div>
          <div class="sb-score">{{ setsWon(2) }}</div>
        </div>
      </div>

      <div class="sets-section">
        <div class="section-label">{{ isReadonly ? "历史比分" : "局分录入" }}</div>

        <div v-for="(set, index) in sets" :key="index" class="set-block">
          <div class="set-header">
            <span class="set-title">第{{ index + 1 }}局</span>
            <van-button
              v-if="!isReadonly && sets.length > 1"
              icon="delete"
              size="small"
              plain
              round
              @click="removeSet(index)"
            />
          </div>
          <div class="set-body">
            <van-field
              v-model="set.player1"
              type="digit"
              placeholder="0"
              class="score-field"
              :readonly="isReadonly"
              inputmode="numeric"
              maxlength="2"
              @update:model-value="!isReadonly && calculateWinner()"
            />
            <span class="set-colon">:</span>
            <van-field
              v-model="set.player2"
              type="digit"
              placeholder="0"
              class="score-field"
              :readonly="isReadonly"
              inputmode="numeric"
              maxlength="2"
              @update:model-value="!isReadonly && calculateWinner()"
            />
          </div>
        </div>

        <van-button
          v-if="!isReadonly"
          icon="plus"
          block
          plain
          round
          class="add-set-btn"
          @click="addSet"
        >
          新增一局
        </van-button>
      </div>

      <div v-if="resultText" class="result-banner" :class="resultValid ? 'valid' : 'invalid'">
        <van-icon :name="resultValid ? 'success' : 'cross'" />
        {{ resultText }}
      </div>

      <div v-if="!isReadonly" class="submit-area">
        <van-button
          type="primary"
          block
          round
          size="large"
          :loading="submitting"
          :disabled="!resultValid"
          @click="handleSubmit"
        >
          确认提交
        </van-button>
      </div>
    </template>

    <van-empty v-else description="比赛信息不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showToast, showSuccessToast } from "vant";
import TournamentAPI, { TournamentAPIExtended } from "@/api/module_badminton/tournament";

const route = useRoute();
const router = useRouter();

const tournamentId = computed(() => Number(route.params.tournamentId));
const matchId = computed(() => Number(route.params.matchId));

const loading = ref(false);
const submitting = ref(false);
const match = ref<any>(null);
const tournament = ref<any>(null);
const winnerId = ref<number | null>(null);

const isReadonly = computed(
  () => match.value?.status === "completed" || tournament.value?.status === "COMPLETED"
);

interface SetScore {
  player1: string;
  player2: string;
}

const sets = ref<SetScore[]>([{ player1: "", player2: "" }]);

const resultValid = ref(false);
const resultText = ref("");

function setsWon(player: 1 | 2): number {
  let count = 0;
  for (const s of sets.value) {
    const p1 = parseInt(s.player1) || 0;
    const p2 = parseInt(s.player2) || 0;
    if (p1 === 0 && p2 === 0) continue;
    if (player === 1 && p1 > p2) count++;
    if (player === 2 && p2 > p1) count++;
  }
  return count;
}

function getNumericSets() {
  return sets.value.map((s) => ({
    player1: parseInt(s.player1) || 0,
    player2: parseInt(s.player2) || 0,
  }));
}

function calculateWinner() {
  const numSets = getNumericSets();
  let p1Wins = 0;
  let p2Wins = 0;
  let hasValue = false;

  for (const s of numSets) {
    if (s.player1 === 0 && s.player2 === 0) continue;
    hasValue = true;
    if (s.player1 > s.player2) p1Wins++;
    else if (s.player2 > s.player1) p2Wins++;
  }

  if (!hasValue) {
    resultValid.value = false;
    resultText.value = "";
    return;
  }

  const total = numSets.filter((s) => s.player1 !== 0 || s.player2 !== 0).length;
  const needed = Math.ceil(total / 2);

  if (p1Wins >= needed && p1Wins > p2Wins) {
    winnerId.value = match.value?.player1?.id;
    resultText.value = `胜者 ${match.value?.player1?.name}  (${p1Wins}:${p2Wins})`;
    resultValid.value = true;
  } else if (p2Wins >= needed && p2Wins > p1Wins) {
    winnerId.value = match.value?.player2?.id;
    resultText.value = `胜者 ${match.value?.player2?.name}  (${p1Wins}:${p2Wins})`;
    resultValid.value = true;
  } else {
    resultValid.value = false;
    resultText.value = "比赛尚未结束，请继续录入比分";
  }
}

function addSet() {
  sets.value.push({ player1: "", player2: "" });
}

function removeSet(index: number) {
  sets.value.splice(index, 1);
  calculateWinner();
}

async function handleSubmit() {
  if (!match.value) return;

  submitting.value = true;
  try {
    const numSets = getNumericSets();
    for (const s of numSets) {
      if (s.player1 < 0 || s.player2 < 0) {
        showToast("比分不能为负数");
        return;
      }
    }

    await TournamentAPIExtended.recordScore(tournamentId.value, matchId.value, {
      sets: numSets,
    });

    showSuccessToast("比分录入成功");
    router.back();
  } catch (e: any) {
    showToast(e.response?.data?.msg || "提交失败");
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    const [matchRes, tournamentRes] = await Promise.all([
      TournamentAPIExtended.getMatches(tournamentId.value),
      TournamentAPI.getTournamentList(),
    ]);
    const list: any[] = matchRes.data.data || [];
    const found = list.find((m: any) => m.id === matchId.value);
    if (!found) {
      showToast("比赛不存在");
      loading.value = false;
      return;
    }
    match.value = found;
    tournament.value = (tournamentRes.data.data || []).find(
      (t: any) => t.id === tournamentId.value
    );

    if (found.scores && found.scores.length > 0) {
      sets.value = found.scores.map((s: any) => ({
        player1: String(s.player1),
        player2: String(s.player2),
      }));
      calculateWinner();
    }
  } catch (e: any) {
    showToast(e.response?.data?.msg || "加载失败");
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.score-page {
  padding-bottom: 32px;
}

.loading {
  margin-top: 60px;
}

.scoreboard {
  display: flex;
  gap: 8px;
  align-items: stretch;
  padding: 20px 0;
}

.sb-player {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 16px 12px;
  background: var(--mobile-scoreboard-bg);
  border-radius: 12px;
  min-height: 90px;
  transition: all 0.3s;
}

.sb-player.is-winner {
  background: var(--mobile-scoreboard-winner-bg);
  box-shadow: 0 0 0 2px var(--mobile-green);
}

.sb-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  text-align: center;
  line-height: 1.3;
}

.is-winner .sb-name {
  color: var(--mobile-winner-text);
}

.sb-score {
  font-size: 32px;
  font-weight: 800;
  color: var(--mobile-text-primary);
  line-height: 1;
}

.is-winner .sb-score {
  color: var(--mobile-winner-text);
}

.sb-vs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
}

.sb-vs-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--mobile-text-muted);
}

.sb-vs-sub {
  font-size: 11px;
  color: var(--mobile-text-muted);
  margin-top: 2px;
}

.sets-section {
  padding: 0 0 16px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 12px;
}

.set-block {
  margin-bottom: 12px;
  padding: 12px;
  background: var(--mobile-set-block-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}

.set-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.set-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--mobile-text-secondary);
}

.set-body {
  display: flex;
  gap: 8px;
  align-items: center;
}

.score-field {
  flex: 1;
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  border: 2px solid var(--mobile-set-block-border);
  border-radius: 10px;
}

.set-colon {
  font-size: 22px;
  font-weight: 700;
  color: var(--mobile-text-muted);
  flex-shrink: 0;
}

.add-set-btn {
  margin-top: 4px;
}

.result-banner {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 10px;
}

.result-banner.valid {
  color: var(--mobile-green-text);
  background: var(--mobile-green-bg);
}

.result-banner.invalid {
  color: var(--mobile-red-text);
  background: var(--mobile-red-bg);
}

.submit-area {
  padding: 0;
}
</style>
