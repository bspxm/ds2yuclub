<template>
  <div class="app-container">
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>家长-学员关联管理</span>
        </div>
      </template>

      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-button
            v-hasPerm="['module_badminton:parent_student:create']"
            type="primary"
            icon="plus"
            @click="handleCreate"
          >
            新建关联
          </el-button>
        </div>
      </div>

      <el-table v-loading="loading" :data="list" stripe @refresh="handleQuery">
        <el-table-column label="ID" prop="id" width="60" />
        <el-table-column label="家长" prop="parent_name" min-width="120" />
        <el-table-column label="学员" prop="student_name" min-width="120" />
        <el-table-column label="关系" prop="relation_type" width="100" />
        <el-table-column label="是否主要联系人" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_primary ? 'success' : 'info'" size="small">
              {{ row.is_primary ? "是" : "否" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-hasPerm="['module_badminton:parent_student:delete']"
              type="danger"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="formTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="家长" prop="parent_id">
          <el-select
            v-model="formData.parent_id"
            placeholder="请选择家长"
            filterable
            style="width: 100%"
          >
            <el-option v-for="u in parentOptions" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学员" prop="student_id">
          <el-select
            v-model="formData.student_id"
            placeholder="请选择学员"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="s in studentOptions"
              :key="s.id"
              :label="`${s.name} (${s.mobile || '无手机'})`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关系">
          <el-select v-model="formData.relation_type" placeholder="请选择关系" style="width: 100%">
            <el-option value="father" label="父亲" />
            <el-option value="mother" label="母亲" />
            <el-option value="grandfather" label="祖父" />
            <el-option value="grandmother" label="祖母" />
            <el-option value="guardian" label="监护人" />
            <el-option value="other" label="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="主要联系人">
          <el-switch v-model="formData.is_primary" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import ParentStudentAPI from "@/api/module_badminton/parent-student";
import UserAPI from "@/api/module_system/user";
import StudentAPI from "@/api/module_badminton/student";

interface FormData {
  parent_id: number | null;
  student_id: number | null;
  relation_type: string;
  is_primary: boolean;
}

const loading = ref(false);
const submitLoading = ref(false);
const list = ref<any[]>([]);
const dialogVisible = ref(false);
const formTitle = ref("新建关联");
const parentOptions = ref<any[]>([]);
const studentOptions = ref<any[]>([]);
const formRef = ref<any>(null);
const formData = ref<FormData>({
  parent_id: null,
  student_id: null,
  relation_type: "other",
  is_primary: true,
});
const rules = {
  parent_id: [{ required: true, message: "请选择家长", trigger: "change" }],
  student_id: [{ required: true, message: "请选择学员", trigger: "change" }],
};

async function loadList() {
  loading.value = true;
  try {
    const res = await ParentStudentAPI.listAll();
    list.value = res.data.data || [];
  } catch {
    list.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadOptions() {
  try {
    const [userRes, studentRes] = await Promise.all([
      UserAPI.listUser({ page_no: 1, page_size: 100 }),
      StudentAPI.getStudentList({ page_no: 1, page_size: 100 }),
    ]);
    const users = (userRes.data as any)?.data?.items || userRes.data?.data?.items || [];
    const students = (studentRes.data as any)?.data?.items || studentRes.data?.data?.items || [];
    parentOptions.value = users.filter((u: any) => u.roles?.some((r: any) => r.code === "PARENTS"));
    studentOptions.value = students;
    if (parentOptions.value.length === 0 && users.length > 0) {
      ElMessage.warning("未找到具有 PARENTS 角色的用户");
    }
  } catch (e: any) {
    ElMessage.error("加载选项失败: " + (e?.message || "未知错误"));
  }
}

function handleCreate() {
  formData.value = { parent_id: null, student_id: null, relation_type: "other", is_primary: true };
  formTitle.value = "新建关联";
  dialogVisible.value = true;
  loadOptions();
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitLoading.value = true;
  try {
    await ParentStudentAPI.createParentStudent({
      parent_id: formData.value.parent_id,
      student_id: formData.value.student_id,
      relation_type: formData.value.relation_type,
      is_primary: formData.value.is_primary,
    });
    ElMessage.success("关联创建成功");
    dialogVisible.value = false;
    await loadList();
  } catch {
    ElMessage.error("创建失败");
  } finally {
    submitLoading.value = false;
  }
}

function handleDelete(row: any) {
  ElMessageBox.confirm("确定删除该关联？", "提示", { type: "warning" }).then(async () => {
    try {
      await ParentStudentAPI.deleteParentStudent([row.id]);
      ElMessage.success("删除成功");
      await loadList();
    } catch {
      ElMessage.error("删除失败");
    }
  });
}

onMounted(() => {
  loadList();
});
</script>
