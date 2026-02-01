-- 创建排课记录列表视图
-- 用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题

-- 删除旧视图（如果存在）
DROP VIEW IF EXISTS view_badminton_class_schedule_list;

-- 创建新视图
CREATE VIEW view_badminton_class_schedule_list AS
SELECT 
    s.id,
    s.uuid,
    s.class_id,
    s.schedule_date,
    s.day_of_week,
    s.time_slot_code,
    s.time_slots_json,
    s.start_time,
    s.end_time,
    s.duration_minutes,
    s.schedule_type,
    s.schedule_status,
    s.coach_id,
    s.coach_confirmed,
    s.coach_confirm_at,
    s.court_number,
    s.location,
    s.topic,
    s.content_summary,
    s.training_focus,
    s.equipment_needed,
    s.is_published,
    s.published_at,
    s.is_auto_generated,
    s.original_schedule_id,
    s.makeup_for_schedule_id,
    s.notes,
    s.status,
    s.created_time,
    s.updated_time,
    s.created_id,
    s.updated_id,
    -- 班级信息
    c.id as class_ref_id,
    c.name as class_ref_name,
    c.semester_id as class_ref_semester_id,
    -- 教练信息
    u.id as coach_user_id,
    u.name as coach_user_name
FROM badminton_class_schedule s
LEFT JOIN badminton_class c ON s.class_id = c.id
LEFT JOIN sys_user u ON s.coach_id = u.id;

-- 添加注释
COMMENT ON VIEW view_badminton_class_schedule_list IS '排课记录列表视图，用于优化查询性能';