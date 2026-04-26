<template>
  <div class="parent-student-page">
    <van-loading v-if="loading" size="24px" class="loading" />
    <van-empty v-else-if="!student" description="暂无关联学员" />

    <template v-else>
      <van-cell-group inset>
        <van-cell title="姓名" :value="student.name" />
        <van-cell title="英文名" :value="student.english_name || '无'" />
        <van-cell title="技术水平" :value="student.level || '未评估'" />
        <van-cell title="组别" :value="student.group_name || '未分组'" />
      </van-cell-group>

      <van-cell-group inset style="margin-top: 12px">
        <van-cell title="出勤统计" />
        <van-cell title="总出勤次数" :value="attendanceStats.total" />
        <van-cell title="本月出勤" :value="attendanceStats.monthly" />
      </van-cell-group>

      <van-cell-group inset style="margin-top: 12px">
        <van-cell
          title="最近评估"
          is-link
          :value="latestAssessment ? formatDate(latestAssessment.assessment_date) : '暂无'"
          @click="showAssessment = true"
        />
      </van-cell-group>

      <van-cell-group inset style="margin-top: 12px">
        <van-cell title="近期课程" />
        <van-cell
          v-for="c in recentCourses"
          :key="c.id"
          :title="c.class_name || '课程'"
          :label="c.schedule_date"
          :value="
            c.attendance_status === 'PRESENT'
              ? '已出勤'
              : c.attendance_status === 'ABSENT'
                ? '缺勤'
                : c.attendance_status === 'LEAVE'
                  ? '请假'
                  : '未记录'
          "
        />
        <van-empty v-if="recentCourses.length === 0" description="暂无课程记录" />
      </van-cell-group>
    </template>

    <van-dialog v-model:show="showAssessment" title="能力评估">
      <div v-if="latestAssessment" class="assessment-detail">
        <div v-for="dim in dimensions" :key="dim.key" class="assess-row">
          <span class="assess-label">{{ dim.label }}</span>
          <van-rate
            v-model="latestAssessment[dim.key]"
            :count="10"
            size="16px"
            readonly
            void-icon="star-o"
            void-color="#eee"
          />
        </div>
      </div>
      <div v-else style=" padding: 20px;text-align: center">暂无评估数据</div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "@/store";
import ParentStudentAPI from "@/api/module_badminton/parent-student";
import ClassAttendanceAPI from "@/api/module_badminton/class-attendance";
import AssessmentAPI from "@/api/module_badminton/assessment";

const userStore = useUserStore();
const currentUser = computed(() => userStore.getBasicInfo);

interface StudentDisplay {
  id: number;
  name: string;
  english_name?: string;
  level?: string;
  group_name?: string;
}

const loading = ref(false);
const student = ref<StudentDisplay | null>(null);
const attendanceStats = ref({ total: 0, monthly: 0 });
const recentCourses = ref<any[]>([]);
const latestAssessment = ref<any>(null);
const showAssessment = ref(false);

const dimensions = [
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

function formatDate(d: string) {
  if (!d) return "";
  return d.split("T")[0];
}

onMounted(async () => {
  const parentId = currentUser.value.id;
  if (!parentId) return;

  loading.value = true;
  try {
    const res = await ParentStudentAPI.getStudentsByParent(parentId);
    const relations = res.data.data || [];
    if (relations.length === 0) {
      loading.value = false;
      return;
    }

    const stuData = relations[0].student;
    if (!stuData || !stuData.id) {
      loading.value = false;
      return;
    }
    const sid = stuData.id;
    student.value = {
      id: sid,
      name: stuData.name || "",
      english_name: stuData.english_name,
      level: stuData.level,
      group_name: stuData.group_name,
    };

    const [attStu, assessStu] = await Promise.all([
      ClassAttendanceAPI.getClassAttendancesByStudent(sid).catch(() => ({ data: { data: [] } })),
      AssessmentAPI.getLatestAssessment(sid).catch(() => ({ data: { data: null } })),
    ]);

    const attList = attStu.data.data || [];
    attendanceStats.value = {
      total: attList.length,
      monthly: attList.filter((a: any) => {
        const d = new Date(a.attendance_date);
        const now = new Date();
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
      }).length,
    };
    recentCourses.value = attList.slice(-5).reverse();
    latestAssessment.value = assessStu.data.data;
  } catch {
    // silent
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.parent-student-page {
  padding-bottom: 24px;
}

.loading {
  margin-top: 60px;
}

.assessment-detail {
  padding: 16px;
}

.assess-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}

.assess-label {
  min-width: 48px;
  font-size: 14px;
}
</style>
