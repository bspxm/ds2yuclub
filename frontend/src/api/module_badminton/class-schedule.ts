import request from "@/utils/request";

const API_PATH = "/badminton/class-schedules";

const ClassScheduleAPI = {
  // 创建排课记录
  createClassSchedule(body: ClassScheduleForm) {
    return request<ApiResponse<ClassScheduleTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 排课记录列表（分页）
  getClassScheduleList(query: ClassSchedulePageQuery) {
    return request<ApiResponse<PageResult<ClassScheduleTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 排课记录详情
  getClassScheduleDetail(id: number) {
    return request<ApiResponse<ClassScheduleTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 更新排课记录（使用 ClassScheduleCreateV2Form 类型）
  updateClassSchedule(id: number, body: ClassScheduleCreateV2Form) {
    return request<ApiResponse<ClassScheduleTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除排课记录（批量）
  deleteClassSchedule(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      params: { ids: ids.join(',') },
    });
  },

  // 获取指定班级的所有排课记录
  getClassSchedulesByClass(class_id: number) {
    return request<ApiResponse<ClassScheduleTable[]>>({
      url: `${API_PATH}/class/${class_id}`,
      method: "get",
    });
  },

  // 获取指定班级的即将上课排课记录
  getUpcomingClassSchedules(class_id: number, days: number = 7) {
    return request<ApiResponse<ClassScheduleTable[]>>({
      url: `${API_PATH}/class/${class_id}/upcoming`,
      method: "get",
      params: { days },
    });
  },

  // 获取可用学员列表（V2版本）
  getAvailableStudents(params: {
    semester_id: number;
    schedule_date: string;
    time_slots: { [key: string]: string[] };
    class_ids?: number[];
  }) {
    return request<ApiResponse<AvailableStudentInfo[]>>({
      url: `${API_PATH}/available-students`,
      method: "get",
      params: {
        ...params,
        time_slots: JSON.stringify(params.time_slots),
        class_ids: params.class_ids ? params.class_ids.join(',') : undefined,
      },
    });
  },

  // 创建排课记录（V2版本）
  createScheduleV2(body: ClassScheduleCreateV2Form) {
    return request<ApiResponse<ClassScheduleTable>>({
      url: `${API_PATH}/v2`,
      method: "post",
      data: body,
    });
  },

  // 获取时间段字典数据
  getTimeSlotDict() {
    return request<ApiResponse<DictDataItem[]>>({
      url: "/system/dict/data/info/badminton_time_slot",
      method: "get",
    });
  },
};

export default ClassScheduleAPI;

// ============================================================================
// 字典数据类型定义
// ============================================================================

// 字典数据项
export interface DictDataItem {
  id: number;
  dict_sort: number;
  dict_label: string;
  dict_value: string;
  css_class: string;
  list_class: string;
  is_default: boolean;
  dict_type: string;
  dict_type_id: number;
  status: string;
  description: string;
  created_time: string;
  updated_time: string;
  uuid: string;
}

// ============================================================================
// V2版本类型定义
// ============================================================================

// 可用学员信息
export interface AvailableStudentInfo {
  student_id: number;
  student_name: string;
  english_name?: string;
  gender?: string;
  birth_date?: string;
  level?: string;
  group_name?: string;
  remaining_sessions: number;
  total_sessions: number;
  used_sessions: number;
  purchase_id: number;
  class_id: number;
  semester_id: number;
}

// 排课记录创建表单（V2版本）
export interface ClassScheduleCreateV2Form {
  semester_id: number | undefined;
  schedule_date: string;
  class_ids: number[];
  coach_id: number | undefined;
  time_slots: { [key: string]: string[] };
  schedule_status: string;
  student_ids: number[];
  location?: string;
  topic?: string;
  content_summary?: string;
  notes?: string;
}

// 时间段信息
export interface TimeSlotInfo {
  id: number;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  day?: string;
}

// 分页查询参数
export interface ClassSchedulePageQuery extends PageQuery {
  class_id?: number;
  schedule_date_start?: string;
  schedule_date_end?: string;
  schedule_status?: string;
}

// 排课记录表格数据
export interface ClassScheduleTable extends BaseType {
  class_id?: number;
  class?: {
    id: number;
    name: string;
  };
  schedule_date?: string;
  day_of_week?: number;
  time_slot_id?: number;
  time_slot_code?: string;
  time_slots_json?: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  schedule_type?: string;
  location?: string;
  coach_id?: number;
  coach?: {
    id: number;
    name: string;
  };
  schedule_status?: string;
  actual_start_time?: string;
  actual_end_time?: string;
  attendance_count?: number;
  student_count?: number;
  absent_count?: number;
  leave_count?: number;
  student_ids?: number[];
  notes?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 排课记录表单数据
export interface ClassScheduleForm extends BaseFormType {
  class_id?: number;
  schedule_date?: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  location?: string;
  coach_id?: number;
  schedule_status?: string;
  notes?: string;
}