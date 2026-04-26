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
        <div class="header-stats">
          <div class="stat" :class="{ active: filterStatus === '' }" @click="setFilter('')">
            <span class="stat-value">{{ matchStats.total }}</span>
            <span class="stat-label">全部</span>
          </div>
          <div
            class="stat"
            :class="{ active: filterStatus === 'completed' }"
            @click="setFilter('completed')"
          >
            <span class="stat-value completed">{{ matchStats.completed }}</span>
            <span class="stat-label">已完成</span>
          </div>
          <div
            class="stat"
            :class="{ active: filterStatus === 'pending' }"
            @click="setFilter('pending')"
          >
            <span class="stat-value pending">{{ matchStats.pending }}</span>
            <span class="stat-label">待比赛</span>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <van-dropdown-menu class="filter-dropdown" active-color="#07c160">
          <van-dropdown-item
            v-model="selectedPlayerId"
            :options="playerOptions"
            @change="onPlayerFilterChange"
          />
        </van-dropdown-menu>
        <van-button
          v-if="tournament.status === 'ACTIVE'"
          class="end-btn"
          size="small"
          round
          @click="handleEndTournament"
        >
          <template #icon><van-icon name="stop-circle-o" /></template>
          结束赛事
        </van-button>
      </div>

      <van-tabs v-model:active="viewTab" class="view-tabs" @change="onViewTabChange">
        <van-tab title="对阵" name="matches" />
        <van-tab v-if="isGroupStageType" title="小组赛" name="groupStage" />
        <van-tab v-if="isKnockoutType || isChampionshipType" title="淘汰赛" name="knockout" />
        <van-tab v-if="isPromotionType" title="位置板" name="position" />
      </van-tabs>

      <template v-if="viewTab === 'matches'">
        <van-sticky v-if="visibleGroups.length > 1" offset-top="0">
          <van-tabs v-model:active="activeGroup" class="group-tabs">
            <van-tab v-for="g in visibleGroups" :key="g.id" :title="g.group_name" />
          </van-tabs>
        </van-sticky>

        <div v-if="filteredMatches.length === 0" class="empty-hint">暂无对阵</div>
        <div v-else class="match-list">
          <div
            v-for="m in filteredMatches"
            :key="m.id"
            class="match-card"
            :class="{ 'is-completed': m.status === 'completed' }"
            @click="goMatchScore(m.id)"
          >
            <div v-if="m.round_number" class="match-round">第{{ m.round_number }}轮</div>
            <div class="match-players">
              <div
                class="player-side"
                :class="{ 'is-winner': m.winner_id && m.winner_id === m.player1?.id }"
              >
                <div class="player-name">{{ m.player1?.name || "待定" }}</div>
                <div v-if="m.scores && m.scores.length > 0" class="player-score">
                  {{ totalScore(m.scores, 1) }}
                </div>
              </div>
              <div class="vs-section"><span class="vs-text">VS</span></div>
              <div
                class="player-side"
                :class="{ 'is-winner': m.winner_id && m.winner_id === m.player2?.id }"
              >
                <div class="player-name">{{ m.player2?.name || "待定" }}</div>
                <div v-if="m.scores && m.scores.length > 0" class="player-score">
                  {{ totalScore(m.scores, 2) }}
                </div>
              </div>
            </div>
            <div v-if="m.scores && m.scores.length > 0" class="sets-row">
              <span
                v-for="(set, i) in m.scores"
                :key="i"
                class="set-badge"
                :class="setWinner(m, set)"
              >
                {{ set.player1 }}:{{ set.player2 }}
              </span>
            </div>
            <div class="match-footer">
              <van-tag
                round
                :type="
                  tournament?.status === 'COMPLETED' || m.status === 'completed'
                    ? 'success'
                    : m.status === 'active'
                      ? 'warning'
                      : 'default'
                "
              >
                {{
                  tournament?.status === "COMPLETED" || m.status === "completed" ? "已结束" : m.status === "active" ? "进行中" : "待比赛"
                }}
              </van-tag>
              <van-icon name="arrow" class="footer-arrow" />
            </div>
          </div>
        </div>
      </template>

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
                    <th v-for="col in currentGroupData.matrix" :key="col.id || col.student_name">
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
                        <div
                          class="gs-matrix-cell-inner"
                          :class="{ clickable: tournament?.status !== 'COMPLETED' }"
                          @click.stop="handleMatrixCellClick(ri, ci)"
                        >
                          <template v-if="result">
                            <div class="gs-matrix-score">{{ result.score }}</div>
                            <div class="gs-matrix-result">
                              {{ result.win ? "胜" : result.draw ? "平" : "负" }}
                            </div>
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

      <!-- 小组赛录入比分弹窗 -->
      <van-popup v-model:show="showScoreDialog" position="bottom" round closeable class="score-popup" @closed="onScoreDialogClosed">
        <div v-if="scoreMatch" class="score-popup-content">
          <div class="scoreboard">
            <div class="sb-player" :class="{ 'is-winner': scoreWinnerId === scoreMatch.player1?.id }">
              <div class="sb-name">{{ scoreMatch.player1?.name || scoreMatch.player1?.student_name || "待定" }}</div>
              <div class="sb-score">{{ scoreSetsWon(1) }}</div>
            </div>
            <div class="sb-vs">
              <div class="sb-vs-text">VS</div>
              <div class="sb-vs-sub">大比分</div>
            </div>
            <div class="sb-player" :class="{ 'is-winner': scoreWinnerId === scoreMatch.player2?.id }">
              <div class="sb-name">{{ scoreMatch.player2?.name || scoreMatch.player2?.student_name || "待定" }}</div>
              <div class="sb-score">{{ scoreSetsWon(2) }}</div>
            </div>
          </div>

          <div class="sets-section">
            <div class="section-label">{{ scoreReadonly ? "历史比分" : "局分录入" }}</div>
            <div v-for="(set, index) in scoreSets" :key="index" class="set-block">
              <div class="set-header">
                <span class="set-title">第{{ index + 1 }}局</span>
                <van-button v-if="!scoreReadonly && scoreSets.length > 1" icon="delete" size="small" plain round @click="scoreRemoveSet(index)" />
              </div>
              <div class="set-body">
                <input v-model="set.player1" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="0" class="score-input" :readonly="scoreReadonly" maxlength="2" @input="!scoreReadonly && scoreCalculateWinner()">
                <span class="set-colon">:</span>
                <input v-model="set.player2" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="0" class="score-input" :readonly="scoreReadonly" maxlength="2" @input="!scoreReadonly && scoreCalculateWinner()">
              </div>
            </div>
            <van-button v-if="!scoreReadonly" icon="plus" block plain round class="add-set-btn" @click="scoreSets.push({ player1: '', player2: '' })">新增一局</van-button>
          </div>

          <div v-if="scoreResultText" class="result-banner" :class="scoreResultValid ? 'valid' : 'invalid'">
            <van-icon :name="scoreResultValid ? 'success' : 'cross'" />
            {{ scoreResultText }}
          </div>

          <div v-if="!scoreReadonly" class="submit-area">
            <van-button type="primary" block round size="large" :loading="scoreSubmitting" :disabled="!scoreResultValid" @click="scoreHandleSubmit">确认提交</van-button>
          </div>
        </div>
        <van-empty v-else description="比赛不存在" />
      </van-popup>

      <div v-if="viewTab === 'knockout'" class="ko-view">
        <van-loading v-if="loadingKnockout" size="24px" />
        <template v-else-if="knockoutData?.rounds">
          <div
            v-for="round in knockoutData.rounds"
            :key="round.key || round.label"
            class="ko-round"
          >
            <div class="ko-round-title">{{ round.label }}</div>
            <div
              v-for="m in round.matches"
              :key="m.id"
              class="match-card"
              @click="goMatchScore(m.id)"
            >
              <div class="match-players">
                <div
                  class="player-side"
                  :class="{ 'is-winner': m.winner_id && m.winner_id === m.player1?.id }"
                >
                  <div class="player-name">
                    {{ m.player1?.name || (m.round_number === 1 ? "轮空" : "等待对手") }}
                  </div>
                  <div v-if="m.scores && m.scores.length > 0" class="player-score">
                    {{ totalScore(m.scores, 1) }}
                  </div>
                </div>
                <div class="vs-section"><span class="vs-text">VS</span></div>
                <div
                  class="player-side"
                  :class="{ 'is-winner': m.winner_id && m.winner_id === m.player2?.id }"
                >
                  <div class="player-name">
                    {{ m.player2?.name || (m.round_number === 1 ? "轮空" : "等待对手") }}
                  </div>
                  <div v-if="m.scores && m.scores.length > 0" class="player-score">
                    {{ totalScore(m.scores, 2) }}
                  </div>
                </div>
              </div>
              <div v-if="m.scores && m.scores.length > 0" class="sets-row">
                <span
                  v-for="(set, i) in m.scores"
                  :key="i"
                  class="set-badge"
                  :class="setWinner(m, set)"
                >
                  {{ set.player1 }}:{{ set.player2 }}
                </span>
              </div>
              <van-tag v-if="tournament?.status === 'COMPLETED' || m.status === 'completed'" type="success" round :size="'small' as any">
                已结束
              </van-tag>
              <van-tag v-else-if="m.status === 'bye'" type="default" round :size="'small' as any">
                轮空
              </van-tag>
              <van-tag v-else type="warning" round :size="'small' as any">待比赛</van-tag>
            </div>
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
          <div v-for="m in prMatches" :key="m.id" class="pr-card" @click="goMatchScore(m.id)">
            <div class="pr-round">第{{ m.round_number }}轮</div>
            <div class="pr-body">
              <div class="pr-row">
                <span class="pr-label">场地</span>
                <span class="pr-value">{{ m.match_number }}号</span>
              </div>
              <div class="pr-row">
                <span class="pr-label">选手1</span>
                <span class="pr-value" :class="{ 'is-winner': m.winner_id && m.winner_id === m.player1_id }">
                  {{ m.player1_name || "待定" }}
                  <van-icon v-if="m.winner_id && m.winner_id === m.player1_id" name="success" class="winner-icon" />
                </span>
              </div>
              <div class="pr-row">
                <span class="pr-label">选手2</span>
                <span class="pr-value" :class="{ 'is-winner': m.winner_id && m.winner_id === m.player2_id }">
                  {{ m.player2_name || "待定" }}
                  <van-icon v-if="m.winner_id && m.winner_id === m.player2_id" name="success" class="winner-icon" />
                </span>
              </div>
              <div class="pr-row">
                <span class="pr-label">比分</span>
                <span class="pr-value pr-score">
                  <template v-if="m.scores?.sets?.length">
                    <span v-for="(set, i) in m.scores.sets" :key="i" class="pr-set" :class="prSetWinner(m, set)">{{ set.player1 || 0 }}:{{ set.player2 || 0 }}</span>
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
            <van-icon name="arrow" class="pr-arrow" />
          </div>
        </div>
      </div>
    </template>

    <van-empty v-else description="赛事信息不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showToast, showSuccessToast, showConfirmDialog } from "vant";
