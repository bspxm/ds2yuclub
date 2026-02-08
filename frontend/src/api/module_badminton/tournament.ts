import request from "@/utils/request";

const API_PATH = "/badminton/tournaments";

const TournamentAPI = {
  // 创建赛事
  createTournament(body: TournamentForm) {
    return request<ApiResponse<TournamentTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 获取赛事列表
  getTournamentList() {
    return request<ApiResponse<TournamentTable[]>>({
      url: `${API_PATH}`,
      method: "get",
    });
  },

  // 获取进行中的赛事
  getActiveTournaments() {
    return request<ApiResponse<TournamentTable[]>>({
      url: `${API_PATH}/active`,
      method: "get",
    });
  },

  // 获取赛制类型
  getTournamentTypes() {
    return request<ApiResponse<TournamentType[]>>({
      url: "/badminton/tournament/types",
      method: "get",
    });
  },

  // 模拟比赛
  simulateTournament() {
    return request<ApiResponse<any>>({
      url: "/badminton/tournament/simulate",
      method: "post",
    });
  },
};

export default TournamentAPI;

// 赛事表格数据
export interface TournamentTable extends BaseType {
  name: string;
  tournament_type: string;
  status: string;
  start_date: string;
  end_date: string;
  registration_deadline?: string;
  max_participants?: number;
  group_size?: number;
  num_groups?: number;
  match_format?: string;
  points_per_game?: number;
  description?: string;
  location?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 赛事表单数据
export interface TournamentForm extends BaseFormType {
  name: string;
  tournament_type: string;
  start_date: string;
  end_date: string;
  registration_deadline?: string;
  max_participants?: number;
  group_size?: number;
  num_groups?: number;
  match_format?: string;
  points_per_game?: number;
  description?: string;
  location?: string;
}

// 赛制类型
export interface TournamentType {
  value: string;
  label: string;
  description: string;
}
