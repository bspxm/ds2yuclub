<template>
  <div class="parent-tournament-page">
    <van-loading v-if="loading" size="24px" class="loading" />
    <van-empty v-else-if="tournaments.length === 0" description="暂无比赛记录" />

    <van-pull-refresh v-else v-model="refreshing" @refresh="onRefresh">
      <van-card
        v-for="t in tournaments"
        :key="t.id"
        :title="t.name"
        :desc="t.description"
        :tag="statusText(t.status)"
        @click="
          selectedTournament = t;
          showMatches = true;
        "
      >
        <template #tags>
          <van-tag plain type="primary">{{ t.start_date }}~{{ t.end_date }}</van-tag>
        </template>
      </van-card>
    </van-pull-refresh>

    <van-action-sheet
      v-model:show="showMatches"
      :title="selectedTournament?.name"
      close-on-click-action
    >
      <div v-if="!matchLoading && matches.length === 0" style="padding: 20px; text-align: center">
        暂无比赛记录
      </div>
      <div v-else class="match-sheet-list">
        <div v-for="m in matches" :key="m.id" class="match-sheet-item">
          <div class="match-players">
            <span :class="{ win: m.winner_id === m.player1?.id }">{{ m.player1?.name }}</span>
            <span class="vs">VS</span>
            <span :class="{ win: m.winner_id === m.player2?.id }">{{ m.player2?.name }}</span>
          </div>
          <div v-if="m.scores" class="match-scores">
            <span v-for="(s, i) in m.scores" :key="i" class="score-badge">
              {{ s.player1 }}:{{ s.player2 }}
            </span>
          </div>
          <div v-else class="pending-text">未开始</div>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import TournamentAPI, { TournamentAPIExtended } from "@/api/module_badminton/tournament";

interface Tournament {
  id: number;
  name: string;
  description?: string;
  status: string;
  start_date: string;
  end_date?: string;
}

const loading = ref(false);
const refreshing = ref(false);
const tournaments = ref<Tournament[]>([]);
const selectedTournament = ref<Tournament | null>(null);
const showMatches = ref(false);
const matches = ref<any[]>([]);
const matchLoading = ref(false);

function statusText(status: string): string {
  const map: Record<string, string> = { DRAFT: "草稿", ACTIVE: "进行中", COMPLETED: "已结束" };
  return map[status] || status;
}

async function loadData() {
  loading.value = true;
  try {
    const res = await TournamentAPI.getTournamentList();
    tournaments.value = (res.data.data || []).filter((t: any) => t.status !== "DRAFT");
  } catch {
    tournaments.value = [];
  } finally {
    loading.value = false;
  }
}

async function onRefresh() {
  await loadData();
  refreshing.value = false;
}

watch(showMatches, async (val) => {
  if (val && selectedTournament.value) {
    matchLoading.value = true;
    try {
      const res = await TournamentAPIExtended.getMatches(selectedTournament.value.id);
      matches.value = res.data.data || [];
    } catch {
      matches.value = [];
    } finally {
      matchLoading.value = false;
    }
  }
});

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.parent-tournament-page {
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.match-sheet-list {
  padding: 16px;
}

.match-sheet-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.match-players {
  display: flex;
  gap: 12px;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.match-players .win {
  color: #07c160;
}

.vs {
  font-size: 12px;
  font-weight: 400;
  color: #999;
}

.match-scores {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-top: 6px;
}

.score-badge {
  padding: 2px 8px;
  font-size: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.pending-text {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
  text-align: center;
}
</style>
