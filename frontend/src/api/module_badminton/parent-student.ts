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
