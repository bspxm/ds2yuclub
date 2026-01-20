#!/usr/bin/env python3
"""
修复模块文件中的语法错误

主要问题：字面字符串 '\n'（两个字符：反斜杠和n）出现在代码中，
导致Python解释为续行符，引发语法错误。
"""

import os
import re
from pathlib import Path

def fix_file(filepath: Path):
    """修复单个文件中的语法错误"""
    if not filepath.exists():
        print(f"文件不存在: {filepath}")
        return False
    
    # 读取文件内容（二进制模式）
    with open(filepath, 'rb') as f:
        content_bytes = f.read()
    
    # 将字面 \n（两个字符：0x5C 0x6E）替换为换行符（0x0A）
    # 注意：我们只替换不在其他转义序列中的 \n
    # 但简单起见，替换所有 \n 序列
    original_len = len(content_bytes)
    
    # 先替换 \n 为换行符
    new_content = content_bytes.replace(b'\\n', b'\n')
    
    # 如果内容有变化，写入文件
    if new_content != content_bytes:
        # 备份原文件
        backup_path = filepath.with_suffix(filepath.suffix + '.backup')
        with open(backup_path, 'wb') as f:
            f.write(content_bytes)
        
        # 写入修复后的内容
        with open(filepath, 'wb') as f:
            f.write(new_content)
        
        print(f"修复 {filepath}: 替换了 {original_len - len(new_content)} 个字节")
        return True
    else:
        print(f"无需修复 {filepath}")
        return False

def fix_all_modules():
    """修复所有模块文件"""
    base_dir = Path(__file__).parent
    module_dir = base_dir / "app" / "plugin" / "module_badminton"
    
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
    
    file_types = ['service.py', 'schema.py', 'crud.py', 'controller.py']
    
    print("开始修复语法错误...")
    
    fixed_count = 0
    for module in modules:
        module_path = module_dir / module
        if not module_path.exists():
            print(f"警告：模块目录不存在 {module_path}")
            continue
        
        print(f"\n处理模块: {module}")
        for file_type in file_types:
            file_path = module_path / file_type
            if file_path.exists():
                if fix_file(file_path):
                    fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")
    
    # 也修复主入口文件
    print("\n检查主入口文件...")
    main_files = [
        module_dir / "controller.py",
        module_dir / "crud.py",
        module_dir / "schema.py",
        module_dir / "service.py"
    ]
    
    for main_file in main_files:
        if main_file.exists():
            fix_file(main_file)
    
    return fixed_count

if __name__ == '__main__':
    fix_all_modules()