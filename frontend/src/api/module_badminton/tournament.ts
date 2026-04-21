import request from "@/utils/request";

const API_PATH = "/badminton/tournament";

const TournamentAPI = {
  // 创建赛事
  createTournament(body: TournamentForm) {
    return request<ApiResponse<TournamentTable>>({
      url: `${API_PATH}`,
      method: "post",
      data: body,
    });
  },

  // 获取赛事列表（后端返回数组，非分页）
  getTournamentList(params?: TournamentPageQuery) {
    return request<ApiResponse<TournamentTable[]>>({
      url: `${API_PATH}`,
      method: "get",
      params,
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

  getTournamentDetail(id: number) {
    console.warn("getTournamentDetail: 后端API未实现");
    return request<ApiResponse<TournamentTable>>({
      url: `${API_PATH}/${id}`,
      method: "get",
    });
  },

  updateTournament(id: number, body: TournamentForm) {
    return request<ApiResponse<TournamentTable>>({
      url: `${API_PATH}/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteTournament(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}`,
      method: "delete",
      data: ids,
    });
  },

  batchSetTournamentStatus(data: { ids: number[]; status: string }) {
    console.warn("batchSetTournamentStatus: 后端API未实现");
    return request<ApiResponse>({
      url: `${API_PATH}/batch-status`,
      method: "post",
      data,
    });
  },
};

// 赛事表格数据
export interface TournamentTable extends BaseType {
  id: number;
  name: string;
  tournament_type: string; // round_robin, pure_group, promotion_relegation, single_elimination
  status: string;
  start_date: string;
  end_date?: string;
  registration_deadline?: string;
  max_participants?: number;
  group_size?: number;
  num_groups?: number;
  match_format?: string;
  points_per_game?: number;
  advance_count?: number;
  advance_top_n?: number;
  description?: string;
  location?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
  participant_count?: number;
  rules_description?: string;
}

export interface TournamentPageQuery extends PageQuery {
  name?: string;
  tournament_type?: string;
  status?: string;
  location?: string;
  start_date?: [string, string] | undefined;
  end_date?: [string, string] | undefined;
  created_time?: [string, string] | undefined;
  updated_time?: [string, string] | undefined;
  created_id?: number;
  updated_id?: number;
}

// 赛事表单数据
export interface TournamentForm extends BaseFormType {
  id?: number;
  name: string;
  tournament_type: string; // 必填：round_robin, pure_group, promotion_relegation, single_elimination
  status?: string;
  start_date: string; // 格式：YYYY-MM-DD
  end_date: string; // 必填：YYYY-MM-DD
  registration_deadline?: string;
  max_participants?: number;
  group_size?: number;
  num_groups?: number;
  match_format?: string;
  points_per_game?: number;
  advance_count?: number;
  advance_top_n?: number;
  description?: string;
  location?: string;
  rules_description?: string;
  format?: string; // 兼容旧字段
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
  name?: string; // 兼容字段，后端返回name或student_name
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
      url: `${API_PATH}/${tournamentId}/participants/batch`,
      method: "post",
      data: { student_ids: studentIds },
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

  // 生成对阵表（超时60秒，对阵生成可能较慢）
  generateMatches(tournamentId: number, useSeeding: boolean = true) {
    return request<ApiResponse<TournamentMatch[]>>({
      url: `${API_PATH}/${tournamentId}/generate-matches`,
      method: "post",
      params: { use_seeding: useSeeding },
      timeout: 60000,
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

  // 获取小组赛详细数据（羽球在线风格）
  getGroupStageData(tournamentId: number, groupId?: number) {
    const params: Record<string, any> = {};
    if (groupId) params.group_id = groupId;
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/group-stage-data`,
      method: "get",
      params,
    });
  },

  // 获取淘汰赛数据
  getKnockoutData(tournamentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/knockout`,
      method: "get",
    });
  },

  // 生成淘汰赛对阵表
  generateKnockout(tournamentId: number, participantIds: number[]) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/knockout/generate`,
      method: "post",
      data: participantIds,
    });
  },

  // 录入淘汰赛比分
  recordKnockoutScore(
    tournamentId: number,
    matchId: number,
    scores: { sets: any[] },
    winnerId: number
  ) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/knockout/matches/${matchId}/score`,
      method: "put",
      params: { winner_id: winnerId }, // winner_id 作为查询参数
      data: scores,
    });
  },

  // 生成锦标赛淘汰赛（从小组赛晋级，超时60秒）
  generateChampionshipKnockout(tournamentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/championship/generate-knockout`,
      method: "post",
      timeout: 60000,
    });
  },

  // 获取锦标赛状态概览
  getChampionshipStatus(tournamentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/championship/status`,
      method: "get",
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

  // 抢位赛：初始化位置
  initPositions(tournamentId: number) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/${tournamentId}/positions/init`,
      method: "post",
    });
  },

  // 抢位赛：获取位置板
  getPositions(tournamentId: number) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/${tournamentId}/positions`,
      method: "get",
    });
  },

  // 抢位赛：生成新一轮
  generateRound(tournamentId: number) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/${tournamentId}/rounds/generate`,
      method: "post",
    });
  },

  // 抢位赛：获取比赛记录
  getPRMatches(tournamentId: number) {
    return request<ApiResponse<any[]>>({
      url: `${API_PATH}/${tournamentId}/pr-matches`,
      method: "get",
    });
  },

  // 结束赛事
  completeTournament(tournamentId: number) {
    return request<ApiResponse<any>>({
      url: `${API_PATH}/${tournamentId}/complete`,
      method: "put",
    });
  },
};

export { TournamentAPIExtended };
export default TournamentAPI;
