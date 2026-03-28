#!/usr/bin/env python3
"""
检查系统中可用的中文字体
"""

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# 列出所有可用字体
fonts = fm.findSystemFonts()
print(f"系统共有 {len(fonts)} 个字体")

# 查找包含中文的字体
chinese_fonts = []
for font in fonts:
    try:
        prop = fm.FontProperties(fname=font)
        name = prop.get_name()
        # 检查字体是否支持中文
        if any(keyword in font.lower() for keyword in ['hei', 'song', 'kai', 'fang', 'ming', 'yuanti', 'pingfang', 'heiti', 'st', 'wqy', 'noto', 'cjk']):
            chinese_fonts.append((font, name))
    except:
        pass

print(f"\n找到 {len(chinese_fonts)} 个可能支持中文的字体:")
for font_path, font_name in chinese_fonts[:20]:  # 只显示前20个
    print(f"  - {font_name}: {font_path}")

# 测试几个常见中文字体
test_fonts = ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'SimHei', 'STHeiti', 'WenQuanYi Micro Hei']
print("\n测试字体可用性:")
for font in test_fonts:
    try:
        plt.rcParams['font.sans-serif'] = [font]
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, '中文测试', fontsize=20, ha='center', transform=ax.transAxes)
        ax.axis('off')
        plt.savefig(f'reports/test_{font.replace(" ", "_")}.png', dpi=100)
        plt.close()
        print(f"  ✓ {font}: 可用")
    except Exception as e:
        print(f"  ✗ {font}: 不可用 - {e}")

print("\n测试图已保存到 reports/ 目录")
