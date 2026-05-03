<template>
  <div class="history-page">
    <van-loading v-if="loading" size="24px" class="loading-center" />
    <van-empty v-else-if="tournaments.length === 0" description="暂无历史赛事" />

    <template v-else>
      <div
        v-for="t in tournaments"
        :key="t.id"
        class="tournament-card"
        @click="router.push(`/m/badminton/parent/tournament-detail/${t.tournament_id}`)"
      >
        <div class="card-top">
          <div class="card-name">{{ t.tournament_name }}</div>
          <div class="card-badges">
            <van-tag type="default" size="small">已结束</van-tag>
            <van-tag v-if="t.tournament_type" plain size="small" class="type-tag">
              {{ typeText(t.tournament_type) }}
            </van-tag>
          </div>
        </div>

        <div class="card-meta">
          <van-icon name="calendar-o" />
          <span>{{ t.start_date }}~{{ t.end_date }}</span>
        </div>

        <div v-if="t.description" class="card-desc">{{ t.description }}</div>

        <div class="card-stats">
          <div class="stat-item">
            <span class="stat-value">{{ t.matches_played }}</span>
            <span class="stat-label">参赛场次</span>
          </div>
          <div class="stat-item">
            <span class="stat-value win">{{ t.matches_won }}</span>
            <span class="stat-label">胜</span>
          </div>
          <div class="stat-item">
            <span class="stat-value lose">{{ t.matches_lost }}</span>
            <span class="stat-label">负</span>
          </div>
          <div v-if="t.final_rank" class="stat-item rank">
            <span class="stat-value rank-value">#{{ t.final_rank }}</span>
            <span class="stat-label">最终排名</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showToast } from "vant";
import ParentStudentAPI from "@/api/module_badminton/parent-student";

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const tournaments = ref<any[]>([]);

const typeMap: Record<string, string> = {
  CHAMPIONSHIP: "锦标赛",
  PURE_GROUP: "小组赛",
  PROMOTION_RELEGATION: "抢位赛",
  SINGLE_ELIMINATION: "单败淘汰赛",
  ROUND_ROBIN: "循环赛",
};

function typeText(type: string): string {
  return typeMap[type] || type;
}

onMounted(async () => {
  const studentId = Number(route.query.student_id);
  if (!studentId) {
    showToast("缺少学员ID");
    return;
  }
  loading.value = true;
  try {
    const res = await ParentStudentAPI.getMyStudentTournaments(studentId);
    tournaments.value = (res.data.data || []).filter(
      (t: any) => t.tournament_status === "COMPLETED"
    );
  } catch {
    tournaments.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.history-page {
  min-height: 100vh;
  padding: 12px 16px 24px;
}

.loading-center {
  margin-top: 60px;
  display: flex;
  justify-content: center;
}

.tournament-card {
  padding: 16px;
  margin-bottom: 12px;
  background: var(--mobile-card-bg);
  border-radius: 12px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
  cursor: pointer;
  transition: opacity 0.15s;
}
.tournament-card:active {
  opacity: 0.7;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.card-name {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  line-height: 1.4;
}

.card-badges {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.type-tag {
  margin-left: 2px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--mobile-text-muted);
  margin-bottom: 6px;
}

.card-desc {
  font-size: 13px;
  color: var(--mobile-text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-stats {
  display: flex;
  gap: 0;
  border-top: 1px solid var(--mobile-border-light);
  padding-top: 12px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--mobile-text-primary);
}

.stat-value.win {
  color: var(--van-green, #07c160);
}

.stat-value.lose {
  color: var(--van-red, #ee0a24);
}

.stat-value.rank-value {
  color: var(--van-orange, #e6a23c);
}

.stat-label {
  display: block;
  font-size: 11px;
  color: var(--mobile-text-muted);
  margin-top: 2px;
}
</style>
