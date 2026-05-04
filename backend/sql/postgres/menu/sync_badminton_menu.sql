-- 羽毛球培训会员管理系统菜单重组脚本
-- 功能：清理旧结构，创建新的分组菜单结构
-- 执行前请确保已备份数据库

-- ========================================
-- 第一步：清理旧数据和可能残留的新分组
-- ========================================

-- 删除所有羽毛球相关的权限菜单(type=3)
DELETE FROM sys_menu WHERE permission LIKE 'module_badminton:%' AND type = 3;

-- 删除可能残留的新分组下的权限子菜单（只删除type=3权限，保留模块菜单）
DELETE FROM sys_menu
WHERE parent_id IN (
    SELECT id FROM sys_menu
    WHERE route_name IN ('BadmintonBasic', 'BadmintonTeaching', 'BadmintonBusiness', 'BadmintonView', 'BadmintonMobileCoach', 'BadmintonMobileParent')
)
AND type = 3;

-- 删除可能残留的新分组菜单（含移动端）
DELETE FROM sys_menu
WHERE route_name IN ('BadmintonBasic', 'BadmintonTeaching', 'BadmintonBusiness', 'BadmintonView', 'BadmintonMobileCoach', 'BadmintonMobileParent');

-- 删除可能残留的移动端子页面（新旧路由名），避免名称冲突
DELETE FROM sys_menu WHERE route_name IN (
    'MobileParentStudent', 'MobileParentTournament', 'MobileParentTournamentHistory', 'MobileParentTournamentDetail', 'MobileParentH2H',
    'MobileCoachHome', 'MobileCoachAttendance', 'MobileCoachSchedule',
    'MobileCoachTournamentList', 'MobileCoachTournamentMatches', 'MobileCoachMatchScore', 'MobileCoachAssessment',
    'DynMobileParentStudent', 'DynMobileParentTournament', 'DynMobileParentTournamentHistory', 'DynMobileParentTournamentDetail', 'DynMobileParentH2H',
    'DynMobileCoachHome', 'DynMobileCoachAttendance', 'DynMobileCoachSchedule',
    'DynMobileCoachTournamentList', 'DynMobileCoachTournamentMatches', 'DynMobileCoachMatchScore', 'DynMobileCoachAssessment'
);

-- ========================================
-- 第二步：重置旧菜单结构
-- ========================================

-- 恢复旧根菜单为可见
UPDATE sys_menu
SET hidden = FALSE, "order" = 8, description = '羽毛球培训会员管理系统'
WHERE route_name = 'Badminton' AND parent_id IS NULL;

-- 将所有模块菜单的 parent_id 重置为旧根菜单
UPDATE sys_menu
SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'Badminton' AND parent_id IS NULL),
    updated_time = NOW()
WHERE route_name IN (
    'BadmintonStudent', 'BadmintonParent', 'BadmintonTournament', 'BadmintonCourse',
    'BadmintonAssessment', 'BadmintonLeaveRequest', 'BadmintonSemester', 'BadmintonTeam',
    'BadmintonPurchase', 'BadmintonAttendance', 'BadmintonSchedule', 'BadmintonGroup',
    'BadmintonCoachSchedule'
);

-- ========================================
-- 第三步：创建分组菜单（一级菜单）
-- ========================================

INSERT INTO sys_menu
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
VALUES
('基础管理', 1, 8, NULL, 'el-icon-List', 'BadmintonBasic', '/basic', NULL, '/Badminton/student', FALSE, TRUE, FALSE, '基础管理', NULL, FALSE, NULL, gen_random_uuid(), '0', '基础数据管理：学期、班级、学员', NOW(), NOW());

INSERT INTO sys_menu
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
VALUES
('教学管理', 1, 9, NULL, 'el-icon-Reading', 'BadmintonTeaching', '/teaching', NULL, '/Badminton/course', FALSE, TRUE, FALSE, '教学管理', NULL, FALSE, NULL, gen_random_uuid(), '0', '教学管理：课程、排课、考勤、评估、分组', NOW(), NOW());

