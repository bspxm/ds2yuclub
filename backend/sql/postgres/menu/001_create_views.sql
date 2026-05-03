-- ========================================
-- 创建羽毛球模块所需的数据库视图
-- ========================================

-- 学员列表视图（已包含家长聚合信息，替代ORM预加载）
DROP VIEW IF EXISTS view_badminton_student_list CASCADE;
CREATE VIEW view_badminton_student_list AS
SELECT
    s.id,
    s.uuid,
    s.description,
    s.status,
    s.created_time,
    s.updated_time,
    s.created_id,
    s.updated_id,
    s.name,
    s.english_name,
    s.gender,
    s.birth_date,
    s.height,
    s.weight,
    s.handedness,
    s.join_date,
    s.level,
    s.group_name,
    s.campus,
    s.contact,
    s.mobile,
    s.total_matches,
    s.wins,
    s.losses,
    s.win_rate,
    COALESCE(pc.parent_count, 0) AS parent_count,
    COALESCE(pc.parents_json, '[]'::jsonb) AS parents_json
FROM badminton_student s
LEFT JOIN (
    SELECT
        ps.student_id,
        COUNT(*)::integer AS parent_count,
        jsonb_agg(
            jsonb_build_object(
                'parent_id', ps.parent_id,
                'relation_type', ps.relation_type,
                'is_primary', ps.is_primary,
                'notes', ps.notes
            )
        ) AS parents_json
    FROM badminton_parent_student ps
    GROUP BY ps.student_id
) pc ON s.id = pc.student_id;
