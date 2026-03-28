#!/usr/bin/env python3
"""
测试可视化功能，验证中文显示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_model import DataStore
from modules.visualization import HeightVisualizer
import pandas as pd

# 创建测试数据
test_data = pd.DataFrame({
    'student_id': [f'202301{i:04d}' for i in range(1, 101)],
    'name': ['张三', '李四', '王五', '赵六', '钱七'] * 20,
    'gender': ['男', '女'] * 50,
    'grade': ['高一'] * 33 + ['高二'] * 34 + ['高三'] * 33,
    'class': list(range(1, 11)) * 10,
    'height': [170 + i % 20 for i in range(100)],
    'measure_date': ['2024-03-15'] * 100
})

# 保存测试数据
test_data.to_csv('data/test_data.csv', index=False)
print("✓ 测试数据已创建")

# 创建可视化器
visualizer = HeightVisualizer(test_data)

# 生成所有图表
print("\n开始生成图表...")
files = visualizer.generate_all_visualizations()

print(f"\n✓ 成功生成 {len(files)} 个图表:")
for f in files:
    print(f"  - {f}")

print("\n请打开 reports/ 目录下的图片文件，检查中文是否显示正常")