INSERT INTO sys_menu
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
VALUES
('业务管理', 1, 10, NULL, 'el-icon-Coordinate', 'BadmintonBusiness', '/business', NULL, '/Badminton/purchase', FALSE, TRUE, FALSE, '业务管理', NULL, FALSE, NULL, gen_random_uuid(), '0', '业务管理：报班、请假、赛事', NOW(), NOW());

INSERT INTO sys_menu
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
VALUES
('视图', 1, 11, NULL, 'el-icon-View', 'BadmintonView', '/view', NULL, '/Badminton/parent', FALSE, TRUE, FALSE, '视图', NULL, FALSE, NULL, gen_random_uuid(), '0', '视图切换：家长端、教练视图', NOW(), NOW());

-- ========================================
-- 第四步：迁移二级菜单到对应分组
-- ========================================

UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonBasic' LIMIT 1), "order" = 1, updated_time = NOW()
WHERE route_name = 'BadmintonStudent';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonBasic' LIMIT 1), "order" = 2, updated_time = NOW()
WHERE route_name = 'BadmintonTeam';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonBasic' LIMIT 1), "order" = 3, updated_time = NOW()
WHERE route_name = 'BadmintonSemester';

UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonTeaching' LIMIT 1), "order" = 1, updated_time = NOW()
WHERE route_name = 'BadmintonCourse';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonTeaching' LIMIT 1), "order" = 2, updated_time = NOW()
WHERE route_name = 'BadmintonSchedule';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonTeaching' LIMIT 1), "order" = 3, updated_time = NOW()
WHERE route_name = 'BadmintonAttendance';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonTeaching' LIMIT 1), "order" = 4, updated_time = NOW()
WHERE route_name = 'BadmintonAssessment';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonTeaching' LIMIT 1), "order" = 5, updated_time = NOW()
WHERE route_name = 'BadmintonGroup';

UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonBusiness' LIMIT 1), "order" = 1, updated_time = NOW()
WHERE route_name = 'BadmintonPurchase';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonBusiness' LIMIT 1), "order" = 2, updated_time = NOW()
WHERE route_name = 'BadmintonLeaveRequest';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonBusiness' LIMIT 1), "order" = 3, updated_time = NOW()
WHERE route_name = 'BadmintonTournament';

UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonView' LIMIT 1), "order" = 1, updated_time = NOW()
WHERE route_name = 'BadmintonParent';
UPDATE sys_menu SET parent_id = (SELECT id FROM sys_menu WHERE route_name = 'BadmintonView' LIMIT 1), "order" = 2, updated_time = NOW()
WHERE route_name = 'BadmintonCoachSchedule';

-- ========================================
-- 第五步：隐藏旧根菜单
-- ========================================
UPDATE sys_menu
SET hidden = TRUE, "order" = 99, description = '已迁移到分组菜单', updated_time = NOW()
WHERE route_name = 'Badminton' AND parent_id IS NULL;

-- ========================================
-- 第六步：同步三级权限菜单
-- ========================================

-- 学员管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询学员', 3, 1, 'module_badminton:student:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增学员', 3, 2, 'module_badminton:student:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑学员', 3, 3, 'module_badminton:student:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '编辑学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除学员', 3, 4, 'module_badminton:student:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情学员', 3, 5, 'module_badminton:student:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看学员详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '批量导入学员', 3, 6, 'module_badminton:student:import', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '批量导入学员信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '批量设置状态', 3, 7, 'module_badminton:student:batch_status', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '批量设置学员状态', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonStudent';

-- 家长端权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询家长端', 3, 1, 'module_badminton:parent_student:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询家长端信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增家长端', 3, 2, 'module_badminton:parent_student:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增家长端信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除家长端', 3, 3, 'module_badminton:parent_student:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除家长端信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情家长端', 3, 4, 'module_badminton:parent_student:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看家长端详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent';

