<template>
  <div class="table-view">
    <div class="table-toolbar">
      <el-select v-model="roundFilter" placeholder="筛选轮次" clearable>
        <el-option
          v-for="opt in roundOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>
    </div>

    <ElTable :data="matches" border stripe highlight-current-row>
      <ElTableColumn prop="round_number" label="轮次" width="100" align="center">
        <template #default="{ row }">
          {{ getRoundText(row.round_type) }}
        </template>
      </ElTableColumn>
      <ElTableColumn prop="match_number" label="场次" width="80" align="center" />
      <ElTableColumn prop="player1" label="选手1" min-width="120">
        <template #default="{ row }">
          {{ row.player1?.name || "TBD" }}
        </template>
      </ElTableColumn>
      <ElTableColumn prop="scores" label="比分" width="150" align="center">
        <template #default="{ row }">
          {{ getScoreText(row) }}
        </template>
      </ElTableColumn>
      <ElTableColumn prop="player2" label="选手2" min-width="120">
        <template #default="{ row }">
          {{ row.player2?.name || "TBD" }}
        </template>
      </ElTableColumn>
      <ElTableColumn prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : 'info'" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </ElTableColumn>
      <ElTableColumn label="操作" width="100" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="emit('matchClick', row)">
            {{ row.status === "completed" ? "查看" : "录入" }}
          </el-button>
        </template>
      </ElTableColumn>
    </ElTable>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElTable, ElTableColumn } from "element-plus";

interface Match {
  id: number;
  round_number: number;
  match_number: number;
  round_type: string;
  status: string;
  player1: { id: number; name: string } | null;
  player2: { id: number; name: string } | null;
  scores?: { player1: number; player2: number }[];
  winner_id?: number;
}

interface TableViewProps {
  matches: Match[];
}

defineProps<TableViewProps>();

const emit = defineEmits<{
  (e: "matchClick", match: Match): void;
}>();

const roundFilter = ref<string>("");

const roundOptions = [
  { label: "全部", value: "" },
  { label: "小组赛", value: "group_stage" },
  { label: "淘汰赛", value: "knockout" },
];

function getRoundText(roundType: string): string {
  const map: Record<string, string> = {
    group_stage: "小组赛",
    knockout: "淘汰赛",
    promotion_relegation: "升降赛",
  };
  return map[roundType] || roundType;
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    // 大写格式（数据库返回）
    SCHEDULED: "待开始",
    IN_PROGRESS: "进行中",
    COMPLETED: "已完成",
    CANCELLED: "已取消",
    WALKOVER: "弃权",
    // 小写格式（兼容旧数据）
    scheduled: "待开始",
    active: "进行中",
    completed: "已完成",
    cancelled: "已取消",
    walkover: "弃权",
  };
  return map[status] || status;
}

function getScoreText(match: Match): string {
  if (!match.scores || match.scores.length === 0) {
    return "-";
  }
  return match.scores.map((s) => `${s.player1}-${s.player2}`).join(", ");
}
</script>

<style scoped>
.table-view {
  padding: 16px;
}

.table-toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}
</style>
