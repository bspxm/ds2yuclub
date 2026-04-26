<template>
  <div class="h2h-page">
    <van-cell-group inset>
      <van-field
        v-model="student1Name"
        is-link
        readonly
        label="学员1"
        placeholder="请选择"
        @click="
          pickerTarget = 1;
          showPicker = true;
        "
      />
      <van-field
        v-model="student2Name"
        is-link
        readonly
        label="学员2"
        placeholder="请选择"
        @click="
          pickerTarget = 2;
          showPicker = true;
        "
      />
    </van-cell-group>

    <div style="padding: 12px 16px">
      <van-button type="primary" block round :loading="loading" @click="handleQuery">
        查询对比
      </van-button>
    </div>

    <template v-if="h2hRecords.length > 0">
      <van-cell-group inset>
        <van-cell
          title="历史对战"
          :value="`${h2hSummary.student1Wins}胜 ${h2hSummary.student2Wins}胜`"
        />
      </van-cell-group>

      <div class="record-list">
        <div v-for="r in h2hRecords" :key="r.tournament_name + r.match_date" class="record-card">
          <div class="record-tournament">{{ r.tournament_name }}</div>
          <div class="record-players">
            <span :class="{ winner: r.winner_id === r.player1?.id }">
              {{ r.player1?.name || "选手1" }}
            </span>
            <span class="vs">VS</span>
            <span :class="{ winner: r.winner_id === r.player2?.id }">
              {{ r.player2?.name || "选手2" }}
            </span>
          </div>
          <div v-if="r.scores" class="record-scores">
            <span v-for="(s, i) in r.scores" :key="i" class="score-item">
              {{ s.player1 }}:{{ s.player2 }}
            </span>
          </div>
          <div class="record-date">{{ r.match_date || r.tournament_name }}</div>
        </div>
      </div>
    </template>

    <van-empty v-else-if="queried && !loading" description="暂无对战记录" />

    <van-popup v-model:show="showPicker" position="bottom" round>
      <van-picker
        :columns="studentColumns"
        title="选择学员"
        @confirm="onStudentConfirm"
        @cancel="showPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { showToast } from "vant";
import StudentAPI from "@/api/module_badminton/student";
import { TournamentAPIExtended } from "@/api/module_badminton/tournament";

const student1Id = ref<number | null>(null);
const student1Name = ref("");
const student2Id = ref<number | null>(null);
const student2Name = ref("");
const pickerTarget = ref(1);
const showPicker = ref(false);
const loading = ref(false);
const queried = ref(false);

const studentColumns = ref<{ text: string; value: number }[]>([]);
const studentOptions = ref<{ id: number; name: string }[]>([]);

const h2hRecords = ref<any[]>([]);
const h2hSummary = ref({ student1Wins: 0, student2Wins: 0 });

function onStudentConfirm({ selectedOptions }: any) {
  const option = selectedOptions[0];
  if (pickerTarget.value === 1) {
    student1Id.value = option.value;
    student1Name.value = option.text;
  } else {
    student2Id.value = option.value;
    student2Name.value = option.text;
  }
  showPicker.value = false;
}

async function handleQuery() {
  if (!student1Id.value || !student2Id.value) {
    showToast("请选择两个学员");
    return;
  }
  if (student1Id.value === student2Id.value) {
    showToast("请选择不同的学员");
    return;
  }

  loading.value = true;
  queried.value = true;
  try {
    const res = await TournamentAPIExtended.getH2H(student1Id.value, student2Id.value);
    const records = res.data.data || [];
    h2hRecords.value = records;
    h2hSummary.value = {
      student1Wins: records.filter((r: any) => r.winner_id === r.player1?.id).length,
      student2Wins: records.filter((r: any) => r.winner_id === r.player2?.id).length,
    };
  } catch {
    h2hRecords.value = [];
    h2hSummary.value = { student1Wins: 0, student2Wins: 0 };
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    const res = await StudentAPI.getStudentList({ page_no: 1, page_size: 200 });
    const items = res.data.data?.items || [];
    studentOptions.value = items.map((s: any) => ({ id: s.id, name: s.name }));
    studentColumns.value = items.map((s: any) => ({ text: s.name, value: s.id }));
  } catch {
    // silent
  }
});
</script>

<style scoped>
.h2h-page {
  padding-bottom: 24px;
}

.record-list {
  padding: 8px 16px;
}

.record-card {
  padding: 12px;
  margin-bottom: 10px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.record-tournament {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
}

.record-players {
  display: flex;
  gap: 12px;
  justify-content: center;
  font-size: 14px;
}

.record-players .winner {
  font-weight: 600;
  color: #07c160;
}

.vs {
  font-size: 12px;
  color: #999;
}

.record-scores {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-top: 6px;
}

.score-item {
  padding: 2px 8px;
  font-size: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.record-date {
  margin-top: 6px;
  font-size: 11px;
  color: #999;
  text-align: center;
}
</style>
