<!-- 购买记录管理 -->
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
        <el-form-item prop="student_id" label="学员">
          <el-select
            v-model="queryFormData.student_id"
            placeholder="学员"
            style="width: 200px"
            clearable
            filterable
          >
            <el-option
              v-for="student in studentList"
              :key="student.id"
              :label="`${student.name}:${calculateAge(student.birth_date)}岁:${student.level || '未设置'}:${student.group_name || '未设置'}`"
              :value="student.id as number"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="purchase_type" label="购买类型">
          <el-select
            v-model="queryFormData.purchase_type"
            placeholder="购买类型"
            style="width: 120px"
            clearable
          >
            <el-option value="new" label="新购" />
            <el-option value="renewal" label="续费" />
            <el-option value="carryover" label="结转" />
            <el-option value="upgrade" label="升级" />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="购买状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="购买状态"
            style="width: 120px"
            clearable
          >
            <el-option value="ACTIVE" label="生效中" />
            <el-option value="COMPLETED" label="已完成" />
            <el-option value="EXPIRED" label="已过期" />
            <el-option value="SETTLED" label="已结算" />
            <el-option value="CANCELLED" label="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item prop="semester_id" label="学期">
          <el-select
            v-model="queryFormData.semester_id"
            placeholder="学期"
            style="width: 150px"
            clearable
          >
            <el-option
              v-for="semester in semesterList"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id as number"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="class_id" label="班级">
          <el-select
            v-model="queryFormData.class_id"
            placeholder="班级"
            style="width: 150px"
            clearable
          >
            <el-option v-for="cls in classList" :key="cls.id" :label="cls.name" :value="cls.id!" />
          </el-select>
        </el-form-item>
        <!-- 查询、重置、展开/收起按钮 -->
        <el-form-item>
          <el-button
            v-hasPerm="['module_badminton:purchase:list']"
            type="primary"
            icon="search"
            @click="handleQuery"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_badminton:purchase:list']"
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
            购买记录管理
            <el-tooltip content="学员课时购买记录管理">
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
                v-hasPerm="['module_badminton:purchase:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增购买记录
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:purchase:create']"
                type="primary"
                icon="document-add"
                @click="handleOpenBatchDialog"
              >
                批量新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_badminton:purchase:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
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
                  v-hasPerm="['module_badminton:purchase:list']"
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
            v-if="tableColumns.find((col) => col.prop === 'student')?.show"
            label="学员"
            prop="student.name"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'semester')?.show"
            label="学期"
            prop="semester.name"
            min-width="100"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'class')?.show"
            label="班级"
            prop="class_ref.name"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'purchase_type')?.show"
            label="购买类型"
            prop="purchase_type"
            min-width="90"
          >
            <template #default="scope">
              <el-tag :type="getPurchaseTypeTagType(scope.row.purchase_type || '') as any">
                {{ getPurchaseTypeText(scope.row.purchase_type || "") }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'session_count')?.show"
            label="购买课次"
            prop="session_count"
            min-width="90"
          >
            <template #default="scope">
              {{ scope.row.session_count || scope.row.total_sessions || 0 }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'remaining_sessions')?.show"
            label="剩余课次"
            prop="remaining_sessions"
            min-width="90"
          >
            <template #default="scope">
              <el-tag :type="(scope.row.remaining_sessions || 0) > 0 ? 'success' : 'danger'">
                {{ scope.row.remaining_sessions || 0 }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'total_amount')?.show"
            label="总金额"
            prop="total_amount"
            min-width="100"
          >
            <template #default="scope">
              ¥{{
                scope.row.total_amount ||
                ((scope.row.total_sessions || 0) * (scope.row.actual_price || 0)).toFixed(2)
              }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'purchase_date')?.show"
            label="购买日期"
            prop="purchase_date"
            min-width="120"
          />
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'status')?.show"
            label="状态"
            prop="status"
            min-width="90"
          >
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status || '') as any">
                {{ getStatusText(scope.row.status || "") }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-if="tableColumns.find((col) => col.prop === 'selected_time_slots')?.show"
            label="选课时间段"
            prop="selected_time_slots"
            min-width="280"
          >
            <template #default="scope">
              <div v-if="scope.row.selected_time_slots" class="time-slots-container">
                <div
                  v-for="(dayGroup, index) in formatSelectedTimeSlots(
                    scope.row.selected_time_slots
                  )"
                  :key="index"
                  class="day-group"
                >
                  <span class="day-label">{{ dayGroup.day }}:</span>
                  <span class="time-labels">{{ dayGroup.slots.join(", ") }}</span>
                </div>
              </div>
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
                v-hasPerm="['module_badminton:purchase:detail']"
                type="info"
                size="small"
                link
                icon="document"
                @click="handleOpenDialog('detail', scope.row.id)"
              >
                详情
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:purchase:update']"
                type="primary"
                size="small"
                link
                icon="edit"
                @click="handleOpenDialog('update', scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['module_badminton:purchase:delete']"
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
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <div v-loading="dialogLoading" element-loading-text="加载中...">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="学员" :span="2">
              {{ detailFormData.student?.name || detailFormData.student_id }}
            </el-descriptions-item>
            <el-descriptions-item label="学期">
              {{ detailFormData.semester?.name || detailFormData.semester_id }}
            </el-descriptions-item>
            <el-descriptions-item label="班级">
              {{ detailFormData.class_ref?.name || detailFormData.class_id }}
            </el-descriptions-item>
            <el-descriptions-item label="购买类型">
              <el-tag :type="getPurchaseTypeTagType(detailFormData.purchase_type || '') as any">
                {{ getPurchaseTypeText(detailFormData.purchase_type || "") }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="购买课次">
              {{ detailFormData.session_count || detailFormData.total_sessions || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="剩余课次">
              <el-tag :type="(detailFormData.remaining_sessions || 0) > 0 ? 'success' : 'danger'">
                {{ detailFormData.remaining_sessions || 0 }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="单价">
              ¥{{ detailFormData.unit_price || detailFormData.actual_price || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="总金额">
              ¥{{
                detailFormData.total_amount ||
                ((detailFormData.total_sessions || 0) * (detailFormData.actual_price || 0)).toFixed(
                  2
                )
              }}
            </el-descriptions-item>
            <el-descriptions-item label="购买日期">
              {{ detailFormData.purchase_date }}
            </el-descriptions-item>
            <el-descriptions-item label="生效开始日期">
              {{ detailFormData.start_date }}
            </el-descriptions-item>
            <el-descriptions-item label="生效结束日期">
              {{ detailFormData.end_date }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusTagType(detailFormData.status || '') as any">
                {{ getStatusText(detailFormData.status || "") }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建人">
              {{ detailFormData.created_by?.name || "系统" }}
            </el-descriptions-item>
            <el-descriptions-item label="更新人">
              {{ detailFormData.updated_by?.name || "系统" }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ detailFormData.created_time }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ detailFormData.updated_time }}
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">
              {{ detailFormData.description || "无" }}
            </el-descriptions-item>
            <el-descriptions-item label="选课时间段" :span="2">
              <div
                v-if="
                  detailFormData.selected_time_slots &&
                  Object.keys(detailFormData.selected_time_slots).length > 0
                "
                class="time-slots-container"
              >
                <div
                  v-for="(dayGroup, index) in formatSelectedTimeSlots(
                    detailFormData.selected_time_slots
                  )"
                  :key="index"
                  class="day-group"
                >
                  <span class="day-label">{{ dayGroup.day }}:</span>
                  <span class="time-labels">{{ dayGroup.slots.join(", ") }}</span>
                </div>
              </div>
              <span v-else style="color: #909399">未选择时间段</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </template>
      <!-- 新增、编辑表单 -->
      <template v-else>
        <div v-loading="dialogLoading" element-loading-text="加载中...">
          <el-form
            ref="dataFormRef"
            :model="formData"
            :rules="rules"
            label-suffix=":"
            label-width="120px"
            label-position="right"
          >
            <el-row :gutter="20">
              <!-- 第一行：学员、学期 -->
              <el-col :span="12">
                <el-form-item label="学员" prop="student_id">
                  <el-select
                    v-model="formData.student_id"
                    placeholder="请选择学员"
                    style="width: 100%"
                    clearable
                    filterable
                  >
                    <el-option
                      v-for="student in studentList"
                      :key="student.id"
                      :label="`${student.name}:${calculateAge(student.birth_date)}岁:${student.level || '未设置'}:${student.group_name || '未设置'}`"
                      :value="student.id as number"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学期" prop="semester_id">
                  <el-select
                    v-model="formData.semester_id"
                    placeholder="请选择学期"
                    style="width: 100%"
                    clearable
                  >
                    <el-option
                      v-for="semester in semesterList"
                      :key="semester.id"
                      :label="semester.name"
                      :value="semester.id!"
                    />
                  </el-select>
                </el-form-item>
              </el-col>

              <!-- 第二行：班级ID、购买类型 -->
              <el-col :span="12">
                <el-form-item label="班级">
                  <el-select
                    v-model="formData.class_id"
                    placeholder="请选择班级"
                    style="width: 100%"
                    clearable
                  >
                    <el-option
                      v-for="cls in classList"
                      :key="cls.id"
                      :label="cls.name"
                      :value="cls.id!"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="购买类型" prop="purchase_type">
                  <el-select
                    v-model="formData.purchase_type"
                    placeholder="请选择购买类型"
                    style="width: 100%"
                  >
                    <el-option value="new" label="新购" />
                    <el-option value="renewal" label="续费" />
                    <el-option value="carryover" label="结转" />
                    <el-option value="upgrade" label="升级" />
                  </el-select>
                </el-form-item>
              </el-col>

              <!-- 第三行：购买课次、单价 -->
              <el-col :span="12">
                <el-form-item label="购买课次">
                  <el-input-number
                    v-model="formData.session_count"
                    :min="1"
                    disabled
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单价">
                  <el-input-number
                    v-model="formData.unit_price"
                    :min="0"
                    :step="10"
                    disabled
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>

              <!-- 第三点五行：总金额 -->
              <el-col :span="24">
                <el-form-item label="总金额">
                  <div style="font-size: 20px; font-weight: bold; color: #f56c6c">
                    ¥{{ formData.total_amount || 0 }}
                  </div>
                </el-form-item>
              </el-col>

              <!-- 第四行：购买日期、生效开始日期 -->
              <el-col :span="12">
                <el-form-item label="购买日期" prop="purchase_date">
                  <el-date-picker
                    v-model="formData.purchase_date"
                    type="date"
                    placeholder="请选择购买日期"
                    style="width: 100%"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="生效开始日期">
                  <el-date-picker
                    v-model="formData.start_date"
                    type="date"
                    placeholder="请选择生效开始日期"
                    style="width: 100%"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </el-col>

              <!-- 第五行：生效结束日期、购买状态 -->
              <el-col :span="12">
                <el-form-item label="生效结束日期">
                  <el-date-picker
                    v-model="formData.end_date"
                    type="date"
                    placeholder="请选择生效结束日期"
                    style="width: 100%"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="购买状态" prop="status">
                  <el-select
                    v-model="formData.status"
                    placeholder="请选择购买状态"
                    style="width: 100%"
                  >
                    <el-option value="ACTIVE" label="生效中" />
                    <el-option value="COMPLETED" label="已完成" />
                    <el-option value="EXPIRED" label="已过期" />
                    <el-option value="SETTLED" label="已结算" />
                    <el-option value="CANCELLED" label="已取消" />
                  </el-select>
                </el-form-item>
              </el-col>

              <!-- 第六行：备注（跨两列） -->
              <el-col :span="24">
                <el-form-item label="上课时间段" prop="selected_time_slots">
                  <div v-if="!formData.class_id" style="color: #909399; font-size: 14px">
                    请先选择班级
                  </div>
                  <div
                    v-else-if="loadingTimeSlotsSingle"
                    style="
                      text-align: center;
                      padding: 40px;
                      background-color: var(--el-fill-color-lighter);
                      border-radius: 4px;
                      border: 1px dashed var(--el-border-color-darker);
                    "
                  >
                    <el-icon class="is-loading" :size="32" color="var(--el-color-primary)">
                      <Loading />
                    </el-icon>
                    <div
                      style="margin-top: 12px; color: var(--el-text-color-regular); font-size: 14px"
                    >
                      加载上课时间段中...
                    </div>
                  </div>
                  <div
                    v-else-if="availableTimeSlotsSingle.length === 0"
                    style="color: #f56c6c; font-size: 14px"
                  >
                    该班级暂无可用时间段
                  </div>
                  <div v-else>
                    <div
                      style="
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                        max-height: 300px;
                        overflow-y: auto;
                        border: 1px solid var(--el-border-color);
                        border-radius: 4px;
                        padding: 15px;
                        background-color: var(--el-fill-color-blank);
                      "
                    >
                      <div
                        v-for="day in getUniqueDaysSingle()"
                        :key="day"
                        style="
                          flex: 1;
                          min-width: 200px;
                          border: 1px solid var(--el-border-color);
                          border-radius: 4px;
                          padding: 10px;
                          background-color: var(--el-fill-color-light);
                        "
                      >
                        <div
                          style="
                            margin-bottom: 10px;
                            font-weight: bold;
                            color: var(--el-text-color-primary);
                            border-bottom: 1px solid var(--el-border-color-light);
                            padding-bottom: 8px;
                            font-size: 16px;
                          "
                        >
                          {{ day }}
                        </div>
                        <el-checkbox-group
                          v-model="formData.selected_time_slots![day]"
                          @change="handleTimeSlotChangeSingle(formData.selected_time_slots!)"
                        >
                          <div style="display: flex; flex-direction: column; gap: 8px">
                            <div
                              v-for="slot in getSlotsByDaySingle(day)"
                              :key="slot.id"
                              style="display: flex; align-items: center"
                            >
                              <el-checkbox
                                :label="slot.slot_code"
                                :disabled="classTypeInfoSingle?.class_type === 'fixed'"
                              >
                                <span
                                  style="
                                    margin-left: 8px;
                                    font-size: 14px;
                                    color: var(--el-text-color-regular);
                                  "
                                >
                                  {{ slot.start_time }}-{{ slot.end_time }}
                                </span>
                              </el-checkbox>
                            </div>
                          </div>
                        </el-checkbox-group>
                      </div>
                    </div>
                    <div
                      v-if="timeSlotWarningSingle"
                      style="margin-top: 8px; color: #e6a23c; font-size: 12px"
                    >
                      <el-icon><WarningFilled /></el-icon>
                      {{ timeSlotWarningSingle }}
                    </div>
                  </div>
                </el-form-item>
              </el-col>

              <!-- 第七行：备注（跨两列） -->
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
        </div>
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

    <!-- 批量新增弹窗 -->
    <el-dialog
      v-model="batchDialogVisible"
      title="批量新增购买记录"
      width="1200px"
      :close-on-click-modal="false"
      @close="handleCloseBatchDialog"
    >
      <el-row :gutter="20">
        <!-- 左侧：学员选择 -->
        <el-col :span="8">
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>选择学员（{{ batchSelectedStudents.length }} 人）</span>
                <el-tag type="info" size="small">
                  已选择 {{ batchSelectedStudents.length }} 人
                </el-tag>
              </div>
            </template>

            <!-- 筛选区域 -->
            <div style="margin-bottom: 15px">
              <el-input
                v-model="batchStudentSearch"
                placeholder="搜索：姓名、手机号或年龄（如：张三、138...、8岁）"
                clearable
                style="width: 100%; margin-bottom: 10px"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-select
                    v-model="batchGroupFilter"
                    placeholder="筛选组别"
                    clearable
                    style="width: 100%"
                  >
                    <el-option label="全部组别" value="" />
                    <el-option
                      v-for="group in uniqueGroups"
                      :key="group"
                      :label="group"
                      :value="group"
                    />
                  </el-select>
                </el-col>
                <el-col :span="12">
                  <el-select
                    v-model="batchLevelFilter"
                    placeholder="筛选水平"
                    clearable
                    style="width: 100%"
                  >
                    <el-option label="全部水平" value="" />
                    <el-option
                      v-for="level in uniqueLevels"
                      :key="level"
                      :label="level"
                      :value="level"
                    />
                  </el-select>
                </el-col>
              </el-row>
            </div>

            <!-- 学员列表 -->
            <div style="height: 450px; overflow-y: auto">
              <el-checkbox-group v-model="batchSelectedStudents">
                <div
                  v-for="student in filteredStudents"
                  :key="student.id"
                  style="padding: 8px; border-bottom: 1px solid #f0f0f0"
                >
                  <el-checkbox :label="student.id">
                    <span style="margin-left: 8px">
                      {{ student.name }}:{{ calculateAge(student.birth_date) }}岁:{{
                        student.level || "未设置"
                      }}:{{ student.group_name || "未设置" }}
                      <span style="color: #909399; font-size: 12px; margin-left: 8px">
                        {{ student.mobile || "无手机号" }}
                      </span>
                    </span>
                  </el-checkbox>
                </div>
              </el-checkbox-group>
              <el-empty v-if="filteredStudents.length === 0" description="暂无学员" />
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：购买信息 -->
        <el-col :span="16">
          <el-card shadow="never">
            <template #header>
              <span>购买信息</span>
            </template>

            <el-form
              ref="batchFormRef"
              :model="batchFormData"
              :rules="batchRules"
              label-suffix=":"
              label-width="100px"
              label-position="right"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="学期" prop="semester_id">
                    <el-select
                      v-model="batchFormData.semester_id"
                      placeholder="请选择学期"
                      style="width: 100%"
                      clearable
                    >
                      <el-option
                        v-for="semester in semesterList"
                        :key="semester.id"
                        :label="semester.name"
                        :value="semester.id as number"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="班级" prop="class_id">
                    <el-select
                      v-model="batchFormData.class_id"
                      placeholder="请选择班级"
                      style="width: 100%"
                      clearable
                      @change="handleClassChange"
                    >
                      <el-option
                        v-for="cls in classList"
                        :key="cls.id"
                        :label="cls.name"
                        :value="cls.id as number"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="购买日期" prop="purchase_date">
                    <el-date-picker
                      v-model="batchFormData.purchase_date"
                      type="date"
                      placeholder="请选择购买日期"
                      style="width: 100%"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="总课时" prop="total_sessions">
                    <el-input-number
                      v-model="batchFormData.total_sessions"
                      :min="1"
                      disabled
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="有效期开始" prop="valid_from">
                    <el-date-picker
                      v-model="batchFormData.valid_from"
                      type="date"
                      placeholder="请选择有效期开始"
                      style="width: 100%"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="有效期截止" prop="valid_until">
                    <el-date-picker
                      v-model="batchFormData.valid_until"
                      type="date"
                      placeholder="请选择有效期截止"
                      style="width: 100%"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="原价" prop="original_price">
                    <el-input-number
                      v-model="batchFormData.original_price"
                      :min="0"
                      :step="10"
                      disabled
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="实付价格" prop="actual_price">
                    <el-input-number
                      v-model="batchFormData.actual_price"
                      :min="0"
                      :step="10"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="上课时间段" prop="selected_time_slots">
                    <div v-if="!batchFormData.class_id" style="color: #909399; font-size: 14px">
                      请先选择班级
                    </div>
                    <div v-else-if="loadingTimeSlots" style="text-align: center; padding: 20px">
                      <el-icon class="is-loading"><Loading /></el-icon>
                      <span style="margin-left: 8px">加载中...</span>
                    </div>
                    <div
                      v-else-if="availableTimeSlots.length === 0"
                      style="color: #f56c6c; font-size: 14px"
                    >
                      该班级暂无可用时间段
                    </div>
                    <div v-else>
                      <div
                        style="
                          display: flex;
                          flex-wrap: wrap;
                          gap: 20px;
                          max-height: 300px;
                          overflow-y: auto;
                          border: 1px solid var(--el-border-color);
                          border-radius: 4px;
                          padding: 15px;
                          background-color: var(--el-fill-color-blank);
                        "
                      >
                        <div
                          v-for="day in getUniqueDays()"
                          :key="day"
                          style="
                            flex: 1;
                            min-width: 200px;
                            border: 1px solid var(--el-border-color);
                            border-radius: 4px;
                            padding: 10px;
                            background-color: var(--el-fill-color-light);
                          "
                        >
                          <div
                            style="
                              margin-bottom: 10px;
                              font-weight: bold;
                              color: var(--el-text-color-primary);
                              border-bottom: 1px solid var(--el-border-color-light);
                              padding-bottom: 8px;
                              font-size: 16px;
                            "
                          >
                            {{ day }}
                          </div>
                          <el-checkbox-group
                            v-model="batchFormData.selected_time_slots![day]"
                            @change="handleTimeSlotChange(batchFormData.selected_time_slots)"
                          >
                            <div style="display: flex; flex-direction: column; gap: 8px">
                              <div
                                v-for="slot in getSlotsByDay(day)"
                                :key="slot.id"
                                style="display: flex; align-items: center"
                              >
                                <el-checkbox
                                  :label="slot.slot_code"
                                  :disabled="classTypeInfo?.class_type === 'fixed'"
                                >
                                  <span
                                    style="
                                      margin-left: 8px;
                                      font-size: 14px;
                                      color: var(--el-text-color-regular);
                                    "
                                  >
                                    {{ slot.start_time }}-{{ slot.end_time }}
                                  </span>
                                </el-checkbox>
                              </div>
                            </div>
                          </el-checkbox-group>
                        </div>
                      </div>
                      <div
                        v-if="timeSlotWarning"
                        style="margin-top: 8px; color: #e6a23c; font-size: 12px"
                      >
                        <el-icon><WarningFilled /></el-icon>
                        {{ timeSlotWarning }}
                      </div>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="购买备注">
                    <el-input
                      v-model="batchFormData.purchase_notes"
                      :rows="3"
                      :maxlength="500"
                      show-word-limit
                      type="textarea"
                      placeholder="请输入购买备注"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseBatchDialog">取消</el-button>
          <el-button
            type="primary"
            :disabled="batchSelectedStudents.length === 0"
            @click="handleBatchSubmit"
          >
            确定（{{ batchSelectedStudents.length }} 人）
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Purchase",
  inheritAttrs: false,
});

import { ref, reactive, onMounted, computed, watch } from "vue";
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import request from "@/utils/request";
import {
  QuestionFilled,
  ArrowUp,
  ArrowDown,
  Search,
  Loading,
  WarningFilled,
} from "@element-plus/icons-vue";
import PurchaseAPI, {
  PurchaseTable,
  PurchaseForm,
  PurchasePageQuery,
  BatchPurchaseForm,
} from "@/api/module_badminton/purchase";
import SemesterAPI, { SemesterTable } from "@/api/module_badminton/semester";
import ClassAPI, {
  ClassTable,
  AvailableTimeSlotsResponse,
  TimeSlot,
} from "@/api/module_badminton/class";
import StudentAPI, { StudentTable } from "@/api/module_badminton/student";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<PurchaseTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);
const dialogLoading = ref(false);

// 分页表单
const pageTableData = ref<PurchaseTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "student", label: "学员", show: true },
  { prop: "semester", label: "学期", show: true },
  { prop: "class", label: "班级", show: true },
  { prop: "purchase_type", label: "购买类型", show: true },
  { prop: "session_count", label: "购买课次", show: true },
  { prop: "remaining_sessions", label: "剩余课次", show: true },
  { prop: "total_amount", label: "总金额", show: true },
  { prop: "purchase_date", label: "购买日期", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "selected_time_slots", label: "选课时间段", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<Partial<PurchaseTable>>({});

// 分页查询参数
const queryFormData = reactive<PurchasePageQuery>({
  page_no: 1,
  page_size: 10,
  student_id: undefined,
  semester_id: undefined,
  class_id: undefined,
  purchase_type: undefined,
  status: undefined,
  purchase_date_start: undefined,
  purchase_date_end: undefined,
});

// 编辑表单
const formData = reactive<PurchaseForm>({
  id: undefined,
  student_id: undefined,
  semester_id: undefined,
  class_id: undefined,
  purchase_type: "new",
  session_count: 10,
  unit_price: 100,
  total_amount: 1000,
  purchase_date: "",
  start_date: "",
  end_date: "",
  status: "ACTIVE",
  description: undefined,
  selected_time_slots: { 周一: [], 周二: [], 周三: [], 周四: [], 周五: [], 周六: [], 周日: [] },
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  student_id: [{ required: true, message: "请选择学员", trigger: "change" }],
  semester_id: [{ required: true, message: "请选择学期", trigger: "change" }],
  purchase_type: [{ required: true, message: "请选择购买类型", trigger: "blur" }],
  purchase_date: [{ required: true, message: "请选择购买日期", trigger: "blur" }],
  status: [{ required: true, message: "请选择购买状态", trigger: "blur" }],
  selected_time_slots: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (!classTypeInfoSingle.value) {
          callback();
          return;
        }
        const requiredCount = classTypeInfoSingle.value.sessions_per_week || 0;
        if (classTypeInfoSingle.value.class_type === "flexible") {
          if (!value || Object.keys(value).length === 0) {
            callback(new Error("请选择上课时间段"));
          } else {
            const selectedCount = Object.keys(value).reduce(
              (sum, day) => sum + (value[day] || []).length,
              0
            );
            if (selectedCount !== requiredCount) {
              callback(new Error(`请选择 ${requiredCount} 个上课时间段`));
            } else {
              callback();
            }
          }
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
});

// 学期列表
const semesterList = ref<SemesterTable[]>([]);

// 班级列表
const classList = ref<ClassTable[]>([]);

// 学员列表
const studentList = ref<StudentTable[]>([]);

// 时间段列表（从字典接口获取）
interface TimeSlotInfo {
  id: number;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
}

const timeSlotList = ref<TimeSlotInfo[]>([]);

// 批量新增弹窗相关
const batchDialogVisible = ref(false);
const batchFormRef = ref();
const batchSelectedStudents = ref<number[]>([]);
const batchStudentSearch = ref("");
const batchGroupFilter = ref("");
const batchLevelFilter = ref("");

// 单个新增表单相关
const availableTimeSlotsSingle = ref<TimeSlot[]>([]);
const classTypeInfoSingle = ref<any>(null);
const loadingTimeSlotsSingle = ref(false);
const timeSlotWarningSingle = ref("");

// 时间段相关
const availableTimeSlots = ref<TimeSlot[]>([]);
const classTypeInfo = ref<AvailableTimeSlotsResponse | null>(null);
const loadingTimeSlots = ref(false);
const timeSlotWarning = ref("");

// 批量新增表单
const batchFormData = reactive<BatchPurchaseForm>({
  student_ids: [],
  semester_id: undefined,
  class_id: undefined,
  purchase_date: "",
  total_sessions: 0,
  valid_from: "",
  valid_until: "",
  original_price: 0,
  actual_price: 0,
  discount_rate: 1.0,
  purchase_notes: undefined,
  selected_time_slots: { 周一: [], 周二: [], 周三: [], 周四: [], 周五: [], 周六: [], 周日: [] },
});

// 批量新增表单验证规则
const batchRules = reactive({
  semester_id: [{ required: true, message: "请选择学期", trigger: "change" }],
  class_id: [{ required: true, message: "请选择班级", trigger: "change" }],
  purchase_date: [{ required: true, message: "请选择购买日期", trigger: "blur" }],
  total_sessions: [{ required: true, message: "请输入购买课次", trigger: "blur" }],
  valid_from: [{ required: true, message: "请选择有效期开始", trigger: "blur" }],
  valid_until: [{ required: true, message: "请选择有效期截止", trigger: "blur" }],
  original_price: [{ required: true, message: "请输入原价", trigger: "blur" }],
  actual_price: [{ required: true, message: "请输入实付价格", trigger: "blur" }],
  selected_time_slots: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (!value || Object.keys(value).length === 0) {
          callback(new Error("请选择上课时间段"));
          return;
        }

        // 如果是自选天班级，验证是否选择了足够的次数
        if (classTypeInfo.value && classTypeInfo.value.class_type === "flexible") {
          const requiredCount = classTypeInfo.value.sessions_per_week || 0;
          const selectedCount = Object.keys(value).reduce(
            (sum, day) => sum + (value[day] || []).length,
            0
          );
          if (selectedCount !== requiredCount) {
            callback();
            return;
          }
        }

        callback();
      },
      trigger: "change",
    },
  ],
});

