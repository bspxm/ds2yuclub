<template>
  <div class="matches-page">
    <van-loading v-if="loading" size="24px" class="loading" />

    <template v-else-if="tournament">
      <div class="tournament-header">
        <div class="header-top">
          <div class="header-name">{{ tournament.name }}</div>
          <van-tag :type="statusType" size="medium">{{ statusLabel }}</van-tag>
        </div>
        <div class="header-meta">
          <span>{{ typeLabel }}</span>
          <span v-if="tournament.start_date">
            {{ tournament.start_date }}~{{ tournament.end_date || "待定" }}
          </span>
        </div>
      </div>

      <van-tabs v-model:active="viewTab" class="view-tabs">
        <van-tab v-if="isGroupStageType" title="小组赛" name="groupStage" />
        <van-tab v-if="isKnockoutType || isChampionshipType" title="淘汰赛" name="knockout" />
        <van-tab v-if="isPromotionType" title="位置板" name="position" />
      </van-tabs>

      <div v-if="viewTab === 'groupStage'" class="gs-view">
        <div v-if="groupStageData?.groups?.length" class="gs-group-selector">
          <van-field
            :model-value="selectedGroupName"
            is-link
            readonly
            label="选择小组"
            placeholder="全部小组"
            @click="showGroupPicker = true"
          />
          <van-popup v-model:show="showGroupPicker" round position="bottom">
            <van-picker
              :columns="groupPickerColumns"
              @confirm="onGroupPickerConfirm"
              @cancel="showGroupPicker = false"
            />
          </van-popup>
        </div>

        <template v-if="currentGroupData">
          <div class="gs-section">
            <div class="gs-section-title">积分排名</div>
            <div class="gs-rankings">
              <div class="gs-rank-header">
                <span class="gs-rank-col rank">#</span>
                <span class="gs-rank-col name">选手</span>
                <span class="gs-rank-col num">场</span>
                <span class="gs-rank-col num">胜</span>
                <span class="gs-rank-col num">负</span>
                <span class="gs-rank-col num">得分</span>
                <span class="gs-rank-col num">失分</span>
                <span class="gs-rank-col num">净胜</span>
              </div>
              <div
                v-for="(r, i) in currentGroupData.rankings"
                :key="r.id || i"
                class="gs-rank-row"
                :class="{ 'gs-rank-top': i < 3 }"
              >
                <span class="gs-rank-col rank">
                  <span class="rank-badge" :class="'rank-' + (i + 1)">{{ i + 1 }}</span>
                </span>
                <span class="gs-rank-col name">{{ r.student_name }}</span>
                <span class="gs-rank-col num">{{ r.total_points }}</span>
                <span class="gs-rank-col num">{{ r.matches_played }}</span>
                <span v-if="tournament.tournament_type !== 'CHAMPIONSHIP'" class="gs-rank-col num">
                  {{ r.wins }}-{{ r.losses }}
                </span>
                <span v-else class="gs-rank-col num">{{ r.wins }}</span>
                <span v-if="tournament.tournament_type !== 'CHAMPIONSHIP'" class="gs-rank-col num">
                  {{ r.draws > 0 ? r.draws + "平" : "-" }}
                </span>
                <span class="gs-rank-col num">{{ r.sets_won || 0 }}-{{ r.sets_lost || 0 }}</span>
                <span class="gs-rank-col num">{{ r.points_scored }}</span>
                <span class="gs-rank-col num">{{ r.points_conceded }}</span>
                <span
                  class="gs-rank-col num"
                  :class="r.points_scored - r.points_conceded > 0 ? 'positive' : 'negative'"
                >
                  {{ r.points_scored - r.points_conceded > 0 ? "+" : ""
                  }}{{ r.points_scored - r.points_conceded }}
                </span>
              </div>
            </div>
          </div>

          <div class="gs-section">
            <div class="gs-section-title">对阵矩阵</div>
            <div class="gs-matrix">
              <table>
                <thead>
                  <tr>
                    <th></th>
                    <th v-for="col in currentGroupData.matrix" :key="col.participant_id">
                      {{ col.student_name }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, ri) in currentGroupData.matrix" :key="row.id || ri">
                    <td class="gs-matrix-name">{{ row.student_name }}</td>
                    <td
                      v-for="(result, ci) in row.results"
                      :key="ci"
                      :class="[
                        'gs-matrix-cell',
                        result?.win
                          ? 'win'
                          : result?.loss
                            ? 'loss'
                            : result?.draw
                              ? 'draw'
                              : 'empty',
                      ]"
                    >
                      <template v-if="ri !== ci">
                        <div class="gs-matrix-cell-inner">
                          <template v-if="result">
                            <div class="gs-matrix-detail">{{ result.detail_score || "-" }}</div>
                            <div class="gs-matrix-result">
                              {{ result.win ? "胜" : result.draw ? "平" : "负" }}
                            </div>
                            <div class="gs-matrix-score">{{ result.score }}</div>
                          </template>
                          <template v-else>
                            <span class="gs-matrix-pending">-</span>
                          </template>
                        </div>
                      </template>
                      <template v-else>
                        <span class="gs-matrix-diag">—</span>
                      </template>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
        <van-empty v-else-if="!groupStageData?.groups?.length" description="暂无小组赛数据" />
      </div>

      <div v-if="viewTab === 'knockout'" class="ko-view">
        <van-loading v-if="loadingKnockout" size="24px" />
        <template v-else-if="knockoutData?.matches?.length">
          <div class="ko-bracket-scroll">
            <KnockoutBracketView
              :matches="knockoutData.matches"
              :total-rounds="knockoutData.total_rounds"
            />
          </div>
        </template>
        <van-empty v-else description="暂无淘汰赛数据" />
      </div>

      <div v-if="viewTab === 'position'" class="pos-view">
        <div class="pos-section-title">当前位置</div>
        <div v-if="positions.length > 0" class="pos-list">
          <div
            v-for="(p, i) in sortedPositions"
            :key="p.participant_id"
            class="pos-item"
            :class="{ 'pos-top': i === 0 }"
          >
            <div class="pos-number">{{ p.current_position }}号位</div>
            <div class="pos-name">{{ p.student_name }}</div>
          </div>
        </div>
        <van-empty v-else description="暂无位置数据" />

        <div class="pos-section-title" style="margin-top: 24px">比赛记录</div>
        <div v-if="prMatches.length === 0" class="empty-hint">暂无比赛记录</div>
        <div v-else class="pr-match-list">
          <div v-for="m in prMatches" :key="m.id" class="pr-card">
            <div class="pr-round">第{{ m.round_number }}轮</div>
            <div class="pr-body">
              <div class="pr-row">
                <span class="pr-label">场地</span>
                <span class="pr-value">{{ m.match_number }}号</span>
              </div>
              <div class="pr-row">
                <span class="pr-label">选手1</span>
                <span
                  class="pr-value"
                  :class="{ 'is-winner': m.winner_id && m.winner_id === m.player1_id }"
                >
                  {{ m.player1_name || "待定" }}
                  <van-icon
                    v-if="m.winner_id && m.winner_id === m.player1_id"
                    name="success"
                    class="winner-icon"
                  />
                </span>
              </div>
              <div class="pr-row">
                <span class="pr-label">选手2</span>
                <span
                  class="pr-value"
                  :class="{ 'is-winner': m.winner_id && m.winner_id === m.player2_id }"
                >
                  {{ m.player2_name || "待定" }}
                  <van-icon
                    v-if="m.winner_id && m.winner_id === m.player2_id"
                    name="success"
                    class="winner-icon"
                  />
                </span>
              </div>
              <div class="pr-row">
                <span class="pr-label">比分</span>
                <span class="pr-value pr-score">
                  <template v-if="m.scores?.sets?.length">
                    <span
                      v-for="(set, i) in m.scores.sets"
                      :key="i"
                      class="pr-set"
                      :class="prSetWinner(m, set)"
                    >
                      {{ set.player1 || 0 }}:{{ set.player2 || 0 }}
                    </span>
                  </template>
                  <span v-else class="pr-no-score">-</span>
                </span>
              </div>
              <div class="pr-row">
                <span class="pr-label">胜者</span>
                <span class="pr-value pr-winner">
                  <template v-if="m.winner_id">
                    {{ m.winner_id === m.player1_id ? m.player1_name : m.player2_name }}
                  </template>
                  <van-tag v-else round type="warning">进行中</van-tag>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <van-empty v-else description="赛事信息不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { showToast } from "vant";
