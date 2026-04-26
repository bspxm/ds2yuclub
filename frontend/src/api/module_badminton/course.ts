import request from "@/utils/request";

const CourseAPI = {
  // 获取近期课程
  getUpcomingCourses(days: number = 7) {
    return request<ApiResponse<CourseTable[]>>({
      url: "/badminton/courses/upcoming",
      method: "get",
      params: { days },
    });
  },

  // 课程列表（分页）
  getCourseList(query: CoursePageQuery) {
    return request<ApiResponse<PageResult<CourseTable[]>>>({
      url: "/badminton/courses",
      method: "get",
      params: query,
    });
  },

  // 创建课程（排课）
  createCourse(body: CourseForm) {
    return request<ApiResponse<{ course_id: number }>>({
      url: "/badminton/courses/schedule",
      method: "post",
      data: body,
    });
  },
};

export default CourseAPI;

// 课程分页查询参数
export interface CoursePageQuery extends PageQuery {
  name?: string;
  course_name?: string;
  course_type?: string;
  coach_id?: number;
  status?: string;
  start_time?: string | string[];
  end_time?: string | string[];
}

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
  course_name?: string;
  duration?: number;
  instructor_name?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 课程表单数据
export interface CourseForm {
  id?: number;
  name: string;
  course_type: string;
  status?: string;
  coach_id?: number;
  assistant_coach_id?: number;
  campus?: string;
  court_number?: string;
  start_time: string;
  end_time: string;
  duration?: number;
  max_students?: number;
  min_students?: number;
  price?: number;
  notes?: string;
}