-- 家长-学员关联管理子页面（挂在家长端下面）
INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '关联管理', 2, 5, NULL, 'el-icon-Connection', 'BadmintonParentStudent', 'parent-student', 'module_badminton/parent-student/index', NULL, FALSE, TRUE, FALSE, '关联管理', NULL, FALSE, m.id, gen_random_uuid(), '0', '家长-学员关联管理', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParent';

INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询关联', 3, 1, 'module_badminton:parent_student:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询关联列表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParentStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新建关联', 3, 2, 'module_badminton:parent_student:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新建关联', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParentStudent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除关联', 3, 3, 'module_badminton:parent_student:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除关联', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonParentStudent';

-- 赛事管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询赛事', 3, 1, 'module_badminton:tournament:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增赛事', 3, 2, 'module_badminton:tournament:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑赛事', 3, 3, 'module_badminton:tournament:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '编辑赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除赛事', 3, 4, 'module_badminton:tournament:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除赛事信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情赛事', 3, 5, 'module_badminton:tournament:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看赛事详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '赛事报名', 3, 6, 'module_badminton:tournament:register', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '赛事报名', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '取消报名', 3, 7, 'module_badminton:tournament:withdraw', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '取消赛事报名', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '参赛者列表', 3, 8, 'module_badminton:tournament:participants', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看参赛者列表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '模拟比赛', 3, 9, 'module_badminton:tournament:simulate', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '模拟比赛', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTournament';

-- 课程管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询课程', 3, 1, 'module_badminton:course:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询课程信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增课程', 3, 2, 'module_badminton:course:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增课程信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑课程', 3, 3, 'module_badminton:course:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '编辑课程信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除课程', 3, 4, 'module_badminton:course:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除课程信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情课程', 3, 5, 'module_badminton:course:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看课程详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCourse';

-- 能力评估权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询评估', 3, 1, 'module_badminton:assessment:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增评估', 3, 2, 'module_badminton:assessment:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑评估', 3, 3, 'module_badminton:assessment:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '编辑能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除评估', 3, 4, 'module_badminton:assessment:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情评估', 3, 5, 'module_badminton:assessment:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看能力评估详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAssessment';

-- 请假管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询请假', 3, 1, 'module_badminton:leave_request:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询请假信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonLeaveRequest';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增请假', 3, 2, 'module_badminton:leave_request:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增请假信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonLeaveRequest';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑请假', 3, 3, 'module_badminton:leave_request:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '编辑请假信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonLeaveRequest';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除请假', 3, 4, 'module_badminton:leave_request:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除请假信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonLeaveRequest';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情请假', 3, 5, 'module_badminton:leave_request:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看请假详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonLeaveRequest';

-- 学期管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询学期', 3, 1, 'module_badminton:semester:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增学期', 3, 2, 'module_badminton:semester:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改学期', 3, 3, 'module_badminton:semester:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '修改学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除学期', 3, 4, 'module_badminton:semester:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除学期信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情学期', 3, 5, 'module_badminton:semester:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看学期详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSemester';

-- 班级管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询班级', 3, 1, 'module_badminton:team:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTeam';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增班级', 3, 2, 'module_badminton:team:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTeam';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改班级', 3, 3, 'module_badminton:team:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '修改班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTeam';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除班级', 3, 4, 'module_badminton:team:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除班级信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTeam';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情班级', 3, 5, 'module_badminton:team:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看班级详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonTeam';

-- 报班管理权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询购买', 3, 1, 'module_badminton:purchase:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增购买', 3, 2, 'module_badminton:purchase:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改购买', 3, 3, 'module_badminton:purchase:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '修改购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除购买', 3, 4, 'module_badminton:purchase:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除购买信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情购买', 3, 5, 'module_badminton:purchase:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看购买详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonPurchase';