import TournamentAPI, { TournamentAPIExtended } from "@/api/module_badminton/tournament";
import KnockoutBracketView from "@/views/module_badminton/tournament/components/KnockoutBracketView.vue";

const route = useRoute();

const loading = ref(false);
const loadingKnockout = ref(false);
const tournament = ref<any>(null);
const viewTab = ref("groupStage");
const groupStageData = ref<any>(null);
const knockoutData = ref<any>(null);
const positions = ref<any[]>([]);
const prMatches = ref<any[]>([]);
const selectedGroupId = ref<number | null>(null);
const showGroupPicker = ref(false);

const isGroupStageType = computed(
  () =>
    tournament.value?.tournament_type === "PURE_GROUP" ||
    tournament.value?.tournament_type === "CHAMPIONSHIP"
);
const isKnockoutType = computed(() => tournament.value?.tournament_type === "SINGLE_ELIMINATION");
const isChampionshipType = computed(() => tournament.value?.tournament_type === "CHAMPIONSHIP");
const isPromotionType = computed(
  () => tournament.value?.tournament_type === "PROMOTION_RELEGATION"
);

const statusType = computed(() => {
  const s = tournament.value?.status;
  if (s === "ACTIVE") return "success";
  if (s === "COMPLETED") return "default";
  return "warning";
});

