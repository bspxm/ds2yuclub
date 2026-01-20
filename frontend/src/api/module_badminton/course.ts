import request from "@/utils/request";

const CourseAPI = {
  // 获取近期课程
  getUpcomingCourses(days: number = 7) {
    return request<ApiResponse<CourseTable[]>>({
      url: "/badminton/course/upcoming",
      method: "get",
      params: { days },
    });
  },

  // 创建课程（排课）
  createCourse(body: CourseForm) {
    return request<ApiResponse<{ course_id: number }>>({
      url: "/badminton/course/schedule",
      method: "post",
      data: body,
    });
  },
};

export default CourseAPI;

// 课程表格数据
export interface CourseTable extends BaseType {
  name: string;
  course_type: string;
  coach_id?: number;
  assistant_coach_id?: number;
  campus?: string;
  court_number?: string;
  start_time: string;
  end_time: string;
  max_students?: number;
  min_students?: number;
  price?: number;
  notes?: string;
  status: string;
  coach?: CommonType;
  assistant_coach?: CommonType;
}

// 课程表单数据
export interface CourseForm {
  name: string;
  course_type: string;
  coach_id?: number;
  assistant_coach_id?: number;
  campus?: string;
  court_number?: string;
  start_time: string;
  end_time: string;
  max_students?: number;
  min_students?: number;
  price?: number;
  notes?: string;
}