<!-- 家长端主页 -->
<template>
  <div class="app-container">
    <!-- 顶部欢迎区域 -->
    <ElCard shadow="hover" class="mb-4">
      <div class="flex flex-wrap justify-between items-center">
        <div class="flex items-center md:mb-0">
          <ElAvatar size="large" src="/src/assets/images/avatar.png" class="mr-20px" />
          <div>
            <div class="text-20px font-bold">
              欢迎家长，{{ welcome }}
            </div>
            <el-text>
              您可以查看学员信息、比赛情况和课程安排
            </el-text>
          </div>
        </div>
        <div class="statItem text-14px text-gray-600 text-right">
          <el-text>今日日期</el-text>
          <div class="mt-5px text-20px">{{ currentDate }}</div>
        </div>
      </div>
    </ElCard>

    <ElRow :gutter="16">
      <!-- 左侧：学员信息 -->
      <ElCol :xl="16" :lg="16" :md="24" :sm="24" :xs="24">
        <!-- 学员信息卡片 -->
        <ElCard shadow="hover" class="mb-4">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">学员信息</span>
              <ElButton
                v-if="currentStudent"
                type="primary"
                link
                @click="handleViewStudentDetail"
              >
                查看详情
              </ElButton>
            </div>
          </template>
          <el-empty
            v-if="!currentStudent"
            :image-size="80"
            description="暂无关联学员"
          />
          <div v-else class="student-info">
            <ElDescriptions :column="2" border>
              <ElDescriptionsItem label="姓名">
                {{ currentStudent.name }}
                <el-tag
                  v-if="currentStudent.gender === '0'"
                  type="primary"
                  size="small"
                >男</el-tag>
                <el-tag
                  v-else-if="currentStudent.gender === '1'"
                  type="danger"
                  size="small"
                >女</el-tag>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="英文名">
                {{ currentStudent.english_name || '无' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="所属组别">
                {{ currentStudent.group_name || '未分组' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="所属校区">
                {{ currentStudent.campus || '未设置' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="技术水平">
                {{ currentStudent.level || '未评估' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="入训日期">
                {{ currentStudent.join_date }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="总比赛场次">
                {{ currentStudent.total_matches || 0 }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="胜率">
                <el-tag :type="getWinRateTagType(currentStudent.win_rate)">
                  {{ currentStudent.win_rate ? `${currentStudent.win_rate}%` : '0%' }}
                </el-tag>
              </ElDescriptionsItem>
            </ElDescriptions>
          </div>
        </ElCard>

        <!-- 近期比赛情况 -->
        <ElCard shadow="hover" class="mb-4">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">近期比赛情况</span>
              <ElButton
                type="primary"
                link
                @click="handleViewAllTournaments"
              >
                查看全部
              </ElButton>
            </div>
          </template>
          <el-empty
            v-if="recentTournaments.length === 0"
            :image-size="80"
            description="暂无比赛记录"
          />
          <ElTimeline v-else>
            <ElTimelineItem
              v-for="tournament in recentTournaments"
              :key="tournament.id"
              :type="getTournamentTimelineType(tournament.status)"
            >
              <div class="tournament-item">
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-center gap-2">
                    <span class="font-medium">
                      {{ tournament.name }}
                    </span>
                    <el-tag
                      size="small"
                      :type="getTournamentStatusTagType(tournament.status)"
                    >
                      {{ getTournamentStatusText(tournament.status) }}
                    </el-tag>
                  </div>
                  <span class="text-xs text-gray-500">
                    {{ formatDate(tournament.start_date) }}
                  </span>
                </div>
                <div class="text-sm mb-2">
                  <span class="text-gray-600">赛制：</span>
                  {{ getTournamentFormatText(tournament.format) }}
                </div>
                <div class="text-sm mb-2" v-if="tournament.result">
                  <span class="text-gray-600">成绩：</span>
                  {{ tournament.result }}
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-500">
                    {{ tournament.location || '未设置场地' }}
                  </span>
                  <ElButton
                    v-if="tournament.id"
                    size="small"
                    type="primary"
                    link
                    @click="handleViewTournamentDetail(tournament.id)"
                  >
                    查看详情
                  </ElButton>
                </div>
              </div>
            </ElTimelineItem>
          </ElTimeline>
        </ElCard>
      </ElCol>

      <!-- 右侧：近期课程安排 + 能力评估 -->
      <ElCol :xl="8" :lg="8" :md="12" :sm="12" :xs="24">
        <!-- 近期课程安排 -->
        <ElCard shadow="hover" class="mb-4">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">近期课程安排</span>
              <ElButton
                type="primary"
                link
                @click="handleViewAllCourses"
              >
                查看全部
              </ElButton>
            </div>
          </template>
          <el-empty
            v-if="recentCourses.length === 0"
            :image-size="80"
            description="暂无课程安排"
          />
          <div v-else class="course-list">
            <div
              v-for="course in recentCourses"
              :key="course.id"
              class="course-item mb-3 p-3 border rounded hover:shadow transition-shadow"
            >
              <div class="flex justify-between items-start mb-2">
                <span class="font-medium">{{ course.course_name }}</span>
                <el-tag
                  size="small"
                  :type="getCourseStatusTagType(course.status)"
                >
                  {{ getCourseStatusText(course.status) }}
                </el-tag>
              </div>
              <div class="text-sm mb-1">
                <el-icon class="mr-1">
                  <Calendar />
                </el-icon>
                {{ formatDateTime(course.start_time) }}
              </div>
              <div class="text-sm mb-2">
                <el-icon class="mr-1">
                  <Clock />
                </el-icon>
                时长: {{ course.duration }}分钟
              </div>
              <div class="text-sm text-gray-600 line-clamp-2">
                {{ course.description || '暂无描述' }}
              </div>
              <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-gray-500">
                  {{ course.instructor_name || '待定教练' }}
                </span>
                <ElButton
                  v-if="course.id"
                  size="small"
                  type="primary"
                  link
                  @click="handleViewCourseDetail(course.id)"
                >
                  详情
                </ElButton>
              </div>
            </div>
          </div>
        </ElCard>

        <!-- 能力评估概览 -->
        <ElCard shadow="hover">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">能力评估概览</span>
              <ElButton
                v-if="currentStudent"
                type="primary"
                link
                @click="handleViewAssessmentDetail"
              >
                查看详情
              </ElButton>
            </div>
          </template>
          <el-empty
            v-if="!currentStudent || !abilityAssessment"
            :image-size="80"
            description="暂无能力评估数据"
          />
          <div v-else class="assessment-overview">
            <div class="text-center mb-4">
              <div class="text-3xl font-bold">
                {{ abilityAssessment.overall_score || 0 }}
              </div>
              <div class="text-sm text-gray-600">综合评分</div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div
                v-for="dimension in assessmentDimensions"
                :key="dimension.key"
                class="dimension-item"
              >
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm">{{ dimension.label }}</span>
                  <span class="text-sm font-bold">
                    {{ abilityAssessment[dimension.key] || 0 }}
                  </span>
                </div>
                <el-progress
                  :percentage="(abilityAssessment[dimension.key] || 0) * 20"
                  :show-text="false"
                  :stroke-width="6"
                  :color="getDimensionColor(abilityAssessment[dimension.key] || 0)"
                />
              </div>
            </div>
            <div class="mt-4 text-center text-xs text-gray-500">
              评估日期: {{ formatDate(abilityAssessment.assessment_date) }}
            </div>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "ParentDashboard",
  inheritAttrs: false,
});

import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Calendar, Clock } from "@element-plus/icons-vue";
import { useUserStoreHook } from "@/store/modules/user.store";
import ParentStudentAPI from "@/api/module_badminton/parent-student";
import StudentAPI, { StudentTable } from "@/api/module_badminton/student";
import TournamentAPI, { TournamentTable } from "@/api/module_badminton/tournament";
import CourseAPI, { CourseTable } from "@/api/module_badminton/course";
import AssessmentAPI, { AbilityAssessmentTable } from "@/api/module_badminton/assessment";

const router = useRouter();
const userStore = useUserStoreHook();

// 当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });
});

const welcome = computed(() => {
  const hour = new Date().getHours();
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

// 当前关联学员
const currentStudent = ref<StudentTable | null>(null);
// 近期比赛
const recentTournaments = ref<TournamentTable[]>([]);
// 近期课程
const recentCourses = ref<CourseTable[]>([]);
// 能力评估
const abilityAssessment = ref<AbilityAssessmentTable | null>(null);

// 能力评估维度配置
const assessmentDimensions = [
  { key: 'technique', label: '技术能力' },
  { key: 'footwork', label: '步法移动' },
  { key: 'tactics', label: '战术意识' },
  { key: 'physical', label: '身体素质' },
  { key: 'mental', label: '心理素质' },
  { key: 'cooperation', label: '配合能力' },
  { key: 'adaptability', label: '适应能力' },
  { key: 'competitiveness', label: '竞技意识' },
  { key: 'growth_potential', label: '成长潜力' }
];

// 加载关联学员信息
const loadStudentInfo = async () => {
  try {
    // 获取当前用户ID
    const currentUserId = userStore.basicInfo.id;
    if (!currentUserId) {
      ElMessage.warning('用户信息未获取到，请重新登录');
      return;
    }
    
    // 获取当前家长关联的学员列表
    const response = await ParentStudentAPI.getStudentsByParent(currentUserId);
    if (response.data.data.length > 0) {
      // 取第一个学员（如果需要，可以修改为支持多个学员的显示）
      const relationWithStudent = response.data.data[0];
      currentStudent.value = relationWithStudent.student;
      
      // 加载学员相关数据
      await loadStudentRelatedData(relationWithStudent.student.id);
    } else {
      ElMessage.info('暂无关联学员');
    }
  } catch (error: any) {
    console.error('加载学员信息失败:', error);
    ElMessage.error('加载学员信息失败');
  }
};

// 加载学员相关数据
const loadStudentRelatedData = async (studentId: number) => {
  try {
    // 加载近期比赛
    const tournamentResponse = await TournamentAPI.getTournamentList({
      page_no: 1,
      page_size: 5,
      student_id: studentId
    });
    recentTournaments.value = tournamentResponse.data.data.items;

    // 加载近期课程
    const courseResponse = await CourseAPI.getCourseList({
      page_no: 1,
      page_size: 5,
      student_id: studentId
    });
    recentCourses.value = courseResponse.data.data.items;

    // 加载最新能力评估
    const assessmentResponse = await AssessmentAPI.getAssessmentList({
      page_no: 1,
      page_size: 1,
      student_id: studentId,
      order_by: 'assessment_date',
      order_desc: true
    });
    if (assessmentResponse.data.data.items.length > 0) {
      abilityAssessment.value = assessmentResponse.data.data.items[0];
    }
  } catch (error: any) {
    console.error('加载相关数据失败:', error);
  }
};

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return '未设置';
  return new Date(dateString).toLocaleDateString('zh-CN');
};

// 格式化日期时间
const formatDateTime = (dateTimeString?: string) => {
  if (!dateTimeString) return '未设置';
  const date = new Date(dateTimeString);
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 获取胜率标签类型
const getWinRateTagType = (winRate?: number) => {
  if (!winRate) return 'info';
  if (winRate >= 70) return 'success';
  if (winRate >= 50) return 'warning';
  return 'danger';
};

// 获取比赛状态标签类型
const getTournamentStatusTagType = (status?: string) => {
  switch (status) {
    case 'planned': return 'info';
    case 'ongoing': return 'warning';
    case 'completed': return 'success';
    case 'cancelled': return 'danger';
    default: return 'info';
  }
};

// 获取比赛状态文本
const getTournamentStatusText = (status?: string) => {
  switch (status) {
    case 'planned': return '计划中';
    case 'ongoing': return '进行中';
    case 'completed': return '已结束';
    case 'cancelled': return '已取消';
    default: return '未知';
  }
};

// 获取比赛时间线类型
const getTournamentTimelineType = (status?: string) => {
  switch (status) {
    case 'completed': return 'success';
    case 'ongoing': return 'warning';
    case 'cancelled': return 'danger';
    default: return 'primary';
  }
};

// 获取赛制文本
const getTournamentFormatText = (format?: string) => {
  switch (format) {
    case 'group_cycle': return '分组循环赛';
    case 'pure_group': return '纯小组赛';
    case 'fixed_zone_promotion': return '定区升降赛';
    case 'single_elimination': return '小组单败制淘汰赛';
    default: return format || '未知';
  }
};

// 获取课程状态标签类型
const getCourseStatusTagType = (status?: string) => {
  switch (status) {
    case 'scheduled': return 'info';
    case 'in_progress': return 'warning';
    case 'completed': return 'success';
    case 'cancelled': return 'danger';
    default: return 'info';
  }
};

// 获取课程状态文本
const getCourseStatusText = (status?: string) => {
  switch (status) {
    case 'scheduled': return '已安排';
    case 'in_progress': return '进行中';
    case 'completed': return '已完成';
    case 'cancelled': return '已取消';
    default: return '未知';
  }
};

// 获取维度颜色
const getDimensionColor = (score: number) => {
  if (score >= 4) return '#67C23A';
  if (score >= 3) return '#E6A23C';
  return '#F56C6C';
};

// 查看学员详情
const handleViewStudentDetail = () => {
  if (currentStudent.value?.id) {
    router.push({
      name: 'StudentDetail',
      params: { id: currentStudent.value.id }
    }).catch(() => {
      ElMessage.warning('查看详情功能暂未实现');
    });
  }
};

// 查看所有比赛
const handleViewAllTournaments = () => {
  router.push({
    name: 'TournamentList'
  }).catch(() => {
    ElMessage.warning('查看比赛列表功能暂未实现');
  });
};

// 查看比赛详情
const handleViewTournamentDetail = (tournamentId: number) => {
  router.push({
    name: 'TournamentDetail',
    params: { id: tournamentId }
  }).catch(() => {
    ElMessage.warning('查看比赛详情功能暂未实现');
  });
};

// 查看所有课程
const handleViewAllCourses = () => {
  router.push({
    name: 'CourseList'
  }).catch(() => {
    ElMessage.warning('查看课程列表功能暂未实现');
  });
};

// 查看课程详情
const handleViewCourseDetail = (courseId: number) => {
  router.push({
    name: 'CourseDetail',
    params: { id: courseId }
  }).catch(() => {
    ElMessage.warning('查看课程详情功能暂未实现');
  });
};

// 查看能力评估详情
const handleViewAssessmentDetail = () => {
  if (currentStudent.value?.id) {
    router.push({
      name: 'AssessmentList',
      query: { student_id: currentStudent.value.id }
    }).catch(() => {
      ElMessage.warning('查看能力评估功能暂未实现');
    });
  }
};

onMounted(() => {
  loadStudentInfo();
});
</script>

<style lang="scss" scoped>
.app-container {
  .student-info {
    .el-descriptions {
      :deep(.el-descriptions__cell) {
        padding: 8px;
      }
    }
  }

  .tournament-item {
    padding: 12px;
    background-color: var(--el-fill-color-light);
    border-radius: 6px;
    border: 1px solid var(--el-border-color);
  }

  .course-item {
    border-color: var(--el-border-color);
    background-color: var(--el-fill-color-light);
  }

  .dimension-item {
    .el-progress {
      margin-top: 4px;
    }
  }
}
</style>