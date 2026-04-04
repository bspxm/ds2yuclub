import request from "@/utils/request";

const API_PATH = "/badminton/class_";

const ClassAPI = {
  // 创建班级
  createClass(body: ClassForm) {
    return request<ApiResponse<ClassTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 班级列表（分页）
  getClassList(query: ClassPageQuery) {
    return request<ApiResponse<PageResult<ClassTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 班级详情
  getClassDetail(id: number) {
    return request<ApiResponse<ClassTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 更新班级
  updateClass(id: number, body: ClassForm) {
    return request<ApiResponse<ClassTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除班级（批量）
  deleteClass(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 获取指定学期的所有班级
  getClassesBySemester(semester_id: number) {
    return request<ApiResponse<ClassTable[]>>({
      url: `${API_PATH}/semester/${semester_id}`,
      method: "get",
    });
  },

  // 获取班级可用时间段
  getAvailableTimeSlots(classId: number, dayOfWeek?: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${classId}/available-time-slots`,
      method: "get",
      params: dayOfWeek !== undefined ? { day_of_week: dayOfWeek } : {},
    });
  },
};

export default ClassAPI;

// 分页查询参数
export interface ClassPageQuery extends PageQuery {
  name?: string;
  class_type?: string;
  semester_id?: number;
  status?: string;
  class_status?: string;
  coach_id?: number;
}

// 班级表格数据
export interface ClassTable extends BaseType {
  name?: string;
  class_type?: string;
  semester_id?: number;
  semester?: {
    id: number;
    name: string;
  };
  max_students?: number;
  current_students?: number;
  class_time?: string;
  duration_minutes?: number;
  weekly_schedule?: string;
  time_slots_json?: string;
  location?: string;
  coach_id?: number;
  coach?: {
    id: number;
    name: string;
  };
  fee_per_session?: number;
  session_price?: number;
  sessions_per_week?: number;
  total_sessions?: number;
  status?: string;
  class_status?: string;
  description?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 班级表单数据
export interface ClassForm extends BaseFormType {
  name?: string;
  class_type?: string;
  semester_id?: number;
  max_students?: number;
  weekly_schedule?: string;
  weekly_schedule_days?: string[];
  time_slots?: { [day: string]: string[] };
  time_slots_json?: string;
  location?: string;
  coach_id?: number;
  fee_per_session?: number;
  sessions_per_week?: number;
  total_sessions?: number;
  status?: string;
  class_status?: string;
  description?: string;
}

// 时间段接口
export interface TimeSlot {
  id: number;
  schedule_date?: string;
  day_of_week?: number;
  day?: string; // 星期名称，如"周一"
  day_index?: number; // 星期索引，0-6
  slot_code?: string; // 时间段代码，如"A"、"B"
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  location?: string;
  schedule_status?: string;
  display_text?: string;
}

// 班级可用时间段响应接口
export interface AvailableTimeSlotsResponse {
  class_id: number;
  class_name?: string;
  class_type?: string;
  total_sessions?: number;
  sessions_per_week: number;
  time_slots: TimeSlot[];
  class_type_display?: string;
}
