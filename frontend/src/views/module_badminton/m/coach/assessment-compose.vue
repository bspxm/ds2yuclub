<template>
  <div class="assessment-page">
    <van-cell-group inset>
      <van-field
        v-model="selectedStudentName"
        is-link
        readonly
        label="学员"
        placeholder="请选择学员"
        @click="openStudentSelector"
      />
    </van-cell-group>

    <div v-if="selectedStudentId" class="dimension-section">
      <div v-if="lastAssessment" class="last-assessment-tip">
        <van-icon name="info-o" size="14" color="#1989fa" />
        <span class="tip-text">
          已载入该学员 {{ formatDate(lastAssessment.assessment_date) }} 的评估结果，仅供参考
        </span>
      </div>

      <van-cell-group inset>
        <van-cell title="评分维度" />
      </van-cell-group>

      <div class="dimension-grid">
        <div v-for="dim in dimensions" :key="dim.key" class="dimension-item">
          <div class="dimension-label">{{ dim.label }}</div>
          <van-rate
            v-model="form[dim.key]"
            :count="5"
            size="18px"
            color="#f59e0b"
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

    <!-- 学员选择弹窗 -->
    <van-popup v-model:show="showStudentPicker" position="bottom" round :style="{ height: '85%' }">
      <div class="student-picker">
        <div class="picker-header">
          <span class="picker-title">选择学员</span>
          <van-icon name="cross" class="close-icon" @click="showStudentPicker = false" />
        </div>

        <!-- 搜索 -->
        <van-search
          v-model="searchName"
          placeholder="搜索学员姓名"
          shape="round"
          clearable
          @update:model-value="onSearchChange"
        />

        <!-- 筛选标签 -->
        <div class="filter-tags">
          <div
            class="filter-tag"
            :class="{ active: filterGroupName }"
            @click="showGroupPicker = true"
          >
            {{ filterGroupName || "组别" }}
            <van-icon name="arrow-down" size="10" />
          </div>
          <div class="filter-tag" :class="{ active: filterLevel }" @click="showLevelPicker = true">
            {{ filterLevel || "技术水平" }}
            <van-icon name="arrow-down" size="10" />
          </div>
          <div
            v-if="filterGroupName || filterLevel || searchName"
            class="filter-tag reset"
            @click="resetFilters"
          >
            重置
          </div>
        </div>

        <!-- 学员列表 -->
        <div class="student-list">
          <van-loading v-if="loadingStudents" size="24px" class="loading" />
          <template v-else>
            <van-cell
              v-for="student in filteredStudents"
              :key="student.id"
              clickable
              @click="selectStudent(student)"
            >
              <template #title>
                <div class="student-title">
                  <span class="student-name">{{ student.name }}</span>
                  <van-tag v-if="student.group_name" type="primary" class="info-tag">
                    {{ student.group_name }}
                  </van-tag>
                  <van-tag v-if="student.level" type="warning" class="info-tag">
                    {{ student.level }}
                  </van-tag>
                </div>
              </template>
              <template #right-icon>
                <van-icon
                  v-if="selectedStudentId === student.id"
                  name="success"
                  color="#1989fa"
                  size="18"
                />
              </template>
            </van-cell>
            <van-empty v-if="filteredStudents.length === 0" description="暂无学员" />
          </template>
        </div>

        <div class="picker-footer">
          <van-button block round @click="showStudentPicker = false">取消</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 组别选择器 -->
    <van-popup v-model:show="showGroupPicker" position="bottom" round>
      <van-picker
        :columns="groupColumns"
        title="选择组别"
        @confirm="onGroupConfirm"
        @cancel="showGroupPicker = false"
      />
    </van-popup>

    <!-- 技术水平选择器 -->
    <van-popup v-model:show="showLevelPicker" position="bottom" round>
      <van-picker
        :columns="levelColumns"
        title="选择技术水平"
        @confirm="onLevelConfirm"
        @cancel="showLevelPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { showToast, showSuccessToast } from "vant";
import StudentAPI from "@/api/module_badminton/student";
import GroupAPI from "@/api/module_badminton/group";
import AssessmentAPI from "@/api/module_badminton/assessment";

