#!/usr/bin/env python3
"""
修复拆分脚本生成的模块文件中的转义字符问题
"""

import os
import re
from pathlib import Path

# 项目根目录
base_dir = Path(__file__).parent
module_dir = base_dir / "app" / "plugin" / "module_badminton"

# 要修复的模块列表
modules = [
    'student',
    'semester',
    'class_',
    'purchase',
    'attendance',
    'schedule',
    'tournament',
    'course',
    'leave'
]

# 要修复的文件类型
file_types = ['service.py', 'schema.py', 'crud.py', 'controller.py']

def fix_escaped_newlines(content: str) -> str:
    """修复转义的换行符（将字面\n替换为真正的换行符）"""
    # 注意：我们只修复文件开头的转义换行符问题
    # 拆分脚本生成的问题模式：三引号后跟字面\n
    lines = content.split('\n')
    if not lines:
        return content
    
    # 检查并修复第一行
    fixed_lines = []
    for i, line in enumerate(lines):
        if i == 0 and line.startswith('"""\\n'):
            # 修复第一行的转义换行符
            line = line.replace('"""\\n', '"""\n')
        # 修复行中的转义导入语句
        if '\\nfrom ' in line and line.startswith('\\n'):
            # 删除行首的\n
            line = line.lstrip('\\n')
            # 修复行中的其他\n转义
            line = line.replace('\\n', '\n')
            # 如果这一行包含多个语句，需要分割
            if '\n' in line:
                sublines = line.split('\n')
                fixed_lines.extend(sublines)
                continue
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(file_path: Path):
    """修复单个文件"""
    if not file_path.exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有问题
    if '\\nfrom ' in content:
        print(f"修复 {file_path}")
        fixed_content = fix_escaped_newlines(content)
        
        # 备份原文件
        backup_path = file_path.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
    else:
        print(f"跳过 {file_path}（未发现问题）")

def main():
    """主函数"""
    print("开始修复模块文件...")
    
    # 修复每个模块的每个文件
    for module in modules:
        module_path = module_dir / module
        if not module_path.exists():
            print(f"警告：模块目录不存在 {module_path}")
            continue
        
        print(f"\n处理模块: {module}")
        for file_type in file_types:
            file_path = module_path / file_type
            if file_path.exists():
                fix_file(file_path)
    
    print("\n修复完成！")

if __name__ == '__main__':
    main()