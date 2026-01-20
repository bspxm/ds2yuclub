#!/usr/bin/env python3
"""
拆分crud.py到各个模块
"""

import os
import re
from pathlib import Path

# 项目根目录
base_dir = Path(__file__).parent
module_dir = base_dir / "app" / "plugin" / "module_badminton"

# 读取原始crud.py
crud_file = module_dir / "crud.py"
with open(crud_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 模块映射
module_map = {
    'StudentCRUD': 'student',
    'ParentStudentCRUD': 'student',
    'AbilityAssessmentCRUD': 'student',
    'TournamentCRUD': 'tournament',
    'TournamentParticipantCRUD': 'tournament',
    'CourseCRUD': 'course',
    'LeaveRequestCRUD': 'leave',
    'SemesterCRUD': 'semester',
    'ClassCRUD': 'class_',
    'PurchaseCRUD': 'purchase',
    'ClassAttendanceCRUD': 'attendance',
    'ClassScheduleCRUD': 'schedule',
}

# 通用CRUD类（保留在主文件中）
common_cruds = set()

# 提取导入部分（文件开头直到第一个类定义或# =）
import_section_match = re.search(r'^.*?(?=class \w+CRUD|# =+=)', content, re.DOTALL)
import_section = import_section_match.group(0) if import_section_match else ''

# 分割各个类定义
# 查找所有CRUD类定义
class_pattern = r'^(# =+[^=]+=+\s*)?class (\w+CRUD)'
class_matches = list(re.finditer(class_pattern, content, re.MULTILINE))

# 为每个模块准备内容
module_contents = {module: [] for module in set(module_map.values())}
module_contents['main'] = []  # 主文件保留通用CRUD类

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
    
    if class_name in common_cruds:
        target_module = 'main'
    
    if target_module is None:
        # 未映射的类，保留在主文件中
        target_module = 'main'
    
    module_contents[target_module].append(class_content)

# 写入各个模块的crud.py
for module, classes in module_contents.items():
    if not classes:
        continue
    
    if module == 'main':
        # 主crud.py，保留导入和所有通用CRUD类
        output_path = module_dir / "crud.py"
        # 先备份原文件
        backup_path = module_dir / "crud.py.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"备份原文件到 {backup_path}")
    else:
        # 模块文件
        module_path = module_dir / module
        if not module_path.exists():
            module_path.mkdir(exist_ok=True)
        output_path = module_path / "crud.py"
    
    # 构建输出内容
    output_lines = []
    
    if module == 'main':
        # 主文件保留所有导入
        output_lines.append(import_section)
    else:
        # 模块文件需要适当的导入
        output_lines.append('"""')
        output_lines.append(f'{module}模块 - CRUD数据操作层')
        output_lines.append('"""')
        output_lines.append('')
        output_lines.append('from typing import Optional, List, Dict, Any')
        output_lines.append('')
        output_lines.append('from app.api.v1.module_system.auth.schema import AuthSchema')
        output_lines.append('from app.core.base_crud import BaseCRUD')
        output_lines.append('from app.core.database import SessionDep')
        output_lines.append('')
        # 导入本模块的model
        output_lines.append(f'from .model import *')
        output_lines.append('')
    
    # 添加类定义
    for class_content in classes:
        output_lines.append(class_content)
        output_lines.append('')  # 空行分隔
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"写入 {output_path} ({len(classes)} 个CRUD类)")

print("拆分完成！")