import TournamentAPI, { TournamentAPIExtended } from "@/api/module_badminton/tournament";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const loadingKnockout = ref(false);
const matches = ref<any[]>([]);
const groups = ref<any[]>([]);
const activeGroup = ref(Number(route.query.group) || 0);
const tournament = ref<any>(null);
const selectedPlayerId = ref((route.query.player as string) || "");
const filterStatus = ref((route.query.status as string) || "");
const viewTab = ref((route.query.view as string) || "matches");
const groupStageData = ref<any>(null);
const knockoutData = ref<any>(null);
const positions = ref<any[]>([]);
const prMatches = ref<any[]>([]);
const selectedGroupId = ref<number | null>(null);
const showGroupPicker = ref(false);

// 小组赛录入比分弹窗
const showScoreDialog = ref(false);
const scoreMatch = ref<any>(null);
const scoreSets = ref<{ player1: string; player2: string }[]>([{ player1: "", player2: "" }]);
const scoreWinnerId = ref<number | null>(null);
const scoreSubmitting = ref(false);
const scoreResultValid = ref(false);
const scoreResultText = ref("");

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

const visibleGroups = computed(() => {
  if (!selectedPlayerId.value) return groups.value;
  return groups.value;
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

const playerOptions = computed(() => {
  const map = new Map<number, string>();
  for (const m of matches.value) {
    if (m.player1?.id && m.player1?.name) map.set(m.player1.id, m.player1.name);
    if (m.player2?.id && m.player2?.name) map.set(m.player2.id, m.player2.name);
  }
  const opts = Array.from(map.entries())
    .map(([id, name]) => ({ text: name, value: String(id) }))
    .sort((a, b) => a.text.localeCompare(b.text, "zh-CN"));
  opts.unshift({ text: "全部选手", value: "" });
  return opts;
});

const filteredMatches = computed(() => {
  let list = matches.value;
  if (filterStatus.value === "completed")
    list = list.filter((m: any) => m.status?.toUpperCase() === "COMPLETED");
  else if (filterStatus.value === "pending")
    list = list.filter((m: any) => m.status?.toUpperCase() !== "COMPLETED");
  if (selectedPlayerId.value) {
    const pid = Number(selectedPlayerId.value);
    list = list.filter((m) => m.player1?.id === pid || m.player2?.id === pid);
  }
  if (visibleGroups.value.length > 1) {
    const group = visibleGroups.value[activeGroup.value];
    if (group) list = list.filter((m: any) => m.group_id === group.id);
  }
  return list;
});

const matchStats = computed(() => {
  const total = matches.value.length;
  const completed = matches.value.filter(
    (m: any) => m.status?.toUpperCase() === "COMPLETED"
  ).length;
  return { total, completed, pending: total - completed };
});

function setFilter(val: string) {
  filterStatus.value = filterStatus.value === val ? "" : val;
}

function syncFilters() {
  const query: Record<string, string> = {};
  if (filterStatus.value) query.status = filterStatus.value;
  if (selectedPlayerId.value) query.player = selectedPlayerId.value;
  if (activeGroup.value) query.group = String(activeGroup.value);
  if (viewTab.value !== "matches") query.view = viewTab.value;
  router.replace({ query });
}

function onPlayerFilterChange() {
  activeGroup.value = 0;
  syncFilters();
}

function onViewTabChange() {
  syncFilters();
  if (viewTab.value === "knockout" && !knockoutData.value) loadKnockoutData();
  if (viewTab.value === "position") {
    if (positions.value.length === 0) loadPositions();
    if (prMatches.value.length === 0) loadPRMatches();
  }
  if (viewTab.value === "groupStage") loadGroupStageOnly();
}

function onGroupPickerConfirm({ selectedValues }: any) {
  selectedGroupId.value = selectedValues[0];
  showGroupPicker.value = false;
}

function goMatchScore(matchId: number) {
  router.push(`/m/badminton/coach/match-score/${route.params.id}/${matchId}`);
}

function handleMatrixCellClick(ri: number, ci: number) {
  if (tournament.value?.status === "COMPLETED") return;
  const matrix = currentGroupData.value?.matrix;
  if (!matrix || !matrix[ri] || !matrix[ci]) return;
  const p1Id = matrix[ri].participant_id;
  const p2Id = matrix[ci].participant_id;
  if (!p1Id || !p2Id) return;
  const pid1 = (m: any) => m.player1_id ?? m.player1?.id;
  const pid2 = (m: any) => m.player2_id ?? m.player2?.id;
  const found = matches.value.find(
    (m: any) =>
      (pid1(m) === p1Id && pid2(m) === p2Id) ||
      (pid1(m) === p2Id && pid2(m) === p1Id)
  );
  if (!found) {
    showToast("找不到该对阵");
    return;
  }
  openScoreDialog(found);
}

const scoreReadonly = computed(
  () => scoreMatch.value?.status === "completed" || tournament.value?.status === "COMPLETED"
);

function scoreSetsWon(player: 1 | 2): number {
  let count = 0;
  for (const s of scoreSets.value) {
    const p1 = parseInt(s.player1) || 0;
    const p2 = parseInt(s.player2) || 0;
    if (p1 === 0 && p2 === 0) continue;
    if (player === 1 && p1 > p2) count++;
    if (player === 2 && p2 > p1) count++;
  }
  return count;
}

function scoreGetNumericSets() {
  return scoreSets.value.map((s) => ({
    player1: parseInt(s.player1) || 0,
    player2: parseInt(s.player2) || 0,
  }));
}

function scoreCalculateWinner() {
  const numSets = scoreGetNumericSets();
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
    scoreResultValid.value = false;
    scoreResultText.value = "";
    return;
  }
  const total = numSets.filter((s) => s.player1 !== 0 || s.player2 !== 0).length;
  const needed = Math.ceil(total / 2);
  if (p1Wins >= needed && p1Wins > p2Wins) {
    scoreWinnerId.value = scoreMatch.value?.player1?.id;
    scoreResultText.value = `胜者 ${scoreMatch.value?.player1?.name}  (${p1Wins}:${p2Wins})`;
    scoreResultValid.value = true;
  } else if (p2Wins >= needed && p2Wins > p1Wins) {
    scoreWinnerId.value = scoreMatch.value?.player2?.id;
    scoreResultText.value = `胜者 ${scoreMatch.value?.player2?.name}  (${p1Wins}:${p2Wins})`;
    scoreResultValid.value = true;
  } else {
    scoreResultValid.value = false;
    scoreResultText.value = "比赛尚未结束，请继续录入比分";
  }
}

function openScoreDialog(match: any) {
  scoreMatch.value = match;
  if (match.scores && match.scores.length > 0) {
    scoreSets.value = match.scores.map((s: any) => ({
      player1: String(s.player1),
      player2: String(s.player2),
    }));
  } else {
    scoreSets.value = [{ player1: "", player2: "" }];
  }
  scoreWinnerId.value = match.winner_id ?? null;
  scoreResultValid.value = false;
  scoreResultText.value = "";
  scoreCalculateWinner();
  showScoreDialog.value = true;
}

function scoreRemoveSet(index: number) {
  scoreSets.value.splice(index, 1);
  scoreCalculateWinner();
}

async function scoreHandleSubmit() {
  if (!scoreMatch.value) return;
  scoreSubmitting.value = true;
  try {
    const numSets = scoreGetNumericSets();
    for (const s of numSets) {
      if (s.player1 < 0 || s.player2 < 0) {
        showToast("比分不能为负数");
        return;
      }
    }
    await TournamentAPIExtended.recordScore(Number(route.params.id), scoreMatch.value.id, { sets: numSets });
    showSuccessToast("比分录入成功");
    showScoreDialog.value = false;
    await loadMatches();
  } catch (e: any) {
    showToast(e.response?.data?.msg || "提交失败");
  } finally {
    scoreSubmitting.value = false;
  }
}

function onScoreDialogClosed() {
  scoreMatch.value = null;
}

function totalScore(scores: any[], player: number): number {
  return scores.filter((s: any) => {
    const p1 = Number(s.player1);
    const p2 = Number(s.player2);
    return player === 1 ? p1 > p2 : p2 > p1;
  }).length;
}

function setWinner(m: any, set: any): string {
  if (m.status !== "completed") return "";
  const p1 = Number(set.player1);
  const p2 = Number(set.player2);
  if (p1 > p2) return "set-winner-p1";
  if (p2 > p1) return "set-winner-p2";
  return "";
}

async function handleEndTournament() {
  const tid = Number(route.params.id);
  const unfinished = matches.value.filter((m: any) => m.status?.toUpperCase() !== "COMPLETED");
  let message = `确认结束"${tournament.value?.name}"吗？结束后将不能再录入比分。`;
  if (unfinished.length > 0)
    message =
      `还有 ${unfinished.length} 场比赛未完成，结束赛事后未完成的比赛将无法录入比分。\n\n` +
      message;
  try {
    await showConfirmDialog({
      title: "结束赛事",
      message,
      confirmButtonText: "确认结束",
      cancelButtonText: "取消",
    });
    await TournamentAPIExtended.completeTournament(tid);
    showSuccessToast("赛事已结束");
    tournament.value.status = "COMPLETED";
    await loadMatches();
  } catch (e: any) {
    if (e !== "cancel") showToast(e?.response?.data?.msg || "操作失败");
  }
}

async function loadTournament() {
  const tid = Number(route.params.id);
  try {
    const res = await TournamentAPI.getTournamentList();
    const list: any[] = res.data.data || [];
    tournament.value = list.find((t: any) => t.id === tid) || null;
  } catch {
    tournament.value = null;
  }
}

async function loadMatches() {
  const tournamentId = Number(route.params.id);
  if (!tournamentId) return;
  try {
    const [matchRes, groupStageRes] = await Promise.all([
      TournamentAPIExtended.getMatches(tournamentId),
      TournamentAPIExtended.getGroupStageData(tournamentId).catch(() => null),
    ]);
    matches.value = matchRes.data.data || [];
    if (groupStageRes?.data?.data?.groups) {
      groupStageData.value = groupStageRes.data.data;
      groups.value = groupStageData.value.groups;
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
  }
}

async function loadGroupStageOnly() {
  if (groupStageData.value) return;
  try {
    const res = await TournamentAPIExtended.getGroupStageData(Number(route.params.id));
    if (res?.data?.data?.groups) groupStageData.value = res.data.data;
  } catch {
    /* silent */
  }
}

async function loadKnockoutData() {
  loadingKnockout.value = true;
  try {
    const res = await TournamentAPIExtended.getKnockoutData(Number(route.params.id));
    knockoutData.value = res.data.data;
  } catch {
    showToast("加载淘汰赛数据失败");
  } finally {
    loadingKnockout.value = false;
  }
}

async function loadPositions() {
  try {
    const res = await TournamentAPIExtended.getPositions(Number(route.params.id));
    positions.value = res.data.data || [];
  } catch {
    showToast("加载位置数据失败");
  }
}

async function loadPRMatches() {
  try {
    const res = await TournamentAPIExtended.getPRMatches(Number(route.params.id));
    prMatches.value = res.data?.data || [];
  } catch {
    /* silent */
  }
}

function prSetWinner(m: any, set: any): string {
  if (m.status !== "completed") return "";
  const p1 = Number(set.player1) || 0;
  const p2 = Number(set.player2) || 0;
  if (p1 > p2) return "set-winner-p1";
  if (p2 > p1) return "set-winner-p2";
  return "";
}

watch([filterStatus, selectedPlayerId, activeGroup, viewTab], syncFilters);

onMounted(async () => {
  loading.value = true;
  await Promise.all([loadTournament(), loadMatches()]);
  if (viewTab.value === "knockout") await loadKnockoutData();
  if (viewTab.value === "position") {
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

/* header */
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
.header-stats {
  display: flex;
  border-top: 1px solid var(--mobile-border-light);
  padding-top: 12px;
}
.stat {
  flex: 1;
  text-align: center;
  cursor: pointer;
  padding: 4px 0;
  border-radius: 6px;
  transition: background 0.2s;
}
.stat.active,
.stat:active {
  background: var(--mobile-tab-active-bg);
}
.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--mobile-text-primary);
}
.stat-value.completed {
  color: var(--mobile-green);
}
.stat-value.pending {
  color: var(--mobile-orange);
}
.stat-label {
  display: block;
  font-size: 11px;
  color: var(--mobile-text-muted);
  margin-top: 2px;
}

/* toolbar */
.toolbar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}
.filter-dropdown {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
}
.end-btn {
  color: var(--mobile-red-text) !important;
  border: 1.5px solid var(--mobile-red-text) !important;
  background: var(--mobile-end-btn-bg) !important;
  font-size: 13px;
  font-weight: 500;
  padding: 0 14px;
  flex-shrink: 0;
}
.end-btn:active {
  opacity: 0.7;
}

/* view tabs */
.view-tabs {
  background: var(--mobile-tab-bg);
}

/* match list (shared) */
.group-tabs {
  background: var(--mobile-tab-bg);
}
.empty-hint {
  padding: 40px 0;
  font-size: 14px;
  color: var(--mobile-text-muted);
  text-align: center;
}
.match-list {
  padding: 12px 0;
}
.match-card {
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
}
.match-card:active {
  opacity: 0.7;
}
.match-card.is-completed {
  border-left: 4px solid var(--mobile-green);
}
.match-round {
  font-size: 12px;
  font-weight: 500;
  color: var(--mobile-text-muted);
  margin-bottom: 8px;
}
.match-players {
  display: flex;
  gap: 8px;
  align-items: stretch;
  margin-bottom: 8px;
}
.player-side {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 10px 8px;
  background: var(--mobile-scoreboard-bg);
  border-radius: 8px;
  min-height: 64px;
}
.player-side.is-winner {
  background: var(--mobile-winner-bg);
}
.player-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  text-align: center;
  line-height: 1.3;
}
.is-winner .player-name {
  color: var(--mobile-winner-text);
}
.player-score {
  font-size: 20px;
  font-weight: 700;
  color: var(--mobile-text-primary);
}
.is-winner .player-score {
  color: var(--mobile-winner-text);
}
.vs-section {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
}
.vs-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--mobile-text-muted);
}
.sets-row {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-bottom: 8px;
}
.set-badge {
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--mobile-text-secondary);
  background: var(--mobile-gray-bg);
  border-radius: 4px;
}
.set-badge.set-winner-p1,
.set-badge.set-winner-p2 {
  color: var(--mobile-winner-text);
  background: var(--mobile-winner-bg);
}
.match-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.footer-arrow {
  font-size: 14px;
  color: var(--mobile-text-muted);
}