interface StudentOption {
  id: number;
  name: string;
  group_name?: string;
  level?: string;
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
const lastAssessment = ref<any>(null);

// 筛选相关状态
const searchName = ref("");
const filterGroupName = ref("");
const filterLevel = ref("");
const showGroupPicker = ref(false);
const showLevelPicker = ref(false);
const loadingStudents = ref(false);
const filteredStudents = ref<StudentOption[]>([]);
const allStudents = ref<StudentOption[]>([]);
const allGroupOptions = ref<{ text: string; value: string }[]>([]);

const groupColumns = computed(() => [{ text: "全部组别", value: "" }, ...allGroupOptions.value]);

const levelColumns = computed(() => {
  const set = new Set<string>();
  for (const s of allStudents.value) {
    if (s.level) set.add(s.level);
  }
  const options = Array.from(set).map((l) => ({ text: l, value: l }));
  return [{ text: "全部水平", value: "" }, ...options];
});

function onGroupConfirm({ selectedOptions }: any) {
  const option = selectedOptions[0];
  filterGroupName.value = option.value;
  showGroupPicker.value = false;
  applyFilters();
}

function onLevelConfirm({ selectedOptions }: any) {
  const option = selectedOptions[0];
  filterLevel.value = option.value;
  showLevelPicker.value = false;
  applyFilters();
}

function resetFilters() {
  searchName.value = "";
  filterGroupName.value = "";
  filterLevel.value = "";
  applyFilters();
}

function onSearchChange() {
  applyFilters();
}

async function applyFilters() {
  loadingStudents.value = true;
  try {
    const res = await StudentAPI.getStudentList({
      page_no: 1,
      page_size: 100,
      name: searchName.value || undefined,
      group_name: filterGroupName.value || undefined,
      level: filterLevel.value || undefined,
    });
    console.log("applyFilters response:", res.data);
    const items = res.data.data?.items || [];
    console.log("applyFilters items count:", items.length, items);
    filteredStudents.value = items.map((s: any) => ({
      id: s.id,
      name: s.name,
      group_name: s.group_name,
      level: s.level,
    }));
  } catch (e) {
    console.error("applyFilters error:", e);
    filteredStudents.value = [];
  } finally {
    loadingStudents.value = false;
  }
}

function formatDate(d: string) {
  if (!d) return "";
  return d.split("T")[0];
}

async function loadLastAssessment(studentId: number) {
  try {
    const res = await AssessmentAPI.getLatestAssessment(studentId);
    const data = res.data.data;
    if (data) {
      lastAssessment.value = data;
      for (const dim of dimensions) {
        form[dim.key] = Math.min(5, Math.max(0, Number((data as any)[dim.key]) || 0));
      }
      form.comments = data.comments || "";
      return;
    }
  } catch {
    // silent
  }
  lastAssessment.value = null;
  for (const dim of dimensions) {
    form[dim.key] = 0;
  }
  form.comments = "";
}

async function selectStudent(student: StudentOption) {
  selectedStudentId.value = student.id;
  selectedStudentName.value = student.name;
  showStudentPicker.value = false;
  await loadLastAssessment(student.id);
}

async function openStudentSelector() {
  showStudentPicker.value = true;
  if (filteredStudents.value.length === 0) {
    await applyFilters();
  }
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
      const val = Math.min(5, Math.max(0, Number(form[dim.key]) || 0));
      body[dim.key] = val;
      form[dim.key] = val;
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
    lastAssessment.value = null;
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
    // 预加载组别选项
    const groupRes = await GroupAPI.getGroupList({ page_no: 1, page_size: 100 });
    const groups = groupRes.data.data?.items || [];
    allGroupOptions.value = groups.map((g: any) => ({ text: g.name, value: g.name }));
  } catch {
    // silent
  }

  try {
    // 预加载全部学员用于提取技术水平选项
    const res = await StudentAPI.getStudentList({ page_no: 1, page_size: 100 });
    const items = res.data.data?.items || [];
    allStudents.value = items.map((s: any) => ({
      id: s.id,
      name: s.name,
      group_name: s.group_name,
      level: s.level,
    }));
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

/* 学员选择弹窗 */
.student-picker {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 12px 16px;
  border-bottom: 1px solid var(--mobile-border-light);
}

.picker-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.close-icon {
  position: absolute;
  right: 16px;
  font-size: 20px;
  color: var(--mobile-text-muted);
}

.filter-tags {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 8px 16px;
  overflow-x: auto;
  border-bottom: 1px solid var(--mobile-border-light);
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  padding: 5px 12px;
  font-size: 13px;
  color: var(--mobile-text-secondary);
  background: var(--mobile-gray-bg);
  border-radius: 14px;
}

.filter-tag.active {
  color: #1989fa;
  background: rgba(25, 137, 250, 0.1);
}

.filter-tag.reset {
  color: #ff976a;
  background: rgba(255, 151, 106, 0.1);
}

.student-list {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 8px;
}

.student-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.student-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--mobile-text-primary);
}

.info-tag {
  margin-left: 2px;
}

.loading {
  margin-top: 60px;
  text-align: center;
}

.picker-footer {
  padding: 10px 16px 16px;
  border-top: 1px solid var(--mobile-border-light);
}

.last-assessment-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 12px 16px 4px;
  padding: 8px 12px;
  font-size: 13px;
  color: #1989fa;
  background: rgba(25, 137, 250, 0.08);
  border-radius: 6px;
}

.tip-text {
  line-height: 1.4;
}
</style>
