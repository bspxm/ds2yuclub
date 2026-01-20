import request from "@/utils/request";

const API_PATH = "/badminton/assessments";

const AssessmentAPI = {
  // 创建能力评估
  createAssessment(body: AssessmentForm) {
    return request<ApiResponse<AssessmentTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 更新能力评估
  updateAssessment(id: number, body: AssessmentForm) {
    return request<ApiResponse<AssessmentTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除评估（批量）
  deleteAssessment(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 获取学员最新评估
  getLatestAssessment(studentId: number) {
    return request<ApiResponse<AssessmentTable>>({
      url: `${API_PATH}/student/${studentId}/latest`,
      method: "get",
    });
  },

  // 获取学员评估历史
  getAssessmentHistory(studentId: number, limit: number = 10) {
    return request<ApiResponse<AssessmentTable[]>>({
      url: `${API_PATH}/student/${studentId}/history`,
      method: "get",
      params: { limit },
    });
  },

  // 评估列表查询
  getAssessmentList(query: AssessmentPageQuery) {
    return request<ApiResponse<AssessmentTable[]>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },
};

export default AssessmentAPI;

// 能力评估分页查询参数
export interface AssessmentPageQuery extends PageQuery {
  student_id?: number;
  coach_id?: number;
  min_overall_score?: number;
  max_overall_score?: number;
  assessment_date_start?: string;
  assessment_date_end?: string;
  created_time?: string[];
  updated_time?: string[];
}

// 能力评估表格数据
export interface AssessmentTable extends BaseType {
  student_id: number;
  assessment_date: string;
  coach_id?: number;
  technique: number;
  footwork: number;
  tactics: number;
  power: number;
  speed: number;
  stamina: number;
  offense: number;
  defense: number;
  mental: number;
  overall_score: number;
  comments?: string;
  student?: CommonType;
  coach?: CommonType;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 能力评估表单数据
export interface AssessmentForm extends BaseFormType {
  student_id: number;
  assessment_date: string;
  coach_id?: number;
  technique: number;
  footwork: number;
  tactics: number;
  power: number;
  speed: number;
  stamina: number;
  offense: number;
  defense: number;
  mental: number;
  comments?: string;
}