// 计算属性：过滤后的学员列表
const filteredStudents = computed(() => {
  return studentList.value.filter((student) => {
    // 智能搜索：匹配姓名、手机号或年龄
    let matchSearch = true;
    if (batchStudentSearch.value) {
      const searchTerm = batchStudentSearch.value.toLowerCase().trim();

      // 尝试匹配姓名
      const matchName = student.name?.toLowerCase().includes(searchTerm);

      // 尝试匹配手机号
      const matchPhone = student.mobile?.includes(searchTerm);

      // 尝试匹配年龄（输入"8"匹配8岁，"8岁"也匹配8岁）
      const age = calculateAge(student.birth_date);
      const matchAge = searchTerm.includes("岁")
        ? searchTerm === `${age}岁`
        : searchTerm === age.toString();

      matchSearch = matchName || matchPhone || matchAge;
    }

    // 组别筛选
    const matchGroup = !batchGroupFilter.value || student.group_name === batchGroupFilter.value;

    // 水平筛选
    const matchLevel = !batchLevelFilter.value || student.level === batchLevelFilter.value;

    return matchSearch && matchGroup && matchLevel;
  });
});

// 计算属性：唯一的组别列表
const uniqueGroups = computed(() => {
  const groups = studentList.value.map((s) => s.group_name).filter((g): g is string => !!g);
  return [...new Set(groups)].sort();
});

