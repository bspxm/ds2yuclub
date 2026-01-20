#!/usr/bin/env python3
"""
分割controller.py到各个模块
"""

import os
import re
from pathlib import Path

# 项目根目录
base_dir = Path(__file__).parent
module_dir = base_dir / "app" / "plugin" / "module_badminton"

# 读取原始controller.py
controller_file = module_dir / "controller.py"
with open(controller_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 路由路径到模块的映射
path_to_module = {
    'students': 'student',
    'parent-students': 'student',
    'ability-assessments': 'student',
    'tournaments': 'tournament',
    'courses': 'course',
    'leave-requests': 'leave',
    'semesters': 'semester',
    'classes': 'class_',
    'purchases': 'purchase',
    'class-attendances': 'attendance',
    'class-schedules': 'schedule',
}

# 通用路由（保留在主文件中）
common_paths = ['health', 'info', 'tournament/types']

# 提取导入部分（文件开头直到第一个路由装饰器）
import_section_match = re.search(r'^.*?(?=@BadmintonRouter)', content, re.DOTALL)
import_section = import_section_match.group(0) if import_section_match else ''

# 分割各个路由函数
# 查找所有路由装饰器
route_pattern = r'^@BadmintonRouter\.(get|post|put|delete|patch)\([^)]*\)\s*\nasync def (\w+)'
route_matches = list(re.finditer(route_pattern, content, re.MULTILINE))

# 为每个模块准复内容
module_contents = {module: [] for module in set(path_to_module.values())}
module_contents['main'] = []  # 主文件保留通用路由

# 遍历每个路由函数
for i, match in enumerate(route_matches):
    method = match.group(1)
    func_name = match.group(2)
    
    # 找到函数定义的开始和结束
    start_pos = match.start()
    if i + 1 < len(route_matches):
        end_pos = route_matches[i + 1].start()
    else:
        end_pos = len(content)
    
    func_content = content[start_pos:end_pos].rstrip()
    
    # 提取路由路径
    # 查找装饰器中的路径参数
    decorator_match = re.search(r'@BadmintonRouter\.\w+\([^)]*"([^"]+)"', func_content)
    if not decorator_match:
        # 无法确定路径，保留在主文件中
        module_contents['main'].append(func_content)
        continue
    
    path = decorator_match.group(1)
    
    # 确定模块
    target_module = None
    for path_keyword, module in path_to_module.items():
        if path_keyword in path:
            target_module = module
            break
    
    # 检查是否为通用路由
    is_common = any(common in path for common in common_paths)
    if is_common:
        target_module = 'main'
    
    if target_module is None:
        # 未映射的路由，保留在主文件中
        target_module = 'main'
    
    module_contents[target_module].append(func_content)

# 写入各个模块的controller.py
for module, functions in module_contents.items():
    if not functions:
        continue
    
    if module == 'main':
        # 主controller.py，保留导入和所有通用路由
        output_path = module_dir / "controller.py"
        # 先备份原文件
        backup_path = module_dir / "controller.py.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"备份原文件到 {backup_path}")
    else:
        # 模块文件
        module_path = module_dir / module
        if not module_path.exists():
            module_path.mkdir(exist_ok=True)
        output_path = module_path / "controller.py"
    
    # 构建输出内容
    output_lines = []
    
    if module == 'main':
        # 主文件保留所有导入
        output_lines.append(import_section)
    else:
        # 模块文件需要适当的导入
        output_lines.append('"""')
        output_lines.append(f'{module}模块 - 控制器')
        output_lines.append('"""')
        output_lines.append('')
        output_lines.append('from typing import Optional')
        output_lines.append('')
        output_lines.append('from fastapi import APIRouter, Depends, Query, UploadFile, File')
        output_lines.append('from fastapi.responses import JSONResponse, StreamingResponse')
        output_lines.append('')
        output_lines.append('from app.api.v1.module_system.auth.schema import AuthSchema')
        output_lines.append('from app.common.response import SuccessResponse')
        output_lines.append('from app.core.dependencies import AuthPermission')
        output_lines.append('from app.core.exceptions import CustomException')
        output_lines.append('from app.core.router_class import OperationLogRoute')
        output_lines.append('')
        # 导入本模块的schema和service
        output_lines.append(f'from .schema import *')
        output_lines.append(f'from .service import *')
        output_lines.append('')
        # 创建模块路由器
        router_name = f'{module.capitalize()}Router'
        output_lines.append(f'# {module}模块路由器')
        output_lines.append(f'{router_name} = APIRouter(')
        output_lines.append(f'    route_class=OperationLogRoute,')
        output_lines.append(f'    prefix="/{module}",')
        output_lines.append(f'    tags=["{module}管理"]')
        output_lines.append(')')
        output_lines.append('')
    
    # 添加路由函数
    for func_content in functions:
        output_lines.append(func_content)
        output_lines.append('')  # 空行分隔
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"写入 {output_path} ({len(functions)} 个路由函数)")

print("分割完成！")
