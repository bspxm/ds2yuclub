-- 排课记录性能优化索引
-- 为 badminton_class_schedule 表添加索引，加速查询

-- 1. 主键索引（通常已存在）
-- CREATE UNIQUE INDEX IF NOT EXISTS pk_badminton_class_schedule ON badminton_class_schedule(id);

-- 2. 班级ID索引（用于关联查询班级信息）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_class_id ON badminton_class_schedule(class_id);

-- 3. 教练ID索引（用于关联查询教练信息）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_coach_id ON badminton_class_schedule(coach_id);

-- 4. 创建人ID索引（用于关联查询创建人信息）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_created_id ON badminton_class_schedule(created_id);

-- 5. 更新人ID索引（用于关联查询更新人信息）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_updated_id ON badminton_class_schedule(updated_id);

-- 6. 排课日期索引（用于按日期查询）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_schedule_date ON badminton_class_schedule(schedule_date);

-- 7. 排课状态索引（用于按状态筛选）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_schedule_status ON badminton_class_schedule(schedule_status);

-- 8. 复合索引：班级ID + 排课日期（常用查询条件）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_class_date ON badminton_class_schedule(class_id, schedule_date);

-- 9. 复合索引：教练ID + 排课日期（常用查询条件）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_coach_date ON badminton_class_schedule(coach_id, schedule_date);

-- 10. 复合索引：排课状态 + 排课日期（常用查询条件）
CREATE INDEX IF NOT EXISTS ix_badminton_class_schedule_status_date ON badminton_class_schedule(schedule_status, schedule_date);

-- 班级表索引优化
-- 11. 学期ID索引（用于查询学期下的班级）
CREATE INDEX IF NOT EXISTS ix_badminton_class_semester_id ON badminton_class(semester_id);

-- 12. 班级状态索引
CREATE INDEX IF NOT EXISTS ix_badminton_class_status ON badminton_class(status);

-- 用户表索引优化
-- 13. 用户ID索引（通常已存在，但确保存在）
-- CREATE INDEX IF NOT EXISTS ix_sys_user_id ON sys_user(id);

-- 考勤记录表索引优化
-- 14. 排课ID索引（用于查询某个排课的考勤记录）
CREATE INDEX IF NOT EXISTS ix_badminton_class_attendance_schedule_id ON badminton_class_attendance(schedule_id);

-- 15. 学员ID索引（用于查询某个学员的考勤记录）
CREATE INDEX IF NOT EXISTS ix_badminton_class_attendance_student_id ON badminton_class_attendance(student_id);

-- 16. 复合索引：排课ID + 学员ID
CREATE INDEX IF NOT EXISTS ix_badminton_class_attendance_schedule_student ON badminton_class_attendance(schedule_id, student_id);