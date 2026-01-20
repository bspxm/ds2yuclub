-- 羽毛球培训会员管理系统菜单初始化脚本
-- 执行此脚本将添加羽毛球管理相关菜单项

DO $$
DECLARE
  root_id INTEGER;
  student_parent_id INTEGER;
  parent_parent_id INTEGER;
  tournament_parent_id INTEGER;
  course_parent_id INTEGER;
  assessment_parent_id INTEGER;
  leave_parent_id INTEGER;
  semester_parent_id INTEGER;
  class_parent_id INTEGER;
  purchase_parent_id INTEGER;
  attendance_parent_id INTEGER;
  schedule_parent_id INTEGER;
BEGIN
  -- 1. 创建一级菜单：羽毛球管理
  SELECT id INTO root_id
  FROM sys_menu
  WHERE route_name = 'Badminton'
  LIMIT 1;

  IF root_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('羽毛球管理', 1, 8, NULL, 'sports', 'Badminton', '/badminton', NULL, '/badminton/student', FALSE, TRUE, FALSE, '羽毛球管理', NULL, FALSE, NULL, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '羽毛球培训会员管理系统', NOW(), NOW())
    RETURNING id INTO root_id;
    
    RAISE NOTICE '已创建一级菜单: 羽毛球管理 (ID: %)', root_id;
  ELSE
    RAISE NOTICE '一级菜单已存在: 羽毛球管理 (ID: %)', root_id;
  END IF;

  -- 2. 创建学员管理二级菜单
  SELECT id INTO student_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonStudent' AND parent_id = root_id
  LIMIT 1;

  IF student_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('学员管理', 2, 1, 'module_badminton:student:query', 'user', 'BadmintonStudent', 'student', 'module_badminton/student/index', NULL, FALSE, TRUE, FALSE, '学员管理', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '学员信息管理', NOW(), NOW())
    RETURNING id INTO student_parent_id;

    -- 3. 为学员管理添加操作权限（三级菜单）
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询学员', 3, 1, 'module_badminton:student:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询学员信息', NOW(), NOW()),
    ('新增学员', 3, 2, 'module_badminton:student:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增学员信息', NOW(), NOW()),
    ('编辑学员', 3, 3, 'module_badminton:student:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '编辑学员信息', NOW(), NOW()),
    ('删除学员', 3, 4, 'module_badminton:student:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除学员信息', NOW(), NOW()),
    ('导出学员', 3, 5, 'module_badminton:student:export', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '导出学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '导出学员信息', NOW(), NOW()),
    ('详情学员', 3, 6, 'module_badminton:student:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看学员详情', NOW(), NOW()),
    ('批量导入学员', 3, 7, 'module_badminton:student:import', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '批量导入学员', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '批量导入学员信息', NOW(), NOW()),
    ('批量设置状态', 3, 8, 'module_badminton:student:batch_status', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '批量设置状态', NULL, FALSE, student_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '批量设置学员状态', NOW(), NOW());

    RAISE NOTICE '已创建学员管理菜单及操作权限 (ID: %)', student_parent_id;
  ELSE
    RAISE NOTICE '学员管理菜单已存在 (ID: %)', student_parent_id;
  END IF;

  -- 4. 创建家长端二级菜单
  SELECT id INTO parent_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonParent' AND parent_id = root_id
  LIMIT 1;

  IF parent_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('家长端', 2, 2, 'module_badminton:parent:query', 'el-icon-User', 'BadmintonParent', 'parent', 'module_badminton/parent/index', NULL, FALSE, TRUE, FALSE, '家长端', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '家长端功能', NOW(), NOW())
    RETURNING id INTO parent_parent_id;

    -- 为家长端添加操作权限
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询家长端', 3, 1, 'module_badminton:parent:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询家长端', NULL, FALSE, parent_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询家长端信息', NOW(), NOW()),
    ('详情家长端', 3, 2, 'module_badminton:parent:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情家长端', NULL, FALSE, parent_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看家长端详情', NOW(), NOW());

    RAISE NOTICE '已创建家长端菜单及操作权限 (ID: %)', parent_parent_id;
  ELSE
    RAISE NOTICE '家长端菜单已存在 (ID: %)', parent_parent_id;
  END IF;

  -- 5. 创建赛事管理二级菜单
  SELECT id INTO tournament_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonTournament' AND parent_id = root_id
  LIMIT 1;

  IF tournament_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('赛事管理', 2, 3, 'module_badminton:tournament:query', 'trophy', 'BadmintonTournament', 'tournament', 'module_badminton/tournament/index', NULL, FALSE, TRUE, FALSE, '赛事管理', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '赛事信息管理', NOW(), NOW())
    RETURNING id INTO tournament_parent_id;

    -- 为赛事管理添加操作权限
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询赛事', 3, 1, 'module_badminton:tournament:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询赛事', NULL, FALSE, tournament_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询赛事信息', NOW(), NOW()),
    ('新增赛事', 3, 2, 'module_badminton:tournament:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增赛事', NULL, FALSE, tournament_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增赛事信息', NOW(), NOW()),
    ('编辑赛事', 3, 3, 'module_badminton:tournament:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑赛事', NULL, FALSE, tournament_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '编辑赛事信息', NOW(), NOW()),
    ('删除赛事', 3, 4, 'module_badminton:tournament:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除赛事', NULL, FALSE, tournament_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除赛事信息', NOW(), NOW()),
    ('导出赛事', 3, 5, 'module_badminton:tournament:export', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '导出赛事', NULL, FALSE, tournament_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '导出赛事信息', NOW(), NOW()),
    ('详情赛事', 3, 6, 'module_badminton:tournament:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情赛事', NULL, FALSE, tournament_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看赛事详情', NOW(), NOW());

    RAISE NOTICE '已创建赛事管理菜单及操作权限 (ID: %)', tournament_parent_id;
  ELSE
    RAISE NOTICE '赛事管理菜单已存在 (ID: %)', tournament_parent_id;
  END IF;

  -- 6. 创建课程管理二级菜单
  SELECT id INTO course_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonCourse' AND parent_id = root_id
  LIMIT 1;

  IF course_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('课程管理', 2, 4, 'module_badminton:course:query', 'calendar', 'BadmintonCourse', 'course', 'module_badminton/course/index', NULL, FALSE, TRUE, FALSE, '课程管理', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '课程信息管理', NOW(), NOW())
    RETURNING id INTO course_parent_id;

    -- 为课程管理添加操作权限
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询课程', 3, 1, 'module_badminton:course:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询课程', NULL, FALSE, course_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询课程信息', NOW(), NOW()),
    ('新增课程', 3, 2, 'module_badminton:course:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增课程', NULL, FALSE, course_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增课程信息', NOW(), NOW()),
    ('编辑课程', 3, 3, 'module_badminton:course:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑课程', NULL, FALSE, course_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '编辑课程信息', NOW(), NOW()),
    ('删除课程', 3, 4, 'module_badminton:course:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除课程', NULL, FALSE, course_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除课程信息', NOW(), NOW()),
    ('导出课程', 3, 5, 'module_badminton:course:export', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '导出课程', NULL, FALSE, course_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '导出课程信息', NOW(), NOW()),
    ('详情课程', 3, 6, 'module_badminton:course:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情课程', NULL, FALSE, course_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看课程详情', NOW(), NOW());

    RAISE NOTICE '已创建课程管理菜单及操作权限 (ID: %)', course_parent_id;
  ELSE
    RAISE NOTICE '课程管理菜单已存在 (ID: %)', course_parent_id;
  END IF;

  -- 7. 创建能力评估二级菜单
  SELECT id INTO assessment_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonAssessment' AND parent_id = root_id
  LIMIT 1;

  IF assessment_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('能力评估', 2, 5, 'module_badminton:assessment:query', 'el-icon-TrendCharts', 'BadmintonAssessment', 'assessment', 'module_badminton/assessment/index', NULL, FALSE, TRUE, FALSE, '能力评估', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '学员能力评估管理', NOW(), NOW())
    RETURNING id INTO assessment_parent_id;

    -- 为能力评估添加操作权限
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询评估', 3, 1, 'module_badminton:assessment:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询评估', NULL, FALSE, assessment_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询能力评估', NOW(), NOW()),
    ('新增评估', 3, 2, 'module_badminton:assessment:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增评估', NULL, FALSE, assessment_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增能力评估', NOW(), NOW()),
    ('编辑评估', 3, 3, 'module_badminton:assessment:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑评估', NULL, FALSE, assessment_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '编辑能力评估', NOW(), NOW()),
    ('删除评估', 3, 4, 'module_badminton:assessment:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除评估', NULL, FALSE, assessment_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除能力评估', NOW(), NOW()),
    ('导出评估', 3, 5, 'module_badminton:assessment:export', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '导出评估', NULL, FALSE, assessment_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '导出能力评估', NOW(), NOW()),
    ('详情评估', 3, 6, 'module_badminton:assessment:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情评估', NULL, FALSE, assessment_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看评估详情', NOW(), NOW());

    RAISE NOTICE '已创建能力评估菜单及操作权限 (ID: %)', assessment_parent_id;
  ELSE
    RAISE NOTICE '能力评估菜单已存在 (ID: %)', assessment_parent_id;
  END IF;

  -- 8. 创建请假管理二级菜单
  SELECT id INTO leave_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonLeaveRequest' AND parent_id = root_id
  LIMIT 1;

  IF leave_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('请假管理', 2, 6, 'module_badminton:leave:query', 'el-icon-Timer', 'BadmintonLeaveRequest', 'leave-request', 'module_badminton/leave-request/index', NULL, FALSE, TRUE, FALSE, '请假管理', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '学员请假管理', NOW(), NOW())
    RETURNING id INTO leave_parent_id;

    -- 为请假管理添加操作权限
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询请假', 3, 1, 'module_badminton:leave:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询请假', NULL, FALSE, leave_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询请假信息', NOW(), NOW()),
    ('新增请假', 3, 2, 'module_badminton:leave:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增请假', NULL, FALSE, leave_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增请假信息', NOW(), NOW()),
    ('编辑请假', 3, 3, 'module_badminton:leave:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑请假', NULL, FALSE, leave_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '编辑请假信息', NOW(), NOW()),
    ('删除请假', 3, 4, 'module_badminton:leave:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除请假', NULL, FALSE, leave_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除请假信息', NOW(), NOW()),
    ('导出请假', 3, 5, 'module_badminton:leave:export', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '导出请假', NULL, FALSE, leave_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '导出请假信息', NOW(), NOW()),
    ('详情请假', 3, 6, 'module_badminton:leave:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情请假', NULL, FALSE, leave_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看请假详情', NOW(), NOW());

    RAISE NOTICE '已创建请假管理菜单及操作权限 (ID: %)', leave_parent_id;
  ELSE
    RAISE NOTICE '请假管理菜单已存在 (ID: %)', leave_parent_id;
  END IF;

  -- 9. 创建学期管理二级菜单
  SELECT id INTO semester_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonSemester' AND parent_id = root_id
  LIMIT 1;

  IF semester_parent_id IS NULL THEN
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('学期管理', 2, 7, 'module_badminton:semester:query', 'calendar', 'BadmintonSemester', 'semester', 'module_badminton/semester/index', NULL, FALSE, TRUE, FALSE, '学期管理', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '学期信息管理', NOW(), NOW())
    RETURNING id INTO semester_parent_id;

    -- 为学期管理添加操作权限（三级菜单）
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('查询学期', 3, 1, 'module_badminton:semester:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询学期', NULL, FALSE, semester_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询学期信息', NOW(), NOW()),
    ('新增学期', 3, 2, 'module_badminton:semester:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增学期', NULL, FALSE, semester_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增学期信息', NOW(), NOW()),
    ('修改学期', 3, 3, 'module_badminton:semester:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '修改学期', NULL, FALSE, semester_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '修改学期信息', NOW(), NOW()),
    ('删除学期', 3, 4, 'module_badminton:semester:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除学期', NULL, FALSE, semester_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除学期信息', NOW(), NOW()),
    ('详情学期', 3, 5, 'module_badminton:semester:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情学期', NULL, FALSE, semester_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看学期详情', NOW(), NOW());

    RAISE NOTICE '已创建学期管理菜单及操作权限 (ID: %)', semester_parent_id;
  ELSE
    RAISE NOTICE '学期管理菜单已存在 (ID: %)', semester_parent_id;
  END IF;

  -- 10. 创建班级管理二级菜单
  SELECT id INTO class_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonClass' AND parent_id = root_id
  LIMIT 1;

  IF class_parent_id IS NULL THEN
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('班级管理', 2, 8, 'module_badminton:class:query', 'team', 'BadmintonClass', 'class', 'module_badminton/class/index', NULL, FALSE, TRUE, FALSE, '班级管理', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '班级信息管理', NOW(), NOW())
    RETURNING id INTO class_parent_id;

    -- 为班级管理添加操作权限（三级菜单）
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('查询班级', 3, 1, 'module_badminton:class:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询班级', NULL, FALSE, class_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询班级信息', NOW(), NOW()),
    ('新增班级', 3, 2, 'module_badminton:class:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增班级', NULL, FALSE, class_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增班级信息', NOW(), NOW()),
    ('修改班级', 3, 3, 'module_badminton:class:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '修改班级', NULL, FALSE, class_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '修改班级信息', NOW(), NOW()),
    ('删除班级', 3, 4, 'module_badminton:class:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除班级', NULL, FALSE, class_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除班级信息', NOW(), NOW()),
    ('详情班级', 3, 5, 'module_badminton:class:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情班级', NULL, FALSE, class_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看班级详情', NOW(), NOW());

    RAISE NOTICE '已创建班级管理菜单及操作权限 (ID: %)', class_parent_id;
  ELSE
    RAISE NOTICE '班级管理菜单已存在 (ID: %)', class_parent_id;
  END IF;

  -- 11. 创建购买记录二级菜单
  SELECT id INTO purchase_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonPurchase' AND parent_id = root_id
  LIMIT 1;

  IF purchase_parent_id IS NULL THEN
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('购买记录', 2, 9, 'module_badminton:purchase:query', 'shopping-cart', 'BadmintonPurchase', 'purchase', 'module_badminton/purchase/index', NULL, FALSE, TRUE, FALSE, '购买记录', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '购买记录管理', NOW(), NOW())
    RETURNING id INTO purchase_parent_id;

    -- 为购买记录添加操作权限（三级菜单）
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('查询购买', 3, 1, 'module_badminton:purchase:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询购买', NULL, FALSE, purchase_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询购买信息', NOW(), NOW()),
    ('新增购买', 3, 2, 'module_badminton:purchase:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增购买', NULL, FALSE, purchase_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增购买信息', NOW(), NOW()),
    ('修改购买', 3, 3, 'module_badminton:purchase:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '修改购买', NULL, FALSE, purchase_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '修改购买信息', NOW(), NOW()),
    ('删除购买', 3, 4, 'module_badminton:purchase:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除购买', NULL, FALSE, purchase_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除购买信息', NOW(), NOW()),
    ('详情购买', 3, 5, 'module_badminton:purchase:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情购买', NULL, FALSE, purchase_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看购买详情', NOW(), NOW());

    RAISE NOTICE '已创建购买记录菜单及操作权限 (ID: %)', purchase_parent_id;
  ELSE
    RAISE NOTICE '购买记录菜单已存在 (ID: %)', purchase_parent_id;
  END IF;

  -- 12. 创建考勤记录二级菜单
  SELECT id INTO attendance_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonAttendance' AND parent_id = root_id
  LIMIT 1;

  IF attendance_parent_id IS NULL THEN
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('考勤记录', 2, 10, 'module_badminton:attendance:query', 'check-circle', 'BadmintonAttendance', 'class-attendance', 'module_badminton/class-attendance/index', NULL, FALSE, TRUE, FALSE, '考勤记录', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '考勤记录管理', NOW(), NOW())
    RETURNING id INTO attendance_parent_id;

    -- 为考勤记录添加操作权限（三级菜单）
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('查询考勤', 3, 1, 'module_badminton:attendance:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询考勤', NULL, FALSE, attendance_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询考勤信息', NOW(), NOW()),
    ('新增考勤', 3, 2, 'module_badminton:attendance:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增考勤', NULL, FALSE, attendance_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增考勤信息', NOW(), NOW()),
    ('修改考勤', 3, 3, 'module_badminton:attendance:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '修改考勤', NULL, FALSE, attendance_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '修改考勤信息', NOW(), NOW()),
    ('删除考勤', 3, 4, 'module_badminton:attendance:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除考勤', NULL, FALSE, attendance_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除考勤信息', NOW(), NOW()),
    ('详情考勤', 3, 5, 'module_badminton:attendance:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情考勤', NULL, FALSE, attendance_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看考勤详情', NOW(), NOW());

    RAISE NOTICE '已创建考勤记录菜单及操作权限 (ID: %)', attendance_parent_id;
  ELSE
    RAISE NOTICE '考勤记录菜单已存在 (ID: %)', attendance_parent_id;
  END IF;

  -- 13. 创建排课记录二级菜单
  SELECT id INTO schedule_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonSchedule' AND parent_id = root_id
  LIMIT 1;

  IF schedule_parent_id IS NULL THEN
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('排课记录', 2, 11, 'module_badminton:schedule:query', 'schedule', 'BadmintonSchedule', 'class-schedule', 'module_badminton/class-schedule/index', NULL, FALSE, TRUE, FALSE, '排课记录', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '排课记录管理', NOW(), NOW())
    RETURNING id INTO schedule_parent_id;

    -- 为排课记录添加操作权限（三级菜单）
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('查询排课', 3, 1, 'module_badminton:schedule:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询排课', NULL, FALSE, schedule_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询排课信息', NOW(), NOW()),
    ('新增排课', 3, 2, 'module_badminton:schedule:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增排课', NULL, FALSE, schedule_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增排课信息', NOW(), NOW()),
    ('修改排课', 3, 3, 'module_badminton:schedule:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '修改排课', NULL, FALSE, schedule_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '修改排课信息', NOW(), NOW()),
    ('删除排课', 3, 4, 'module_badminton:schedule:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除排课', NULL, FALSE, schedule_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除排课信息', NOW(), NOW()),
    ('详情排课', 3, 5, 'module_badminton:schedule:detail', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '详情排课', NULL, FALSE, schedule_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查看排课详情', NOW(), NOW());

    RAISE NOTICE '已创建排课记录菜单及操作权限 (ID: %)', schedule_parent_id;
  ELSE
    RAISE NOTICE '排课记录菜单已存在 (ID: %)', schedule_parent_id;
  END IF;

  RAISE NOTICE '羽毛球培训会员管理系统菜单初始化完成！';
END $$;