<template>
  <div class="tournament-page">
    <van-tabs v-model:active="activeType" class="type-tabs" @change="onTypeChange">
      <van-tab title="全部" name="" />
      <van-tab title="小组赛" name="PURE_GROUP" />
      <van-tab title="单败淘汰赛" name="SINGLE_ELIMINATION" />
      <van-tab title="锦标赛" name="CHAMPIONSHIP" />
      <van-tab title="抢位赛" name="PROMOTION_RELEGATION" />
    </van-tabs>

    <van-loading v-if="loading" size="24px" class="loading" />

    <van-empty v-else-if="filteredTournaments.length === 0" description="暂无赛事" />

    <van-pull-refresh v-else v-model="refreshing" @refresh="onRefresh">
      <div class="tournament-list">
        <div
          v-for="t in filteredTournaments"
          :key="t.id"
          class="tournament-card"
          :class="statusClass(t.status)"
          @click="router.push(`/m/badminton/coach/tournament-matches/${t.id}`)"
        >
          <div class="card-top">
            <span class="card-status">{{ statusText(t.status) }}</span>
            <span class="card-type">{{ typeText(t.tournament_type) }}</span>
          </div>
          <div class="card-name">{{ t.name }}</div>
          <div class="card-meta">
            <span class="meta-date">{{ t.start_date }}~{{ t.end_date || "待定" }}</span>
            <span v-if="t.participant_count" class="meta-count">
              <van-icon name="friends-o" />
              {{ t.participant_count }}人
            </span>
          </div>
          <van-icon name="arrow" class="card-arrow" />
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import TournamentAPI from "@/api/module_badminton/tournament";

const route = useRoute();
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
const activeType = ref((route.query.type as string) || "");

const filteredTournaments = computed(() => {
  if (!activeType.value) return tournaments.value;
  return tournaments.value.filter((t) => t.tournament_type === activeType.value);
});

function onTypeChange() {
  router.replace({ query: activeType.value ? { type: activeType.value } : {} });
}

function statusClass(status: string): string {
  if (status === "ACTIVE") return "status-active";
  if (status === "COMPLETED") return "status-completed";
  return "status-draft";
}

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
    PURE_GROUP: "小组赛",
    PROMOTION_RELEGATION: "抢位赛",
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

.type-tabs {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--mobile-tab-bg);
}

.loading {
  margin-top: 60px;
}

.tournament-list {
  padding: 4px 0;
}

.tournament-card {
  position: relative;
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
  border-left: 4px solid var(--mobile-text-muted);
}

.tournament-card:active {
  opacity: 0.7;
}

.tournament-card.status-active {
  border-left-color: var(--mobile-green);
}

.tournament-card.status-completed {
  border-left-color: var(--mobile-text-muted);
}

.tournament-card.status-draft {
  border-left-color: var(--mobile-orange);
}

.card-top {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
}

.card-status {
  display: inline-block;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 500;
  line-height: 18px;
  color: #fff;
  border-radius: 10px;
}

.status-active .card-status {
  background: var(--mobile-green);
}

.status-completed .card-status {
  background: var(--mobile-text-muted);
}

.status-draft .card-status {
  background: var(--mobile-orange);
}

.card-type {
  padding: 1px 6px;
  font-size: 11px;
  color: var(--mobile-text-secondary);
  background: var(--mobile-gray-bg);
  border-radius: 4px;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: var(--mobile-text-muted);
}

.meta-count {
  display: inline-flex;
  gap: 2px;
  align-items: center;
}

.card-arrow {
  position: absolute;
  top: 50%;
  right: 12px;
  font-size: 14px;
  color: var(--mobile-text-muted);
  transform: translateY(-50%);
}
</style>