/* group stage view */
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

/* rankings */
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

/* matrix */
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
.gs-matrix-cell {
  min-width: 52px;
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
.gs-matrix-score {
  font-weight: 600;
  font-size: 14px;
  color: var(--mobile-text-primary);
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
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}
.gs-matrix-cell-inner:active {
  background: var(--mobile-tab-active-bg);
}

/* score popup */
.score-popup {
  max-height: 92vh;
  overflow: hidden;
}
.score-popup :deep(.van-popup__close-icon) {
  top: 4px;
  z-index: 1;
}
.score-popup-content {
  padding: 20px 16px calc(env(safe-area-inset-bottom, 0px) + 16px);
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  max-height: calc(92vh - 50px);
}
.scoreboard {
  display: flex;
  gap: 6px;
  align-items: stretch;
  padding: 8px 0;
}
.sb-player {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 10px 6px;
  background: var(--mobile-scoreboard-bg);
  border-radius: 10px;
  min-height: 60px;
  transition: all 0.3s;
}
.sb-player.is-winner {
  background: var(--mobile-scoreboard-winner-bg);
  box-shadow: 0 0 0 2px var(--mobile-green);
}
.sb-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
.is-winner .sb-name {
  color: var(--mobile-winner-text);
}
.sb-score {
  font-size: 24px;
  font-weight: 800;
  color: var(--mobile-text-primary);
  line-height: 1;
}
.is-winner .sb-score {
  color: var(--mobile-winner-text);
}
.sb-vs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 32px;
}
.sb-vs-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--mobile-text-muted);
}
.sb-vs-sub {
  font-size: 9px;
  color: var(--mobile-text-muted);
  margin-top: 2px;
}
.sets-section {
  margin: 10px 0;
}
.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 8px;
}
.set-block {
  padding: 10px;
  margin-bottom: 8px;
  background: var(--mobile-card-bg);
  border: 1px solid var(--mobile-set-block-border);
  border-radius: 8px;
}
.set-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.set-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--mobile-text-secondary);
}
.set-body {
  display: flex;
  gap: 6px;
  align-items: center;
}
.score-input {
  flex: 1;
  min-width: 0;
  width: 0;
  max-width: 100%;
  box-sizing: border-box;
  padding: 10px 2px;
  border: none;
  border-radius: 8px;
  background: var(--mobile-gray-bg, #f5f5f5);
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}
.score-input[readonly] {
  background: transparent;
  color: var(--mobile-text-secondary);
}
.score-input::placeholder {
  color: var(--mobile-text-muted);
}
.set-colon {
  font-size: 18px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  flex-shrink: 0;
  width: 16px;
  text-align: center;
}
.add-set-btn {
  margin-top: 6px;
  font-size: 13px;
}
.result-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  margin: 10px 0;
  font-size: 14px;
  font-weight: 500;
}
.result-banner.valid {
  color: var(--mobile-green-text);
  background: var(--mobile-green-bg);
}
.result-banner.invalid {
  color: var(--mobile-orange-text);
  background: var(--mobile-orange-bg);
}
.submit-area {
  margin-top: 12px;
}
.score-overlay-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.score-overlay-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--mobile-text-primary);
}
.score-overlay-bd {
  flex: 1;
  overflow-y: auto;
}
.score-popup-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  text-align: center;
  margin-bottom: 16px;
}
.scoreboard {
  display: flex;
  gap: 8px;
  align-items: stretch;
  padding: 12px 0;
}
.sb-player {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  background: var(--mobile-scoreboard-bg);
  border-radius: 10px;
  min-height: 70px;
  transition: all 0.3s;
}
.sb-player.is-winner {
  background: var(--mobile-scoreboard-winner-bg);
  box-shadow: 0 0 0 2px var(--mobile-green);
}
.sb-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  text-align: center;
}
.is-winner .sb-name {
  color: var(--mobile-winner-text);
}
.sb-score {
  font-size: 28px;
  font-weight: 800;
  color: var(--mobile-text-primary);
  line-height: 1;
}
.is-winner .sb-score {
  color: var(--mobile-winner-text);
}
.sb-vs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
}
.sb-vs-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--mobile-text-muted);
}
.sb-vs-sub {
  font-size: 10px;
  color: var(--mobile-text-muted);
  margin-top: 2px;
}
.sets-section {
  margin: 12px 0;
}
.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 10px;
}
.set-block {
  padding: 12px;
  margin-bottom: 10px;
  background: var(--mobile-card-bg);
  border: 1px solid var(--mobile-set-block-border);
  border-radius: 8px;
}
.set-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.set-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--mobile-text-secondary);
}
.set-body {
  display: flex;
  gap: 8px;
  align-items: center;
}
.score-field {
  flex: 1;
  text-align: center;
  font-size: 20px !important;
  font-weight: 700 !important;
}
.set-colon {
  font-size: 20px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  flex-shrink: 0;
}
.add-set-btn {
  margin-top: 8px;
  font-size: 13px;
}
.result-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-radius: 8px;
  margin: 12px 0;
  font-size: 14px;
  font-weight: 500;
}
.result-banner.valid {
  color: var(--mobile-green-text);
  background: var(--mobile-green-bg);
}
.result-banner.invalid {
  color: var(--mobile-orange-text);
  background: var(--mobile-orange-bg);
}
.submit-area {
  margin-top: 16px;
}