-- 考勤记录权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询考勤', 3, 1, 'module_badminton:class_attendance:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增考勤', 3, 2, 'module_badminton:class_attendance:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改考勤', 3, 3, 'module_badminton:class_attendance:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '修改考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除考勤', 3, 4, 'module_badminton:class_attendance:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除考勤信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情考勤', 3, 5, 'module_badminton:class_attendance:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看考勤详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonAttendance';

-- 排课记录权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询排课', 3, 1, 'module_badminton:class-schedule:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增排课', 3, 2, 'module_badminton:class-schedule:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '修改排课', 3, 3, 'module_badminton:class-schedule:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '修改排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除排课', 3, 4, 'module_badminton:class-schedule:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '详情排课', 3, 5, 'module_badminton:class-schedule:detail', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看排课详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonSchedule';

-- 能力分组权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询分组', 3, 1, 'module_badminton:group:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '新增分组', 3, 2, 'module_badminton:group:create', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '新增能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '编辑分组', 3, 3, 'module_badminton:group:update', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '编辑能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '删除分组', 3, 4, 'module_badminton:group:delete', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '删除能力分组', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonGroup';

-- 教练视图权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查询教练视图', 3, 1, 'module_badminton:coach_schedule:list', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查询教练排课信息', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonCoachSchedule';

-- ========================================
-- 第七步：修正旧权限命名
-- ========================================
UPDATE sys_menu SET permission = REPLACE(permission, ':query', ':list'), updated_time = NOW()
WHERE permission LIKE 'module_badminton:%:query';
UPDATE sys_menu SET permission = REPLACE(permission, 'module_badminton:parent:', 'module_badminton:parent_student:'), updated_time = NOW()
WHERE permission LIKE 'module_badminton:parent:%';
UPDATE sys_menu SET permission = REPLACE(permission, 'module_badminton:leave:', 'module_badminton:leave_request:'), updated_time = NOW()
WHERE permission LIKE 'module_badminton:leave:%';
UPDATE sys_menu SET permission = REPLACE(permission, 'module_badminton:attendance:', 'module_badminton:class_attendance:'), updated_time = NOW()
WHERE permission LIKE 'module_badminton:attendance:%';
UPDATE sys_menu SET permission = REPLACE(permission, 'module_badminton:schedule:', 'module_badminton:class-schedule:'), updated_time = NOW()
WHERE permission LIKE 'module_badminton:schedule:%';

-- ========================================
-- 第九步：注册移动端模块菜单
-- ========================================

-- 教练移动端根菜单（挂在视图分组下）
INSERT INTO sys_menu
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '教练移动端', 2, 3, NULL, 'el-icon-Phone', 'BadmintonMobileCoach', '/m/badminton/coach', 'module_badminton/m/coach/home', NULL, TRUE, TRUE, FALSE, '教练移动端', NULL, FALSE, m.id, gen_random_uuid(), '0', '教练手机端：签到、课表、比赛、评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonView' LIMIT 1;

