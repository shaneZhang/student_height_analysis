#!/usr/bin/env python3
"""
生成示例数据脚本
生成1000条学生身高数据用于测试
"""

import pandas as pd
import random
import numpy as np
from datetime import datetime

# 设置随机种子以便复现
random.seed(42)
np.random.seed(42)

# 姓名库
last_names = [
    '张', '王', '李', '刘', '陈', '杨', '黄', '赵', '周', '吴',
    '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗',
    '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
    '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡',
    '余', '杜', '叶', '程', '苏', '魏', '吕', '丁', '任', '沈'
]

first_names_male = [
    '伟', '强', '磊', '军', '洋', '勇', '杰', '涛', '明', '超',
    '俊', '峰', '建', '辉', '宇', '浩', '博', '文', '斌', '龙',
    '刚', '毅', '林', '斌', '晨', '昊', '瑞', '翔', '凯', '志',
    '鹏', '飞', '鑫', '帅', '云', '天', '宁', '旭', '阳', '锋'
]

first_names_female = [
    '芳', '娜', '敏', '静', '丽', '艳', '娟', '霞', '平', '玲',
    '婷', '雪', '颖', '慧', '秀', '英', '华', '兰', '洁', '倩',
    '欣', '怡', '蓉', '月', '莹', '玲', '琳', '瑶', '媛', '茹',
    '燕', '梅', '莉', '薇', '晶', '晴', '彤', '璐', '菲', '琪'
]


def generate_name(gender):
    """生成姓名"""
    last = random.choice(last_names)
    if gender == '男':
        first = random.choice(first_names_male)
    else:
        first = random.choice(first_names_female)
    return last + first


def generate_height(grade, gender):
    """
    生成身高数据
    基于年级和性别的正态分布
    """
    # 基础身高配置 (均值, 标准差)
    height_config = {
        '高一': {'男': (170.0, 6.5), '女': (160.0, 5.5)},
        '高二': {'男': (172.0, 6.5), '女': (161.0, 5.5)},
        '高三': {'男': (173.0, 6.5), '女': (162.0, 5.5)}
    }

    mean, std = height_config[grade][gender]
    height = np.random.normal(mean, std)

    # 限制在合理范围内
    height = max(145.0, min(195.0, height))
    return round(height, 1)


def generate_student_id(grade, class_num, index):
    """生成学号"""
    grade_code = {'高一': '1', '高二': '2', '高三': '3'}[grade]
    return f"2023{grade_code}{class_num:02d}{index:04d}"


def generate_data(count=1000):
    """生成学生数据"""
    data = []

    grades = ['高一', '高二', '高三']
    genders = ['男', '女']

    # 每个年级约333人，分布到10个班级
    students_per_grade = count // 3

    index = 1
    for grade in grades:
        for _ in range(students_per_grade):
            gender = random.choice(genders)
            class_num = random.randint(1, 10)

            student = {
                'student_id': generate_student_id(grade, class_num, index),
                'name': generate_name(gender),
                'gender': gender,
                'grade': grade,
                'class': class_num,
                'height': generate_height(grade, gender),
                'measure_date': '2024-03-15'
            }
            data.append(student)
            index += 1

    return pd.DataFrame(data)


def main():
    print("正在生成示例数据...")

    # 生成1000条数据
    df = generate_data(1000)

    # 保存为Excel
    excel_path = 'data/sample_students_1000.xlsx'
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f"✓ Excel文件已生成: {excel_path}")

    # 同时保存为CSV
    csv_path = 'data/sample_students_1000.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ CSV文件已生成: {csv_path}")

    # 打印统计信息
    print("\n数据统计:")
    print(f"  总记录数: {len(df)}")
    print(f"  男生: {len(df[df['gender'] == '男'])} 人")
    print(f"  女生: {len(df[df['gender'] == '女'])} 人")
    print(f"\n各年级分布:")
    print(df['grade'].value_counts().sort_index())
    print(f"\n身高统计:")
    print(f"  平均值: {df['height'].mean():.2f} cm")
    print(f"  最小值: {df['height'].min():.1f} cm")
    print(f"  最大值: {df['height'].max():.1f} cm")
    print(f"  标准差: {df['height'].std():.2f} cm")

    print("\n前10条数据预览:")
    print(df.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
