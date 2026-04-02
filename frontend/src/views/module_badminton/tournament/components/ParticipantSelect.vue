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

    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="students"
      max-height="400"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="姓名" />
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
  id: number;
  name: string;
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
}>();

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "submit", participants: SelectedParticipant[]): void;
}>();

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit("update:visible", val),
});

const loading = ref(false);
const searchQuery = ref("");
const selectedIds = ref<number[]>([]);
const students = ref<Student[]>([]);
const allStudents = ref<Student[]>([]);

async function loadStudents() {
  loading.value = true;
  try {
    const res = await StudentAPI.getStudentList({ page_no: 1, page_size: 100 });
    const items = res.data?.data?.items || [];
    allStudents.value = items.filter((s: any) => !props.existingParticipants.includes(s.id));
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
    students.value = allStudents.value.filter((s) =>
      s.name.toLowerCase().includes(query.toLowerCase())
    );
  }
}

function handleSelectionChange(ids: number[]) {
  selectedIds.value = ids;
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
  margin-bottom: 16px;
}
</style>