-- 家长移动端根菜单（挂在视图分组下）
INSERT INTO sys_menu
(name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '家长移动端', 2, 4, NULL, 'el-icon-Phone', 'BadmintonMobileParent', '/m/badminton/parent', 'module_badminton/m/parent/student', '/m/badminton/parent/student', TRUE, TRUE, FALSE, '家长移动端', NULL, FALSE, m.id, gen_random_uuid(), '0', '家长手机端：学习情况、比赛、H2H', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonView' LIMIT 1;

-- ========================================
-- 第十步：注册移动端三级权限（教练移动端）
-- ========================================

INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查看教练首页', 3, 1, 'module_badminton:mobile_coach:home', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '查看教练手机端首页', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '点名签到', 3, 2, 'module_badminton:mobile_coach:attendance', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '移动端点名签到', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查看课表', 3, 3, 'module_badminton:mobile_coach:schedule', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '移动端查看课表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '比赛管理', 3, 4, 'module_badminton:mobile_coach:tournament', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '移动端比赛列表和比分录入', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '能力评估', 3, 5, 'module_badminton:mobile_coach:assessment', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '移动端学员能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach';

-- 家长移动端三级权限
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查看学习情况', 3, 1, 'module_badminton:mobile_parent:student', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '家长端查看学员学习情况', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '查看比赛结果', 3, 2, 'module_badminton:mobile_parent:tournament', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '家长端查看比赛结果', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent';
INSERT INTO sys_menu (name, type, "order", permission, hidden, keep_alive, always_show, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '学员H2H对比', 3, 3, 'module_badminton:mobile_parent:h2h', FALSE, FALSE, TRUE, FALSE, m.id, gen_random_uuid(), '0', '学员历史对战H2H对比', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent';

-- ========================================
-- 第十一步：注册移动端子页面（路由由菜单系统控制）
-- ========================================

-- 家长移动端子页面
INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '学习情况', 2, 1, NULL, NULL, 'DynMobileParentStudent', 'student', 'module_badminton/m/parent/student', NULL, TRUE, TRUE, FALSE, '学习情况', NULL, FALSE, m.id, gen_random_uuid(), '0', '查看学员学习情况', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileParentStudent');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '比赛结果', 2, 2, NULL, NULL, 'DynMobileParentTournament', 'tournament', 'module_badminton/m/parent/tournament', NULL, TRUE, TRUE, FALSE, '比赛结果', NULL, FALSE, m.id, gen_random_uuid(), '0', '查看比赛结果', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileParentTournament');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '历史赛事', 2, 3, NULL, NULL, 'DynMobileParentTournamentHistory', 'tournament-history', 'module_badminton/m/parent/tournament-history', NULL, TRUE, TRUE, FALSE, '历史赛事', NULL, FALSE, m.id, gen_random_uuid(), '0', '查看历史赛事', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileParentTournamentHistory');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '学员H2H', 2, 4, NULL, NULL, 'DynMobileParentH2H', 'h2h', 'module_badminton/m/parent/h2h', NULL, TRUE, TRUE, FALSE, '学员H2H', NULL, FALSE, m.id, gen_random_uuid(), '0', '学员历史对战H2H对比', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileParentH2H');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '赛事详情', 2, 5, NULL, NULL, 'DynMobileParentTournamentDetail', 'tournament-detail/:tournamentId', 'module_badminton/m/parent/tournament-detail', NULL, TRUE, TRUE, FALSE, '赛事详情', NULL, FALSE, m.id, gen_random_uuid(), '0', '查看赛事详情', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileParent'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileParentTournamentDetail');

-- 教练移动端子页面
INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '教练首页', 2, 1, NULL, NULL, 'DynMobileCoachHome', 'home', 'module_badminton/m/coach/home', NULL, TRUE, TRUE, FALSE, '教练首页', NULL, FALSE, m.id, gen_random_uuid(), '0', '教练手机端首页', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachHome');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '点名签到', 2, 2, NULL, NULL, 'DynMobileCoachAttendance', 'attendance', 'module_badminton/m/coach/attendance', NULL, TRUE, TRUE, FALSE, '点名签到', NULL, FALSE, m.id, gen_random_uuid(), '0', '移动端点名签到', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachAttendance');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '我的课表', 2, 3, NULL, NULL, 'DynMobileCoachSchedule', 'schedule', 'module_badminton/m/coach/schedule', NULL, TRUE, TRUE, FALSE, '我的课表', NULL, FALSE, m.id, gen_random_uuid(), '0', '移动端查看课表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachSchedule');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '赛事列表', 2, 4, NULL, NULL, 'DynMobileCoachTournamentList', 'tournament-list', 'module_badminton/m/coach/tournament-list', NULL, TRUE, TRUE, FALSE, '赛事列表', NULL, FALSE, m.id, gen_random_uuid(), '0', '移动端比赛列表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachTournamentList');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '对阵列表', 2, 5, NULL, NULL, 'DynMobileCoachTournamentMatches', 'tournament-matches/:id', 'module_badminton/m/coach/tournament-matches', NULL, TRUE, TRUE, FALSE, '对阵列表', NULL, FALSE, m.id, gen_random_uuid(), '0', '对阵列表', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachTournamentMatches');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '录入比分', 2, 6, NULL, NULL, 'DynMobileCoachMatchScore', 'match-score/:tournamentId/:matchId', 'module_badminton/m/coach/match-score', NULL, TRUE, TRUE, FALSE, '录入比分', NULL, FALSE, m.id, gen_random_uuid(), '0', '录入比分', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachMatchScore');

