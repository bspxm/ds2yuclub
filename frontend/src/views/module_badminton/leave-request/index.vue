<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>请假管理</span>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-container mb-4">
        <el-form :inline="true" :model="queryForm">
          <el-form-item label="学员姓名">
            <el-input v-model="queryForm.student_name" placeholder="请输入学员姓名" clearable />
          </el-form-item>
          <el-form-item label="课程名称">
            <el-input v-model="queryForm.course_name" placeholder="请输入课程名称" clearable />
          </el-form-item>
          <el-form-item label="请假状态">
            <el-select v-model="queryForm.status" placeholder="请选择状态" clearable>
              <el-option label="待审批" value="pending" />
              <el-option label="已批准" value="approved" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="请假日期">
            <el-date-picker
              v-model="queryForm.leave_date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="search" @click="handleSearch">查询</el-button>
            <el-button icon="refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 功能区域 -->
      <div class="mb-4">
        <el-button type="primary" icon="plus" @click="handleCreate">新增请假</el-button>
        <el-button type="danger" icon="delete" :disabled="selectedIds.length === 0" @click="handleBatchDelete">
          批量删除
        </el-button>
      </div>
      
      <!-- 表格区域 -->
      <el-table :data="tableData" border stripe v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="student_name" label="学员姓名" min-width="120" />
        <el-table-column prop="course_name" label="课程名称" min-width="150" />
        <el-table-column prop="leave_date" label="请假日期" min-width="120" />
        <el-table-column prop="reason" label="请假原因" min-width="200" />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{row}">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批人" min-width="120" />
        <el-table-column prop="approved_time" label="审批时间" min-width="180" />
        <el-table-column prop="created_time" label="创建时间" min-width="180" />
        <el-table-column label="操作" min-width="200" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.status === 'pending'" type="success" size="small" link icon="check" @click="handleApprove(row)">
              批准
            </el-button>
            <el-button v-if="row.status === 'pending'" type="danger" size="small" link icon="close" @click="handleReject(row)">
              拒绝
            </el-button>
            <el-button type="primary" size="small" link icon="edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" link icon="delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="mt-4 text-right">
        <el-pagination
          v-model:current-page="queryForm.page_no"
          v-model:page-size="queryForm.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 请假表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学员" prop="student_id">
          <el-select v-model="formData.student_id" placeholder="请选择学员" style="width: 100%">
            <el-option label="张三" value="1" />
            <el-option label="李四" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="formData.course_id" placeholder="请选择课程" style="width: 100%">
            <el-option label="周一基础班" value="1" />
            <el-option label="周三提高班" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假日期" prop="leave_date">
          <el-date-picker
            v-model="formData.leave_date"
            type="date"
            placeholder="请选择请假日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="请假原因" prop="reason">
          <el-input
            v-model="formData.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入请假原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const selectedIds = ref<number[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)

const queryForm = reactive({
  page_no: 1,
  page_size: 10,
  student_name: '',
  course_name: '',
  status: '',
  leave_date_range: []
})

const formData = reactive({
  id: undefined as number | undefined,
  student_id: '',
  course_id: '',
  leave_date: '',
  reason: ''
})

const rules: FormRules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'blur' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'blur' }],
  leave_date: [{ required: true, message: '请选择请假日期', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入请假原因', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑请假' : '新增请假')

const getStatusType = (status: string) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'cancelled': return 'info'
    default: return 'warning'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待审批'
    case 'approved': return '已批准'
    case 'rejected': return '已拒绝'
    case 'cancelled': return '已取消'
    default: return status
  }
}

const handleSearch = () => {
  queryForm.page_no = 1
  loadData()
}

const handleReset = () => {
  queryForm.student_name = ''
  queryForm.course_name = ''
  queryForm.status = ''
  queryForm.leave_date_range = []
  queryForm.page_no = 1
  loadData()
}

const handleSizeChange = (size: number) => {
  queryForm.page_size = size
  loadData()
}

const handleCurrentChange = (page: number) => {
  queryForm.page_no = page
  loadData()
}

const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(formData, {
    id: undefined,
    student_id: '',
    course_id: '',
    leave_date: '',
    reason: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定删除请假记录吗？`, '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }
  ElMessageBox.confirm(`确定删除选中的${selectedIds.value.length}条记录吗？`, '批量删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {})
}

const handleApprove = (row: any) => {
  ElMessageBox.confirm(`确定批准该请假申请吗？`, '批准请假', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('已批准')
    loadData()
  }).catch(() => {})
}

const handleReject = (row: any) => {
  ElMessageBox.confirm(`确定拒绝该请假申请吗？`, '拒绝请假', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('已拒绝')
    loadData()
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    }
  })
}

const loadData = async () => {
  loading.value = true
  try {
    // 模拟数据
    tableData.value = [
      {
        id: 1,
        student_name: '张三',
        course_name: '周一基础班',
        leave_date: '2026-01-20',
        reason: '生病发烧',
        status: 'pending',
        approver_name: '',
        approved_time: '',
        created_time: '2026-01-18 14:30:00'
      },
      {
        id: 2,
        student_name: '李四',
        course_name: '周三提高班',
        leave_date: '2026-01-19',
        reason: '家庭事务',
        status: 'approved',
        approver_name: '王教练',
        approved_time: '2026-01-18 10:15:00',
        created_time: '2026-01-17 09:20:00'
      }
    ]
    total.value = 2
  } catch (error) {
    console.error(error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.search-container {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}
</style>