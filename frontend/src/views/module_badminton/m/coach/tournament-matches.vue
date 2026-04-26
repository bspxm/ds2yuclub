<template>
  <div class="matches-page">
    <van-loading v-if="loading" size="24px" class="loading" />
    <van-empty v-else-if="matches.length === 0" description="暂无对阵" />

    <template v-else>
      <van-tabs v-if="groups.length > 1" v-model:active="activeGroup">
        <van-tab v-for="g in groups" :key="g.id" :title="g.group_name" />
      </van-tabs>

      <div class="match-list">
        <div
          v-for="m in currentMatches"
          :key="m.id"
          class="match-card"
          @click="router.push(`/m/badminton/coach/match-score/${route.params.id}/${m.id}`)"
        >
          <div class="match-players">
            <span class="player">{{ m.player1?.name || "待定" }}</span>
            <span class="vs">VS</span>
            <span class="player">{{ m.player2?.name || "待定" }}</span>
          </div>
          <div v-if="m.scores && m.scores.length > 0" class="match-scores">
            <span v-for="(set, i) in m.scores" :key="i" class="set-score">
              {{ set.player1 }}:{{ set.player2 }}
            </span>
          </div>
          <div v-else class="match-status">
            <van-tag round :type="m.status === 'completed' ? 'success' : 'warning'">
              {{ m.status === "completed" ? "已结束" : "待比赛" }}
            </van-tag>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showToast } from "vant";
import { TournamentAPIExtended } from "@/api/module_badminton/tournament";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const matches = ref<any[]>([]);
const groups = ref<any[]>([]);
const activeGroup = ref(0);

const currentMatches = computed(() => {
  if (groups.value.length <= 1) return matches.value;
  const group = groups.value[activeGroup.value];
  if (!group) return matches.value;
  return matches.value.filter((m: any) => m.group_id === group.id);
});

async function loadData() {
  const tournamentId = Number(route.params.id);
  if (!tournamentId) return;

  loading.value = true;
  try {
    const [matchRes, groupStageRes] = await Promise.all([
      TournamentAPIExtended.getMatches(tournamentId),
      TournamentAPIExtended.getGroupStageData(tournamentId).catch(() => null),
    ]);

    matches.value = matchRes.data.data || [];

    if (groupStageRes?.data?.data?.groups) {
      groups.value = groupStageRes.data.data.groups;
    } else {
      const uniqueGroups = new Map();
      for (const m of matches.value) {
        if (m.group_id && !uniqueGroups.has(m.group_id)) {
          uniqueGroups.set(m.group_id, {
            id: m.group_id,
            group_name: m.group_name || `第${uniqueGroups.size + 1}组`,
          });
        }
      }
      groups.value = Array.from(uniqueGroups.values());
    }
  } catch (e: any) {
    showToast(e.response?.data?.msg || "加载失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.matches-page {
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.match-list {
  padding: 12px 16px;
}

.match-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  margin-bottom: 10px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.match-players {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 500;
}

.vs {
  font-size: 12px;
  font-weight: 400;
  color: #999;
}

.match-scores {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.set-score {
  padding: 2px 8px;
  font-size: 13px;
  background: #f5f5f5;
  border-radius: 4px;
}

.match-status {
  text-align: center;
}
</style>
