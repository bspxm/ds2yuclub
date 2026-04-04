-- 羽毛球培训会员管理系统菜单同步脚本
-- 功能：自动同步菜单，存在则更新，不存在则新增
-- 执行时间：2026-04-04
-- 权限命名规范：与后端控制器保持一致（使用 :list 而非 :query）

-- 使用 PostgreSQL 的 UPSERT 功能（INSERT ... ON CONFLICT DO UPDATE）
-- 需要先确保有唯一约束，这里使用 route_name + parent_id 作为唯一标识

-- ========================================
-- 第一步：确保唯一约束存在
-- ========================================
DO $$
BEGIN
    -- 检查是否已存在唯一索引
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_sys_menu_route_parent_unique'
    ) THEN
        -- 创建唯一索引（route_name + parent_id），排除 NULL 的 route_name
        EXECUTE 'CREATE UNIQUE INDEX idx_sys_menu_route_parent_unique ON sys_menu (route_name, parent_id) WHERE route_name IS NOT NULL';
        RAISE NOTICE '已创建唯一索引: idx_sys_menu_route_parent_unique';
    ELSE
        RAISE NOTICE '唯一索引已存在: idx_sys_menu_route_parent_unique';
    END IF;
END $$;

-- ========================================
-- 第二步：同步一级菜单（羽毛球管理）
-- ========================================
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
VALUES
('羽毛球管理', 1, 8, NULL, 'sports', 'Badminton', '/badminton', NULL, '/badminton/student', FALSE, TRUE, FALSE, '羽毛球管理', NULL, FALSE, NULL, 'badminton-root-00000000-0000-0000-0000-000000000001'::uuid, '0', '羽毛球培训会员管理系统', NOW(), NOW())
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    type = EXCLUDED.type,
    "order" = EXCLUDED."order",
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    redirect = EXCLUDED.redirect,
    hidden = EXCLUDED.hidden,
    keep_alive = EXCLUDED.keep_alive,
    always_show = EXCLUDED.always_show,
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    description = EXCLUDED.description,
    updated_time = NOW();

-- ========================================
-- 第三步：同步二级菜单和三级权限菜单
-- ========================================

-- 使用 CTE 获取一级菜单ID
WITH root_menu AS (
    SELECT id FROM sys_menu WHERE route_name = 'Badminton' LIMIT 1
)

-- 3.1 学员管理
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '学员管理', 2, 1, 'module_badminton:student:list', 'user', 'BadmintonStudent', 'student', 'module_badminton/student/index', NULL, FALSE, TRUE, FALSE, '学员管理', NULL, FALSE, id, 'badminton-student-00000000-0000-0000-0000-000000000001'::uuid, '0', '学员信息管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    type = EXCLUDED.type,
    "order" = EXCLUDED."order",
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 学员管理权限（三级菜单）
INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询学员', 3, 1, 'module_badminton:student:list', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询学员', NULL, FALSE, m.id, 'badminton-student-list-0000-0000-0000-000000000001'::uuid, '0', '查询学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增学员', 3, 2, 'module_badminton:student:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增学员', NULL, FALSE, m.id, 'badminton-student-create-0000-0000-0000-000000000001'::uuid, '0', '新增学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑学员', 3, 3, 'module_badminton:student:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑学员', NULL, FALSE, m.id, 'badminton-student-update-0000-0000-0000-000000000001'::uuid, '0', '编辑学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除学员', 3, 4, 'module_badminton:student:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除学员', NULL, FALSE, m.id, 'badminton-student-delete-0000-0000-0000-000000000001'::uuid, '0', '删除学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情学员', 3, 5, 'module_badminton:student:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情学员', NULL, FALSE, m.id, 'badminton-student-detail-0000-0000-0000-000000000001'::uuid, '0', '查看学员详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '批量导入学员', 3, 6, 'module_badminton:student:import', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '批量导入学员', NULL, FALSE, m.id, 'badminton-student-import-0000-0000-0000-000000000001'::uuid, '0', '批量导入学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '批量设置状态', 3, 7, 'module_badminton:student:batch_status', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '批量设置状态', NULL, FALSE, m.id, 'badminton-student-batch-0000-0000-0000-000000000001'::uuid, '0', '批量设置学员状态', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent'
ON CONFLICT DO NOTHING;