/* knockout view */
.ko-view {
  padding: 12px 0;
}
.ko-round {
  margin-bottom: 20px;
}
.ko-round-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  margin-bottom: 10px;
  padding-left: 4px;
  border-left: 3px solid var(--mobile-green);
}

/* position view */
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

/* PR match records */
.pr-card {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  margin-bottom: 10px;
  background: var(--mobile-card-bg);
  border-radius: 10px;
  box-shadow: 0 1px 4px var(--mobile-shimmer);
  cursor: pointer;
  gap: 12px;
}
.pr-card:active {
  opacity: 0.7;
}
.pr-round {
  font-size: 13px;
  font-weight: 700;
  color: var(--mobile-text-primary);
  min-width: 64px;
  text-align: center;
}
.pr-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.pr-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.pr-label {
  color: var(--mobile-text-muted);
  min-width: 42px;
  flex-shrink: 0;
}
.pr-value {
  color: var(--mobile-text-primary);
  flex: 1;
}
.pr-value.is-winner {
  color: var(--mobile-green);
  font-weight: 600;
}
.winner-icon {
  margin-left: 4px;
  vertical-align: middle;
}
.pr-score {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.pr-set {
  padding: 1px 6px;
  font-size: 12px;
  background: var(--mobile-gray-bg);
  border-radius: 4px;
  color: var(--mobile-text-secondary);
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
  font-weight: 600;
}
.pr-arrow {
  font-size: 14px;
  color: var(--mobile-text-muted);
  flex-shrink: 0;
}

</style>
