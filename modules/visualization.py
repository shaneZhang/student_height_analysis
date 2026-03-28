import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
import os
import platform

# 设置中文字体 - 根据操作系统选择合适字体
def setup_chinese_font():
    """配置中文字体"""
    import matplotlib.font_manager as fm

    system = platform.system()

    # 尝试设置中文字体
    if system == 'Darwin':  # macOS
        # 尝试使用系统自带的中文字体
        chinese_fonts = ['STHeiti', 'Heiti TC', 'PingFang SC', 'Arial Unicode MS']
    elif system == 'Windows':
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    else:  # Linux
        chinese_fonts = ['WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']

    # 检查字体是否可用
    available_fonts = []
    for font in chinese_fonts:
        try:
            # 尝试查找字体
            font_path = fm.findfont(fm.FontProperties(family=font))
            if font_path and 'DejaVuSans' not in font_path:
                available_fonts.append(font)
        except:
            pass

    if available_fonts:
        plt.rcParams['font.sans-serif'] = available_fonts + ['DejaVu Sans']
        print(f"已设置中文字体: {available_fonts[0]}")
    else:
        # 如果没有找到中文字体，使用备用方案
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        print("警告: 未找到中文字体，图表中的中文可能显示为方框")

    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 初始化字体设置
setup_chinese_font()