-- 3.2 家长端
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '家长端', 2, 2, 'module_badminton:parent_student:list', 'el-icon-User', 'BadmintonParent', 'parent', 'module_badminton/parent/index', NULL, FALSE, TRUE, FALSE, '家长端', NULL, FALSE, id, 'badminton-parent-00000000-0000-0000-0000-000000000001'::uuid, '0', '家长端功能', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 家长端权限
INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询家长端', 3, 1, 'module_badminton:parent_student:list', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询家长端', NULL, FALSE, m.id, 'badminton-parent-list-0000-0000-0000-000000000001'::uuid, '0', '查询家长端信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增家长端', 3, 2, 'module_badminton:parent_student:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增家长端', NULL, FALSE, m.id, 'badminton-parent-create-0000-0000-0000-000000000001'::uuid, '0', '新增家长端信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除家长端', 3, 3, 'module_badminton:parent_student:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除家长端', NULL, FALSE, m.id, 'badminton-parent-delete-0000-0000-0000-000000000001'::uuid, '0', '删除家长端信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情家长端', 3, 4, 'module_badminton:parent_student:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情家长端', NULL, FALSE, m.id, 'badminton-parent-detail-0000-0000-0000-000000000001'::uuid, '0', '查看家长端详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent'
ON CONFLICT DO NOTHING;

-- 3.3 赛事管理
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '赛事管理', 2, 3, 'module_badminton:tournament:list', 'trophy', 'BadmintonTournament', 'tournament', 'module_badminton/tournament/index', NULL, FALSE, TRUE, FALSE, '赛事管理', NULL, FALSE, id, 'badminton-tournament-00000000-0000-0000-0000-000000000001'::uuid, '0', '赛事信息管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 赛事管理权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询赛事', 3, 1, 'module_badminton:tournament:list', m.id, 'badminton-tournament-list-0000-0000-0000-000000000001'::uuid, '0', '查询赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增赛事', 3, 2, 'module_badminton:tournament:create', m.id, 'badminton-tournament-create-0000-0000-0000-000000000001'::uuid, '0', '新增赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑赛事', 3, 3, 'module_badminton:tournament:update', m.id, 'badminton-tournament-update-0000-0000-0000-000000000001'::uuid, '0', '编辑赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除赛事', 3, 4, 'module_badminton:tournament:delete', m.id, 'badminton-tournament-delete-0000-0000-0000-000000000001'::uuid, '0', '删除赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情赛事', 3, 5, 'module_badminton:tournament:detail', m.id, 'badminton-tournament-detail-0000-0000-0000-000000000001'::uuid, '0', '查看赛事详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '赛事报名', 3, 6, 'module_badminton:tournament:register', m.id, 'badminton-tournament-register-0000-0000-0000-000000000001'::uuid, '0', '赛事报名', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '取消报名', 3, 7, 'module_badminton:tournament:withdraw', m.id, 'badminton-tournament-withdraw-0000-0000-0000-000000000001'::uuid, '0', '取消赛事报名', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '参赛者列表', 3, 8, 'module_badminton:tournament:participants', m.id, 'badminton-tournament-participants-0000-0000-0000-000000000001'::uuid, '0', '查看参赛者列表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '模拟比赛', 3, 9, 'module_badminton:tournament:simulate', m.id, 'badminton-tournament-simulate-0000-0000-0000-000000000001'::uuid, '0', '模拟比赛', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament'
ON CONFLICT DO NOTHING;

-- 3.4 课程管理
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '课程管理', 2, 4, 'module_badminton:course:list', 'calendar', 'BadmintonCourse', 'course', 'module_badminton/course/index', NULL, FALSE, TRUE, FALSE, '课程管理', NULL, FALSE, id, 'badminton-course-00000000-0000-0000-0000-000000000001'::uuid, '0', '课程信息管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 课程管理权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询课程', 3, 1, 'module_badminton:course:list', m.id, 'badminton-course-list-0000-0000-0000-000000000001'::uuid, '0', '查询课程信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增课程', 3, 2, 'module_badminton:course:create', m.id, 'badminton-course-create-0000-0000-0000-000000000001'::uuid, '0', '新增课程信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse'
ON CONFLICT DO NOTHING;

