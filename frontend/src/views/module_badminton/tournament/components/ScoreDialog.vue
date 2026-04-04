<template>
  <el-dialog v-model="dialogVisible" title="录入比分" width="500px" @close="dialogVisible = false">
    <div v-if="match">
      <div class="match-info">
        <span class="player-name">{{ match.player1?.name }}</span>
        <span class="vs">VS</span>
        <span class="player-name">{{ match.player2?.name }}</span>
      </div>

      <el-divider />

      <div class="scores">
        <div v-for="(set, index) in scores" :key="index" class="score-row">
          <span class="set-label">第{{ index + 1 }}局</span>
          <el-input-number v-model="set.player1" :min="0" :max="99" size="large" />
          <span class="score-separator">:</span>
          <el-input-number v-model="set.player2" :min="0" :max="99" size="large" />
          <el-button v-if="scores.length > 1" type="danger" link @click="removeSet(index)">
            删除
          </el-button>
        </div>
      </div>

      <el-button type="primary" link @click="addSet">+ 添加局数</el-button>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确认</el-button>
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

const props = defineProps<{
  visible: boolean;
  match: {
    id: number;
    player1: { id: number; name: string };
    player2: { id: number; name: string };
    scores?: { player1: number; player2: number }[];
  } | null;
}>();

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "submit", data: { matchId: number; sets: SetScore[] }): void;
}>();

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit("update:visible", val),
});

const scores = ref<SetScore[]>([
  { player1: 0, player2: 0 },
]);

const currentSet = ref(1);

watch(
  () => props.visible,
  (val) => {
    if (val && props.match) {
      // 如果有已有比分数据，加载它
      if (props.match.scores && props.match.scores.length > 0) {
        scores.value = props.match.scores.map((s: any) => ({
          player1: typeof s.player1 === 'number' ? s.player1 : 0,
          player2: typeof s.player2 === 'number' ? s.player2 : 0,
        }));
      } else {
        // 默认只显示一局
        scores.value = [{ player1: 0, player2: 0 }];
      }
      currentSet.value = 1;
    }
  }
);

function addSet() {
  if (scores.value.length < 5) {
    scores.value.push({ player1: 0, player2: 0 });
    currentSet.value = scores.value.length;
  }
}

function removeSet(index: number) {
  if (scores.value.length > 1) {
    scores.value.splice(index, 1);
    if (currentSet.value > scores.value.length) {
      currentSet.value = scores.value.length;
    }
  }
}

function handleSubmit() {
  for (const set of scores.value) {
    if (set.player1 < 0 || set.player2 < 0) {
      ElMessage.error("比分不能为负数");
      return;
    }
    if (set.player1 === 0 && set.player2 === 0) {
      ElMessage.error("请输入有效的比分");
      return;
    }
  }

  if (!props.match) return;

  emit("submit", {
    matchId: props.match.id,
    sets: scores.value,
  });
  dialogVisible.value = false;
}
</script>

<style scoped>
.match-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  font-size: 18px;
}

.player-name {
  font-weight: bold;
  min-width: 100px;
  text-align: center;
}

.vs {
  color: #999;
}

.scores {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.score-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.set-label {
  width: 60px;
  color: #666;
}

.score-separator {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}
</style>