// 计算属性：唯一的水平列表
const uniqueLevels = computed(() => {
  const levels = studentList.value.map((s) => s.level).filter((l): l is string => !!l);
  return [...new Set(levels)].sort();
});

// 计算年龄
function calculateAge(birthDate: string | undefined): number {
  if (!birthDate) return 0;
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

// 时间段代码映射
const timeSlotMap: Record<string, string> = {
  A: "08:00-09:30",
  B: "09:30-11:00",
  C: "14:00-15:30",
  D: "15:30-17:00",
  E: "18:00-19:30",
};

// 加载时间段字典数据
async function loadTimeSlotDict() {
  if (timeSlotList.value.length > 0) {
    return;
  }

  try {
    const response = await request<ApiResponse<any[]>>({
      url: "/system/dict/data/info/badminton_time_slot",
      method: "get",
    });
    const dictData = response.data.data || [];

    timeSlotList.value = dictData.map((item: any) => ({
      id: item.dict_sort,
      code: item.dict_value,
      name: item.dict_label,
      start_time: item.dict_label.split("-")[0],
      end_time: item.dict_label.split("-")[1],
    }));
  } catch (error: any) {
    console.error("加载时间段字典失败:", error);
  }
}

// 格式化选课时间段
function formatSelectedTimeSlots(
  timeSlots: { [key: string]: string[] } | undefined
): { day: string; slots: string[] }[] {
  if (!timeSlots) return [];

  const result: { day: string; slots: string[] }[] = [];

  // 按天排序
  const dayOrder = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];

  // 遍历每天的时段
  dayOrder.forEach((day) => {
    const daySlots = timeSlots[day];
    if (daySlots && Array.isArray(daySlots) && daySlots.length > 0) {
      const slots: string[] = [];
      daySlots.forEach((slotCode: string) => {
        // 从时间段列表中查找对应的时间段
        const slot = timeSlotList.value.find((s) => s.code === slotCode);
        if (slot) {
          slots.push(`${slot.start_time}-${slot.end_time}`);
        } else {
          // 降级使用 timeSlotMap
          const timeRange = timeSlotMap[slotCode];
          if (timeRange) {
            slots.push(timeRange);
          }
        }
      });
      if (slots.length > 0) {
        result.push({ day, slots });
      }
    }
  });

  return result;
}

