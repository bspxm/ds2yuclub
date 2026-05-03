<!-- 学员管理 -->
<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <div v-show="visible" class="search-container">
      <el-form
        ref="queryFormRef"
        :model="queryFormData"
        label-suffix=":"
        :inline="true"
        @submit.prevent="handleQuery"
      >
        <el-form-item prop="name" label="姓名">
          <el-input v-model="queryFormData.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item prop="gender" label="性别">
          <el-select
            v-model="queryFormData.gender"
            placeholder="请选择性别"
            style="width: 120px"
            clearable
          >
            <el-option value="0" label="男" />
            <el-option value="1" label="女" />
            <el-option value="2" label="未知" />
          </el-select>
        </el-form-item>
        <el-form-item prop="group_name" label="所属组别">
          <el-input v-model="queryFormData.group_name" placeholder="请输入组别" clearable />
        </el-form-item>
        <el-form-item prop="campus" label="所属校区">
          <el-input v-model="queryFormData.campus" placeholder="请输入校区" clearable />
        </el-form-item>
        <el-form-item v-if="isExpand" prop="level" label="技术水平">
          <el-input v-model="queryFormData.level" placeholder="请输入技术水平" clearable />
        </el-form-item>
        <el-form-item v-if="isExpand" prop="created_time" label="创建时间">
          <DatePicker
            v-model="createdDateRange"
            @update:model-value="handleCreatedDateRangeChange"
          />
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:student:query']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:student:query']"
            icon="refresh"
            @click="handleResetQuery"
          >
            重置
          </el-button>
          <!-- 展开/收起 -->
          <template v-if="isExpandable">
            <el-link class="ml-3" type="primary" underline="never" @click="isExpand = !isExpand">
              {{ isExpand ? "收起" : "展开" }}
              <el-icon>
                <template v-if="isExpand">
                  <ArrowUp />
                </template>
                <template v-else>
                  <ArrowDown />
                </template>
              </el-icon>
            </el-link>
          </template>
        </el-form-item>
      </el-form>
    </div>

    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            学员管理
            <el-tooltip content="学员信息管理">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
          </span>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:student:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增学员
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:student:import']"
                type="primary"
                icon="download"
                @click="handleDownloadTemplate"
              >
                下载模板
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:student:import']"
                type="warning"
                icon="upload"
                @click="importDialogVisible = true"
              >
                批量导入
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:student:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_badminton:student:patch']" trigger="click">
                <el-button type="default" :disabled="selectIds.length === 0" icon="ArrowDown">
                  更多
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item icon="Check" @click="handleMoreClick('0')">
                      批量启用
                    </el-dropdown-item>
                    <el-dropdown-item icon="CircleClose" @click="handleMoreClick('1')">
                      批量停用
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="搜索显示/隐藏">
                <el-button
                  v-hasPerm="['*:*:*']"
                  type="info"
                  icon="search"
                  circle
                  @click="visible = !visible"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button
                  v-hasPerm="['module_badminton:student:query']"
                  type="primary"
                  icon="refresh"
                  circle
                  @click="handleRefresh"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-popover placement="bottom" trigger="click">
                <template #reference>
                  <el-button type="danger" icon="operation" circle></el-button>
                </template>
                <el-scrollbar max-height="350px">
                  <template v-for="column in tableColumns" :key="column.prop">
                    <el-checkbox v-if="column.prop" v-model="column.show" :label="column.label" />
                  </template>
                </el-scrollbar>
              </el-popover>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 表格区域 -->
      <div class="data-table__content-wrapper">
        <el-table
          ref="tableRef"
          v-loading="loading"
          :data="pageTableData"
          highlight-current-row
          class="data-table__content"
          border
          stripe
          @selection-change="handleSelectionChange"
        >
          <template #empty>
            <el-empty :image-size="80" description="暂无数据" />
          </template>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'selection')?.show"
            type="selection"
            min-width="55"
            align="center"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'index')?.show"
            fixed
            label="序号"
            min-width="60"
          >
            <template #default="scope">
              {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'name')?.show"
            label="姓名"
            prop="name"
            min-width="100"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'gender')?.show"
            label="性别"
            prop="gender"
            min-width="80"
          >
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.gender === '0'
                    ? 'primary'
                    : scope.row.gender === '1'
                      ? 'danger'
                      : 'info'
                "
              >
                {{ scope.row.gender === "0" ? "男" : scope.row.gender === "1" ? "女" : "未知" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'birth_date')?.show"
            label="出生日期"
            prop="birth_date"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'group_name')?.show"
            label="所属组别"
            prop="group_name"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'campus')?.show"
            label="所属校区"
            prop="campus"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'level')?.show"
            label="技术水平"
            prop="level"
            min-width="100"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'total_matches')?.show"
            label="总比赛"
            prop="total_matches"
            min-width="90"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'win_rate')?.show"
            label="胜率"
            prop="win_rate"
            min-width="90"
          >
            <template #default="scope">
              {{ scope.row.win_rate ? `${scope.row.win_rate}%` : "0%" }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'status')?.show"
            label="状态"
            prop="status"
            min-width="90"
          >
            <template #default="scope">
              <el-tag :type="scope.row.status === '0' ? 'success' : 'info'">
                {{ scope.row.status === "0" ? "启用" : "停用" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
            label="创建时间"
            prop="created_time"
            min-width="180"
          >
            <template #default="scope">
              {{ formatDateTime(scope.row.created_time) }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'operation')?.show"
            fixed="right"
            label="操作"
            align="center"
            min-width="180"
          >
            <template #default="scope">
              <el-button
                v-hasPerm="['module_badminton:student:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:student:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:student:delete']"
                type="danger"
                size="small"
                link
                icon="delete"
                @click="handleDelete([scope.row.id])"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页区域 -->
      <template #footer>
        <pagination
          v-model:total="total"
          v-model:page="queryFormData.page_no"
          v-model:limit="queryFormData.page_size"
          @pagination="loadingData"
        />
      </template>
    </el-card>

    <!-- 弹窗区域 -->
    <el-dialog
      v-model="dialogVisible.visible"
      :title="dialogVisible.title"
      width="800px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="英文名">
            {{ detailFormData.english_name || "无" }}
          </el-descriptions-item>
          <el-descriptions-item label="性别">
            <el-tag
              :type="
                detailFormData.gender === '0'
                  ? 'primary'
                  : detailFormData.gender === '1'
                    ? 'danger'
                    : 'info'
              "
            >
              {{
                detailFormData.gender === "0" ? "男" : detailFormData.gender === "1" ? "女" : "未知"
              }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="出生日期">
            {{ detailFormData.birth_date || "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="身高">
            {{ detailFormData.height ? `${detailFormData.height}cm` : "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="体重">
            {{ detailFormData.weight ? `${detailFormData.weight}kg` : "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="惯用手">
            <el-tag>
              {{
                detailFormData.handedness === "right"
                  ? "右手"
                  : detailFormData.handedness === "left"
                    ? "左手"
                    : "双手"
              }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="入训日期">
            {{ detailFormData.join_date }}
          </el-descriptions-item>
          <el-descriptions-item label="技术水平">
            {{ detailFormData.level || "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="所属组别">
            {{ detailFormData.group_name || "未分组" }}
          </el-descriptions-item>
          <el-descriptions-item label="所属校区">
            {{ detailFormData.campus || "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="联系人">
            {{ detailFormData.contact || "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="手机号码">
            {{ detailFormData.mobile || "未设置" }}
          </el-descriptions-item>
          <el-descriptions-item label="总比赛场次">
            {{ detailFormData.total_matches || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="胜场">
            {{ detailFormData.wins || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="负场">
            {{ detailFormData.losses || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="胜率">
            {{ detailFormData.win_rate ? `${detailFormData.win_rate}%` : "0%" }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailFormData.status === '0' ? 'success' : 'info'">
              {{ detailFormData.status === "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ detailFormData.created_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="更新人">
            {{ detailFormData.updated_by?.name || "系统" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(detailFormData.created_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(detailFormData.updated_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detailFormData.description || "无" }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="120px"
          label-position="right"
        >
          <el-row :gutter="20">
            <!-- 第一行：姓名、英文名 -->
            <el-col :span="12">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="formData.name" placeholder="请输入姓名" :maxlength="32" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="英文名">
                <el-input
                  v-model="formData.english_name"
                  placeholder="请输入英文名"
                  :maxlength="64"
                />
              </el-form-item>
            </el-col>

            <!-- 第二行：性别、出生日期 -->
            <el-col :span="12">
              <el-form-item label="性别" prop="gender">
                <el-radio-group v-model="formData.gender">
                  <el-radio value="0">男</el-radio>
                  <el-radio value="1">女</el-radio>
                  <el-radio value="2">未知</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="出生日期">
                <el-date-picker
                  v-model="formData.birth_date"
                  type="date"
                  placeholder="请选择出生日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>

            <!-- 第三行：身高、体重 -->
            <el-col :span="12">
              <el-form-item label="身高(cm)">
                <el-input-number
                  v-model="formData.height"
                  :min="50"
                  :max="250"
                  :step="0.5"
                  placeholder="身高"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="体重(kg)">
                <el-input-number
                  v-model="formData.weight"
                  :min="10"
                  :max="200"
                  :step="0.5"
                  placeholder="体重"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>

            <!-- 第四行：惯用手、入训日期 -->
            <el-col :span="12">
              <el-form-item label="惯用手" prop="handedness">
                <el-select
                  v-model="formData.handedness"
                  placeholder="请选择惯用手"
                  style="width: 100%"
                >
                  <el-option value="right" label="右手" />
                  <el-option value="left" label="左手" />
                  <el-option value="both" label="双手" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="入训日期" prop="join_date">
                <el-date-picker
                  v-model="formData.join_date"
                  type="date"
                  placeholder="请选择入训日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>

            <!-- 第五行：技术水平、所属组别 -->
            <el-col :span="12">
              <el-form-item label="技术水平">
                <el-input v-model="formData.level" placeholder="请输入技术水平" :maxlength="32" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属组别">
                <el-input
                  v-model="formData.group_name"
                  placeholder="请输入所属组别"
                  :maxlength="64"
                />
              </el-form-item>
            </el-col>

            <!-- 第六行：所属校区、联系人 -->
            <el-col :span="12">
              <el-form-item label="所属校区">
                <el-input v-model="formData.campus" placeholder="请输入所属校区" :maxlength="128" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系人">
                <el-input v-model="formData.contact" placeholder="请输入联系人" :maxlength="32" />
              </el-form-item>
            </el-col>

            <!-- 第七行：手机号码、状态 -->
            <el-col :span="12">
              <el-form-item label="手机号码">
                <el-input v-model="formData.mobile" placeholder="请输入手机号码" :maxlength="20" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-radio-group v-model="formData.status">
                  <el-radio value="0">启用</el-radio>
                  <el-radio value="1">停用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>

            <!-- 第八行：备注（跨两列） -->
            <el-col :span="24">
              <el-form-item label="备注">
                <el-input
                  v-model="formData.description"
                  :rows="3"
                  :maxlength="500"
                  show-word-limit
                  type="textarea"
                  placeholder="请输入备注"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button v-if="dialogVisible.type !== 'detail'" type="primary" @click="handleSubmit">
            确定
          </el-button>
          <el-button v-else type="primary" @click="handleCloseDialog">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入学员"
      width="600px"
      @close="handleCloseImportDialog"
    >
      <div class="import-container">
        <el-alert type="info" show-icon class="mb-4">
          <template #title>
            <div>
              <p>
                1. 请先
                <el-link type="primary" @click="handleDownloadTemplate">下载导入模板</el-link>
              </p>
              <p>2. 按照模板格式填写学员信息</p>
              <p>3. 上传填写好的Excel文件</p>
              <p class="text-red-500">注意：姓名、性别、入训日期为必填项</p>
            </div>
          </template>
        </el-alert>

        <!-- 文件上传区域 -->
        <div class="upload-area mb-4">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :limit="1"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :file-list="fileList"
            accept=".xlsx,.xls"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或
              <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">仅支持 Excel 文件 (.xlsx, .xls)，文件大小不超过 10MB</div>
            </template>
          </el-upload>
        </div>

        <!-- 导入结果展示 -->
        <div v-if="importResult" class="import-result">
          <el-divider content-position="left">导入结果</el-divider>
          <div class="result-stats">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="总记录数">
                <el-tag>{{ importResult.total }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="成功数">
                <el-tag type="success">{{ importResult.success }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="失败数">
                <el-tag v-if="importResult.failed > 0" type="danger">
                  {{ importResult.failed }}
                </el-tag>
                <el-tag v-else type="info">{{ importResult.failed }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 错误详情 -->
          <div
            v-if="importResult.errors && importResult.errors.length > 0"
            class="error-details mt-4"
          >
            <el-alert type="error" show-icon title="导入错误详情" />
            <el-table :data="importResult.errors" size="small" border class="mt-2" height="200">
              <el-table-column prop="row" label="行号" width="80" align="center" />
              <el-table-column prop="name" label="学员姓名" min-width="120" />
              <el-table-column prop="error" label="错误信息" min-width="200" />
            </el-table>
          </div>
        </div>

        <!-- 导入进度 -->
        <div v-if="importing" class="import-progress mt-4">
          <el-progress
            :percentage="importProgress"
            :status="importProgress === 100 ? 'success' : ''"
          />
          <div class="progress-text text-center mt-2">
            {{ importMessage }}
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button :disabled="importing" @click="handleCloseImportDialog">取消</el-button>
          <el-button
            type="primary"
            :loading="importing"
            :disabled="!selectedFile || importing"
            @click="handleImportSubmit"
          >
            {{ importing ? "导入中..." : "开始导入" }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Student",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown, UploadFilled } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import DatePicker from "@/components/DatePicker/index.vue";
import StudentAPI, {
  StudentTable,
  StudentForm,
  StudentPageQuery,
  ImportResult,
} from "@/api/module_badminton/student";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<StudentTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 批量导入相关变量
const importDialogVisible = ref(false);
const uploadRef = ref();
const fileList = ref<any[]>([]);
const selectedFile = ref<File | null>(null);
const importing = ref(false);
const importProgress = ref(0);
const importMessage = ref("");
const importResult = ref<ImportResult | null>(null);

// 分页表单
const pageTableData = ref<StudentTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "姓名", show: true },
  { prop: "gender", label: "性别", show: true },
  { prop: "birth_date", label: "出生日期", show: true },
  { prop: "group_name", label: "所属组别", show: true },
  { prop: "campus", label: "所属校区", show: true },
  { prop: "level", label: "技术水平", show: true },
  { prop: "total_matches", label: "总比赛", show: true },
  { prop: "win_rate", label: "胜率", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<StudentTable>({});
// 日期范围临时变量
const createdDateRange = ref<[Date, Date] | []>([]);

// 处理创建时间范围变化
function handleCreatedDateRangeChange(range: [Date, Date]) {
  createdDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.created_time = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.created_time = undefined;
  }
}

// 格式化时间（精确到秒）
function formatDateTime(dateTime: string | null | undefined) {
  if (!dateTime) return "";
  try {
    const date = new Date(dateTime);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    console.error("时间格式化失败:", error);
    return dateTime;
  }
}

// 分页查询参数
const queryFormData = reactive<StudentPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  gender: undefined,
  group_name: undefined,
  campus: undefined,
  level: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<StudentForm>({
  id: undefined,
  name: "",
  english_name: undefined,
  gender: "2",
  birth_date: undefined,
  height: undefined,
  weight: undefined,
  handedness: "right",
  join_date: "",
  level: undefined,
  group_name: undefined,
  campus: undefined,
  contact: undefined,
  mobile: undefined,
  status: "0",
  description: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  gender: [{ required: true, message: "请选择性别", trigger: "blur" }],
  handedness: [{ required: true, message: "请选择惯用手", trigger: "blur" }],
  join_date: [{ required: true, message: "请选择入训日期", trigger: "blur" }],
  status: [{ required: true, message: "请选择状态", trigger: "blur" }],
});

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await StudentAPI.getStudentList(queryFormData);
    pageTableData.value = response.data.data.items;
    total.value = response.data.data.total;
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 查询（重置页码后获取数据）
async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 重置查询
async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  // 重置日期范围选择器
  createdDateRange.value = [];
  queryFormData.created_time = undefined;
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: StudentForm = {
  id: undefined,
  name: "",
  english_name: undefined,
  gender: "2",
  birth_date: undefined,
  height: undefined,
  weight: undefined,
  handedness: "right",
  join_date: "",
  level: undefined,
  group_name: undefined,
  campus: undefined,
  contact: undefined,
  mobile: undefined,
  status: "0",
  description: undefined,
};

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
}

// 行复选框选中项变化
async function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
  selectionRows.value = selection;
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

// 打开弹窗
async function handleOpenDialog(type: "create" | "update" | "detail", id?: number) {
  // 每次打开弹窗前先重置表单
  resetForm();
  dialogVisible.type = type;
  if (id) {
    const response = await StudentAPI.getStudentDetail(id);
    if (type === "detail") {
      dialogVisible.title = "学员详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改学员";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增学员";
    formData.id = undefined;
  }
  dialogVisible.visible = true;
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 保存表单数据副本
  const submitData = { ...formData };
  delete submitData.id;

  // 保存操作类型和ID
  const operationType = formData.id ? "update" : "create";
  const updateId = formData.id;

  // 立即关闭窗口
  handleCloseDialog();

  // 显示持久化通知
  const notification = ElNotification({
    title: operationType === "create" ? "创建" : "更新",
    message: "后台保存中...",
    type: "info",
    duration: 0,
    position: "bottom-right",
  });

  // 在后台保存
  try {
    let res;
    if (operationType === "create") {
      res = await StudentAPI.createStudent(submitData);
    } else if (operationType === "update" && updateId) {
      res = await StudentAPI.updateStudent(updateId, submitData);
    }

    if (res && res.data.code === 0) {
      notification.close();
      ElNotification({
        title: operationType === "create" ? "创建成功" : "更新成功",
        message: operationType === "create" ? "创建成功" : "更新成功",
        type: "success",
        duration: 3000,
        position: "bottom-right",
      });
      handleResetQuery();
    } else {
      notification.close();
      ElNotification({
        title: "操作失败",
        message: res?.data?.msg || "操作失败",
        type: "error",
        duration: 3000,
        position: "bottom-right",
      });
    }
  } catch (error: any) {
    console.error("提交失败:", error);
    notification.close();
    ElNotification({
      title: "提交失败",
      message: "网络错误或服务器异常",
      type: "error",
      duration: 3000,
      position: "bottom-right",
    });
  }
}

// 删除、批量删除
async function handleDelete(ids: number[]) {
  ElMessageBox.confirm("确认删除该学员数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await StudentAPI.deleteStudent(ids);
        handleResetQuery();
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 批量启用/停用
async function handleMoreClick(status: string) {
  if (selectIds.value.length) {
    ElMessageBox.confirm(`确认${status === "0" ? "启用" : "停用"}该学员数据?`, "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(async () => {
        try {
          loading.value = true;
          await StudentAPI.batchSetStudentStatus({ ids: selectIds.value, status });
          handleResetQuery();
        } catch (error: any) {
          console.error(error);
        } finally {
          loading.value = false;
        }
      })
      .catch(() => {
        ElMessageBox.close();
      });
  }
}

// 列表刷新
async function handleRefresh() {
  await loadingData();
}

// ============================================================================
// 批量导入相关方法
// ============================================================================

// 下载导入模板
async function handleDownloadTemplate() {
  try {
    importMessage.value = "正在下载模板...";
    const response = await StudentAPI.downloadImportTemplate();

    // request拦截器返回的是response对象，需要从response.data获取blob
    const blob =
      response.data instanceof Blob
        ? response.data
        : new Blob([response.data], {
            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          });

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `学员导入模板_${new Date().toISOString().slice(0, 10)}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    ElMessage.success("模板下载成功");
  } catch (error: any) {
    console.error("下载模板失败:", error);
    ElMessage.error("模板下载失败，请稍后重试");
  } finally {
    importMessage.value = "";
  }
}

// 关闭导入对话框
function handleCloseImportDialog() {
  importDialogVisible.value = false;
  importResult.value = null;
  fileList.value = [];
  selectedFile.value = null;
  importProgress.value = 0;
  importing.value = false;
  importMessage.value = "";

  // 清除上传组件
  if (uploadRef.value) {
    uploadRef.value.clearFiles();
  }
}

// 文件选择变化
function handleFileChange(file: any, fileList: any[]) {
  if (fileList.length > 0) {
    selectedFile.value = file.raw;
    importResult.value = null; // 清除之前的导入结果
  } else {
    selectedFile.value = null;
  }
}

// 文件超出限制
function handleExceed() {
  ElMessage.warning("最多只能上传一个文件");
}

// 提交导入
async function handleImportSubmit() {
  if (!selectedFile.value) {
    ElMessage.warning("请先选择要导入的文件");
    return;
  }

  // 验证文件类型
  const allowedTypes = [".xlsx", ".xls"];
  const fileName = selectedFile.value.name.toLowerCase();
  const isValidType = allowedTypes.some((type) => fileName.endsWith(type));

  if (!isValidType) {
    ElMessage.warning("只支持 Excel 文件 (.xlsx, .xls)");
    return;
  }

  // 验证文件大小（10MB）
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (selectedFile.value.size > maxSize) {
    ElMessage.warning("文件大小不能超过 10MB");
    return;
  }

  importing.value = true;
  importProgress.value = 10;
  importMessage.value = "正在读取文件...";

  try {
    const formData = new FormData();
    formData.append("file", selectedFile.value);

    importProgress.value = 30;
    importMessage.value = "正在上传文件...";

    const response = await StudentAPI.batchImportStudents(formData);

    importProgress.value = 80;
    importMessage.value = "正在处理导入数据...";

    // 模拟进度完成
    setTimeout(() => {
      importProgress.value = 100;
      importMessage.value = "导入完成";
    }, 500);

    // 处理导入结果
    importResult.value = response.data.data;

    if (importResult.value.failed > 0) {
      ElMessage.warning(
        `导入完成，成功 ${importResult.value.success} 条，失败 ${importResult.value.failed} 条`
      );
    } else {
      ElMessage.success(`导入成功，共导入 ${importResult.value.success} 条学员数据`);

      // 导入成功后刷新表格数据
      setTimeout(() => {
        handleResetQuery();
      }, 1000);
    }

    // 导入完成后重置文件选择
    fileList.value = [];
    selectedFile.value = null;
    if (uploadRef.value) {
      uploadRef.value.clearFiles();
    }
  } catch (error: any) {
    console.error("导入失败:", error);
    ElMessage.error(`导入失败: ${error.response?.data?.msg || error.message}`);
    importResult.value = null;
  } finally {
    // 延迟重置导入状态，让用户能看到结果
    setTimeout(() => {
      importing.value = false;
      importProgress.value = 0;
      importMessage.value = "";
    }, 2000);
  }
}

onMounted(() => {
  loadingData();
});
</script>

<style scoped>
/* 使表格容器使用flex布局自动填充剩余空间 */
.data-table {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.data-table__content-wrapper {
  display: flex;
  flex: 1;
  flex-direction: column;
  overflow: hidden;
}

.data-table__content {
  flex: 1;
}
</style>
