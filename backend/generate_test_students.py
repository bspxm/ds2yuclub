#!/usr/bin/env python3
"""
生成10个虚拟学员测试数据Excel文件
用于测试批量导入功能

使用方式:
cd backend
.venv/bin/python generate_test_students.py
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_test_data():
    """生成测试学员数据"""
    
    # 姓名池
    chinese_family_names = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
    chinese_male_names = ["明", "强", "伟", "杰", "超", "浩", "宇", "峰", "鑫", "鹏"]
    chinese_female_names = ["婷", "芳", "敏", "丽", "娜", "静", "雨", "雪", "琳", "媛"]
    english_names = ["Tom", "Jerry", "Mike", "John", "David", "Emma", "Lucy", "Lily", "Amy", "Anna"]
    
    # 组别和校区
    groups = ["初级组", "中级组", "高级组", "精英组", "竞赛组"]
    campuses = ["东校区", "西校区", "南校区", "北校区", "中心校区"]
    levels = ["初学者", "入门级", "进阶级", "熟练级", "专业级"]
    
    # 生成10个学员数据
    data = []
    for i in range(1, 11):
        # 随机性别
        is_male = random.choice([True, False])
        
        # 姓名
        family_name = random.choice(chinese_family_names)
        if is_male:
            given_name = random.choice(chinese_male_names)
            gender = "男"
        else:
            given_name = random.choice(chinese_female_names)
            gender = "女"
        full_name = f"{family_name}{given_name}"
        
        # 英文名
        english_name = random.choice(english_names)
        
        # 出生日期 (8-15岁之间)
        age = random.randint(8, 15)
        birth_date = (datetime.now() - timedelta(days=age*365 + random.randint(0, 365))).strftime("%Y-%m-%d")
        
        # 身高体重 (根据年龄和性别生成合理数据)
        if is_male:
            height = round(random.uniform(130.0, 175.0), 1)
            weight = round(height * 0.3 + random.uniform(-5, 5), 1)
        else:
            height = round(random.uniform(125.0, 165.0), 1)
            weight = round(height * 0.28 + random.uniform(-5, 5), 1)
        
        # 惯用手
        handedness = random.choice(["右手", "左手", "双手"])
        
        # 入训日期 (1个月到3年之间)
        join_days = random.randint(30, 3*365)
        join_date = (datetime.now() - timedelta(days=join_days)).strftime("%Y-%m-%d")
        
        # 技术水平
        level = random.choice(levels)
        
        # 组别和校区
        group_name = random.choice(groups)
        campus = random.choice(campuses)
        
        # 紧急联系人
        emergency_contact = random.choice(["父亲", "母亲", "叔叔", "阿姨"])
        emergency_phone = f"13{random.randint(100000000, 999999999)}"
        
        # 备注
        description = random.choice([
            "热爱羽毛球运动",
            "训练认真刻苦",
            "协调性好",
            "反应速度快",
            "有比赛经验",
            "需要加强力量训练",
            "技术全面",
            "进步明显",
            "有团队合作精神",
            "目标明确"
        ])
        
        # 添加记录
        data.append({
            "姓名": full_name,
            "英文名": english_name,
            "性别": gender,
            "出生日期": birth_date,
            "身高(cm)": height,
            "体重(kg)": weight,
            "惯用手": handedness,
            "入训日期": join_date,
            "技术水平": level,
            "所属组别": group_name,
            "所属校区": campus,
            "紧急联系人": emergency_contact,
            "紧急电话": emergency_phone,
            "备注": description
        })
    
    return data

def main():
    """主函数"""
    print("正在生成10个虚拟学员测试数据...")
    
    # 生成数据
    students = generate_test_data()
    
    # 创建DataFrame
    df = pd.DataFrame(students)
    
    # 保存Excel文件
    output_file = "test_students_import.xlsx"
    df.to_excel(output_file, index=False)
    
    print(f"✅ 已生成测试数据文件: {output_file}")
    print(f"📊 数据量: {len(students)} 条记录")
    print(f"📋 列名: {', '.join(df.columns.tolist())}")
    print()
    print("学员数据预览:")
    print(df.head(5))
    print()
    print("📝 字段说明:")
    print("  - 必填字段: 姓名, 性别, 入训日期")
    print("  - 性别选项: 男, 女, 未知")
    print("  - 惯用手选项: 右手, 左手, 双手")
    print()
    print("📌 使用说明:")
    print(f"  1. 将此文件上传到学员管理页面的批量导入功能")
    print(f"  2. 文件位置: {os.path.abspath(output_file)}")
    print(f"  3. 或复制文件到所需位置: cp {output_file} /path/to/desired/location/")
    
    # 显示详细数据
    print()
    print("📋 详细数据:")
    for i, student in enumerate(students, 1):
        print(f"\n学员 {i}:")
        for key, value in student.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()