// 获取购买类型文本
function getPurchaseTypeText(type: string): string {
  const typeMap: Record<string, string> = {
    new: "新购",
    renewal: "续费",
    carryover: "结转",
    upgrade: "升级",
  };
  return typeMap[type] || "新购";
}

// 获取购买类型标签样式
function getPurchaseTypeTagType(
  type: string
): "primary" | "success" | "warning" | "info" | "danger" {
  const typeMap: Record<string, "primary" | "success" | "warning" | "info" | "danger"> = {
    new: "primary",
    renewal: "success",
    carryover: "warning",
    upgrade: "info",
  };
  return typeMap[type] || "primary";
}

// 获取状态文本
function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    active: "生效中",
    ACTIVE: "生效中",
    completed: "已完成",
    COMPLETED: "已完成",
    expired: "已过期",
    EXPIRED: "已过期",
    settled: "已结算",
    SETTLED: "已结算",
    cancelled: "已取消",
    CANCELLED: "已取消",
  };
  return statusMap[status] || status;
}

// 获取状态标签样式
function getStatusTagType(status: string): "primary" | "success" | "warning" | "info" | "danger" {
  const statusMap: Record<string, "primary" | "success" | "warning" | "info" | "danger"> = {
    active: "success",
    ACTIVE: "success",
    completed: "warning",
    COMPLETED: "warning",
    expired: "danger",
    EXPIRED: "danger",
    settled: "info",
    SETTLED: "info",
    cancelled: "danger",
    CANCELLED: "danger",
  };
  return statusMap[status] || "info";
}