const statusLabel = computed(() => {
  const s = tournament.value?.status;
  if (s === "ACTIVE") return "进行中";
  if (s === "COMPLETED") return "已结束";
  return "草稿";
});

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    CHAMPIONSHIP: "锦标赛",
    PURE_GROUP: "小组赛",
    PROMOTION_RELEGATION: "抢位赛",
    SINGLE_ELIMINATION: "单败淘汰赛",
  };
  return map[tournament.value?.tournament_type] || tournament.value?.tournament_type || "";
});

const selectedGroupName = computed(() => {
  if (!selectedGroupId.value || !groupStageData.value?.groups) return "";
  const g = groupStageData.value.groups.find((g: any) => g.id === selectedGroupId.value);
  return g?.name || "";
});

const currentGroupData = computed(() => {
  if (!groupStageData.value?.groups?.length) return null;
  if (!selectedGroupId.value) return groupStageData.value.groups[0]?.data || null;
  const g = groupStageData.value.groups.find((g: any) => g.id === selectedGroupId.value);
  return g?.data || groupStageData.value.groups[0]?.data || null;
});

const groupPickerColumns = computed(() => {
  if (!groupStageData.value?.groups) return [];
  return groupStageData.value.groups.map((g: any) => ({ text: g.name, value: g.id }));
});

const sortedPositions = computed(() => {
  return [...positions.value].sort((a: any, b: any) => a.current_position - b.current_position);
});

function onGroupPickerConfirm({ selectedValues }: any) {
  selectedGroupId.value = selectedValues[0];
  showGroupPicker.value = false;
}

function prSetWinner(m: any, set: any): string {
  if (m.status !== "completed") return "";
  const p1 = Number(set.player1) || 0;
  const p2 = Number(set.player2) || 0;
  if (p1 > p2) return "set-winner-p1";
  if (p2 > p1) return "set-winner-p2";
  return "";
}

