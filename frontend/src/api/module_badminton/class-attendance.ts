import request from "@/utils/request";

const API_PATH = "/badminton/class-attendances";

const ClassAttendanceAPI = {
  // 创建考勤记录
  createClassAttendance(body: ClassAttendanceForm) {
    return request<ApiResponse<ClassAttendanceTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 考勤记录列表（分页）
  getClassAttendanceList(query: ClassAttendancePageQuery) {
    return request<ApiResponse<PageResult<ClassAttendanceTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 考勤记录详情
  getClassAttendanceDetail(id: number) {
    return request<ApiResponse<ClassAttendanceTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 更新考勤记录
  updateClassAttendance(id: number, body: ClassAttendanceForm) {
    return request<ApiResponse<ClassAttendanceTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除考勤记录（批量）
  deleteClassAttendance(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 获取指定学员的所有考勤记录
  getClassAttendancesByStudent(student_id: number) {
    return request<ApiResponse<ClassAttendanceTable[]>>({
      url: `${API_PATH}/student/${student_id}`,
      method: "get",
    });
  },

  // 获取指定班级的所有考勤记录
  getClassAttendancesByClass(class_id: number) {
    return request<ApiResponse<ClassAttendanceTable[]>>({
      url: `${API_PATH}/class/${class_id}`,
      method: "get",
    });
  },
};

export default ClassAttendanceAPI;

// 分页查询参数
export interface ClassAttendancePageQuery extends PageQuery {
  student_id?: number;
  class_id?: number;
  schedule_id?: number;
  attendance_status?: string;
  attendance_date_start?: string;
  attendance_date_end?: string;
}

// 考勤记录表格数据
export interface ClassAttendanceTable extends BaseType {
  student_id?: number;
  student?: {
    id: number;
    name: string;
  };
  class_id?: number;
  class?: {
    id: number;
    name: string;
  };
  schedule_id?: number;
  schedule?: {
    id: number;
    schedule_date: string;
    start_time: string;
  };
  attendance_date?: string;
  attendance_status?: string;
  attendance_time?: string;
  leave_reason?: string;
  makeup_schedule_id?: number;
  makeup_schedule?: {
    id: number;
    schedule_date: string;
  };
  notes?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 考勤记录表单数据
export interface ClassAttendanceForm extends BaseFormType {
  student_id?: number;
  class_id?: number;
  schedule_id?: number;
  attendance_date?: string;
  attendance_status?: string;
  attendance_time?: string;
  leave_reason?: string;
  makeup_schedule_id?: number;
  notes?: string;
}