// 加载学期列表（过滤掉已结束的学期）
async function loadSemesterList() {
  try {
    const response = await SemesterAPI.getSemesterList({
      page_no: 1,
      page_size: 100, // 获取学期列表
    });
    // 过滤掉已结束状态的学期
    semesterList.value = response.data.data.items.filter(
      (semester: SemesterTable) => semester.status !== "settled"
    );
  } catch (error: any) {
    console.error("加载学期列表失败:", error);
  }
}

// 加载班级列表（过滤掉已结束的班级）
async function loadClassList() {
  try {
    const response = await ClassAPI.getClassList({
      page_no: 1,
      page_size: 100, // 获取班级列表
    });
    // 过滤掉已结束状态的班级
    classList.value = response.data.data.items.filter(
      (cls: ClassTable) => cls.class_status !== "completed" && cls.class_status !== "cancelled"
    );
  } catch (error: any) {
    console.error("加载班级列表失败:", error);
  }
}

// 加载学员列表（只显示启用状态的学员）
async function loadStudentList() {
  try {
    const response = await StudentAPI.getStudentList({
      page_no: 1,
      page_size: 100,
    });
    // 过滤掉禁用状态的学员（status !== '0' 表示禁用）
    studentList.value = response.data.data.items.filter((student) => student.status === "0");
  } catch (error: any) {
    console.error("加载学员列表失败:", error);
  }
}