INSERT INTO sys_menu (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
SELECT '能力评估', 2, 7, NULL, NULL, 'DynMobileCoachAssessment', 'assessment', 'module_badminton/m/coach/assessment-compose', NULL, TRUE, TRUE, FALSE, '能力评估', NULL, FALSE, m.id, gen_random_uuid(), '0', '移动端学员能力评估', NOW(), NOW()
FROM sys_menu m WHERE m.route_name = 'BadmintonMobileCoach'
AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'DynMobileCoachAssessment');

-- ========================================
-- 第十二步：分配移动端菜单到角色
-- ========================================

-- 家长移动端菜单分配给家长角色
INSERT INTO sys_role_menus (role_id, menu_id)
SELECT r.id, m.id
FROM sys_role r, sys_menu m
WHERE r.code = 'PARENTS'
AND (m.route_name = 'BadmintonMobileParent' OR m.route_name LIKE 'DynMobileParent%')
AND NOT EXISTS (SELECT 1 FROM sys_role_menus WHERE role_id = r.id AND menu_id = m.id);

-- 教练移动端菜单分配给教练角色
INSERT INTO sys_role_menus (role_id, menu_id)
SELECT r.id, m.id
FROM sys_role r, sys_menu m
WHERE r.code = 'COACH'
AND (m.route_name = 'BadmintonMobileCoach' OR m.route_name LIKE 'DynMobileCoach%')
AND NOT EXISTS (SELECT 1 FROM sys_role_menus WHERE role_id = r.id AND menu_id = m.id);

-- 排课管理权限分配给教练角色（教练移动端需要调用排课接口）
INSERT INTO sys_role_menus (role_id, menu_id)
SELECT r.id, m.id
FROM sys_role r, sys_menu m
WHERE r.code = 'COACH'
AND m.permission LIKE 'module_badminton:class-schedule:%'
AND NOT EXISTS (SELECT 1 FROM sys_role_menus WHERE role_id = r.id AND menu_id = m.id);

-- ========================================
-- 第十三步：验证结果
-- ========================================
DO $$
DECLARE
    v_group_count INTEGER;
    v_module_count INTEGER;
    v_perm_count INTEGER;
    v_old_root_hidden BOOLEAN;
BEGIN
    SELECT hidden INTO v_old_root_hidden
    FROM sys_menu WHERE route_name = 'Badminton' AND parent_id IS NULL;

    SELECT COUNT(*) INTO v_group_count
    FROM sys_menu
    WHERE route_name IN ('BadmintonBasic','BadmintonTeaching','BadmintonBusiness','BadmintonView')
      AND parent_id IS NULL;

    SELECT COUNT(*) INTO v_module_count
    FROM sys_menu
    WHERE route_name LIKE 'Badminton%' AND type = 2;

    SELECT COUNT(*) INTO v_perm_count
    FROM sys_menu WHERE permission LIKE 'module_badminton:%';

    RAISE NOTICE '========================================';
    RAISE NOTICE '羽毛球菜单重组完成';
    RAISE NOTICE '========================================';
    RAISE NOTICE '旧根菜单已隐藏: %', v_old_root_hidden;
    RAISE NOTICE '新分组菜单数: % (应为4+)', v_group_count;
    RAISE NOTICE '模块菜单数: % (应为15)', v_module_count;
    RAISE NOTICE '权限总数: %', v_perm_count;
    RAISE NOTICE '========================================';
END $$;
