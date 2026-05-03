<template>
  <div class="history-page">
    <van-loading v-if="loading" size="24px" class="loading-center" />
    <van-empty v-else-if="tournaments.length === 0" description="暂无历史赛事" />
    <template v-else>
      <van-cell-group inset>
        <van-cell
          v-for="t in tournaments"
          :key="t.id"
          is-link
          :title="t.tournament_name"
          :label="`${t.start_date}~${t.end_date}`"
          @click="onTournamentClick(t)"
        >
          <template #value>
            <span v-if="t.final_rank" class="rank-badge">第{{ t.final_rank }}名</span>
            <span v-else-if="t.matches_played > 0" class="record-text">
              {{ t.matches_won }}W/{{ t.matches_lost }}L
            </span>
          </template>
        </van-cell>
      </van-cell-group>
    </template>

    <van-action-sheet v-model:show="showDetail" :title="selected?.tournament_name">
      <div v-if="selected" class="detail-content">
        <van-cell-group>
          <van-cell
            title="状态"
            :value="
              selected.tournament_status === 'COMPLETED' ? '已结束' : selected.tournament_status
            "
          />
          <van-cell title="日期" :value="`${selected.start_date} ~ ${selected.end_date}`" />
          <van-cell
            v-if="selected.final_rank"
            title="最终排名"
            :value="`第${selected.final_rank}名`"
          />
          <van-cell title="参赛场次" :value="selected.matches_played" />
          <van-cell title="胜/负" :value="`${selected.matches_won} / ${selected.matches_lost}`" />
        </van-cell-group>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { showToast } from "vant";
import ParentStudentAPI from "@/api/module_badminton/parent-student";

const route = useRoute();
const loading = ref(false);
const tournaments = ref<any[]>([]);
const showDetail = ref(false);
const selected = ref<any>(null);

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

function onTournamentClick(t: any) {
  selected.value = t;
  showDetail.value = true;
}
</script>

<style scoped>
.history-page {
  min-height: 100vh;
  padding-bottom: 24px;
}

.loading-center {
  margin-top: 60px;
  display: flex;
  justify-content: center;
}

.rank-badge {
  font-size: 12px;
  color: var(--van-orange);
  font-weight: 500;
}

.record-text {
  font-size: 12px;
  color: var(--van-text-color-2);
}

.detail-content {
  padding: 16px;
}
</style>