// 计算总金额
function calculateTotalAmount() {
  const count = formData.session_count || 0;
  const price = formData.unit_price || 0;
  formData.total_amount = count * price;
}

// 监听班级选择变化，自动填充学期、购买课次和单价
watch(
  () => formData.class_id,
  (newClassId) => {
    // 如果正在加载弹窗数据，不执行自动填充逻辑
    if (dialogLoading.value) return;

    if (newClassId && classList.value.length > 0) {
      const selectedClass = classList.value.find((cls) => cls.id === newClassId);
      if (selectedClass) {
        // 自动填充学期ID
        if (selectedClass.semester_id) {
          formData.semester_id = selectedClass.semester_id;
        }
        // 自动填充购买课次和单价
        if (formData.purchase_type === "single") {
          formData.session_count = 1;
        } else {
          formData.session_count = selectedClass.total_sessions || 0;
        }
        formData.unit_price = selectedClass.session_price || selectedClass.fee_per_session || 0;
        calculateTotalAmount();
      }
    }
    // 加载班级可用时间段，保留已选的时间段
    const currentSelectedSlots =
      formData.selected_time_slots && Object.keys(formData.selected_time_slots).length > 0
        ? formData.selected_time_slots
        : null;
    handleClassChangeSingle(newClassId || 0, currentSelectedSlots);
  }
);

// 监听购买类型变化
watch(
  () => formData.purchase_type,
  (newType) => {
    // 如果正在加载弹窗数据，不执行自动填充逻辑
    if (dialogLoading.value) return;

    if (newType === "single") {
      formData.session_count = 1;
    } else {
      // 如果切回课时包，重新从选中的班级获取总课时
      if (formData.class_id && classList.value.length > 0) {
        const selectedClass = classList.value.find((cls) => cls.id === formData.class_id);
        if (selectedClass) {
          formData.session_count = selectedClass.total_sessions || 0;
        }
      }
    }
    calculateTotalAmount();
  }
);

// 监听购买课次和单价变化
watch(
  () => [formData.session_count, formData.unit_price],
  () => {
    // 如果正在加载弹窗数据，不执行自动填充逻辑
    if (dialogLoading.value) return;
    calculateTotalAmount();
  }
);

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await PurchaseAPI.getPurchaseList(queryFormData);
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
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: PurchaseForm = {
  id: undefined,
  student_id: undefined,
  semester_id: undefined,
  class_id: undefined,
  purchase_type: "new",
  session_count: 10,
  unit_price: 100,
  total_amount: 1000,
  purchase_date: "",
  start_date: "",
  end_date: "",
  status: "ACTIVE",
  description: undefined,
  selected_time_slots: { 周一: [], 周二: [], 周三: [], 周四: [], 周五: [], 周六: [], 周日: [] },
};

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
  // 重置单个新增表单相关变量
  availableTimeSlotsSingle.value = [];
  classTypeInfoSingle.value = null;
  loadingTimeSlotsSingle.value = false;
  timeSlotWarningSingle.value = "";
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

  // 先显示弹窗，提升响应速度
  dialogVisible.visible = true;

  if (id) {
    // 设置加载状态

    dialogLoading.value = true;

    try {
      const response = await PurchaseAPI.getPurchaseDetail(id);

      if (type === "detail") {
        dialogVisible.title = "购买记录详情";

        Object.assign(detailFormData.value, response.data.data);
      } else if (type === "update") {
        dialogVisible.title = "修改购买记录";

        Object.assign(formData, response.data.data);

        // 保存已选的时间段

        const savedSelectedSlots = formData.selected_time_slots || {};

        // 如果有班级ID，加载该班级的可用时间段，并保留已选的时间段

        if (formData.class_id) {
          await handleClassChangeSingle(formData.class_id, savedSelectedSlots);
        }
      }
    } catch (error) {
      console.error("获取购买记录详情失败:", error);

      ElMessage.error("获取购买记录详情失败");
    } finally {
      dialogLoading.value = false;
    }
  } else {
    dialogVisible.title = "新增购买记录";
  }
}