class HeightVisualizer:
    """身高数据可视化类"""

    def __init__(self, df: pd.DataFrame, output_dir: str = 'reports'):
        self.df = df.copy()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_height_distribution_histogram(self, save_path: Optional[str] = None,
                                           show_plot: bool = False) -> str:
        """身高分布直方图"""
        if self.df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        heights = self.df['height']
        ax.hist(heights, bins=20, edgecolor='black', alpha=0.7, color='steelblue')

        ax.axvline(heights.mean(), color='red', linestyle='--', linewidth=2, label=f'平均值: {heights.mean():.1f}cm')
        ax.axvline(heights.median(), color='green', linestyle='--', linewidth=2, label=f'中位数: {heights.median():.1f}cm')

        ax.set_xlabel('身高 (cm)', fontsize=12)
        ax.set_ylabel('人数', fontsize=12)
        ax.set_title('学生身高分布直方图', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path is None:
            save_path = os.path.join(self.output_dir, 'height_distribution_histogram.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def plot_gender_comparison_boxplot(self, save_path: Optional[str] = None,
                                       show_plot: bool = False) -> str:
        """男女生身高对比箱线图"""
        if self.df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(8, 6))

        male_data = self.df[self.df['gender'] == '男']['height']
        female_data = self.df[self.df['gender'] == '女']['height']

        box_data = [male_data, female_data]
        labels = ['男生', '女生']

        bp = ax.boxplot(box_data, labels=labels, patch_artist=True)

        colors = ['lightblue', 'lightpink']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        ax.set_ylabel('身高 (cm)', fontsize=12)
        ax.set_title('男女生身高对比箱线图', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # 添加统计信息
        for i, data in enumerate(box_data):
            if not data.empty:
                ax.text(i + 1, data.max() + 1, f'n={len(data)}\n均值={data.mean():.1f}',
                        ha='center', fontsize=10)

        if save_path is None:
            save_path = os.path.join(self.output_dir, 'gender_comparison_boxplot.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def plot_grade_trend(self, save_path: Optional[str] = None,
                         show_plot: bool = False) -> str:
        """各年级平均身高趋势图"""
        if self.df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        grade_order = ['高一', '高二', '高三']
        grade_means = []
        grade_labels = []

        for grade in grade_order:
            grade_df = self.df[self.df['grade'] == grade]
            if not grade_df.empty:
                grade_means.append(grade_df['height'].mean())
                grade_labels.append(grade)

        if not grade_means:
            return ""

        ax.plot(grade_labels, grade_means, marker='o', linewidth=2, markersize=8, color='steelblue')

        for i, (label, mean) in enumerate(zip(grade_labels, grade_means)):
            ax.text(i, mean + 0.5, f'{mean:.1f}cm', ha='center', fontsize=10)

        ax.set_xlabel('年级', fontsize=12)
        ax.set_ylabel('平均身高 (cm)', fontsize=12)
        ax.set_title('各年级平均身高趋势图', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        if save_path is None:
            save_path = os.path.join(self.output_dir, 'grade_trend.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def plot_height_distribution_pie(self, save_path: Optional[str] = None,
                                     show_plot: bool = False) -> str:
        """身高分布饼图"""
        if self.df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(10, 8))

        intervals = [
            (0, 150), (150, 155), (155, 160), (160, 165),
            (165, 170), (170, 175), (175, 180), (180, 185), (185, 200)
        ]

        labels = []
        sizes = []
        colors = plt.cm.Set3(np.linspace(0, 1, len(intervals)))

        for i, (min_h, max_h) in enumerate(intervals):
            count = len(self.df[(self.df['height'] >= min_h) & (self.df['height'] < max_h)])
            if count > 0:
                labels.append(f'{min_h}-{max_h}cm')
                sizes.append(count)

        if not sizes:
            return ""

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors[:len(sizes)], startangle=90)

        ax.set_title('身高分布比例图', fontsize=14, fontweight='bold')

        if save_path is None:
            save_path = os.path.join(self.output_dir, 'height_distribution_pie.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def plot_gender_grade_heatmap(self, save_path: Optional[str] = None,
                                  show_plot: bool = False) -> str:
        """性别-年级身高热力图"""
        if self.df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(8, 6))

        pivot_table = self.df.pivot_table(values='height', index='gender',
                                          columns='grade', aggfunc='mean')

        # 确保列的顺序
        grade_order = ['高一', '高二', '高三']
        pivot_table = pivot_table.reindex(columns=[g for g in grade_order if g in pivot_table.columns])

        im = ax.imshow(pivot_table.values, cmap='YlOrRd', aspect='auto')

        ax.set_xticks(np.arange(len(pivot_table.columns)))
        ax.set_yticks(np.arange(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.columns)
        ax.set_yticklabels(pivot_table.index)

        # 在每个格子中显示数值
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                value = pivot_table.iloc[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.1f}', ha='center', va='center', fontsize=12)

        ax.set_xlabel('年级', fontsize=12)
        ax.set_ylabel('性别', fontsize=12)
        ax.set_title('各年级男女生平均身高热力图', fontsize=14, fontweight='bold')

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('平均身高 (cm)', fontsize=10)

        if save_path is None:
            save_path = os.path.join(self.output_dir, 'gender_grade_heatmap.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def plot_class_comparison(self, grade: Optional[str] = None,
                              save_path: Optional[str] = None,
                              show_plot: bool = False) -> str:
        """班级身高对比图"""
        if self.df.empty:
            return ""

        df_filtered = self.df.copy()
        if grade:
            df_filtered = df_filtered[df_filtered['grade'] == grade]

        if df_filtered.empty:
            return ""

        fig, ax = plt.subplots(figsize=(12, 6))

        class_stats = df_filtered.groupby(['grade', 'class'])['height'].mean().reset_index()
        class_stats['label'] = class_stats['grade'] + class_stats['class'].astype(str) + '班'

        bars = ax.bar(range(len(class_stats)), class_stats['height'], color='steelblue', alpha=0.7)

        ax.set_xticks(range(len(class_stats)))
        ax.set_xticklabels(class_stats['label'], rotation=45, ha='right')
        ax.set_ylabel('平均身高 (cm)', fontsize=12)
        ax.set_title(f'{grade if grade else "全校"}各班平均身高对比', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # 在柱子上显示数值
        for i, (bar, height) in enumerate(zip(bars, class_stats['height'])):
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f'{height:.1f}', ha='center', fontsize=9)

        if save_path is None:
            grade_str = grade if grade else 'all'
            save_path = os.path.join(self.output_dir, f'class_comparison_{grade_str}.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def plot_national_comparison(self, save_path: Optional[str] = None,
                                 show_plot: bool = False) -> str:
        """与全国平均值对比图"""
        if self.df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(12, 6))

        national_avg = {
            '高一': {'男': 170.0, '女': 160.0},
            '高二': {'男': 172.0, '女': 161.0},
            '高三': {'男': 173.0, '女': 162.0}
        }

        x_labels = []
        actual_means = []
        national_means = []

        for grade in ['高一', '高二', '高三']:
            for gender in ['男', '女']:
                subset = self.df[(self.df['grade'] == grade) & (self.df['gender'] == gender)]
                if not subset.empty:
                    x_labels.append(f'{grade}\n{gender}')
                    actual_means.append(subset['height'].mean())
                    national_means.append(national_avg[grade][gender])

        if not actual_means:
            return ""

        x = np.arange(len(x_labels))
        width = 0.35

        bars1 = ax.bar(x - width/2, actual_means, width, label='本校平均', color='steelblue', alpha=0.8)
        bars2 = ax.bar(x + width/2, national_means, width, label='全国平均', color='orange', alpha=0.8)

        ax.set_ylabel('身高 (cm)', fontsize=12)
        ax.set_title('本校与全国平均身高对比', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                        f'{height:.1f}', ha='center', fontsize=9)

        if save_path is None:
            save_path = os.path.join(self.output_dir, 'national_comparison.png')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close()

        return save_path

    def generate_all_visualizations(self) -> List[str]:
        """生成所有可视化图表"""
        generated_files = []

        if not self.df.empty:
            files = [
                self.plot_height_distribution_histogram(),
                self.plot_gender_comparison_boxplot(),
                self.plot_grade_trend(),
                self.plot_height_distribution_pie(),
                self.plot_gender_grade_heatmap(),
                self.plot_class_comparison(),
                self.plot_national_comparison()
            ]
            generated_files = [f for f in files if f]

        return generated_files
