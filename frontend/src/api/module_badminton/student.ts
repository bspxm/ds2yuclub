import request from "@/utils/request";

const API_PATH = "/badminton/students";

const StudentAPI = {
  // 学员列表（分页）
  getStudentList(query: StudentPageQuery) {
    return request<ApiResponse<PageResult<StudentTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 学员详情
  getStudentDetail(id: number) {
    return request<ApiResponse<StudentTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 创建学员
  createStudent(body: StudentForm) {
    return request<ApiResponse<StudentTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 更新学员
  updateStudent(id: number, body: StudentForm) {
    return request<ApiResponse<StudentTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除学员（批量）
  deleteStudent(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 批量设置状态
  batchSetStudentStatus(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/batch-status`,
      method: "post",
      data: body,
    });
  },

  // 下载导入模板
  downloadImportTemplate() {
    return request<Blob>({
      url: `${API_PATH}/import-template`,
      method: "get",
      responseType: "blob",
    });
  },

  // 批量导入学员
  batchImportStudents(formData: FormData) {
    return request<ApiResponse<ImportResult>>({
      url: `${API_PATH}/import`,
      method: "post",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

// 导入结果接口
export interface ImportResult {
  total: number;
  success: number;
  failed: number;
  errors: Array<{
    row: number;
    name: string;
    error: string;
  }>;
}

export default StudentAPI;

// 分页查询参数
export interface StudentPageQuery extends PageQuery {
  name?: string;
  gender?: string;
  group_name?: string;
  campus?: string;
  level?: string;
  created_time?: string[];
  updated_time?: string[];
  created_id?: number;
  updated_id?: number;
}

// 学员表格数据
export interface StudentTable extends BaseType {
  name?: string;
  english_name?: string;
  gender?: string;
  birth_date?: string;
  height?: number;
  weight?: number;
  handedness?: string;
  join_date?: string;
  level?: string;
  group_name?: string;
  campus?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  total_matches?: number;
  wins?: number;
  losses?: number;
  win_rate?: number;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 学员表单数据
export interface StudentForm extends BaseFormType {
  name?: string;
  english_name?: string;
  gender?: string;
  birth_date?: string;
  height?: number;
  weight?: number;
  handedness?: string;
  join_date?: string;
  level?: string;
  group_name?: string;
  campus?: string;
  emergency_contact?: string;
  emergency_phone?: string;
}