-- 3.5 能力评估
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '能力评估', 2, 5, 'module_badminton:assessment:list', 'el-icon-TrendCharts', 'BadmintonAssessment', 'assessment', 'module_badminton/assessment/index', NULL, FALSE, TRUE, FALSE, '能力评估', NULL, FALSE, id, 'badminton-assessment-00000000-0000-0000-0000-000000000001'::uuid, '0', '学员能力评估管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 能力评估权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询评估', 3, 1, 'module_badminton:assessment:list', m.id, 'badminton-assessment-list-0000-0000-0000-000000000001'::uuid, '0', '查询能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增评估', 3, 2, 'module_badminton:assessment:create', m.id, 'badminton-assessment-create-0000-0000-0000-000000000001'::uuid, '0', '新增能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑评估', 3, 3, 'module_badminton:assessment:update', m.id, 'badminton-assessment-update-0000-0000-0000-000000000001'::uuid, '0', '编辑能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除评估', 3, 4, 'module_badminton:assessment:delete', m.id, 'badminton-assessment-delete-0000-0000-0000-000000000001'::uuid, '0', '删除能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment'
ON CONFLICT DO NOTHING;

-- 3.6 请假管理
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '请假管理', 2, 6, 'module_badminton:leave_request:list', 'el-icon-Timer', 'BadmintonLeaveRequest', 'leave-request', 'module_badminton/leave-request/index', NULL, FALSE, TRUE, FALSE, '请假管理', NULL, FALSE, id, 'badminton-leave-00000000-0000-0000-0000-000000000001'::uuid, '0', '学员请假管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 请假管理权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询请假', 3, 1, 'module_badminton:leave_request:list', m.id, 'badminton-leave-list-0000-0000-0000-000000000001'::uuid, '0', '查询请假信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonLeaveRequest'
ON CONFLICT DO NOTHING;

-- 3.7 学期管理
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '学期管理', 2, 7, 'module_badminton:semester:list', 'calendar', 'BadmintonSemester', 'semester', 'module_badminton/semester/index', NULL, FALSE, TRUE, FALSE, '学期管理', NULL, FALSE, id, 'badminton-semester-00000000-0000-0000-0000-000000000001'::uuid, '0', '学期信息管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 学期管理权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询学期', 3, 1, 'module_badminton:semester:list', m.id, 'badminton-semester-list-0000-0000-0000-000000000001'::uuid, '0', '查询学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增学期', 3, 2, 'module_badminton:semester:create', m.id, 'badminton-semester-create-0000-0000-0000-000000000001'::uuid, '0', '新增学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改学期', 3, 3, 'module_badminton:semester:update', m.id, 'badminton-semester-update-0000-0000-0000-000000000001'::uuid, '0', '修改学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除学期', 3, 4, 'module_badminton:semester:delete', m.id, 'badminton-semester-delete-0000-0000-0000-000000000001'::uuid, '0', '删除学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情学期', 3, 5, 'module_badminton:semester:detail', m.id, 'badminton-semester-detail-0000-0000-0000-000000000001'::uuid, '0', '查看学期详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester'
ON CONFLICT DO NOTHING;

-- 3.8 班级管理
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '班级管理', 2, 8, 'module_badminton:class:list', 'team', 'BadmintonClass', 'class', 'module_badminton/class/index', NULL, FALSE, TRUE, FALSE, '班级管理', NULL, FALSE, id, 'badminton-class-00000000-0000-0000-0000-000000000001'::uuid, '0', '班级信息管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 班级管理权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询班级', 3, 1, 'module_badminton:class:list', m.id, 'badminton-class-list-0000-0000-0000-000000000001'::uuid, '0', '查询班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonClass'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增班级', 3, 2, 'module_badminton:class:create', m.id, 'badminton-class-create-0000-0000-0000-000000000001'::uuid, '0', '新增班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonClass'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改班级', 3, 3, 'module_badminton:class:update', m.id, 'badminton-class-update-0000-0000-0000-000000000001'::uuid, '0', '修改班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonClass'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除班级', 3, 4, 'module_badminton:class:delete', m.id, 'badminton-class-delete-0000-0000-0000-000000000001'::uuid, '0', '删除班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonClass'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情班级', 3, 5, 'module_badminton:class:detail', m.id, 'badminton-class-detail-0000-0000-0000-000000000001'::uuid, '0', '查看班级详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonClass'
ON CONFLICT DO NOTHING;