// 提交表单
async function handleSubmit() {
  if (!dataFormRef.value) return;

  const valid = await dataFormRef.value.validate().catch(() => false);
  if (!valid) return;

  // 手动构建 selected_time_slots 对象
  const timeSlots: { [key: string]: string[] } = {};
  if (formData.selected_time_slots) {
    Object.keys(formData.selected_time_slots).forEach((key) => {
      timeSlots[key] = [...(formData.selected_time_slots![key] || [])];
    });
  }

  // 保存表单数据副本
  const submitData = {
    student_id: formData.student_id,
    semester_id: formData.semester_id,
    class_id: formData.class_id,
    purchase_type: formData.purchase_type,
    session_count: formData.session_count,
    unit_price: formData.unit_price,
    total_amount: formData.total_amount,
    total_sessions: formData.session_count,
    original_price: formData.unit_price,
    actual_price: formData.unit_price,
    discount_rate: 1.0,
    purchase_date: formData.purchase_date,
    valid_from: formData.start_date,
    valid_until: formData.end_date,
    status: formData.status,
    purchase_notes: formData.description,
    selected_time_slots: timeSlots,
  };

  // 保存操作类型和ID
  const operationType = dialogVisible.type;
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
      res = await PurchaseAPI.createPurchase(submitData);
    } else if (operationType === "update" && updateId) {
      res = await PurchaseAPI.updatePurchase(updateId, submitData);
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
      loadingData();
    } else if (res) {
      notification.close();
      ElNotification({
        title: "操作失败",
        message: res.data.msg || "操作失败",
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

// 删除
async function handleDelete(ids: number[]) {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${ids.length} 条记录吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await PurchaseAPI.deletePurchase(ids);
    ElMessage.success("删除成功");
    loadingData();
    selectIds.value = [];
  } catch (error: any) {
    if (error !== "cancel") {
      console.error(error);
    }
  }
}

// 打开批量新增弹窗
async function handleOpenBatchDialog() {
  batchSelectedStudents.value = [];
  batchStudentSearch.value = "";
  batchGroupFilter.value = "";
  batchLevelFilter.value = "";
  batchFormData.student_ids = [];
  batchFormData.semester_id = undefined;
  batchFormData.class_id = undefined;
  batchFormData.purchase_date = "";
  batchFormData.total_sessions = 0;
  batchFormData.valid_from = "";
  batchFormData.valid_until = "";
  batchFormData.original_price = 0;
  batchFormData.actual_price = 0;
  batchFormData.discount_rate = 1.0;
  batchFormData.purchase_notes = undefined;
  batchFormData.selected_time_slots = {
    周一: [],
    周二: [],
    周三: [],
    周四: [],
    周五: [],
    周六: [],
    周日: [],
  };
  availableTimeSlots.value = [];
  classTypeInfo.value = null;
  loadingTimeSlots.value = false;
  timeSlotWarning.value = "";
  batchDialogVisible.value = true;
}

// 关闭批量新增弹窗
async function handleCloseBatchDialog() {
  batchDialogVisible.value = false;
  batchSelectedStudents.value = [];
  batchStudentSearch.value = "";
  batchGroupFilter.value = "";
  batchLevelFilter.value = "";
}

// 批量提交
async function handleBatchSubmit() {
  if (!batchFormRef.value) return;

  if (batchSelectedStudents.value.length === 0) {
    ElMessage.warning("请至少选择一名学员");
    return;
  }

  // 验证时间段选择
  if (
    !batchFormData.selected_time_slots ||
    Object.keys(batchFormData.selected_time_slots).length === 0
  ) {
    ElMessage.warning("请选择上课时间段");
    return;
  }

  // 如果是自选天班级，验证是否选择了足够的次数
  if (classTypeInfo.value && classTypeInfo.value.class_type === "flexible") {
    const requiredCount = classTypeInfo.value.sessions_per_week || 0;
    const selectedCount = Object.keys(batchFormData.selected_time_slots || {}).reduce(
      (sum, day) => sum + (batchFormData.selected_time_slots![day] || []).length,
      0
    );
    if (selectedCount !== requiredCount) {
      ElMessage.warning(`请选择 ${requiredCount} 个上课时间段，当前已选择 ${selectedCount} 个`);
      return;
    }
  }

  await batchFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return;

    try {
      // 构建提交数据，确保包含时间段
      // 手动构建 selected_time_slots 对象，避免 Vue Proxy 的问题
      const timeSlots: { [key: string]: string[] } = {};
      if (batchFormData.selected_time_slots) {
        Object.keys(batchFormData.selected_time_slots).forEach((key) => {
          timeSlots[key] = [...(batchFormData.selected_time_slots![key] || [])];
        });
      }

      const submitData = {
        student_ids: batchSelectedStudents.value,
        semester_id: batchFormData.semester_id,
        class_id: batchFormData.class_id,
        purchase_date: batchFormData.purchase_date,
        total_sessions: batchFormData.total_sessions,
        valid_from: batchFormData.valid_from,
        valid_until: batchFormData.valid_until,
        original_price: batchFormData.original_price,
        actual_price: batchFormData.actual_price,
        discount_rate: batchFormData.discount_rate,
        purchase_notes: batchFormData.purchase_notes,
        selected_time_slots: timeSlots,
      };

      console.log("提交的数据:", submitData);
      console.log("时间段数据:", submitData.selected_time_slots);

      await PurchaseAPI.batchCreatePurchase(submitData);
      ElMessage.success(`成功创建 ${batchSelectedStudents.value.length} 条购买记录`);
      batchDialogVisible.value = false;
      loadingData();
    } catch (error: any) {
      console.error(error);
      ElMessage.error("批量创建失败");
    }
  });
}

// 监听班级选择变化，自动填充学期、购买课次和单价
watch(
  () => batchFormData.class_id,
  (newClassId) => {
    if (newClassId && classList.value.length > 0) {
      const selectedClass = classList.value.find((cls) => cls.id === newClassId);
      if (selectedClass) {
        // 自动填充学期ID
        if (selectedClass.semester_id) {
          batchFormData.semester_id = selectedClass.semester_id;
        }
        // 自动填充购买课次和单价
        batchFormData.total_sessions = selectedClass.total_sessions || 0;
        batchFormData.original_price = selectedClass.fee_per_session || 0;
        batchFormData.actual_price = selectedClass.fee_per_session || 0;
      }
    }
  }
);

