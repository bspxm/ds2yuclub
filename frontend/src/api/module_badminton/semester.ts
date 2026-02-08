import request from "@/utils/request";

const API_PATH = "/badminton/semesters";

const SemesterAPI = {
  // 创建学期
  createSemester(body: SemesterForm) {
    return request<ApiResponse<SemesterTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 学期列表（分页）
  getSemesterList(query: SemesterPageQuery) {
    return request<ApiResponse<PageResult<SemesterTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 学期详情
  getSemesterDetail(id: number) {
    return request<ApiResponse<SemesterTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 更新学期
  updateSemester(id: number, body: SemesterForm) {
    return request<ApiResponse<SemesterTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除学期（批量）
  deleteSemester(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 获取当前活跃学期
  getCurrentSemester() {
    return request<ApiResponse<SemesterTable>>({
      url: `${API_PATH}/current`,
      method: "get",
    });
  },
};

export default SemesterAPI;

// 分页查询参数
export interface SemesterPageQuery extends PageQuery {
  name?: string;
  semester_type?: string;
  status?: string;
  start_date_start?: string;
  start_date_end?: string;
}

// 学期表格数据
export interface SemesterTable extends BaseType {
  name?: string;
  semester_type?: string;
  start_date?: string;
  end_date?: string;
  week_count?: number;
  status?: string;
  description?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 学期表单数据
export interface SemesterForm extends BaseFormType {
  name?: string;
  semester_type?: string;
  start_date?: string;
  end_date?: string;
  week_count?: number;
  status?: string;
  description?: string;
}
