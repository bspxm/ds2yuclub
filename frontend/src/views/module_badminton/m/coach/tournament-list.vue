<template>
  <div class="tournament-page">
    <van-loading v-if="loading" size="24px" class="loading" />
    <van-empty v-else-if="tournaments.length === 0" description="暂无赛事" />

    <van-pull-refresh v-else v-model="refreshing" @refresh="onRefresh">
      <van-card
        v-for="t in tournaments"
        :key="t.id"
        :title="t.name"
        :desc="t.description"
        :tag="statusText(t.status)"
        @click="router.push(`/m/badminton/coach/tournament-matches/${t.id}`)"
      >
        <template #tags>
          <van-tag plain type="primary">{{ typeText(t.tournament_type) }}</van-tag>
          <van-tag plain type="primary">{{ t.start_date }}~{{ t.end_date }}</van-tag>
        </template>
        <template #footer>
          <span v-if="t.participant_count" class="participant-count">
            {{ t.participant_count }}人参赛
          </span>
        </template>
      </van-card>
    </van-pull-refresh>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import TournamentAPI from "@/api/module_badminton/tournament";

const router = useRouter();

interface Tournament {
  id: number;
  name: string;
  description?: string;
  status: string;
  tournament_type: string;
  start_date: string;
  end_date?: string;
  participant_count?: number;
}

const tournaments = ref<Tournament[]>([]);
const loading = ref(false);
const refreshing = ref(false);

function statusText(status: string): string {
  const map: Record<string, string> = {
    DRAFT: "草稿",
    ACTIVE: "进行中",
    COMPLETED: "已结束",
  };
  return map[status] || status;
}

function typeText(type: string): string {
  const map: Record<string, string> = {
    CHAMPIONSHIP: "锦标赛",
    PURE_GROUP: "纯小组赛",
    PROMOTION_RELEGATION: "定区升降赛",
    SINGLE_ELIMINATION: "单败淘汰赛",
  };
  return map[type] || type;
}

async function loadData() {
  loading.value = true;
  try {
    const res = await TournamentAPI.getTournamentList();
    tournaments.value = res.data.data || [];
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

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.tournament-page {
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.participant-count {
  font-size: 12px;
  color: #999;
}
</style>
