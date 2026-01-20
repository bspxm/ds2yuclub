import request from "@/utils/request";

const API_PATH = "/badminton/purchases";

const PurchaseAPI = {
  // 创建购买记录
  createPurchase(body: PurchaseForm) {
    return request<ApiResponse<PurchaseTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 购买记录列表（分页）
  getPurchaseList(query: PurchasePageQuery) {
    return request<ApiResponse<PageResult<PurchaseTable[]>>>({
      url: `${API_PATH}`,
      method: "get",
      params: query,
    });
  },

  // 购买记录详情
  getPurchaseDetail(id: number) {
    return request<ApiResponse<PurchaseTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  // 更新购买记录
  updatePurchase(id: number, body: PurchaseForm) {
    return request<ApiResponse<PurchaseTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除购买记录（批量）
  deletePurchase(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: body,
    });
  },

  // 获取指定学员的所有购买记录
  getPurchasesByStudent(student_id: number) {
    return request<ApiResponse<PurchaseTable[]>>({
      url: `${API_PATH}/student/${student_id}`,
      method: "get",
    });
  },
};

export default PurchaseAPI;

// 分页查询参数
export interface PurchasePageQuery extends PageQuery {
  student_id?: number;
  semester_id?: number;
  class_id?: number;
  purchase_type?: string;
  status?: string;
  purchase_date_start?: string;
  purchase_date_end?: string;
}

// 购买记录表格数据
export interface PurchaseTable extends BaseType {
  student_id?: number;
  student?: {
    id: number;
    name: string;
  };
  semester_id?: number;
  semester?: {
    id: number;
    name: string;
  };
  class_id?: number;
  class?: {
    id: number;
    name: string;
  };
  purchase_type?: string;
  session_count?: number;
  remaining_sessions?: number;
  unit_price?: number;
  total_amount?: number;
  purchase_date?: string;
  start_date?: string;
  end_date?: string;
  status?: string;
  description?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 购买记录表单数据
export interface PurchaseForm extends BaseFormType {
  student_id?: number;
  semester_id?: number;
  class_id?: number;
  purchase_type?: string;
  session_count?: number;
  unit_price?: number;
  total_amount?: number;
  purchase_date?: string;
  start_date?: string;
  end_date?: string;
  status?: string;
  description?: string;
}