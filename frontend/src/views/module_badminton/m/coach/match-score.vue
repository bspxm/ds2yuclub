<template>
  <div class="score-page">
    <van-loading v-if="loading" size="24px" class="loading" />

    <template v-else-if="match">
      <div class="match-header">
        <div class="player-name" :class="{ isWinner: winnerId === match.player1?.id }">
          {{ match.player1?.name || "待定" }}
        </div>
        <div class="vs-text">VS</div>
        <div class="player-name" :class="{ isWinner: winnerId === match.player2?.id }">
          {{ match.player2?.name || "待定" }}
        </div>
      </div>

      <div class="sets-section">
        <div v-for="(set, index) in sets" :key="index" class="set-row">
          <div class="set-label">第{{ index + 1 }}局</div>
          <div class="set-inputs">
            <van-field
              v-model="set.player1"
              type="digit"
              placeholder="0"
              class="score-input"
              maxlength="2"
              @update:model-value="calculateWinner"
            />
            <span class="colon">:</span>
            <van-field
              v-model="set.player2"
              type="digit"
              placeholder="0"
              class="score-input"
              maxlength="2"
              @update:model-value="calculateWinner"
            />
          </div>
          <van-button
            v-if="sets.length > 1"
            icon="delete"
            size="small"
            plain
            round
            @click="removeSet(index)"
          />
        </div>

        <van-button icon="plus" size="small" plain round class="add-set-btn" @click="addSet">
          新增一局
        </van-button>
      </div>

      <div v-if="resultText" class="result-bar" :class="resultValid ? 'valid' : 'invalid'">
        {{ resultText }}
      </div>

      <div class="submit-area">
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
import { TournamentAPIExtended } from "@/api/module_badminton/tournament";

const route = useRoute();
const router = useRouter();

const tournamentId = computed(() => Number(route.params.tournamentId));
const matchId = computed(() => Number(route.params.matchId));

const loading = ref(false);
const submitting = ref(false);
const match = ref<any>(null);
const winnerId = ref<number | null>(null);

interface SetScore {
  player1: string;
  player2: string;
}

const sets = ref<SetScore[]>([{ player1: "", player2: "" }]);

const resultValid = ref(false);
const resultText = ref("");

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
    resultText.value = `大比分 ${p1Wins}:${p2Wins} · 胜者 ${match.value?.player1?.name}`;
    resultValid.value = true;
  } else if (p2Wins >= needed && p2Wins > p1Wins) {
    winnerId.value = match.value?.player2?.id;
    resultText.value = `大比分 ${p1Wins}:${p2Wins} · 胜者 ${match.value?.player2?.name}`;
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
    const res = await TournamentAPIExtended.getMatchDetail(tournamentId.value, matchId.value);
    match.value = res.data.data;

    if (match.value?.scores && match.value.scores.length > 0) {
      sets.value = match.value.scores.map((s: any) => ({
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
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.match-header {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
}

.player-name {
  padding: 8px 16px;
  font-size: 16px;
  font-weight: 600;
  background: #f5f5f5;
  border-radius: 8px;
  transition: all 0.3s;
}

.player-name.isWinner {
  color: #fff;
  background: var(--van-success-color, #07c160);
}

.vs-text {
  font-size: 13px;
  color: #999;
}

.sets-section {
  padding: 0 16px;
}

.set-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}

.set-label {
  width: 50px;
  font-size: 14px;
  color: #666;
}

.set-inputs {
  display: flex;
  flex: 1;
  gap: 6px;
  align-items: center;
}

.score-input {
  flex: 1;
  text-align: center;
}

.colon {
  font-size: 18px;
  font-weight: 600;
}

.add-set-btn {
  width: 100%;
  margin-bottom: 16px;
}

.result-bar {
  padding: 10px 16px;
  margin: 0 16px 16px;
  font-size: 14px;
  text-align: center;
  border-radius: 8px;
}

.result-bar.valid {
  color: #07c160;
  background: #f0f9eb;
}

.result-bar.invalid {
  color: #ee0a24;
  background: #fef0f0;
}

.submit-area {
  padding: 16px;
}
</style>
