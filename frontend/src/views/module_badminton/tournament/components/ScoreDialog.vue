<template>
  <el-dialog
    v-model="dialogVisible"
    :title="readonly ? '查看比分' : '录入比分'"
    width="550px"
    @close="dialogVisible = false"
  >
    <div v-if="match">
      <div class="match-info">
        <span class="player-name" :class="{ winner: calculatedWinner === match.player1?.id }">
          {{ match.player1?.name }}
        </span>
        <span class="vs">VS</span>
        <span class="player-name" :class="{ winner: calculatedWinner === match.player2?.id }">
          {{ match.player2?.name }}
        </span>
      </div>

      <el-divider />

      <div class="scores">
        <div v-for="(set, index) in scores" :key="index" class="score-row">
          <span class="set-label">第{{ index + 1 }}局</span>
          <el-input-number
            v-model="set.player1"
            :min="0"
            :max="99"
            size="large"
            :disabled="readonly"
            @change="calculateWinner"
          />
          <span class="score-separator">:</span>
          <el-input-number
            v-model="set.player2"
            :min="0"
            :max="99"
            size="large"
            :disabled="readonly"
            @change="calculateWinner"
          />
          <el-button
            v-if="!readonly && scores.length > 1"
            type="danger"
            link
            @click="removeSet(index)"
          >
            删除
          </el-button>
        </div>
      </div>

      <div v-if="!readonly" class="actions">
        <el-button type="primary" link @click="addSet">+ 添加局数</el-button>
      </div>

      <!-- 计算结果显示 -->
      <div v-if="calculatedWinner && matchResult" class="result-info">
        <el-alert :type="matchResult.isValid ? 'success' : 'warning'" :closable="false">
          <template #title>
            <div class="result-content">
              <span>大比分：{{ matchResult.player1Wins }} : {{ matchResult.player2Wins }}</span>
              <span v-if="matchResult.isValid" class="winner-text">
                胜者：
                <strong>{{ matchResult.winnerName }}</strong>
              </span>
              <span v-else class="error-text">{{ matchResult.errorMessage }}</span>
            </div>
          </template>
        </el-alert>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">{{ readonly ? "关闭" : "取消" }}</el-button>
      <el-button v-if="!readonly" type="primary" @click="handleSubmit">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { ElMessage } from "element-plus";

interface SetScore {
  player1: number;
  player2: number;
}

interface MatchResult {
  player1Wins: number;
  player2Wins: number;
  winnerId: number | null;
  winnerName: string;
  isValid: boolean;
  errorMessage?: string;
}

const props = defineProps<{
  visible: boolean;
  match: {
    id: number;
    player1: { id: number; name: string };
    player2: { id: number; name: string };
    scores?: { player1: number; player2: number }[];
    status?: string;
    roundType?: string;
  } | null;
  readonly?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "submit", data: { matchId: number; sets: SetScore[]; winnerId?: number }): void;
}>();

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit("update:visible", val),
});

const scores = ref<SetScore[]>([{ player1: 0, player2: 0 }]);
const calculatedWinner = ref<number | null>(null);
const matchResult = ref<MatchResult | null>(null);

watch(
  () => props.visible,
  (val) => {
    if (val && props.match) {
      // 如果有已有比分数据，加载它
      if (props.match.scores && props.match.scores.length > 0) {
        scores.value = props.match.scores.map((s: any) => ({
          player1: typeof s.player1 === "number" ? s.player1 : 0,
          player2: typeof s.player2 === "number" ? s.player2 : 0,
        }));
      } else {
        // 默认只显示一局
        scores.value = [{ player1: 0, player2: 0 }];
      }
      calculatedWinner.value = null;
      matchResult.value = null;
      calculateWinner();
    }
  }
);

function addSet() {
  scores.value.push({ player1: 0, player2: 0 });
}

function removeSet(index: number) {
  if (scores.value.length > 1) {
    scores.value.splice(index, 1);
    calculateWinner();
  }
}

// 计算胜者（根据局分）
function calculateWinner() {
  if (!props.match) return;

  let player1Wins = 0;
  let player2Wins = 0;

  // 统计每局胜者
  for (const set of scores.value) {
    // 忽略未完成的局（都是0）
    if (set.player1 === 0 && set.player2 === 0) continue;

    if (set.player1 > set.player2) {
      player1Wins++;
    } else if (set.player2 > set.player1) {
      player2Wins++;
    }
  }

  // 判断是否有胜者（大比分达到所需局数）
  const totalSets = scores.value.filter((s) => s.player1 !== 0 || s.player2 !== 0).length;
  const setsNeeded = Math.ceil(totalSets / 2);

  let winnerId: number | null = null;
  let winnerName = "";
  let isValid = false;
  let errorMessage = "";

  if (player1Wins >= setsNeeded && player1Wins > player2Wins) {
    winnerId = props.match.player1?.id || null;
    winnerName = props.match.player1?.name || "";
    isValid = true;
  } else if (player2Wins >= setsNeeded && player2Wins > player1Wins) {
    winnerId = props.match.player2?.id || null;
    winnerName = props.match.player2?.name || "";
    isValid = true;
  } else if (totalSets > 0) {
    errorMessage = "比赛尚未结束，请继续录入比分";
  }

  calculatedWinner.value = winnerId;
  matchResult.value = {
    player1Wins,
    player2Wins,
    winnerId,
    winnerName,
    isValid,
    errorMessage,
  };
}

function handleSubmit() {
  for (const set of scores.value) {
    if (set.player1 < 0 || set.player2 < 0) {
      ElMessage.error("比分不能为负数");
      return;
    }
  }

  if (!props.match) return;

  // 计算胜者
  calculateWinner();

  emit("submit", {
    matchId: props.match.id,
    sets: scores.value,
    winnerId: matchResult.value?.winnerId || undefined,
  });
  dialogVisible.value = false;
}
</script>

<style scoped>
.match-info {
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-size: 18px;
}

.player-name {
  min-width: 100px;
  padding: 8px 16px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  text-align: center;
  border-radius: 8px;
  transition: all 0.3s;
}

.player-name.winner {
  color: white;
  background: var(--el-color-success);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.dark .player-name.winner {
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.5);
}

.vs {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.scores {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.score-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.set-label {
  width: 60px;
  color: var(--el-text-color-secondary);
}

.score-separator {
  font-size: 20px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
}

.result-info {
  margin-top: 20px;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.winner-text {
  font-size: 16px;
  color: var(--el-color-success);
}

.error-text {
  font-size: 14px;
  color: var(--el-color-warning);
}
</style>
