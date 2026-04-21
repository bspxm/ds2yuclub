<template>
  <el-dialog
    v-model="dialogVisible"
    title="添加参赛学员"
    width="600px"
    @open="loadStudents"
    @close="selectedIds = []"
  >
    <div class="search-box">
      <el-input v-model="searchQuery" placeholder="搜索学员姓名" clearable @input="handleSearch">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="capacity-info">
      <el-tag :type="isOverCapacity ? 'danger' : 'info'" size="large">
        已选择
        <strong>{{ selectedIds.length }}</strong>
        人，每组
        <strong>{{ groupSize || 4 }}</strong>
        人，共分
        <strong>{{ numGroups }}</strong>
        个小组
      </el-tag>
    </div>

    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="students"
      max-height="400"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column label="年龄" width="70" align="center">
        <template #default="{ row }">
          {{ getAge(row.birth_date) }}
        </template>
      </el-table-column>
      <el-table-column label="组别" width="100">
        <template #default="{ row }">
          {{ row.group_name || "-" }}
        </template>
      </el-table-column>
      <el-table-column label="水平" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.level" size="small" type="primary">{{ row.level }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定 ({{ selectedIds.length }})</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import StudentAPI from "@/api/module_badminton/student";

interface Student {
  id?: number;
  name?: string;
  birth_date?: string;
  level?: string;
  group_name?: string;
}

interface SelectedParticipant {
  student_id: number;
  student_name: string;
  seed_rank?: number;
}

const props = defineProps<{
  visible: boolean;
  tournamentId: number;
  existingParticipants: number[];
  maxParticipants?: number;
  groupSize?: number;
}>();

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "submit", participants: SelectedParticipant[]): void;
}>();

const tableRef = ref();
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit("update:visible", val),
});

const loading = ref(false);
const searchQuery = ref("");
const selectedIds = ref<number[]>([]);
const students = ref<Student[]>([]);
const allStudents = ref<Student[]>([]);

const isOverCapacity = computed(() => {
  return props.maxParticipants && selectedIds.value.length > props.maxParticipants;
});

const numGroups = computed(() => {
  if (!props.groupSize || props.groupSize <= 0) return 1;
  return Math.ceil(selectedIds.value.length / props.groupSize) || 1;
});

async function loadStudents() {
  loading.value = true;
  try {
    const res = await StudentAPI.getStudentList({ page_no: 1, page_size: 100 });
    const items = res.data?.data?.items || [];
    // 确保 existingParticipants 和 student id 都是数字类型进行比较
    const existingIds = props.existingParticipants.map((id) => Number(id));
    allStudents.value = items.filter((s: any) => !existingIds.includes(Number(s.id)));
    students.value = allStudents.value;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

function handleSearch(query: string) {
  searchQuery.value = query;
  if (!query) {
    students.value = allStudents.value;
  } else {
    const lowerQuery = query.toLowerCase();
    students.value = allStudents.value.filter(
      (s) =>
        s.name?.toLowerCase().includes(lowerQuery) ||
        s.group_name?.toLowerCase().includes(lowerQuery) ||
        s.level?.toLowerCase().includes(lowerQuery)
    );
  }
}

function getAge(birthDate: string | undefined): string {
  if (!birthDate) return "-";
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age > 0 ? String(age) : "-";
}

function handleSelectionChange(rows: Student[]) {
  const newIds = rows.map((r) => r.id).filter(Boolean) as number[];

  // 检查是否超过最大容量
  if (props.maxParticipants && newIds.length > props.maxParticipants) {
    // 使用 MessageBox 弹窗提示，更醒目
    ElMessage({
      type: "error",
      message: `最多只能选择 ${props.maxParticipants} 名参赛学员！`,
      duration: 3000,
      showClose: true,
    });
    // 取消最后选中的项
    const lastSelected = rows[rows.length - 1];
    if (lastSelected && tableRef.value) {
      tableRef.value.toggleRowSelection(lastSelected, false);
    }
    return;
  }

  selectedIds.value = newIds;
}

function handleRowClick(row: Student) {
  const table = tableRef.value;
  if (table) {
    table.toggleRowSelection(row);
  }
}

function handleSubmit() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning("请选择参赛学员");
    return;
  }

  const selected = selectedIds.value.map((id) => {
    const student = allStudents.value.find((s) => s.id === id);
    return {
      student_id: id,
      student_name: student?.name || "",
    };
  });

  emit("submit", selected);
  dialogVisible.value = false;
}

defineExpose({
  loadStudents,
});
</script>

<style scoped>
.search-box {
  margin-bottom: 12px;
}

.capacity-info {
  margin-bottom: 16px;
  text-align: center;
}

.capacity-info strong {
  font-size: 16px;
  color: var(--el-color-primary);
}
</style>