async function loadTournament() {
  const tid = Number(route.params.tournamentId);
  try {
    const res = await TournamentAPI.getTournamentList();
    const list: any[] = res.data.data || [];
    tournament.value = list.find((t: any) => t.id === tid) || null;
  } catch {
    tournament.value = null;
  }
}

async function loadMatches() {
  const tid = Number(route.params.tournamentId);
  if (!tid) return;
  try {
    const [matchRes, groupStageRes] = await Promise.all([
      TournamentAPIExtended.getMatches(tid),
      TournamentAPIExtended.getGroupStageData(tid).catch(() => null),
    ]);
    if (groupStageRes?.data?.data?.groups) {
      groupStageData.value = groupStageRes.data.data;
    }
  } catch {
    /* silent */
  }
}

async function loadKnockoutData() {
  loadingKnockout.value = true;
  try {
    const res = await TournamentAPIExtended.getKnockoutData(Number(route.params.tournamentId));
    knockoutData.value = res.data.data;
  } catch {
    showToast("加载淘汰赛数据失败");
  } finally {
    loadingKnockout.value = false;
  }
}

async function loadPositions() {
  try {
    const res = await TournamentAPIExtended.getPositions(Number(route.params.tournamentId));
    positions.value = res.data.data || [];
  } catch {
    /* silent */
  }
}

async function loadPRMatches() {
  try {
    const res = await TournamentAPIExtended.getPRMatches(Number(route.params.tournamentId));
    prMatches.value = res.data?.data || [];
  } catch {
    /* silent */
  }
}

onMounted(async () => {
  loading.value = true;
  await loadTournament();
  if (isGroupStageType.value) {
    await loadMatches();
    viewTab.value = "groupStage";
  } else if (isKnockoutType.value) {
    viewTab.value = "knockout";
    await loadKnockoutData();
  } else if (isPromotionType.value) {
    viewTab.value = "position";
    await Promise.all([loadPositions(), loadPRMatches()]);
  }
  loading.value = false;
});
</script>

<style scoped>
.matches-page {
  padding-bottom: 24px;
}
.loading {
  margin-top: 60px;
}

.tournament-header {
  padding: 16px;
  margin-bottom: 8px;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}
.header-top {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}
.header-name {
  flex: 1;
  font-size: 17px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  line-height: 1.3;
}
.header-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--mobile-text-muted);
  margin-bottom: 12px;
}

.view-tabs {
  background: var(--mobile-tab-bg);
}

.empty-hint {
  padding: 40px 0;
  font-size: 14px;
  color: var(--mobile-text-muted);
  text-align: center;
}

.gs-view {
  padding: 12px 0;
}
.gs-group-selector {
  margin-bottom: 12px;
}
.gs-section {
  margin-bottom: 20px;
}
.gs-section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 10px;
}

.gs-rankings {
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
  overflow: hidden;
}
.gs-rank-header,
.gs-rank-row {
  display: flex;
  gap: 0;
  padding: 10px 8px;
  font-size: 12px;
  align-items: center;
}
.gs-rank-header {
  background: var(--mobile-rank-header-bg);
  font-weight: 600;
  color: var(--mobile-text-secondary);
}
.gs-rank-row {
  border-bottom: 1px solid var(--mobile-rank-row-border);
}
.gs-rank-row:last-child {
  border-bottom: none;
}
.gs-rank-top {
  background: var(--mobile-rank-top-bg);
}
.gs-rank-col {
  flex-shrink: 0;
  text-align: center;
}
.gs-rank-col.rank {
  width: 28px;
}
.gs-rank-col.name {
  flex: 1;
  text-align: left;
  padding-left: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--mobile-text-primary);
}
.gs-rank-col.num {
  width: 36px;
  color: var(--mobile-text-primary);
}
.rank-badge {
  display: inline-block;
  width: 22px;
  height: 22px;
  line-height: 22px;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  text-align: center;
}
.rank-1 {
  background: #e6a23c;
}
.rank-2 {
  background: #909399;
}
.rank-3 {
  background: #a78bfa;
}
.positive {
  color: var(--mobile-green-text);
  font-weight: 600;
}
.negative {
  color: var(--mobile-red-text);
  font-weight: 600;
}

