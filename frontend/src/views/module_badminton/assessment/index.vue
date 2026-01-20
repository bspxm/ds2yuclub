<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header flex justify-between items-center">
          <span>能力评估管理</span>
          <div>
            <el-button type="primary" icon="plus" @click="handleCreate">
              新建评估
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="mb-4">
        <el-alert type="info" show-icon>
          能力评估包含9个维度：技术、步法、战术、力量、速度、耐力、进攻、防守、心理，每项评分1-5分
        </el-alert>
      </div>
      
      <!-- 搜索区域 -->
      <div class="search-container mb-4">
        <el-form :inline="true" :model="queryForm">
          <el-form-item label="学员">
            <el-select
              v-model="queryForm.student_id"
              placeholder="选择学员"
              clearable
              filterable
              style="width: 200px"
            >
              <el-option
                v-for="student in studentOptions"
                :key="student.id"
                :label="student.name"
                :value="student.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="评估日期范围">
            <el-date-picker
              v-model="queryForm.assessment_date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="search" @click="handleSearch">查询</el-button>
            <el-button icon="refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 表格区域 -->
      <el-table
        :data="tableData"
        border
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="student.name" label="学员姓名" min-width="120">
          <template #default="{row}">
            {{ row.student?.name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="assessment_date" label="评估日期" min-width="120" />
        <el-table-column label="技术" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.technique" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="步法" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.footwork" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="战术" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.tactics" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="力量" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.power" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="速度" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.speed" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="耐力" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.stamina" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="进攻" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.offense" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="防守" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.defense" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="心理" min-width="100">
          <template #default="{row}">
            <el-rate v-model="row.mental" disabled show-score :max="5" />
          </template>
        </el-table-column>
        <el-table-column prop="overall_score" label="综合评分" min-width="120">
          <template #default="{row}">
            <el-progress :percentage="row.overall_score * 20" :format="formatScore" />
          </template>
        </el-table-column>
        <el-table-column label="评估人" min-width="120">
          <template #default="{row}">
            {{ row.coach?.name || row.created_by?.name || '系统' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" min-width="180" />
        <el-table-column label="操作" min-width="180" fixed="right">
          <template #default="{row}">
            <el-button type="primary" size="small" link icon="edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" link icon="delete" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 批量操作 -->
      <div class="mt-4 flex justify-between items-center">
        <div>
          <el-button
            v-if="multipleSelection.length > 0"
            type="danger"
            icon="delete"
            @click="handleBatchDelete"
          >
            批量删除 ({{ multipleSelection.length }})
          </el-button>
        </div>
        
        <!-- 分页 -->
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
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="学员" prop="student_id">
          <el-select
            v-model="formData.student_id"
            placeholder="选择学员"
            filterable
            style="width: 100%"
            :disabled="!!formData.id"
          >
            <el-option
              v-for="student in studentOptions"
              :key="student.id"
              :label="student.name"
              :value="student.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="评估日期" prop="assessment_date">
          <el-date-picker
            v-model="formData.assessment_date"
            type="date"
            placeholder="选择评估日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="教练">
          <el-select
            v-model="formData.coach_id"
            placeholder="选择教练（可选）"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="coach in coachOptions"
              :key="coach.id"
              :label="coach.name"
              :value="coach.id"
            />
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12" v-for="dimension in assessmentDimensions" :key="dimension.key">
            <el-form-item :label="dimension.label" :prop="dimension.key">
              <el-rate
                v-model="formData[dimension.key]"
                :max="5"
                :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                show-score
                text-color="#ff9900"
                score-template="{value}分"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="教练评语" prop="comments">
          <el-input
            v-model="formData.comments"
            type="textarea"
            :rows="3"
            placeholder="请输入教练评语（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import AssessmentAPI, { type AssessmentForm, type AssessmentTable, type AssessmentPageQuery } from '@/api/module_badminton/assessment'
import StudentAPI, { type StudentTable } from '@/api/module_badminton/student'
import UserAPI, { type UserInfo } from '@/api/module_system/user'
import { useUserStoreHook } from '@/store/modules/user.store'

const loading = ref(false)
const tableData = ref<AssessmentTable[]>([])
const total = ref(0)
const multipleSelection = ref<AssessmentTable[]>([])
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const studentOptions = ref<StudentTable[]>([])
const coachOptions = ref<any[]>([])

// 查询表单
const queryForm = reactive<AssessmentPageQuery>({
  page_no: 1,
  page_size: 10,
  student_id: undefined,
  assessment_date_start: undefined,
  assessment_date_end: undefined
})

// 表单数据
const formData = reactive<AssessmentForm>({
  student_id: 0,
  assessment_date: '',
  coach_id: undefined,
  technique: 3,
  footwork: 3,
  tactics: 3,
  power: 3,
  speed: 3,
  stamina: 3,
  offense: 3,
  defense: 3,
  mental: 3,
  comments: ''
})

// 表单验证规则
const formRules: FormRules = {
  student_id: [
    { required: true, message: '请选择学员', trigger: 'change' }
  ],
  assessment_date: [
    { required: true, message: '请选择评估日期', trigger: 'change' }
  ],
  technique: [
    { required: true, message: '请评分技术能力', trigger: 'change' }
  ]
}

// 能力评估维度配置
const assessmentDimensions = [
  { key: 'technique', label: '技术能力' },
  { key: 'footwork', label: '步法移动' },
  { key: 'tactics', label: '战术意识' },
  { key: 'power', label: '力量' },
  { key: 'speed', label: '速度' },
  { key: 'stamina', label: '耐力' },
  { key: 'offense', label: '进攻能力' },
  { key: 'defense', label: '防守能力' },
  { key: 'mental', label: '心理素质' }
]

// 对话框标题
const dialogTitle = computed(() => {
  return formData.id ? '编辑能力评估' : '新建能力评估'
})

// 格式化评分显示
const formatScore = (percentage: number) => {
  return `${(percentage / 20).toFixed(1)}分`
}

// 加载学员列表（用于下拉选择）
const loadStudentOptions = async () => {
  try {
    const response = await StudentAPI.getStudentList({
      page_no: 1,
      page_size: 100
    })
    studentOptions.value = response.data.data.items
  } catch (error) {
    console.error('加载学员列表失败:', error)
  }
}

// 加载教练列表（从用户表获取）
const loadCoachOptions = async () => {
  try {
    const response = await UserAPI.listUser({
      page: 1,
      page_size: 100,
      status: "0" // 只获取启用状态的用户
    } as any)
    if (response.data?.data?.items) {
      coachOptions.value = response.data.data.items
    }
  } catch (error) {
    console.error('加载教练列表失败:', error)
  }
}

// 加载评估列表
const loadData = async () => {
  loading.value = true
  try {
    // 处理日期范围查询
    if (queryForm.assessment_date_range && queryForm.assessment_date_range.length === 2) {
      queryForm.assessment_date_start = queryForm.assessment_date_range[0]
      queryForm.assessment_date_end = queryForm.assessment_date_range[1]
    } else {
      queryForm.assessment_date_start = undefined
      queryForm.assessment_date_end = undefined
    }
    
    const response = await AssessmentAPI.getAssessmentList(queryForm)
    // 分页API返回数据结构：{ items: [], total: number, page_no: number, page_size: number }
    tableData.value = response.data.data.items || []
    total.value = response.data.data.total || 0
  } catch (error) {
    console.error('加载评估列表失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  queryForm.page_no = 1
  loadData()
}

// 重置查询条件
const handleReset = () => {
  queryForm.student_id = undefined
  queryForm.assessment_date_range = []
  queryForm.assessment_date_start = undefined
  queryForm.assessment_date_end = undefined
  queryForm.page_no = 1
  loadData()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  queryForm.page_size = size
  loadData()
}

// 页码变化
const handleCurrentChange = (page: number) => {
  queryForm.page_no = page
  loadData()
}

// 表格多选
const handleSelectionChange = (selection: AssessmentTable[]) => {
  multipleSelection.value = selection
}

// 新建评估
const handleCreate = () => {
  // 重置表单数据
  Object.assign(formData, {
    id: undefined,
    student_id: 0,
    assessment_date: '',
    coach_id: useUserStoreHook().basicInfo.id || undefined,
    technique: 3,
    footwork: 3,
    tactics: 3,
    power: 3,
    speed: 3,
    stamina: 3,
    offense: 3,
    defense: 3,
    mental: 3,
    comments: ''
  })
  dialogVisible.value = true
}

// 编辑评估
const handleEdit = (row: AssessmentTable) => {
  Object.assign(formData, {
    id: row.id,
    student_id: row.student_id,
    assessment_date: row.assessment_date,
    coach_id: row.coach_id,
    technique: row.technique,
    footwork: row.footwork,
    tactics: row.tactics,
    power: row.power,
    speed: row.speed,
    stamina: row.stamina,
    offense: row.offense,
    defense: row.defense,
    mental: row.mental,
    comments: row.comments
  })
  dialogVisible.value = true
}

// 删除评估
const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评估记录吗？', '提示', {
      type: 'warning'
    })
    
    await AssessmentAPI.deleteAssessment([id])
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${multipleSelection.value.length} 条评估记录吗？`, '提示', {
      type: 'warning'
    })
    
    const ids = multipleSelection.value.map(item => item.id)
    await AssessmentAPI.deleteAssessment(ids)
    ElMessage.success('批量删除成功')
    multipleSelection.value = []
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 关闭对话框
const handleDialogClose = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate()
  if (!valid) return
  
  submitting.value = true
  try {
    if (formData.id) {
      // 更新
      await AssessmentAPI.updateAssessment(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      // 创建
      await AssessmentAPI.createAssessment(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.msg || '提交失败')
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  loadStudentOptions()
  loadCoachOptions()
  loadData()
})
</script>

<style lang="scss" scoped>
.app-container {
  .search-container {
    background-color: var(--el-fill-color-light);
    padding: 20px;
    border-radius: 4px;
  }
  
  .card-header {
    font-size: 16px;
    font-weight: 500;
  }
}
</style>