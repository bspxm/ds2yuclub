import request from "@/utils/request";

const TournamentParticipantAPI = {
  // 报名参赛
  registerTournament(tournamentId: number, studentId: number, seedRank?: number) {
    return request<ApiResponse<any>>({
      url: `/badminton/tournaments/${tournamentId}/register`,
      method: "post",
      params: { student_id: studentId, seed_rank: seedRank },
    });
  },

  // 退赛
  withdrawTournament(participantId: number) {
    return request<ApiResponse<any>>({
      url: `/badminton/tournaments/participants/${participantId}/withdraw`,
      method: "post",
    });
  },

  // 获取赛事所有参赛者
  getTournamentParticipants(tournamentId: number) {
    return request<ApiResponse<TournamentParticipantTable[]>>({
      url: `/badminton/tournaments/${tournamentId}/participants`,
      method: "get",
    });
  },
};

export default TournamentParticipantAPI;

// 参赛者表格数据
export interface TournamentParticipantTable extends BaseType {
  tournament_id: number;
  group_id?: number;
  student_id: number;
  seed_rank?: number;
  final_rank?: number;
  is_withdrawn: boolean;
  matches_played: number;
  matches_won: number;
  matches_lost: number;
  total_points_scored: number;
  total_points_conceded: number;
  tournament?: CommonType;
  group?: CommonType;
  student?: CommonType;
}