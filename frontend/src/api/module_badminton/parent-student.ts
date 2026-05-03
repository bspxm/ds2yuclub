import request from "@/utils/request";
import type { StudentTable } from "./student";

const API_PATH = "/badminton/parent-student";

const ParentStudentAPI = {
  // 创建家长-学员关联
  createParentStudent(body: ParentStudentForm) {
    return request<ApiResponse<ParentStudentTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 获取家长的所有学员
  getStudentsByParent(parentId: number) {
    return request<ApiResponse<ParentStudentWithStudent[]>>({
      url: `${API_PATH}/parent/${parentId}`,
      method: "get",
    });
  },

  // 获取学员的所有家长
  getParentsByStudent(studentId: number) {
    return request<ApiResponse<ParentStudentTable[]>>({
      url: `${API_PATH}/student/${studentId}`,
      method: "get",
    });
  },

  // 删除关联（批量）
  deleteParentStudent(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // ========== 家长移动端 API（通过认证信息获取，无需管理员权限） ==========

  // 获取当前登录家长的学员
  getMyStudents() {
    return request<ApiResponse<ParentStudentWithStudent[]>>({
      url: `${API_PATH}/my-students`,
      method: "get",
    });
  },

  // 获取家长关联学员的考勤记录
  getMyStudentAttendances(studentId: number) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/my-students/${studentId}/attendances`,
      method: "get",
    });
  },

  // 获取家长关联学员的最新评估
  getMyStudentLatestAssessment(studentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/my-students/${studentId}/assessments/latest`,
      method: "get",
    });
  },

  // 获取家长关联学员的评估历史
  getMyStudentAssessmentHistory(studentId: number, limit: number = 5) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/my-students/${studentId}/assessments/history`,
      method: "get",
      params: { limit },
    });
  },

  // 获取家长关联学员的赛事记录
  getMyStudentTournaments(studentId: number) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/my-students/${studentId}/tournaments`,
      method: "get",
    });
  },

  // 获取所有关联（管理端）
  listAll() {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/list-all`,
      method: "get",
    });
  },

  // 根据手机号匹配学员（家长端自助）
  matchByMobile() {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/match-by-mobile`,
      method: "get",
    });
  },

  // 自助绑定学员（家长端）
  selfBind(studentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/self-bind`,
      method: "post",
      data: { student_id: studentId },
    });
  },
};

export default ParentStudentAPI;

// 家长-学员关联表单
export interface ParentStudentForm extends BaseFormType {
  parent_id: number;
  student_id: number;
  relation_type: string;
  is_primary: boolean;
  notes?: string;
}

// 家长-学员关联表格数据
export interface ParentStudentTable extends BaseType {
  parent_id: number;
  student_id: number;
  relation_type: string;
  is_primary: boolean;
  notes?: string;
  parent?: CommonType;
  student?: CommonType;
}

// 家长-学员关联带学员信息
export interface ParentStudentWithStudent {
  relation: ParentStudentTable;
  student: StudentTable;
}