-- 3.9 购买记录（报班管理）
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '报班管理', 2, 9, 'module_badminton:purchase:list', 'shopping-cart', 'BadmintonPurchase', 'purchase', 'module_badminton/purchase/index', NULL, FALSE, TRUE, FALSE, '报班管理', NULL, FALSE, id, 'badminton-purchase-00000000-0000-0000-0000-000000000001'::uuid, '0', '购买记录管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 购买记录权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询购买', 3, 1, 'module_badminton:purchase:list', m.id, 'badminton-purchase-list-0000-0000-0000-000000000001'::uuid, '0', '查询购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增购买', 3, 2, 'module_badminton:purchase:create', m.id, 'badminton-purchase-create-0000-0000-0000-000000000001'::uuid, '0', '新增购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改购买', 3, 3, 'module_badminton:purchase:update', m.id, 'badminton-purchase-update-0000-0000-0000-000000000001'::uuid, '0', '修改购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除购买', 3, 4, 'module_badminton:purchase:delete', m.id, 'badminton-purchase-delete-0000-0000-0000-000000000001'::uuid, '0', '删除购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情购买', 3, 5, 'module_badminton:purchase:detail', m.id, 'badminton-purchase-detail-0000-0000-0000-000000000001'::uuid, '0', '查看购买详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase'
ON CONFLICT DO NOTHING;

-- 3.10 考勤记录
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '考勤记录', 2, 10, 'module_badminton:class_attendance:list', 'check-circle', 'BadmintonAttendance', 'class-attendance', 'module_badminton/class-attendance/index', NULL, FALSE, TRUE, FALSE, '考勤记录', NULL, FALSE, id, 'badminton-attendance-00000000-0000-0000-0000-000000000001'::uuid, '0', '考勤记录管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 考勤记录权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询考勤', 3, 1, 'module_badminton:class_attendance:list', m.id, 'badminton-attendance-list-0000-0000-0000-000000000001'::uuid, '0', '查询考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增考勤', 3, 2, 'module_badminton:class_attendance:create', m.id, 'badminton-attendance-create-0000-0000-0000-000000000001'::uuid, '0', '新增考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改考勤', 3, 3, 'module_badminton:class_attendance:update', m.id, 'badminton-attendance-update-0000-0000-0000-000000000001'::uuid, '0', '修改考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除考勤', 3, 4, 'module_badminton:class_attendance:delete', m.id, 'badminton-attendance-delete-0000-0000-0000-000000000001'::uuid, '0', '删除考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情考勤', 3, 5, 'module_badminton:class_attendance:detail', m.id, 'badminton-attendance-detail-0000-0000-0000-000000000001'::uuid, '0', '查看考勤详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance'
ON CONFLICT DO NOTHING;

-- 3.11 排课记录
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '排课记录', 2, 11, 'module_badminton:class_schedule:list', 'schedule', 'BadmintonSchedule', 'class-schedule', 'module_badminton/class-schedule/index', NULL, FALSE, TRUE, FALSE, '排课记录', NULL, FALSE, id, 'badminton-schedule-00000000-0000-0000-0000-000000000001'::uuid, '0', '排课记录管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 排课记录权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询排课', 3, 1, 'module_badminton:class_schedule:list', m.id, 'badminton-schedule-list-0000-0000-0000-000000000001'::uuid, '0', '查询排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增排课', 3, 2, 'module_badminton:class_schedule:create', m.id, 'badminton-schedule-create-0000-0000-0000-000000000001'::uuid, '0', '新增排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改排课', 3, 3, 'module_badminton:class_schedule:update', m.id, 'badminton-schedule-update-0000-0000-0000-000000000001'::uuid, '0', '修改排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除排课', 3, 4, 'module_badminton:class_schedule:delete', m.id, 'badminton-schedule-delete-0000-0000-0000-000000000001'::uuid, '0', '删除排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情排课', 3, 5, 'module_badminton:class_schedule:detail', m.id, 'badminton-schedule-detail-0000-0000-0000-000000000001'::uuid, '0', '查看排课详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule'
ON CONFLICT DO NOTHING;

-- 3.12 能力分组
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '能力分组', 2, 12, 'module_badminton:group:list', 'grid', 'BadmintonGroup', 'group', 'module_badminton/group/index', NULL, FALSE, TRUE, FALSE, '能力分组', NULL, FALSE, id, 'badminton-group-00000000-0000-0000-0000-000000000001'::uuid, '0', '学员能力分组管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 能力分组权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询分组', 3, 1, 'module_badminton:group:list', m.id, 'badminton-group-list-0000-0000-0000-000000000001'::uuid, '0', '查询能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增分组', 3, 2, 'module_badminton:group:create', m.id, 'badminton-group-create-0000-0000-0000-000000000001'::uuid, '0', '新增能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑分组', 3, 3, 'module_badminton:group:update', m.id, 'badminton-group-update-0000-0000-0000-000000000001'::uuid, '0', '编辑能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup'
ON CONFLICT DO NOTHING;

INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除分组', 3, 4, 'module_badminton:group:delete', m.id, 'badminton-group-delete-0000-0000-0000-000000000001'::uuid, '0', '删除能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup'
ON CONFLICT DO NOTHING;

-- 3.13 教练视图
INSERT INTO sys_menu 
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '教练视图', 2, 13, 'module_badminton:coach_schedule:list', 'date', 'BadmintonCoachSchedule', 'coach-schedule', 'module_badminton/coach-schedule/index', NULL, FALSE, TRUE, FALSE, '教练视图', NULL, FALSE, id, 'badminton-coach-00000000-0000-0000-0000-000000000001'::uuid, '0', '教练排课管理', NOW(), NOW()
FROM root_menu
ON CONFLICT (route_name, parent_id) WHERE route_name IS NOT NULL
DO UPDATE SET
    name = EXCLUDED.name,
    permission = EXCLUDED.permission,
    icon = EXCLUDED.icon,
    route_path = EXCLUDED.route_path,
    component_path = EXCLUDED.component_path,
    updated_time = NOW();

-- 教练视图权限
INSERT INTO sys_menu (name, type, "order", permission, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询教练视图', 3, 1, 'module_badminton:coach_schedule:list', m.id, 'badminton-coach-list-0000-0000-0000-000000000001'::uuid, '0', '查询教练排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCoachSchedule'
ON CONFLICT DO NOTHING;

-- ========================================
-- 第四步：更新已存在菜单的权限（修正旧数据）
-- ========================================
-- 修正所有 :query 为 :list
UPDATE sys_menu 
SET permission = REPLACE(permission, ':query', ':list'),
    updated_time = NOW()
WHERE permission LIKE 'module_badminton:%:query';

-- 修正 parent -> parent_student
UPDATE sys_menu 
SET permission = REPLACE(permission, 'module_badminton:parent:', 'module_badminton:parent_student:'),
    updated_time = NOW()
WHERE permission LIKE 'module_badminton:parent:%';

-- 修正 leave -> leave_request
UPDATE sys_menu 
SET permission = REPLACE(permission, 'module_badminton:leave:', 'module_badminton:leave_request:'),
    updated_time = NOW()
WHERE permission LIKE 'module_badminton:leave:%';

-- 修正 attendance -> class_attendance
UPDATE sys_menu 
SET permission = REPLACE(permission, 'module_badminton:attendance:', 'module_badminton:class_attendance:'),
    updated_time = NOW()
WHERE permission LIKE 'module_badminton:attendance:%';

-- 修正 schedule -> class_schedule
UPDATE sys_menu 
SET permission = REPLACE(permission, 'module_badminton:schedule:', 'module_badminton:class_schedule:'),
    updated_time = NOW()
WHERE permission LIKE 'module_badminton:schedule:%';

-- ========================================
-- 第五步：验证同步结果
-- ========================================
DO $$
DECLARE
    menu_count INTEGER;
    permission_count INTEGER;
    error_count INTEGER;
BEGIN
    -- 统计菜单数量
    SELECT COUNT(*) INTO menu_count
    FROM sys_menu 
    WHERE route_name LIKE 'Badminton%' OR permission LIKE 'module_badminton:%';
    
    -- 统计权限数量
    SELECT COUNT(*) INTO permission_count
    FROM sys_menu 
    WHERE permission LIKE 'module_badminton:%';
    
    -- 检查是否有错误的权限命名
    SELECT COUNT(*) INTO error_count
    FROM sys_menu 
    WHERE permission LIKE 'module_badminton:%' 
      AND (
          permission LIKE '%:query'
          OR permission LIKE 'module_badminton:parent:%'
          OR permission LIKE 'module_badminton:leave:%'
          OR permission LIKE 'module_badminton:attendance:%'
          OR permission LIKE 'module_badminton:schedule:%'
      );
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '羽毛球管理菜单同步完成';
    RAISE NOTICE '========================================';
    RAISE NOTICE '菜单总数: %', menu_count;
    RAISE NOTICE '权限总数: %', permission_count;
    
    IF error_count = 0 THEN
        RAISE NOTICE '✓ 所有权限命名正确';
    ELSE
        RAISE NOTICE '✗ 发现 % 个权限命名错误', error_count;
    END IF;
    
    RAISE NOTICE '========================================';
END $$;
