-- 清理课程管理模块（Course）相关菜单和权限
-- 执行前请确保已备份数据库

-- ========================================
-- 第一步：删除课程管理的权限按钮（type=3）
-- ========================================
DELETE FROM sys_menu WHERE permission LIKE 'module_badminton:course:%' AND type = 3;

-- ========================================
-- 第二步：删除课程管理菜单本身（type=2）
-- ========================================
DELETE FROM sys_menu WHERE route_name = 'BadmintonCourse';

-- ========================================
-- 第三步：清理教学管理分组的描述和重定向
-- ========================================
UPDATE sys_menu
SET description = '教学管理：排课、考勤、评估、分组',
    redirect = '/Badminton/schedule',
    updated_time = NOW()
WHERE route_name = 'BadmintonTeaching';
