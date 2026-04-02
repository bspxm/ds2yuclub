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

// 参赛队员
export interface TournamentParticipant {
  id: number;
  student_id: number;
  student_name: string;
  seed_rank?: number;
  final_rank?: number;
  matches_played: number;
  wins: number;
  losses: number;
}

// 比赛对阵
export interface TournamentMatch {
  id: number;
  round_number: number;
  match_number: number;
  round_type: "group_stage" | "knockout" | "promotion_relegation";
  player1: TournamentParticipant;
  player2: TournamentParticipant;
  scores?: MatchScore[];
  winner_id?: number;
  status: "scheduled" | "active" | "completed" | "cancelled";
}

// 比分
export interface MatchScore {
  player1: number;
  player2: number;
}

// 排名
export interface TournamentRanking {
  rank: number;
  participant: TournamentParticipant;
  wins: number;
  losses: number;
  points_diff: number;
}

// H2H记录
export interface H2HRecord {
  tournament_name: string;
  match_date: string;
  player1: TournamentParticipant;
  player2: TournamentParticipant;
  scores: MatchScore[];
  winner_id: number;
}

// 新增API函数
const TournamentAPIExtended = {
  // 批量添加参赛队员
  batchAddParticipants(tournamentId: number, studentIds: number[]) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/participants/batch`,
      method: "post",
      data: { tournament_id: tournamentId, student_ids: studentIds },
    });
  },

  // 获取参赛队员列表
  getParticipants(tournamentId: number) {
    return request<ApiResponse<TournamentParticipant[]>>({
      url: `${API_PATH}/${tournamentId}/participants`,
      method: "get",
    });
  },

  // 移除参赛队员
  removeParticipant(tournamentId: number, participantId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/participants/${participantId}`,
      method: "delete",
    });
  },

  // 生成对阵表
  generateMatches(tournamentId: number, useSeeding: boolean = true) {
    return request<ApiResponse<TournamentMatch[]>>({
      url: `${API_PATH}/${tournamentId}/generate-matches`,
      method: "post",
      data: { use_seeding: useSeeding },
    });
  },

  // 获取对阵列表
  getMatches(tournamentId: number, groupId?: number, roundType?: string) {
    const params: Record<string, any> = {};
    if (groupId) params.group_id = groupId;
    if (roundType) params.round_type = roundType;
    return request<ApiResponse<TournamentMatch[]>>({
      url: `${API_PATH}/${tournamentId}/matches`,
      method: "get",
      params,
    });
  },

  // 获取比赛详情
  getMatchDetail(tournamentId: number, matchId: number) {
    return request<ApiResponse<TournamentMatch>>({
      url: `${API_PATH}/${tournamentId}/matches/${matchId}`,
      method: "get",
    });
  },

  // 录入比分
  recordScore(tournamentId: number, matchId: number, scores: { sets: MatchScore[] }) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/matches/${matchId}/score`,
      method: "put",
      data: scores,
    });
  },

  // 获取排名
  getRankings(tournamentId: number, groupId?: number) {
    const params: Record<string, any> = {};
    if (groupId) params.group_id = groupId;
    return request<ApiResponse<TournamentRanking[]>>({
      url: `${API_PATH}/${tournamentId}/rankings`,
      method: "get",
      params,
    });
  },

  // H2H查询
  getH2H(studentId1: number, studentId2: number) {
    return request<ApiResponse<any>>({
      url: `/badminton/tournament/h2h`,
      method: "get",
      params: { student_id_1: studentId1, student_id_2: studentId2 },
    });
  },
};

export { TournamentAPIExtended };
export default TournamentAPI;
