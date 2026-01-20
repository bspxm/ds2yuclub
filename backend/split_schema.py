#!/usr/bin/env python3
"""
拆分schema.py到各个模块
"""

import os
import re
from pathlib import Path

# 项目根目录
base_dir = Path(__file__).parent
module_dir = base_dir / "app" / "plugin" / "module_badminton"

# 读取原始schema.py
schema_file = module_dir / "schema.py"
with open(schema_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 模块映射
module_map = {
    'Student': 'student',
    'ParentStudent': 'student',
    'AbilityAssessment': 'student',
    'Tournament': 'tournament',
    'Course': 'course',
    'LeaveRequest': 'leave',
    'Semester': 'semester',
    'Class': 'class_',
    'Purchase': 'purchase',
    'ClassAttendance': 'attendance',
    'ClassSchedule': 'schedule',
}

# 通用模型（保留在主文件中）
common_models = {'SimpleResponse', 'PaginatedResponse'}

# 提取导入部分（文件开头直到第一个# =）
import_section_match = re.search(r'^.*?(?=# =+=)', content, re.DOTALL)
import_section = import_section_match.group(0) if import_section_match else ''

# 分割各个类定义
# 查找所有类定义
class_pattern = r'^(# =+[^=]+=+\s*)?class (\w+)'
class_matches = list(re.finditer(class_pattern, content, re.MULTILINE))

# 为每个模块准备内容
module_contents = {module: [] for module in set(module_map.values())}
module_contents['main'] = []  # 主文件保留通用模型

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
        if class_name.startswith(prefix):
            target_module = module
            break
    
    if class_name in common_models:
        target_module = 'main'
    
    if target_module is None:
        # 未映射的类，保留在主文件中
        target_module = 'main'
    
    module_contents[target_module].append(class_content)

# 写入各个模块的schema.py
for module, classes in module_contents.items():
    if not classes:
        continue
    
    if module == 'main':
        # 主schema.py，保留导入和所有通用模型
        output_path = module_dir / "schema.py"
        # 先备份原文件
        backup_path = module_dir / "schema.py.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"备份原文件到 {backup_path}")
    else:
        # 模块文件
        module_path = module_dir / module
        if not module_path.exists():
            module_path.mkdir(exist_ok=True)
        output_path = module_path / "schema.py"
    
    # 构建输出内容
    output_lines = []
    
    if module == 'main':
        # 主文件保留所有导入
        output_lines.append(import_section)
    else:
        # 模块文件需要简化导入
        # 提取必要的导入
        output_lines.append('"""')
        output_lines.append(f'{module}模块 - Schema定义')
        output_lines.append('"""')
        output_lines.append('')
        output_lines.append('from datetime import date, datetime, time')
        output_lines.append('from typing import Optional')
        output_lines.append('')
        output_lines.append('from fastapi import Query')
        output_lines.append('from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer')
        output_lines.append('')
        output_lines.append('from app.api.v1.module_system.user.schema import UserOutSchema')
        output_lines.append('from app.core.base_schema import BaseSchema, UserBySchema')
        output_lines.append('from app.core.validator import DateStr, DateTimeStr, TimeStr')
        output_lines.append('')
        # 导入枚举
        output_lines.append(f'from ..enums import (')
        # 需要根据类确定需要哪些枚举
        enums_needed = set()
        for class_content in classes:
            # 简单检测枚举使用
            if 'GenderEnum' in class_content:
                enums_needed.add('GenderEnum')
            if 'HandednessEnum' in class_content:
                enums_needed.add('HandednessEnum')
            if 'RelationTypeEnum' in class_content:
                enums_needed.add('RelationTypeEnum')
            # 更多枚举...
        if enums_needed:
            output_lines.append(', '.join(sorted(enums_needed)))
        output_lines.append(')')
        output_lines.append('')
    
    # 添加类定义
    for class_content in classes:
        output_lines.append(class_content)
        output_lines.append('')  # 空行分隔
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"写入 {output_path} ({len(classes)} 个类)")

print("拆分完成！")