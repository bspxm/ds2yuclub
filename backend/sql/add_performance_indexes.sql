-- 为考勤表添加 schedule_id 索引（优化学员数量统计查询）
CREATE INDEX IF NOT EXISTS ix_badminton_class_attendance_schedule_id 
ON badminton_class_attendance(schedule_id);

-- 为排课表添加复合索引（优化常用的组合查询）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_class_date 
ON badminton_class_schedule(class_id, schedule_date);

CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_coach_date 
ON badminton_class_schedule(coach_id, schedule_date);

CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_status_date 
ON badminton_class_schedule(schedule_status, schedule_date);