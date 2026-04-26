<template>
  <div class="assessment-page">
    <van-cell-group inset>
      <van-field
        v-model="selectedStudentName"
        is-link
        readonly
        label="学员"
        placeholder="请选择学员"
        @click="showStudentPicker = true"
      />
    </van-cell-group>

    <div v-if="selectedStudentId" class="dimension-section">
      <van-cell-group inset>
        <van-cell title="评分维度" />
      </van-cell-group>

      <div class="dimension-grid">
        <div v-for="dim in dimensions" :key="dim.key" class="dimension-item">
          <div class="dimension-label">{{ dim.label }}</div>
          <van-rate
            v-model="form[dim.key]"
            :count="10"
            size="18px"
            void-icon="star-o"
            void-color="#eee"
          />
        </div>
      </div>

      <van-cell-group inset style="margin-top: 12px">
        <van-field
          v-model="form.comments"
          rows="3"
          autosize
          type="textarea"
          maxlength="500"
          placeholder="输入评语（选填）"
          show-word-limit
        />
      </van-cell-group>

      <div style="padding: 16px">
        <van-button
          type="primary"
          block
          round
          size="large"
          :loading="submitting"
          @click="handleSubmit"
        >
          提交评估
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showStudentPicker" position="bottom" round>
      <van-picker
        :columns="studentColumns"
        title="选择学员"
        @confirm="onStudentConfirm"
        @cancel="showStudentPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { showToast, showSuccessToast } from "vant";
import StudentAPI from "@/api/module_badminton/student";
import AssessmentAPI from "@/api/module_badminton/assessment";

interface StudentOption {
  id: number;
  name: string;
}

interface Dimension {
  key: string;
  label: string;
}

const dimensions: Dimension[] = [
  { key: "technique", label: "技术" },
  { key: "footwork", label: "步伐" },
  { key: "tactics", label: "战术" },
  { key: "power", label: "力量" },
  { key: "speed", label: "速度" },
  { key: "stamina", label: "耐力" },
  { key: "offense", label: "进攻" },
  { key: "defense", label: "防守" },
  { key: "mental", label: "心理" },
];

const form = reactive<Record<string, any>>({
  technique: 0,
  footwork: 0,
  tactics: 0,
  power: 0,
  speed: 0,
  stamina: 0,
  offense: 0,
  defense: 0,
  mental: 0,
  comments: "",
});

const selectedStudentId = ref<number | null>(null);
const selectedStudentName = ref("");
const showStudentPicker = ref(false);
const submitting = ref(false);
const studentColumns = ref<{ text: string; value: number }[]>([]);
const studentOptions = ref<StudentOption[]>([]);

function onStudentConfirm({ selectedOptions }: any) {
  const option = selectedOptions[0];
  selectedStudentId.value = option.value;
  selectedStudentName.value = option.text;
  showStudentPicker.value = false;
}

async function handleSubmit() {
  if (!selectedStudentId.value) {
    showToast("请选择学员");
    return;
  }

  submitting.value = true;
  try {
    const body: Record<string, any> = {
      student_id: selectedStudentId.value,
      assessment_date: new Date().toISOString().split("T")[0],
    };
    for (const dim of dimensions) {
      body[dim.key] = form[dim.key] || 0;
    }
    if (form.comments) {
      body.comments = form.comments;
    }

    await AssessmentAPI.createAssessment(body as any);
    showSuccessToast("评估提交成功");

    for (const dim of dimensions) {
      form[dim.key] = 0;
    }
    form.comments = "";
    selectedStudentId.value = null;
    selectedStudentName.value = "";
  } catch (e: any) {
    showToast(e.response?.data?.msg || "提交失败");
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  try {
    const res = await StudentAPI.getStudentList({ page_no: 1, page_size: 100 });
    const items = res.data.data?.items || [];
    studentOptions.value = items.map((s: any) => ({ id: s.id, name: s.name }));
    studentColumns.value = items.map((s: any) => ({ text: s.name, value: s.id }));
  } catch {
    // silent
  }
});
</script>

<style scoped>
.assessment-page {
  padding-bottom: 24px;
}

.dimension-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  padding: 12px 16px;
}

.dimension-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--mobile-dimension-bg);
  border-radius: 8px;
}

.dimension-label {
  min-width: 48px;
  font-size: 14px;
  font-weight: 500;
  color: var(--mobile-text-primary);
}
</style>
