-- 添加教练视图菜单
-- 执行此脚本将添加教练视图菜单项

DO $$
DECLARE
  root_id INTEGER;
  coach_schedule_parent_id INTEGER;
BEGIN
  -- 1. 查找羽毛球管理一级菜单
  SELECT id INTO root_id
  FROM sys_menu
  WHERE route_name = 'Badminton'
  LIMIT 1;

  IF root_id IS NULL THEN
    RAISE EXCEPTION '羽毛球管理一级菜单不存在，请先执行 add_badminton_menu.sql';
  END IF;

  -- 2. 创建教练视图二级菜单
  SELECT id INTO coach_schedule_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonCoachSchedule' AND parent_id = root_id
  LIMIT 1;

  IF coach_schedule_parent_id IS NULL THEN
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('教练视图', 2, 12, 'module_badminton:coach_schedule:query', 'user', 'BadmintonCoachSchedule', 'coach-schedule', 'module_badminton/coach-schedule/index', NULL, FALSE, TRUE, FALSE, '教练视图', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '教练排课视图', NOW(), NOW())
    RETURNING id INTO coach_schedule_parent_id;

    -- 为教练视图添加操作权限（三级菜单）
    INSERT INTO sys_menu
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time)
    VALUES
    ('查询教练视图', 3, 1, 'module_badminton:coach_schedule:query', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询教练视图', NULL, FALSE, coach_schedule_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询教练视图', NOW(), NOW());

    RAISE NOTICE '已创建教练视图菜单及操作权限 (ID: %)', coach_schedule_parent_id;
  ELSE
    RAISE NOTICE '教练视图菜单已存在 (ID: %)', coach_schedule_parent_id;
  END IF;

  RAISE NOTICE '教练视图菜单初始化完成！';
END $$;