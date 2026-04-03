import request from "@/utils/request";
import type { StudentTable } from "./student";

const API_PATH = "/badminton/groups";

const GroupAPI = {
  // 分组列表（分页）
  getGroupList(query: GroupPageQuery) {
    return request<ApiResponse<PageResult<GroupTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 分组详情
  getGroupDetail(id: number) {
    return request<ApiResponse<GroupTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 创建分组
  createGroup(body: GroupForm) {
    return request<ApiResponse<GroupTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 更新分组
  updateGroup(id: number, body: GroupForm) {
    return request<ApiResponse<GroupTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除分组（批量）
  deleteGroup(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 获取教练列表
  getCoaches() {
    return request<ApiResponse<CommonType[]>>({
      url: `${API_PATH}/meta/coaches`,
      method: "get",
    });
  },

  // 获取可用学员
  getAvailableStudents(excludeGroupId?: number) {
    return request<ApiResponse<StudentTable[]>>({
      url: `${API_PATH}/meta/available-students`,
      method: "get",
      params: { excludeGroupId },
    });
  },
};

export default GroupAPI;

// 分页查询参数
export interface GroupPageQuery extends PageQuery {
  name?: string;
  coach_id?: number;
  student_id?: number;
  created_time?: string[];
  updated_time?: string[];
  created_id?: number;
  updated_id?: number;
}

// 分组表格数据
export interface GroupTable extends BaseType {
  name?: string;
  description?: string;
  coach_count?: number;
  student_count?: number;
  coaches?: CommonType[];
  students?: StudentTable[];
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 分组表单数据
export interface GroupForm extends BaseFormType {
  name?: string;
  description?: string;
  coach_ids?: number[];
  student_ids?: number[];
}
