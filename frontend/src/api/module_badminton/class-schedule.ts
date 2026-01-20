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

  // 更新排课记录
  updateClassSchedule(id: number, body: ClassScheduleForm) {
    return request<ApiResponse<ClassScheduleTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除排课记录（批量）
  deleteClassSchedule(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
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
};

export default ClassScheduleAPI;

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
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
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
  absent_count?: number;
  leave_count?: number;
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