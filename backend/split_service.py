#!/usr/bin/env python3
"""
拆分service.py到各个模块
"""

import os
import re
from pathlib import Path

# 项目根目录
base_dir = Path(__file__).parent
module_dir = base_dir / "app" / "plugin" / "module_badminton"

# 读取原始service.py
service_file = module_dir / "service.py"
with open(service_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 模块映射
module_map = {
    'StudentService': 'student',
    'ParentStudentService': 'student',
    'AbilityAssessmentService': 'student',
    'TournamentService': 'tournament',
    'CourseService': 'course',
    'LeaveRequestService': 'leave',
    'SemesterService': 'semester',
    'ClassService': 'class_',
    'PurchaseService': 'purchase',
    'ClassAttendanceService': 'attendance',
    'ClassScheduleService': 'schedule',
}

# 通用服务类（保留在主文件中）
common_services = {'BaseBadmintonService'}

# 提取导入部分（文件开头直到第一个类定义或# =）
import_section_match = re.search(r'^.*?(?=class \w+Service|# =+=)', content, re.DOTALL)
import_section = import_section_match.group(0) if import_section_match else ''

# 分割各个类定义
# 查找所有服务类定义
class_pattern = r'^(# =+[^=]+=+\s*)?class (\w+Service)'
class_matches = list(re.finditer(class_pattern, content, re.MULTILINE))

# 为每个模块准复内容
module_contents = {module: [] for module in set(module_map.values())}
module_contents['main'] = []  # 主文件保留通用服务类

# 遍历每个类
for i, match in enumerate(class_matches):
    class_name = match.group(2)
    # 找到类定义的开始和结束
    start_pos = match.start()
    if i + 1 < len(class_matches):
        end_pos = class_matches[i + 1].start()
    else:
        end_pos = len(content)
    
    class_content = content[start_pos:end_pos].rstrip()
    
    # 确定模块
    target_module = None
    for prefix, module in module_map.items():
        if class_name == prefix:
            target_module = module
            break
    
    if class_name in common_services:
        target_module = 'main'
    
    if target_module is None:
        # 未映射的类，保留在主文件中
        target_module = 'main'
    
    module_contents[target_module].append(class_content)

# 写入各个模块的service.py
for module, classes in module_contents.items():
    if not classes:
        continue
    
    if module == 'main':
        # 主service.py，保留导入和所有通用服务类
        output_path = module_dir / "service.py"
        # 先备份原文件
        backup_path = module_dir / "service.py.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\u5907份\u539f\u6587\u4ef6\u5230 {backup_path}")
    else:
        # 模块文件
        module_path = module_dir / module
        if not module_path.exists():
            module_path.mkdir(exist_ok=True)
        output_path = module_path / "service.py"
    
    # 构建输出内容
    output_lines = []
    
    if module == 'main':
        # 主文件保留所有导入
        output_lines.append(import_section)
    else:
        # 模块文件需要适当的导入
        output_lines.append('"""')
        output_lines.append(f'{module}\u6a21\u5757 - Service\u670d\u52a1\u5c42')
        output_lines.append('"""')
        output_lines.append('')
        output_lines.append('from datetime import date, datetime, timedelta')
        output_lines.append('from typing import Optional, List, Dict, Any')
        output_lines.append('')
        output_lines.append('from sqlalchemy.orm import Session')
        output_lines.append('')
        output_lines.append('from app.api.v1.module_system.auth.service import UserService')
        output_lines.append('from app.core.base_crud import BaseCRUD')
        output_lines.append('from app.core.database import SessionDep')
        output_lines.append('from app.core.exceptions import CustomException')
        output_lines.append('from app.core.logger import logger')
        output_lines.append('')
        # 导入本模块的model、crud、schema
        output_lines.append(f'from .model import *')
        output_lines.append(f'from .crud import *')
        output_lines.append(f'from .schema import *')
        output_lines.append('')
        # 导入其他模块的服务（可能需要的依赖）
        # 这里可以根据类内容添加需要的导入
        # 例如：from ..purchase.service import PurchaseService
        # 我们暂时不添加，稍后手动调整
    
    # 添加类定义
    for class_content in classes:
        output_lines.append(class_content)
        output_lines.append('')  # 空行分隔
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\\n'.join(output_lines))
    
    print(f"\u5199\u5165 {output_path} ({len(classes)} \u4e2a\u670d\u52a1\u7c7b)")

print("\u62c6\u5206\u5b8c\u6210\uff01")