.gs-matrix {
  overflow-x: auto;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}
.gs-matrix table {
  border-collapse: collapse;
  font-size: 12px;
  min-width: 100%;
}
.gs-matrix th,
.gs-matrix td {
  padding: 8px 6px;
  text-align: center;
  border: 1px solid var(--mobile-border);
  white-space: nowrap;
}
.gs-matrix th {
  background: var(--mobile-matrix-th-bg);
  font-weight: 600;
  color: var(--mobile-text-secondary);
}
.gs-matrix-name {
  font-weight: 500;
  color: var(--mobile-text-primary);
  background: var(--mobile-matrix-td-bg);
}
.gs-matrix-cell.win {
  background: var(--mobile-matrix-win-bg);
}
.gs-matrix-cell.loss {
  background: var(--mobile-matrix-loss-bg);
}
.gs-matrix-cell.draw {
  background: var(--mobile-matrix-draw-bg);
}
.gs-matrix-cell {
  min-width: 76px;
}
.gs-matrix-score {
  font-weight: 600;
  font-size: 14px;
  color: var(--mobile-text-primary);
}
.gs-matrix-detail {
  font-size: 10px;
  color: var(--mobile-text-secondary);
  margin-top: 1px;
  white-space: normal;
  word-break: break-all;
  line-height: 1.3;
}
.gs-matrix-result {
  font-size: 10px;
  color: var(--mobile-text-muted);
  margin-top: 2px;
}
.gs-matrix-diag {
  color: var(--mobile-border);
}
.gs-matrix-pending {
  color: var(--mobile-border);
}
.gs-matrix-cell-inner {
  min-width: 52px;
  padding: 4px 2px;
  border-radius: 4px;
}

.ko-view {
  padding: 12px 0;
}
.ko-bracket-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 12px;
}

.pos-view {
  padding: 12px 0;
}
.pos-section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 10px;
}
.pos-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pos-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: var(--mobile-card-bg);
  border-left: 4px solid var(--mobile-text-muted);
  border-radius: 8px;
  gap: 12px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}
.pos-top {
  background: var(--mobile-orange-bg);
  border-left-color: #e6a23c;
}
.pos-number {
  font-size: 15px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  min-width: 60px;
}
.pos-name {
  flex: 1;
  font-size: 14px;
  color: var(--mobile-text-secondary);
}

.pr-match-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.pr-card {
  position: relative;
  padding: 14px 16px;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}
.pr-round {
  font-size: 12px;
  font-weight: 500;
  color: var(--mobile-text-muted);
  margin-bottom: 8px;
}
.pr-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.pr-row {
  display: flex;
  align-items: center;
  font-size: 13px;
}
.pr-label {
  width: 48px;
  flex-shrink: 0;
  color: var(--mobile-text-muted);
}
.pr-value {
  flex: 1;
  color: var(--mobile-text-primary);
}
.pr-value.is-winner {
  color: var(--mobile-green);
  font-weight: 600;
}
.winner-icon {
  margin-left: 4px;
  color: var(--mobile-green);
}
.pr-score {
  display: flex;
  gap: 6px;
}
.pr-set {
  padding: 1px 6px;
  font-size: 12px;
  background: var(--mobile-gray-bg);
  border-radius: 4px;
}
.pr-set.set-winner-p1,
.pr-set.set-winner-p2 {
  color: var(--mobile-winner-text);
  background: var(--mobile-winner-bg);
}
.pr-no-score {
  color: var(--mobile-text-muted);
}
.pr-winner {
  font-weight: 500;
}
</style>
