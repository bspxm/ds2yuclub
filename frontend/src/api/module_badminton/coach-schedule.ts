import request from "@/utils/request";

const API_PATH = "/badminton/class-schedules";

const CoachScheduleAPI = {
  // 获取教练在指定日期的排课列表（按时间段分组）
  getCoachScheduleByDate(params: { coach_id: number; schedule_date: string }) {
    return request<ApiResponse<CoachScheduleGroupedData>>({
      url: `${API_PATH}/coach/daily`,
      method: "get",
      params,
    });
  },
};

export default CoachScheduleAPI;

// ============================================================================
// 类型定义
// ============================================================================

// 教练排课分组数据
export interface CoachScheduleGroupedData {
  date: string;
  coach_id: number;
  coach_name: string;
  time_slots: CoachTimeSlotGroup[];
}

// 时间段分组数据
export interface CoachTimeSlotGroup {
  time_slot_code: string;
  time_slot_name: string;
  start_time: string;
  end_time: string;
  schedules: CoachScheduleItem[];
}

// 教练排课项
export interface CoachScheduleItem {
  id: number;
  class_id: number;
  class_name: string;
  location?: string;
  topic?: string;
  content_summary?: string;
  schedule_status: string;
  students: CoachStudentInfo[];
  student_count: number;
  attendance_count?: number;
  notes?: string;
}

// 学员信息
export interface CoachStudentInfo {
  student_id: number;
  student_name: string;
  english_name?: string;
  level?: string;
  group_name?: string;
  has_attended?: boolean;
}
