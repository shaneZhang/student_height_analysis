#!/usr/bin/env python3
"""
测试中文显示是否正常
"""

import matplotlib.pyplot as plt
import platform
import os

# 设置中文字体 - 根据操作系统选择合适字体
def setup_chinese_font():
    """配置中文字体"""
    system = platform.system()
    print(f"检测到操作系统: {system}")

    if system == 'Darwin':  # macOS
        fonts = ['Arial Unicode MS', 'Heiti TC', 'PingFang SC', 'STHeiti', 'SimHei']
    elif system == 'Windows':
        fonts = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    else:  # Linux
        fonts = ['WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']

    plt.rcParams['font.sans-serif'] = fonts
    plt.rcParams['axes.unicode_minus'] = False
    print(f"设置字体: {fonts}")

setup_chinese_font()

# 创建测试图
fig, ax = plt.subplots(figsize=(8, 6))

# 测试中文显示
ax.text(0.5, 0.8, '中文显示测试', fontsize=20, ha='center', transform=ax.transAxes)
ax.text(0.5, 0.6, '学生身高统计分析', fontsize=16, ha='center', transform=ax.transAxes)
ax.text(0.5, 0.4, '高一 高二 高三', fontsize=14, ha='center', transform=ax.transAxes)
ax.text(0.5, 0.2, '男生 女生 平均值', fontsize=14, ha='center', transform=ax.transAxes)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# 保存测试图
test_path = 'reports/font_test.png'
os.makedirs('reports', exist_ok=True)
plt.savefig(test_path, dpi=150, bbox_inches='tight')
print(f"\n测试图已保存: {test_path}")
print("请打开图片检查中文是否显示正常")

plt.close()

# 同时测试一个带图表的
fig, ax = plt.subplots(figsize=(8, 6))

categories = ['高一男生', '高一女生', '高二男生', '高二女生', '高三男生', '高三女生']
values = [170, 160, 172, 161, 173, 162]
colors = ['lightblue', 'lightpink'] * 3

bars = ax.bar(categories, values, color=colors)
ax.set_ylabel('平均身高 (cm)', fontsize=12)
ax.set_title('各年级男女生平均身高对比', fontsize=14, fontweight='bold')
ax.tick_params(axis='x', rotation=45)

# 在柱子上添加数值
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val}cm', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
test_chart_path = 'reports/font_test_chart.png'
plt.savefig(test_chart_path, dpi=150, bbox_inches='tight')
print(f"图表测试已保存: {test_chart_path}")

plt.close()
print("\n测试完成！")
