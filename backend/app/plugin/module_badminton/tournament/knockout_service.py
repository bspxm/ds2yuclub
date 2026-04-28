"""
淘汰赛服务模块

提供单败淘汰赛的数据生成、晋级逻辑和状态管理
"""

import math
from typing import Optional

from sqlalchemy import text

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.exceptions import CustomException

from .model import TournamentMatchModel
from .crud import TournamentMatchCRUD


class KnockoutService:
    """淘汰赛服务"""

    @classmethod
    async def get_knockout_data(cls, tournament_id: int, auth: AuthSchema) -> dict:
        """获取淘汰赛数据"""
        # 查询所有淘汰赛比赛，直接JOIN获取选手信息
        sql = text("""
            SELECT 
                m.id,
                m.round_number,
                m.match_number,
                m.player1_id,
                m.player2_id,
                m.scores,
                m.winner_id,
                m.status,
                m.prev_match1_id,
                m.prev_match2_id,
                m.next_match_id,
                p1.id as p1_id,
                p2.id as p2_id,
                s1.name as player1_name,
                s2.name as player2_name,
                p1.seed_rank as player1_seed,
                p2.seed_rank as player2_seed
            FROM badminton_tournament_match m
            LEFT JOIN badminton_tournament_participant p1 ON m.player1_id = p1.id
            LEFT JOIN badminton_tournament_participant p2 ON m.player2_id = p2.id
            LEFT JOIN view_badminton_student_list s1 ON p1.student_id = s1.id
            LEFT JOIN view_badminton_student_list s2 ON p2.student_id = s2.id
            WHERE m.tournament_id = :tournament_id
            AND m.round_type = 'KNOCKOUT'
            ORDER BY m.round_number, m.match_number
        """)

        result = await auth.db.execute(sql, {"tournament_id": tournament_id})
        rows = result.mappings().all()

        if not rows:
            return {
                "matches": [],
                "total_rounds": 0,
                "current_round": None,
                "is_completed": False,
            }

        # 构建比赛数据
        matches = []
        for row in rows:
            match = {
                "id": row["id"],
                "round": cls._get_round_label(row["round_number"]),
                "round_number": row["round_number"],
                "match_number": row["match_number"],
                "status": row["status"],
                "prev_match1_id": row["prev_match1_id"],
                "prev_match2_id": row["prev_match2_id"],
                "next_match_id": row["next_match_id"],
                "player1": {
                    "id": row["player1_id"],
                    "name": row["player1_name"],
                    "seed": row["player1_seed"],
                    "is_winner": row["winner_id"] == row["player1_id"]
                    if row["winner_id"]
                    else False,
                }
                if row["player1_id"]
                else None,
                "player2": {
                    "id": row["player2_id"],
                    "name": row["player2_name"],
                    "seed": row["player2_seed"],
                    "is_winner": row["winner_id"] == row["player2_id"]
                    if row["winner_id"]
                    else False,
                }
                if row["player2_id"]
                else None,
                "scores": cls._format_scores(row["scores"]),
                "winner_id": row["winner_id"],
            }
            matches.append(match)

        # 计算总轮数
        total_rounds = max(m["round_number"] for m in matches) if matches else 0

        # 确定当前轮次
        current_round = None
        for m in matches:
            if m["status"] == "SCHEDULED":
                current_round = m["round"]
                break

        # 检查是否完成
        is_completed = all(
            m["status"] == "COMPLETED"
            for m in matches
            if m["round_number"] == total_rounds
        )

        return {
            "matches": matches,
            "total_rounds": total_rounds,
            "current_round": current_round,
            "is_completed": is_completed,
        }

    @classmethod
    async def generate_bracket(
        cls, tournament_id: int, participant_ids: list[int], auth: AuthSchema
    ) -> dict:
        """生成淘汰赛对阵表（支持增量添加学员到轮空位置）"""
        from app.core.logger import logger

        num_participants = len(participant_ids)

        if num_participants < 2:
            raise CustomException(msg="参赛人数不足，无法生成淘汰赛")

        # 查询现有对阵表
        existing_matches = await cls._get_existing_matches(tournament_id, auth)

        if existing_matches:
            logger.info(
                f"[generate_bracket] 发现现有对阵表，尝试将新学员填充到轮空位置"
            )
            # 尝试将新学员填充到轮空位置
            filled_count = await cls._fill_empty_slots(
                tournament_id, existing_matches, participant_ids, auth
            )
            if filled_count > 0:
                logger.info(
                    f"[generate_bracket] 已将 {filled_count} 个新学员填充到轮空位置"
                )
                # 返回更新后的对阵表
                updated_matches = await cls._get_existing_matches(tournament_id, auth)
                return {
                    "matches": updated_matches,
                    "total_rounds": max(m["round_number"] for m in updated_matches)
                    if updated_matches
                    else 0,
                }
            else:
                logger.info(
                    f"[generate_bracket] 没有可填充的轮空位置，将重新生成对阵表"
                )
                # 删除现有对阵表，重新生成
                await cls._delete_existing_matches(tournament_id, auth)

        # 计算轮数（向上取整到2的幂）
        total_rounds = math.ceil(math.log2(num_participants))
        next_power_of_two = 2**total_rounds

        # 种子排序
        seeded_participants = await cls._get_seeded_participants(
            tournament_id, participant_ids, auth
        )

        # 生成对阵表
        matches = []
        match_id_counter = 1

        logger.info(
            f"[generate_bracket] 生成对阵表: {num_participants}人, {total_rounds}轮, 对阵布局开始"
        )
        for idx, p in enumerate(seeded_participants):
            logger.info(
                f"[generate_bracket] 参与者{idx}: id={p['id']}, name={p.get('student_name', 'N/A')}, seed={p.get('seed_rank')}"
            )

        # 第一轮：处理轮空
        first_round_matches = []
        bye_count = next_power_of_two - num_participants

        for i in range(0, next_power_of_two // 2):
            player1_idx = i
            player2_idx = next_power_of_two - 1 - i

            player1 = (
                seeded_participants[player1_idx]
                if player1_idx < num_participants
                else None
            )
            player2 = (
                seeded_participants[player2_idx]
                if player2_idx < num_participants
                else None
            )

            logger.info(
                f"[generate_bracket] 比赛{i + 1}: idx{player1_idx} vs idx{player2_idx}, p1={'有' if player1 else '无'}, p2={'有' if player2 else '无'}"
            )

            # 处理轮空
            if player1 and not player2:
                # player1 轮空晋级
                match = {
                    "id": match_id_counter,
                    "round_number": 1,
                    "match_number": i + 1,
                    "player1_id": player1["id"],
                    "player2_id": None,
                    "status": "COMPLETED",
                    "winner_id": player1["id"],
                }
            elif player2 and not player1:
                # player2 轮空晋级
                match = {
                    "id": match_id_counter,
                    "round_number": 1,
                    "match_number": i + 1,
                    "player1_id": None,
                    "player2_id": player2["id"],
                    "status": "COMPLETED",
                    "winner_id": player2["id"],
                }
            else:
                # 正常比赛
                match = {
                    "id": match_id_counter,
                    "round_number": 1,
                    "match_number": i + 1,
                    "player1_id": player1["id"] if player1 else None,
                    "player2_id": player2["id"] if player2 else None,
                    "status": "SCHEDULED",
                }

            first_round_matches.append(match)
            matches.append(match)
            match_id_counter += 1

        # 后续轮次
        prev_round_matches = first_round_matches
        for round_num in range(2, total_rounds + 1):
            current_round_matches = []
            num_matches = len(prev_round_matches) // 2

            for i in range(num_matches):
                prev_match1 = prev_round_matches[i * 2]
                prev_match2 = prev_round_matches[i * 2 + 1]

                # 检查上游比赛是否是轮空（已完成），如果是，自动晋级胜者
                player1_id = None
                player2_id = None

                if prev_match1.get("status") == "COMPLETED" and prev_match1.get(
                    "winner_id"
                ):
                    player1_id = prev_match1["winner_id"]

                if prev_match2.get("status") == "COMPLETED" and prev_match2.get(
                    "winner_id"
                ):
                    player2_id = prev_match2["winner_id"]

                match = {
                    "id": match_id_counter,
                    "round_number": round_num,
                    "match_number": i + 1,
                    "player1_id": player1_id,  # 轮空已晋级，否则等待比赛结果
                    "player2_id": player2_id,
                    "status": "SCHEDULED",
                    "prev_match1_id": prev_match1["id"],
                    "prev_match2_id": prev_match2["id"],
                }

                # 设置上游比赛的 next_match_id
                prev_match1["next_match_id"] = match["id"]
                prev_match2["next_match_id"] = match["id"]

                current_round_matches.append(match)
                matches.append(match)
                match_id_counter += 1

            prev_round_matches = current_round_matches

        # 保存到数据库
        await cls._save_bracket(tournament_id, matches, auth)

        return {"matches": matches, "total_rounds": total_rounds}

    @classmethod
    async def update_match(
        cls, match_id: int, scores: dict, winner_id: int, auth: AuthSchema
    ) -> dict:
        """更新比赛结果并晋级"""
        from app.core.logger import logger

        logger.info(f"[update_match] 开始更新比赛 {match_id}, winner_id={winner_id}")

        # 更新当前比赛
        crud = TournamentMatchCRUD(auth)
        await crud.update_score_crud(
            match_id=match_id, scores=scores, winner_id=winner_id, status="COMPLETED"
        )
        logger.info(f"[update_match] 比赛 {match_id} 比分已更新")

        # 查询比赛信息（包括下游比赛）
        sql = text("""
            SELECT 
                m.next_match_id,
                m.player1_id,
                m.player2_id,
                nm.id as next_id,
                nm.prev_match1_id,
                nm.prev_match2_id
            FROM badminton_tournament_match m
            LEFT JOIN badminton_tournament_match nm ON m.next_match_id = nm.id
            WHERE m.id = :match_id
        """)
        result = await auth.db.execute(sql, {"match_id": match_id})
        row = result.fetchone()

        logger.info(
            f"[update_match] 查询结果: next_match_id={row.next_match_id if row else None}, "
            f"prev_match1_id={row.prev_match1_id if row else None}, "
            f"prev_match2_id={row.prev_match2_id if row else None}"
        )

        if not row or not row.next_match_id:
            logger.info(f"[update_match] 比赛 {match_id} 无下游比赛")
            return {"message": "比赛已更新，无下游比赛"}

        # 将胜者晋级到下一轮
        next_match_id = row.next_match_id

        # 确定是左上游还是右上游：看当前比赛是下游比赛的 prev_match1 还是 prev_match2
        is_left = row.prev_match1_id == match_id
        logger.info(
            f"[update_match] is_left={is_left}, current_match_id={match_id}, prev_match1_id={row.prev_match1_id}"
        )

        update_sql = text(f"""
            UPDATE badminton_tournament_match
            SET {"player1_id" if is_left else "player2_id"} = :winner_id
            WHERE id = :next_match_id
        """)

        logger.info(
            f"[update_match] 执行晋级 SQL: next_match_id={next_match_id}, winner_id={winner_id}"
        )

        await auth.db.execute(
            update_sql, {"winner_id": winner_id, "next_match_id": next_match_id}
        )

        logger.info(
            f"[update_match] 胜者 {winner_id} 已晋级到比赛 {next_match_id}"
        )

        return {"message": "比赛已更新，胜者已晋级", "next_match_id": next_match_id}

    @classmethod
    def _get_round_label(cls, round_number: int) -> str:
        """获取轮次标签"""
        labels = {
            1: "1/32赛",
            2: "1/16赛",
            3: "1/8赛",
            4: "1/4赛",
            5: "半决赛",
            6: "决赛",
            7: "冠军",
        }
        return labels.get(round_number, f"第{round_number}轮")

    @classmethod
    def _format_scores(cls, scores: Optional[dict]) -> Optional[str]:
        """格式化比分"""
        if not scores or not scores.get("sets"):
            return None

        sets = scores["sets"]
        return ", ".join([f"{s['player1']}-{s['player2']}" for s in sets])

    @classmethod
    async def _get_seeded_participants(
        cls, tournament_id: int, participant_ids: list[int], auth: AuthSchema
    ) -> list[dict]:
        """获取按种子排序的参赛者（种子有序，非种子随机）"""
        from app.core.logger import logger

        logger.info(
            f"[_get_seeded_participants] tournament_id={tournament_id}, participant_ids={participant_ids}"
        )

        sql = text("""
            SELECT 
                p.id,
                p.seed_rank,
                s.name as student_name
            FROM badminton_tournament_participant p
            JOIN view_badminton_student_list s ON p.student_id = s.id
            WHERE p.tournament_id = :tournament_id
            AND p.id = ANY(:participant_ids)
        """)

        result = await auth.db.execute(
            sql, {"tournament_id": tournament_id, "participant_ids": participant_ids}
        )

        rows = result.mappings().all()
        participants = [dict(row) for row in rows]

        # 检查是否有缺失的参与者
        found_ids = {p["id"] for p in participants}
        missing_ids = set(participant_ids) - found_ids
        if missing_ids:
            logger.warning(
                f"[_get_seeded_participants] 以下参与者未找到: {missing_ids}"
            )

        logger.info(
            f"[_get_seeded_participants] 查询到 {len(participants)} 个参与者, 输入 {len(participant_ids)} 个"
        )

        # 分离种子和非种子
        seeded = [p for p in participants if p["seed_rank"] is not None]
        unseeded = [p for p in participants if p["seed_rank"] is None]

        logger.info(
            f"[_get_seeded_participants] 种子选手: {len(seeded)}, 非种子: {len(unseeded)}"
        )

        # 种子按排名排序
        seeded_sorted = sorted(seeded, key=lambda p: p["seed_rank"])

        # 非种子随机打乱
        import random

        random.shuffle(unseeded)

        # 合并返回
        result = seeded_sorted + unseeded
        logger.info(f"[_get_seeded_participants] 返回 {len(result)} 个参与者")
        return result

    @classmethod
    async def _save_bracket(
        cls, tournament_id: int, matches: list[dict], auth: AuthSchema
    ) -> None:
        """保存对阵表到数据库"""
        from app.core.logger import logger

        logger.info(f"[_save_bracket] 开始保存对阵表，共 {len(matches)} 场比赛")

        # 第一步：插入所有比赛（不含关联ID），并获取真实数据库ID
        id_map = {}  # 临时ID -> 真实数据库ID

        for match in matches:
            temp_id = match["id"]

            sql = text("""
                INSERT INTO badminton_tournament_match (
                    tournament_id, round_type, round_number, match_number,
                    player1_id, player2_id, status, winner_id,
                    prev_match1_id, prev_match2_id, next_match_id,
                    uuid, created_time, updated_time
                ) VALUES (
                    :tournament_id, 'KNOCKOUT', :round_number, :match_number,
                    :player1_id, :player2_id, :status, :winner_id,
                    NULL, NULL, NULL,
                    gen_random_uuid(), NOW(), NOW()
                )
                RETURNING id
            """)

            result = await auth.db.execute(
                sql,
                {
                    "tournament_id": tournament_id,
                    "round_number": match["round_number"],
                    "match_number": match["match_number"],
                    "player1_id": match.get("player1_id"),
                    "player2_id": match.get("player2_id"),
                    "status": match["status"],
                    "winner_id": match.get("winner_id"),
                },
            )
            row = result.fetchone()
            real_id = row[0]
            id_map[temp_id] = real_id

            logger.info(f"[_save_bracket] 比赛临时ID {temp_id} -> 真实ID {real_id}")

        # 第二步：更新所有比赛的关联ID
        for match in matches:
            temp_id = match["id"]
            real_id = id_map[temp_id]

            # 获取关联的真实ID
            prev_match1_id = (
                id_map.get(match.get("prev_match1_id"))
                if match.get("prev_match1_id")
                else None
            )
            prev_match2_id = (
                id_map.get(match.get("prev_match2_id"))
                if match.get("prev_match2_id")
                else None
            )
            next_match_id = (
                id_map.get(match.get("next_match_id"))
                if match.get("next_match_id")
                else None
            )

            if prev_match1_id or prev_match2_id or next_match_id:
                update_sql = text("""
                    UPDATE badminton_tournament_match
                    SET prev_match1_id = :prev_match1_id,
                        prev_match2_id = :prev_match2_id,
                        next_match_id = :next_match_id
                    WHERE id = :match_id
                """)

                await auth.db.execute(
                    update_sql,
                    {
                        "match_id": real_id,
                        "prev_match1_id": prev_match1_id,
                        "prev_match2_id": prev_match2_id,
                        "next_match_id": next_match_id,
                    },
                )

                logger.info(
                    f"[_save_bracket] 更新比赛 {real_id}: prev1={prev_match1_id}, prev2={prev_match2_id}, next={next_match_id}"
                )

        logger.info("[_save_bracket] 对阵表保存完成")

    @classmethod
    async def _get_existing_matches(
        cls, tournament_id: int, auth: AuthSchema
    ) -> list[dict]:
        """获取现有淘汰赛对阵表"""
        sql = text("""
            SELECT id, round_number, match_number, player1_id, player2_id, 
                   status, winner_id, prev_match1_id, prev_match2_id, next_match_id
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'KNOCKOUT'
            ORDER BY round_number, match_number
        """)
        result = await auth.db.execute(sql, {"tournament_id": tournament_id})
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    @classmethod
    async def _delete_existing_matches(
        cls, tournament_id: int, auth: AuthSchema
    ) -> None:
        """删除现有淘汰赛对阵表"""
        from app.core.logger import logger

        sql = text("""
            DELETE FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'KNOCKOUT'
        """)
        await auth.db.execute(sql, {"tournament_id": tournament_id})
        # 注意：不在此处提交事务，由调用方统一处理
        logger.info(
            f"[_delete_existing_matches] 已删除赛事 {tournament_id} 的现有对阵表"
        )

    @classmethod
    async def _fill_empty_slots(
        cls,
        tournament_id: int,
        existing_matches: list[dict],
        participant_ids: list[int],
        auth: AuthSchema,
    ) -> int:
        """将新学员填充到轮空位置，返回成功填充的数量"""
        from app.core.logger import logger

        # 找出已在现有对阵中的学员
        existing_participant_ids = set()
        for match in existing_matches:
            if match.get("player1_id"):
                existing_participant_ids.add(match["player1_id"])
            if match.get("player2_id"):
                existing_participant_ids.add(match["player2_id"])

        # 找出新学员（不在现有对阵中的）
        new_participant_ids = [
            pid for pid in participant_ids if pid not in existing_participant_ids
        ]

        if not new_participant_ids:
            logger.info("[_fill_empty_slots] 没有新学员需要添加")
            return 0

        logger.info(f"[_fill_empty_slots] 新学员: {new_participant_ids}")

        # 找出第一轮的轮空位置（SCHEDULED状态且只有一个选手）
        filled_count = 0
        first_round_matches = [
            m
            for m in existing_matches
            if m["round_number"] == 1 and m["status"] == "SCHEDULED"
        ]

        for match in first_round_matches:
            if filled_count >= len(new_participant_ids):
                break

            player1_id = match.get("player1_id")
            player2_id = match.get("player2_id")

            # 如果只有一个空位，填充新学员
            if (player1_id is None) != (player2_id is None):  # XOR - 只有一个为空
                new_player_id = new_participant_ids[filled_count]

                if player1_id is None:
                    # 填充 player1
                    update_sql = text("""
                        UPDATE badminton_tournament_match
                        SET player1_id = :player_id
                        WHERE id = :match_id
                    """)
                else:
                    # 填充 player2
                    update_sql = text("""
                        UPDATE badminton_tournament_match
                        SET player2_id = :player_id
                        WHERE id = :match_id
                    """)

                await auth.db.execute(
                    update_sql, {"player_id": new_player_id, "match_id": match["id"]}
                )
                filled_count += 1
                logger.info(
                    f"[_fill_empty_slots] 将学员 {new_player_id} 填充到比赛 {match['id']}"
                )

        # 注意：不在此处提交事务，由调用方统一处理
        return filled_count
