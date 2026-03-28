import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats


class HeightStatistics:
    """身高统计分析类"""

    # 全国青少年平均身高参考值（cm）
    NATIONAL_AVERAGE = {
        '高一': {'男': 170.0, '女': 160.0},
        '高二': {'男': 172.0, '女': 161.0},
        '高三': {'男': 173.0, '女': 162.0}
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.results = {}

    def basic_statistics(self) -> Dict:
        """基础统计指标"""
        if self.df.empty:
            return {}

        heights = self.df['height']
        
        valid_heights = heights[heights.notna() & np.isfinite(heights)]
        
        if valid_heights.empty:
            return {}

        stats_dict = {
            'count': len(valid_heights),
            'mean': round(valid_heights.mean(), 2),
            'median': round(valid_heights.median(), 2),
            'mode': round(valid_heights.mode().iloc[0], 2) if not valid_heights.mode().empty else None,
            'std': round(valid_heights.std(), 2),
            'var': round(valid_heights.var(), 2),
            'min': round(valid_heights.min(), 2),
            'max': round(valid_heights.max(), 2),
            'range': round(valid_heights.max() - valid_heights.min(), 2),
            'q1': round(valid_heights.quantile(0.25), 2),
            'q3': round(valid_heights.quantile(0.75), 2),
            'iqr': round(valid_heights.quantile(0.75) - valid_heights.quantile(0.25), 2)
        }

        return stats_dict

    def distribution_by_intervals(self, intervals: List[Tuple[float, float]] = None) -> pd.DataFrame:
        """按身高区间统计分布"""
        if self.df.empty:
            return pd.DataFrame()

        if intervals is None:
            intervals = [
                (0, 150), (150, 155), (155, 160), (160, 165),
                (165, 170), (170, 175), (175, 180), (180, 185), (185, 200)
            ]

        distribution = []
        for min_h, max_h in intervals:
            count = len(self.df[(self.df['height'] >= min_h) & (self.df['height'] < max_h)])
            percentage = round(count / len(self.df) * 100, 2) if len(self.df) > 0 else 0
            distribution.append({
                'interval': f'{min_h}-{max_h}cm',
                'count': count,
                'percentage': percentage
            })

        return pd.DataFrame(distribution)

    def group_by_gender(self) -> pd.DataFrame:
        """按性别分组统计"""
        if self.df.empty:
            return pd.DataFrame()

        gender_stats = self.df.groupby('gender')['height'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).round(2)

        return gender_stats.reset_index()

    def group_by_grade(self) -> pd.DataFrame:
        """按年级分组统计"""
        if self.df.empty:
            return pd.DataFrame()

        grade_stats = self.df.groupby('grade')['height'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).round(2)

        grade_order = ['高一', '高二', '高三']
        grade_stats = grade_stats.reindex([g for g in grade_order if g in grade_stats.index])

        return grade_stats.reset_index()

    def group_by_class(self) -> pd.DataFrame:
        """按班级分组统计"""
        if self.df.empty:
            return pd.DataFrame()

        class_stats = self.df.groupby(['grade', 'class'])['height'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std')
        ]).round(2)

        return class_stats.reset_index()

    def cross_group_analysis(self) -> pd.DataFrame:
        """交叉分组统计（年级+性别）"""
        if self.df.empty:
            return pd.DataFrame()

        cross_stats = self.df.groupby(['grade', 'gender'])['height'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).round(2)

        return cross_stats.reset_index()

    def trend_analysis(self) -> pd.DataFrame:
        """年级身高趋势分析"""
        if self.df.empty:
            return pd.DataFrame()

        trend_data = []
        for grade in ['高一', '高二', '高三']:
            grade_df = self.df[self.df['grade'] == grade]
            if not grade_df.empty:
                trend_data.append({
                    'grade': grade,
                    'mean_height': round(grade_df['height'].mean(), 2),
                    'median_height': round(grade_df['height'].median(), 2),
                    'count': len(grade_df)
                })

        return pd.DataFrame(trend_data)

    def gender_difference_analysis(self) -> Dict:
        """男女生身高差异分析"""
        if self.df.empty:
            return {}

        male_df = self.df[self.df['gender'] == '男']
        female_df = self.df[self.df['gender'] == '女']

        if male_df.empty or female_df.empty:
            return {'error': '缺少男生或女生数据'}

        male_heights = male_df['height']
        female_heights = female_df['height']

        t_stat, p_value = stats.ttest_ind(male_heights, female_heights)

        result = {
            'male_count': len(male_heights),
            'female_count': len(female_heights),
            'male_mean': round(male_heights.mean(), 2),
            'female_mean': round(female_heights.mean(), 2),
            'mean_difference': round(male_heights.mean() - female_heights.mean(), 2),
            't_statistic': round(t_stat, 4),
            'p_value': round(p_value, 4),
            'significant': p_value < 0.05
        }

        return result

    def compare_with_national(self) -> pd.DataFrame:
        """与全国平均值对比"""
        if self.df.empty:
            return pd.DataFrame()

        comparison_data = []

        for grade in ['高一', '高二', '高三']:
            for gender in ['男', '女']:
                subset = self.df[(self.df['grade'] == grade) & (self.df['gender'] == gender)]
                if not subset.empty:
                    actual_mean = subset['height'].mean()
                    national_mean = self.NATIONAL_AVERAGE.get(grade, {}).get(gender, 0)
                    difference = actual_mean - national_mean

                    comparison_data.append({
                        'grade': grade,
                        'gender': gender,
                        'sample_count': len(subset),
                        'actual_mean': round(actual_mean, 2),
                        'national_mean': national_mean,
                        'difference': round(difference, 2),
                        'difference_percent': round(difference / national_mean * 100, 2) if national_mean > 0 else 0
                    })

        return pd.DataFrame(comparison_data)

    def outliers_analysis(self, method: str = 'iqr') -> pd.DataFrame:
        """异常值分析"""
        if self.df.empty:
            return pd.DataFrame()

        if method == 'iqr':
            Q1 = self.df['height'].quantile(0.25)
            Q3 = self.df['height'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
        else:
            mean = self.df['height'].mean()
            std = self.df['height'].std()
            lower_bound = mean - 3 * std
            upper_bound = mean + 3 * std

        outliers = self.df[(self.df['height'] < lower_bound) | (self.df['height'] > upper_bound)]

        return outliers.copy()

    def generate_full_report(self) -> Dict:
        """生成完整统计报告"""
        report = {
            'basic_stats': self.basic_statistics(),
            'distribution': self.distribution_by_intervals(),
            'by_gender': self.group_by_gender(),
            'by_grade': self.group_by_grade(),
            'cross_analysis': self.cross_group_analysis(),
            'trend': self.trend_analysis(),
            'gender_diff': self.gender_difference_analysis(),
            'national_comparison': self.compare_with_national(),
            'outliers': self.outliers_analysis()
        }
        return report

    def export_report_to_text(self, file_path: str):
        """导出文本格式报告"""
        report = self.generate_full_report()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("高中学生身高情况统计分析报告\n")
            f.write("=" * 60 + "\n\n")

            f.write("【一、基础统计指标】\n")
            for key, value in report['basic_stats'].items():
                f.write(f"  {key}: {value}\n")

            f.write("\n【二、身高区间分布】\n")
            f.write(report['distribution'].to_string(index=False))

            f.write("\n\n【三、按性别统计】\n")
            f.write(report['by_gender'].to_string(index=False))

            f.write("\n\n【四、按年级统计】\n")
            f.write(report['by_grade'].to_string(index=False))

            f.write("\n\n【五、性别差异分析】\n")
            for key, value in report['gender_diff'].items():
                f.write(f"  {key}: {value}\n")

            f.write("\n【六、与全国平均值对比】\n")
            f.write(report['national_comparison'].to_string(index=False))

            if not report['outliers'].empty:
                f.write("\n\n【七、异常值】\n")
                f.write(report['outliers'].to_string(index=False))