// 处理班级变化，加载可用时间段
async function handleClassChange(classId: number) {
  if (!classId) {
    availableTimeSlots.value = [];
    classTypeInfo.value = null;
    batchFormData.selected_time_slots = {
      周一: [],
      周二: [],
      周三: [],
      周四: [],
      周五: [],
      周六: [],
      周日: [],
    };
    timeSlotWarning.value = "";
    return;
  }

  loadingTimeSlots.value = true;
  try {
    const response = await ClassAPI.getAvailableTimeSlots(classId);
    const data = response.data.data;

    availableTimeSlots.value = data.time_slots || [];
    classTypeInfo.value = data;

    // 根据班级类型处理默认选择
    if (data.class_type === "fixed") {
      // 固定班：默认全选，转换为星期+代码格式
      const converted: { [key: string]: string[] } = {};
      availableTimeSlots.value.forEach((slot) => {
        const day = slot.day || "";
        if (day) {
          if (!converted[day]) {
            converted[day] = [];
          }
          converted[day].push(slot.slot_code || "");
        }
      });
      batchFormData.selected_time_slots = converted;
      timeSlotWarning.value = "";
    } else if (data.class_type === "flexible") {
      // 自选天：清空选择，需要用户手动选择
      batchFormData.selected_time_slots = {};
      timeSlotWarning.value = `请选择 ${data.sessions_per_week} 个上课时间段`;
    }
  } catch (error: any) {
    console.error("加载班级可用时间段失败:", error);
    ElMessage.error("加载班级可用时间段失败");
    availableTimeSlots.value = [];
    classTypeInfo.value = null;
    batchFormData.selected_time_slots = {};
  } finally {
    loadingTimeSlots.value = false;
  }
}

// 处理时间段选择变化
function handleTimeSlotChange(selectedSlots: any) {
  if (!classTypeInfo.value) return;

  const requiredCount = classTypeInfo.value.sessions_per_week || 0;
  const selectedCount = Object.keys(selectedSlots).reduce(
    (sum, day) => sum + selectedSlots[day].length,
    0
  );

  if (classTypeInfo.value.class_type === "flexible") {
    if (selectedCount < requiredCount) {
      timeSlotWarning.value = `已选择 ${selectedCount} 个时间段，还需选择 ${requiredCount - selectedCount} 个`;
    } else if (selectedCount > requiredCount) {
      timeSlotWarning.value = `已选择 ${selectedCount} 个时间段，超出 ${selectedCount - requiredCount} 个`;
    } else {
      timeSlotWarning.value = "";
    }
  }
}

// 获取所有不重复的星期
function getUniqueDays(): string[] {
  const days = availableTimeSlots.value
    .map((slot) => slot.day)
    .filter((d): d is string => d !== undefined);
  const dayOrder = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
  // 按星期顺序排序
  return [...new Set(days)].sort((a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b));
}

// 获取指定星期的时间段
function getSlotsByDay(day: string) {
  const slots = availableTimeSlots.value.filter((slot) => slot.day === day);
  // 按开始时间排序
  return slots.sort((a, b) => {
    if (!a.start_time || !b.start_time) return 0;
    return a.start_time.localeCompare(b.start_time);
  });
}

// 单个新增表单的辅助函数
function getUniqueDaysSingle(): string[] {
  const days = availableTimeSlotsSingle.value
    .map((slot) => slot.day)
    .filter((d): d is string => d !== undefined);
  const dayOrder = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
  return [...new Set(days)].sort((a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b));
}

function getSlotsByDaySingle(day: string) {
  const slots = availableTimeSlotsSingle.value.filter((slot) => slot.day === day);
  return slots.sort((a, b) => {
    if (!a.start_time || !b.start_time) return 0;
    return a.start_time.localeCompare(b.start_time);
  });
}

function handleTimeSlotChangeSingle(selectedSlots: any) {
  if (!classTypeInfoSingle.value) return;

  const requiredCount = classTypeInfoSingle.value.sessions_per_week || 0;
  const selectedCount = Object.keys(selectedSlots).reduce(
    (sum, day) => sum + selectedSlots[day].length,
    0
  );

  if (classTypeInfoSingle.value.class_type === "flexible") {
    if (selectedCount < requiredCount) {
      timeSlotWarningSingle.value = `已选择 ${selectedCount} 个时间段，还需选择 ${requiredCount - selectedCount} 个`;
    } else if (selectedCount > requiredCount) {
      timeSlotWarningSingle.value = `已选择 ${selectedCount} 个时间段，超出 ${selectedCount - requiredCount} 个`;
    } else {
      timeSlotWarningSingle.value = "";
    }
  }
}

async function handleClassChangeSingle(
  classId: number,
  preserveSelectedSlots: { [key: string]: string[] } | null = null
) {
  if (!classId) {
    availableTimeSlotsSingle.value = [];
    classTypeInfoSingle.value = null;
    formData.selected_time_slots = {
      周一: [],
      周二: [],
      周三: [],
      周四: [],
      周五: [],
      周六: [],
      周日: [],
    };
    timeSlotWarningSingle.value = "";
    return;
  }

  loadingTimeSlotsSingle.value = true;
  try {
    const response = await ClassAPI.getAvailableTimeSlots(classId);
    const data = response.data.data;

    availableTimeSlotsSingle.value = data.time_slots || [];
    classTypeInfoSingle.value = data;

    // 根据班级类型处理默认选择
    if (data.class_type === "fixed") {
      // 固定班：默认全选，转换为星期+代码格式
      const converted: { [key: string]: string[] } = {};
      availableTimeSlotsSingle.value.forEach((slot) => {
        const day = slot.day || "";
        if (day) {
          if (!converted[day]) {
            converted[day] = [];
          }
          converted[day].push(slot.slot_code || "");
        }
      });
      formData.selected_time_slots = converted;
      timeSlotWarningSingle.value = "";
    } else if (data.class_type === "flexible") {
      // 自选天：如果需要保留已选时间段，则使用它们；否则清空选择
      if (preserveSelectedSlots && typeof preserveSelectedSlots === "object") {
        formData.selected_time_slots = preserveSelectedSlots;
        timeSlotWarningSingle.value = "";
      } else {
        formData.selected_time_slots = {};
        timeSlotWarningSingle.value = `请选择 ${data.sessions_per_week} 个上课时间段`;
      }
    }
  } catch (error: any) {
    console.error("加载班级可用时间段失败:", error);
    ElMessage.error("加载班级可用时间段失败");
    availableTimeSlotsSingle.value = [];
    classTypeInfoSingle.value = null;
    formData.selected_time_slots = {};
  } finally {
    loadingTimeSlotsSingle.value = false;
  }
}

// 刷新
async function handleRefresh() {
  loadingData();
}

// 页面加载时获取数据
onMounted(() => {
  loadingData();
  loadSemesterList();
  loadClassList();
  loadStudentList();
  loadTimeSlotDict();
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
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.data-table__content {
  flex: 1;
}

/* 时间段显示样式 */
.time-slots-container {
  line-height: 1.8;
}

.day-group {
  display: flex;
  align-items: flex-start;
  margin-bottom: 4px;
}

.day-label {
  font-weight: 600;
  color: #606266;
  min-width: 40px;
  flex-shrink: 0;
}

.time-labels {
  color: #909399;
  font-size: 13px;
}
</style>
