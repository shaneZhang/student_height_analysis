#!/usr/bin/env python3
"""
全量回归测试 - 验证所有功能正常工作
"""

import os
import sys
import tempfile
import shutil
import threading
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_model import DataStore, Student
from modules.data_collector import DataCollector, DataValidator
from modules.statistics import HeightStatistics
from modules.visualization import HeightVisualizer
from modules.data_manager import DataManager

import pandas as pd
import numpy as np


class RegressionTestReport:
    """回归测试报告"""
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add_result(self, test_name, passed, details=""):
        self.tests.append({
            'name': test_name,
            'passed': passed,
            'details': details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def generate_report(self):
        report = []
        report.append("=" * 80)
        report.append("学生身高分析系统 - 全量回归测试报告")
        report.append("=" * 80)
        report.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总测试数: {len(self.tests)}")
        report.append(f"通过: {self.passed}")
        report.append(f"失败: {self.failed}")
        report.append(f"通过率: {self.passed/len(self.tests)*100:.1f}%")

        report.append("\n" + "=" * 80)
        report.append("详细测试结果")
        report.append("=" * 80)

        for i, test in enumerate(self.tests, 1):
            status = "✓ PASS" if test['passed'] else "✗ FAIL"
            report.append(f"\n[{i}] {status}: {test['name']}")
            if test['details']:
                report.append(f"    详情: {test['details']}")

        report.append("\n" + "=" * 80)
        return "\n".join(report)


report = RegressionTestReport()


def run_data_model_tests():
    """数据模型模块测试"""
    print("\n[模块] 数据模型 (data_model)")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: Student类创建
        try:
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            report.add_result("Student类创建", True)
        except Exception as e:
            report.add_result("Student类创建", False, str(e))

        # 测试2: Student.to_dict
        try:
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            d = s.to_dict()
            assert d['student_id'] == '2023010001'
            report.add_result("Student.to_dict", True)
        except Exception as e:
            report.add_result("Student.to_dict", False, str(e))

        # 测试3: Student.from_dict
        try:
            data = {
                'student_id': '2023010002',
                'name': '李四',
                'gender': '女',
                'grade': '高二',
                'class': 2,
                'height': 162.0,
                'measure_date': '2024-03-15'
            }
            s = Student.from_dict(data)
            assert s.student_id == '2023010002'
            report.add_result("Student.from_dict", True)
        except Exception as e:
            report.add_result("Student.from_dict", False, str(e))

        # 测试4: DataStore初始化
        try:
            data_file = os.path.join(temp_dir, 'test1.csv')
            ds = DataStore(data_file)
            assert ds.df is not None
            report.add_result("DataStore初始化", True)
        except Exception as e:
            report.add_result("DataStore初始化", False, str(e))

        # 测试5: DataStore.add_student
        try:
            data_file = os.path.join(temp_dir, 'test2.csv')
            ds = DataStore(data_file)
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            result = ds.add_student(s)
            assert result == True
            assert len(ds.df) == 1
            report.add_result("DataStore.add_student", True)
        except Exception as e:
            report.add_result("DataStore.add_student", False, str(e))

        # 测试6: DataStore.add_student重复学号
        try:
            data_file = os.path.join(temp_dir, 'test3.csv')
            ds = DataStore(data_file)
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            ds.add_student(s)
            result = ds.add_student(s)
            assert result == False  # 应该返回False
            report.add_result("DataStore.add_student重复检测", True)
        except Exception as e:
            report.add_result("DataStore.add_student重复检测", False, str(e))

        # 测试7: DataStore.get_student
        try:
            data_file = os.path.join(temp_dir, 'test4.csv')
            ds = DataStore(data_file)
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            ds.add_student(s)
            result = ds.get_student('2023010001')
            assert result is not None
            assert result['name'] == '张三'
            report.add_result("DataStore.get_student", True)
        except Exception as e:
            report.add_result("DataStore.get_student", False, str(e))

        # 测试8: DataStore.update_student
        try:
            data_file = os.path.join(temp_dir, 'test5.csv')
            ds = DataStore(data_file)
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            ds.add_student(s)
            result = ds.update_student('2023010001', height=180.0)
            assert result == True
            student = ds.get_student('2023010001')
            assert student['height'] == 180.0
            report.add_result("DataStore.update_student", True)
        except Exception as e:
            report.add_result("DataStore.update_student", False, str(e))

        # 测试9: DataStore.delete_student
        try:
            data_file = os.path.join(temp_dir, 'test6.csv')
            ds = DataStore(data_file)
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            ds.add_student(s)
            result = ds.delete_student('2023010001')
            assert result == True
            assert len(ds.df) == 0
            report.add_result("DataStore.delete_student", True)
        except Exception as e:
            report.add_result("DataStore.delete_student", False, str(e))

        # 测试10: DataStore.query
        try:
            data_file = os.path.join(temp_dir, 'test7.csv')
            ds = DataStore(data_file)
            for i in range(5):
                s = Student(f'20230100{i+1:02d}', f'学生{i}', '男' if i % 2 == 0 else '女', '高一', i+1, 170.0+i, '2024-03-15')
                ds.add_student(s)
            result = ds.query(gender='男')
            assert len(result) >= 3
            report.add_result("DataStore.query", True)
        except Exception as e:
            report.add_result("DataStore.query", False, str(e))

        # 测试11: DataStore.clear_data
        try:
            data_file = os.path.join(temp_dir, 'test8.csv')
            ds = DataStore(data_file)
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            ds.add_student(s)
            ds.clear_data()
            assert len(ds.df) == 0
            report.add_result("DataStore.clear_data", True)
        except Exception as e:
            report.add_result("DataStore.clear_data", False, str(e))

        # 测试12: DataStore.import_from_dataframe
        try:
            data_file = os.path.join(temp_dir, 'test9.csv')
            ds = DataStore(data_file)
            df = pd.DataFrame({
                'student_id': ['2023010001', '2023010002'],
                'name': ['张三', '李四'],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, 162.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            success, message = ds.import_from_dataframe(df)
            assert success == True
            assert len(ds.df) == 2
            report.add_result("DataStore.import_from_dataframe", True)
        except Exception as e:
            report.add_result("DataStore.import_from_dataframe", False, str(e))

        # 测试13: DataStore.import_from_dataframe重复学号检测
        try:
            data_file = os.path.join(temp_dir, 'test10.csv')
            ds = DataStore(data_file)
            df = pd.DataFrame({
                'student_id': ['2023010001', '2023010001'],  # 重复学号
                'name': ['张三', '张三重复'],
                'gender': ['男', '男'],
                'grade': ['高一', '高一'],
                'class': [1, 1],
                'height': [175.5, 176.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            success, message = ds.import_from_dataframe(df)
            assert success == False and '重复学号' in message
            report.add_result("DataStore.import_from_dataframe重复检测", True)
        except Exception as e:
            report.add_result("DataStore.import_from_dataframe重复检测", False, str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_data_collector_tests():
    """数据收集模块测试"""
    print("\n[模块] 数据收集 (data_collector)")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: DataValidator.validate_student有效数据
        try:
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')
            is_valid, errors = DataValidator.validate_student(s)
            assert is_valid == True
            report.add_result("DataValidator.validate_student有效数据", True)
        except Exception as e:
            report.add_result("DataValidator.validate_student有效数据", False, str(e))

        # 测试2: DataValidator.validate_student无效性别
        try:
            s = Student('2023010001', '张三', '未知', '高一', 1, 175.5, '2024-03-15')
            is_valid, errors = DataValidator.validate_student(s)
            assert is_valid == False and any('性别' in err for err in errors)
            report.add_result("DataValidator.validate_student无效性别", True)
        except Exception as e:
            report.add_result("DataValidator.validate_student无效性别", False, str(e))

        # 测试3: DataValidator.validate_student无效年级
        try:
            s = Student('2023010001', '张三', '男', '大四', 1, 175.5, '2024-03-15')
            is_valid, errors = DataValidator.validate_student(s)
            assert is_valid == False and any('年级' in err for err in errors)
            report.add_result("DataValidator.validate_student无效年级", True)
        except Exception as e:
            report.add_result("DataValidator.validate_student无效年级", False, str(e))

        # 测试4: DataValidator.validate_student无效身高
        try:
            s = Student('2023010001', '张三', '男', '高一', 1, 250.0, '2024-03-15')
            is_valid, errors = DataValidator.validate_student(s)
            assert is_valid == False and any('身高' in err for err in errors)
            report.add_result("DataValidator.validate_student无效身高", True)
        except Exception as e:
            report.add_result("DataValidator.validate_student无效身高", False, str(e))

        # 测试5: DataValidator.validate_student未来日期
        try:
            future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, future_date)
            is_valid, errors = DataValidator.validate_student(s)
            assert is_valid == False and any('未来' in err for err in errors)
            report.add_result("DataValidator.validate_student未来日期", True)
        except Exception as e:
            report.add_result("DataValidator.validate_student未来日期", False, str(e))

        # 测试6: DataValidator.validate_student极早日期
        try:
            s = Student('2023010001', '张三', '男', '高一', 1, 175.5, '1900-01-01')
            is_valid, errors = DataValidator.validate_student(s)
            assert is_valid == False and any('2000' in err for err in errors)
            report.add_result("DataValidator.validate_student极早日期", True)
        except Exception as e:
            report.add_result("DataValidator.validate_student极早日期", False, str(e))

        # 测试7: DataCollector.add_student_manual
        try:
            data_file = os.path.join(temp_dir, 'collector1.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            success, message = collector.add_student_manual(
                '2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15'
            )
            assert success == True
            report.add_result("DataCollector.add_student_manual", True)
        except Exception as e:
            report.add_result("DataCollector.add_student_manual", False, str(e))

        # 测试8: DataCollector.check_duplicate_ids
        try:
            data_file = os.path.join(temp_dir, 'collector2.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            df = pd.DataFrame({
                'student_id': ['2023010001', '2023010002'],
                'name': ['张三', '李四'],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, 162.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            duplicates = collector.check_duplicate_ids(df)
            assert '2023010001' in duplicates
            report.add_result("DataCollector.check_duplicate_ids", True)
        except Exception as e:
            report.add_result("DataCollector.check_duplicate_ids", False, str(e))

        # 测试9: DataCollector.get_import_template
        try:
            template = DataCollector.get_import_template(DataCollector)
            assert 'student_id' in template.columns
            report.add_result("DataCollector.get_import_template", True)
        except Exception as e:
            report.add_result("DataCollector.get_import_template", False, str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_statistics_tests():
    """统计模块测试"""
    print("\n[模块] 统计分析 (statistics)")

    try:
        # 创建测试数据
        df = pd.DataFrame({
            'student_id': [f'20230100{i:02d}' for i in range(1, 21)],
            'name': [f'学生{i}' for i in range(1, 21)],
            'gender': ['男', '女'] * 10,
            'grade': ['高一'] * 7 + ['高二'] * 7 + ['高三'] * 6,
            'class': list(range(1, 21)),
            'height': [170.0 + i * 0.5 for i in range(20)],
            'measure_date': ['2024-03-15'] * 20
        })

        stats = HeightStatistics(df)

        # 测试1: basic_statistics
        try:
            result = stats.basic_statistics()
            assert 'count' in result
            assert 'mean' in result
            assert 'std' in result
            report.add_result("HeightStatistics.basic_statistics", True)
        except Exception as e:
            report.add_result("HeightStatistics.basic_statistics", False, str(e))

        # 测试2: distribution_by_intervals
        try:
            result = stats.distribution_by_intervals()
            assert len(result) > 0
            report.add_result("HeightStatistics.distribution_by_intervals", True)
        except Exception as e:
            report.add_result("HeightStatistics.distribution_by_intervals", False, str(e))

        # 测试3: group_by_gender
        try:
            result = stats.group_by_gender()
            assert len(result) >= 2
            report.add_result("HeightStatistics.group_by_gender", True)
        except Exception as e:
            report.add_result("HeightStatistics.group_by_gender", False, str(e))

        # 测试4: group_by_grade
        try:
            result = stats.group_by_grade()
            assert len(result) >= 3
            report.add_result("HeightStatistics.group_by_grade", True)
        except Exception as e:
            report.add_result("HeightStatistics.group_by_grade", False, str(e))

        # 测试5: cross_group_analysis
        try:
            result = stats.cross_group_analysis()
            assert len(result) >= 6
            report.add_result("HeightStatistics.cross_group_analysis", True)
        except Exception as e:
            report.add_result("HeightStatistics.cross_group_analysis", False, str(e))

        # 测试6: trend_analysis
        try:
            result = stats.trend_analysis()
            assert len(result) >= 3
            report.add_result("HeightStatistics.trend_analysis", True)
        except Exception as e:
            report.add_result("HeightStatistics.trend_analysis", False, str(e))

        # 测试7: gender_difference_analysis
        try:
            result = stats.gender_difference_analysis()
            assert 'male_mean' in result
            assert 'female_mean' in result
            report.add_result("HeightStatistics.gender_difference_analysis", True)
        except Exception as e:
            report.add_result("HeightStatistics.gender_difference_analysis", False, str(e))

        # 测试8: compare_with_national
        try:
            result = stats.compare_with_national()
            assert len(result) >= 6
            report.add_result("HeightStatistics.compare_with_national", True)
        except Exception as e:
            report.add_result("HeightStatistics.compare_with_national", False, str(e))

        # 测试9: outliers_analysis
        try:
            result = stats.outliers_analysis()
            assert isinstance(result, pd.DataFrame)
            report.add_result("HeightStatistics.outliers_analysis", True)
        except Exception as e:
            report.add_result("HeightStatistics.outliers_analysis", False, str(e))

        # 测试10: Infinity值过滤
        try:
            df_with_inf = pd.DataFrame({
                'student_id': ['INF001', 'INF002'],
                'name': ['张三', '李四'],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, float('inf')],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            stats_inf = HeightStatistics(df_with_inf)
            result = stats_inf.basic_statistics()
            assert result.get('count') == 1
            report.add_result("HeightStatistics.Infinity值过滤", True)
        except Exception as e:
            report.add_result("HeightStatistics.Infinity值过滤", False, str(e))

    except Exception as e:
        print(f"统计模块测试初始化失败: {e}")


def run_data_manager_tests():
    """数据管理模块测试"""
    print("\n[模块] 数据管理 (data_manager)")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: DataManager.query_by_student_id
        try:
            data_file = os.path.join(temp_dir, 'dm1.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            result = dm.query_by_student_id('2023010001')
            assert result is not None
            report.add_result("DataManager.query_by_student_id", True)
        except Exception as e:
            report.add_result("DataManager.query_by_student_id", False, str(e))

        # 测试2: DataManager.query_by_name
        try:
            data_file = os.path.join(temp_dir, 'dm2.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三丰', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            result = dm.query_by_name('张')
            assert len(result) >= 1
            report.add_result("DataManager.query_by_name", True)
        except Exception as e:
            report.add_result("DataManager.query_by_name", False, str(e))

        # 测试3: DataManager.query_by_name正则特殊字符
        try:
            data_file = os.path.join(temp_dir, 'dm3.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            # 测试正则特殊字符不会导致异常
            for char in ['*', '+', '?', '[', '(', '{']:
                result = dm.query_by_name(char)
            report.add_result("DataManager.query_by_name正则特殊字符", True)
        except Exception as e:
            report.add_result("DataManager.query_by_name正则特殊字符", False, str(e))

        # 测试4: DataManager.query_by_filters
        try:
            data_file = os.path.join(temp_dir, 'dm4.csv')
            ds = DataStore(data_file)
            for i in range(5):
                collector = DataCollector(ds)
                collector.add_student_manual(
                    f'20230100{i+1:02d}', f'学生{i}', '男' if i % 2 == 0 else '女',
                    '高一', i+1, 170.0 + i, '2024-03-15'
                )

            dm = DataManager(ds)
            result = dm.query_by_filters(gender='男', grade='高一')
            assert len(result) >= 3
            report.add_result("DataManager.query_by_filters", True)
        except Exception as e:
            report.add_result("DataManager.query_by_filters", False, str(e))

        # 测试5: DataManager.update_student_info
        try:
            data_file = os.path.join(temp_dir, 'dm5.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            success, message = dm.update_student_info('2023010001', height=180.0)
            assert success == True
            report.add_result("DataManager.update_student_info", True)
        except Exception as e:
            report.add_result("DataManager.update_student_info", False, str(e))

        # 测试6: DataManager.delete_student
        try:
            data_file = os.path.join(temp_dir, 'dm6.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            success, message = dm.delete_student('2023010001')
            assert success == True
            report.add_result("DataManager.delete_student", True)
        except Exception as e:
            report.add_result("DataManager.delete_student", False, str(e))

        # 测试7: DataManager.backup_data
        try:
            data_file = os.path.join(temp_dir, 'dm7.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            backup_path = dm.backup_data('test_backup.csv')
            assert os.path.exists(backup_path)
            report.add_result("DataManager.backup_data", True)
        except Exception as e:
            report.add_result("DataManager.backup_data", False, str(e))

        # 测试8: DataManager.backup_data自动创建目录
        try:
            data_file = os.path.join(temp_dir, 'dm8.csv')
            ds = DataStore(data_file)
            dm = DataManager(ds)

            # 删除备份目录
            if os.path.exists(dm.backup_dir):
                shutil.rmtree(dm.backup_dir)

            backup_path = dm.backup_data('test_backup.csv')
            assert os.path.exists(backup_path)
            report.add_result("DataManager.backup_data自动创建目录", True)
        except Exception as e:
            report.add_result("DataManager.backup_data自动创建目录", False, str(e))

        # 测试9: DataManager.restore_from_backup
        try:
            data_file = os.path.join(temp_dir, 'dm9.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            dm.backup_data('restore_test.csv')
            ds.delete_student('2023010001')

            success, message = dm.restore_from_backup('restore_test.csv')
            assert success == True
            assert len(ds.df) == 1
            report.add_result("DataManager.restore_from_backup", True)
        except Exception as e:
            report.add_result("DataManager.restore_from_backup", False, str(e))

        # 测试10: DataManager.restore_from_backup损坏文件
        try:
            data_file = os.path.join(temp_dir, 'dm10.csv')
            ds = DataStore(data_file)
            dm = DataManager(ds)

            # 创建损坏的备份文件
            os.makedirs(dm.backup_dir, exist_ok=True)
            corrupted_file = os.path.join(dm.backup_dir, 'corrupted.csv')
            with open(corrupted_file, 'w') as f:
                f.write('无效数据')

            success, message = dm.restore_from_backup('corrupted.csv')
            assert success == False
            report.add_result("DataManager.restore_from_backup损坏文件", True)
        except Exception as e:
            report.add_result("DataManager.restore_from_backup损坏文件", False, str(e))

        # 测试11: DataManager.export_data
        try:
            data_file = os.path.join(temp_dir, 'dm11.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            export_path = os.path.join(temp_dir, 'export.csv')
            success, message = dm.export_data(export_path, 'csv')
            assert success == True
            assert os.path.exists(export_path)
            report.add_result("DataManager.export_data", True)
        except Exception as e:
            report.add_result("DataManager.export_data", False, str(e))

        # 测试12: DataManager.get_statistics_summary
        try:
            data_file = os.path.join(temp_dir, 'dm12.csv')
            ds = DataStore(data_file)
            for i in range(5):
                collector = DataCollector(ds)
                collector.add_student_manual(
                    f'20230100{i+1:02d}', f'学生{i}', '男' if i % 2 == 0 else '女',
                    '高一', i+1, 170.0 + i, '2024-03-15'
                )

            dm = DataManager(ds)
            result = dm.get_statistics_summary()
            assert 'total_students' in result
            assert result['total_students'] == 5
            report.add_result("DataManager.get_statistics_summary", True)
        except Exception as e:
            report.add_result("DataManager.get_statistics_summary", False, str(e))

        # 测试13: DataManager.validate_data_integrity
        try:
            data_file = os.path.join(temp_dir, 'dm13.csv')
            ds = DataStore(data_file)
            collector = DataCollector(ds)
            collector.add_student_manual('2023010001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

            dm = DataManager(ds)
            is_valid, issues = dm.validate_data_integrity()
            assert is_valid == True
            report.add_result("DataManager.validate_data_integrity", True)
        except Exception as e:
            report.add_result("DataManager.validate_data_integrity", False, str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_visualization_tests():
    """可视化模块测试"""
    print("\n[模块] 可视化 (visualization)")

    temp_dir = tempfile.mkdtemp()
    output_dir = os.path.join(temp_dir, 'reports')

    try:
        # 创建测试数据
        df = pd.DataFrame({
            'student_id': [f'20230100{i:02d}' for i in range(1, 21)],
            'name': [f'学生{i}' for i in range(1, 21)],
            'gender': ['男', '女'] * 10,
            'grade': ['高一'] * 7 + ['高二'] * 7 + ['高三'] * 6,
            'class': list(range(1, 21)),
            'height': [170.0 + i * 0.5 for i in range(20)],
            'measure_date': ['2024-03-15'] * 20
        })

        visualizer = HeightVisualizer(df, output_dir)

        # 测试1: plot_height_distribution_histogram
        try:
            result = visualizer.plot_height_distribution_histogram()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_height_distribution_histogram", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_height_distribution_histogram", False, str(e))

        # 测试2: plot_gender_comparison_boxplot
        try:
            result = visualizer.plot_gender_comparison_boxplot()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_gender_comparison_boxplot", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_gender_comparison_boxplot", False, str(e))

        # 测试3: plot_grade_trend
        try:
            result = visualizer.plot_grade_trend()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_grade_trend", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_grade_trend", False, str(e))

        # 测试4: plot_height_distribution_pie
        try:
            result = visualizer.plot_height_distribution_pie()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_height_distribution_pie", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_height_distribution_pie", False, str(e))

        # 测试5: plot_gender_grade_heatmap
        try:
            result = visualizer.plot_gender_grade_heatmap()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_gender_grade_heatmap", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_gender_grade_heatmap", False, str(e))

        # 测试6: plot_class_comparison
        try:
            result = visualizer.plot_class_comparison()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_class_comparison", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_class_comparison", False, str(e))

        # 测试7: plot_national_comparison
        try:
            result = visualizer.plot_national_comparison()
            assert result != "" and os.path.exists(result)
            report.add_result("HeightVisualizer.plot_national_comparison", True)
        except Exception as e:
            report.add_result("HeightVisualizer.plot_national_comparison", False, str(e))

        # 测试8: generate_all_visualizations
        try:
            results = visualizer.generate_all_visualizations()
            assert len(results) >= 6
            report.add_result("HeightVisualizer.generate_all_visualizations", True)
        except Exception as e:
            report.add_result("HeightVisualizer.generate_all_visualizations", False, str(e))

    except Exception as e:
        print(f"可视化模块测试初始化失败: {e}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_concurrency_tests():
    """并发测试"""
    print("\n[模块] 并发测试")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 并发添加数据
        try:
            data_file = os.path.join(temp_dir, 'concurrent.csv')

            errors = []
            def add_students(start_id):
                try:
                    ds = DataStore(data_file)
                    collector = DataCollector(ds)
                    for i in range(5):
                        collector.add_student_manual(
                            f'CONC{start_id:03d}{i:02d}',
                            f'并发学生{start_id}_{i}',
                            '男', '高一', 1, 175.0 + i, '2024-03-15'
                        )
                except Exception as e:
                    errors.append(str(e))

            threads = []
            for i in range(3):
                t = threading.Thread(target=add_students, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            if not errors:
                report.add_result("并发添加数据", True)
            else:
                report.add_result("并发添加数据", False, f"错误数: {len(errors)}")
        except Exception as e:
            report.add_result("并发添加数据", False, str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    print("=" * 80)
    print("学生身高分析系统 - 全量回归测试")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    run_data_model_tests()
    run_data_collector_tests()
    run_statistics_tests()
    run_data_manager_tests()
    run_visualization_tests()
    run_concurrency_tests()

    print("\n" + "=" * 80)
    print("测试完成，生成报告...")
    print("=" * 80)

    print(report.generate_report())

    # 保存报告
    report_file = 'regression_test_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report.generate_report())
    print(f"\n报告已保存到: {report_file}")

    return report.failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
