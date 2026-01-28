-- 能力分组管理菜单初始化脚本
-- 执行此脚本将添加能力分组管理相关菜单项

DO $$
DECLARE
  root_id INTEGER;
  group_parent_id INTEGER;
BEGIN
  -- 1. 获取羽毛球管理一级菜单ID
  SELECT id INTO root_id
  FROM sys_menu
  WHERE route_name = 'Badminton'
  LIMIT 1;

  IF root_id IS NULL THEN
    RAISE NOTICE '一级菜单羽毛球管理不存在，请先执行 add_badminton_menu.sql';
    RETURN;
  END IF;

  -- 2. 创建能力分组管理二级菜单
  SELECT id INTO group_parent_id
  FROM sys_menu
  WHERE route_name = 'BadmintonGroup' AND parent_id = root_id
  LIMIT 1;

  IF group_parent_id IS NULL THEN
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('能力分组', 2, 12, 'module_badminton:group:list', 'user-group', 'BadmintonGroup', 'group', 'module_badminton/group/index', NULL, FALSE, TRUE, FALSE, '能力分组', NULL, FALSE, root_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '能力分组管理', NOW(), NOW())
    RETURNING id INTO group_parent_id;

    -- 3. 为能力分组管理添加操作权限（三级菜单）
    INSERT INTO sys_menu 
    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
    VALUES 
    ('查询分组', 3, 1, 'module_badminton:group:list', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '查询分组', NULL, FALSE, group_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '查询能力分组', NOW(), NOW()),
    ('新增分组', 3, 2, 'module_badminton:group:create', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '新增分组', NULL, FALSE, group_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '新增能力分组', NOW(), NOW()),
    ('编辑分组', 3, 3, 'module_badminton:group:update', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '编辑分组', NULL, FALSE, group_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '编辑能力分组', NOW(), NOW()),
    ('删除分组', 3, 4, 'module_badminton:group:delete', NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, '删除分组', NULL, FALSE, group_parent_id, (lower(substr(md5(random()::text),1,8) || '-' || substr(md5(random()::text),9,4) || '-' || substr(md5(random()::text),13,4) || '-' || substr(md5(random()::text),17,4) || '-' || substr(md5(random()::text || clock_timestamp()::text),1,12)))::uuid, '0', '删除能力分组', NOW(), NOW());

    RAISE NOTICE '已创建能力分组管理菜单及操作权限 (ID: %)', group_parent_id;
  ELSE
    RAISE NOTICE '能力分组管理菜单已存在 (ID: %)', group_parent_id;
  END IF;

  RAISE NOTICE '能力分组管理菜单初始化完成！';
END $$;