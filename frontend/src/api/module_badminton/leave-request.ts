import request from "@/utils/request";

const LeaveRequestAPI = {
  // 获取待审核的请假申请
  getPendingLeaveRequests() {
    return request<ApiResponse<LeaveRequestTable[]>>({
      url: "/badminton/leave-requests/pending",
      method: "get",
    });
  },
};

export default LeaveRequestAPI;

// 请假申请表格数据
export interface LeaveRequestTable extends BaseType {
  student_id: number;
  course_id: number;
  leave_date: string;
  reason: string;
  status: string;
  reviewed_by?: number;
  reviewed_time?: string;
  review_notes?: string;
  student?: CommonType;
  course?: CommonType;
  reviewed_by_user?: CommonType;
}