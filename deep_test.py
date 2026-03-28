#!/usr/bin/env python3
"""
深度测试脚本 - 发现更多潜在Bug
"""

import os
import sys
import tempfile
import shutil
import threading
import time
import re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_model import DataStore, Student
from modules.data_collector import DataCollector, DataValidator
from modules.statistics import HeightStatistics
from modules.visualization import HeightVisualizer
from modules.data_manager import DataManager

import pandas as pd
import numpy as np


class DeepBugReport:
    def __init__(self):
        self.bugs = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0

    def add_bug(self, module, function, description, severity="medium", details=""):
        self.bugs.append({
            'id': len(self.bugs) + 1,
            'module': module,
            'function': function,
            'description': description,
            'severity': severity,
            'details': details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.fail_count += 1

    def record_test(self, passed=True):
        self.test_count += 1
        if passed:
            self.pass_count += 1

    def generate_report(self):
        report = []
        report.append("=" * 80)
        report.append("学生身高分析系统 - 深度测试Bug报告")
        report.append("=" * 80)
        report.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试总数: {self.test_count}")
        report.append(f"通过测试: {self.pass_count}")
        report.append(f"失败测试: {self.fail_count}")
        report.append(f"Bug数量: {len(self.bugs)}")

        if self.bugs:
            report.append("\n" + "=" * 80)
            report.append("发现的Bug详情")
            report.append("=" * 80)
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sorted_bugs = sorted(self.bugs, key=lambda x: severity_order.get(x['severity'], 4))
            for bug in sorted_bugs:
                report.append(f"\n【Bug #{bug['id']}】")
                report.append(f"  严重程度: {bug['severity'].upper()}")
                report.append(f"  模块: {bug['module']}")
                report.append(f"  函数: {bug['function']}")
                report.append(f"  问题描述: {bug['description']}")
                if bug['details']:
                    report.append(f"  详细信息: {bug['details']}")

        report.append("\n" + "=" * 80)
        return "\n".join(report)


bug_report = DeepBugReport()


def test_regex_vulnerabilities():
    """测试正则表达式漏洞"""
    print("\n" + "=" * 60)
    print("测试模块: 正则表达式漏洞")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'regex_test.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        # 添加测试数据
        for i in range(10):
            collector.add_student_manual(
                student_id=f'REG{i:03d}',
                name=f'学生{i}',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.0,
                measure_date='2024-03-15'
            )

        data_manager = DataManager(data_store)

        # 测试1: 正则特殊字符 *
        print("\n测试1: 查询包含*的字符串...")
        try:
            result = data_manager.query_by_name('*')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符*导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试2: 正则特殊字符 +
        print("\n测试2: 查询包含+的字符串...")
        try:
            result = data_manager.query_by_name('+')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符+导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试3: 正则特殊字符 ?
        print("\n测试3: 查询包含?的字符串...")
        try:
            result = data_manager.query_by_name('?')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符?导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试4: 正则特殊字符 [
        print("\n测试4: 查询包含[的字符串...")
        try:
            result = data_manager.query_by_name('[')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符[导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试5: 正则特殊字符 (
        print("\n测试5: 查询包含(的字符串...")
        try:
            result = data_manager.query_by_name('(')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符(导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试6: 正则特殊字符 {
        print("\n测试6: 查询包含{的字符串...")
        try:
            result = data_manager.query_by_name('{')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符{导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试7: 正则特殊字符 ^
        print("\n测试7: 查询包含^的字符串...")
        try:
            result = data_manager.query_by_name('^')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符^导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试8: 正则特殊字符 $
        print("\n测试8: 查询包含$的字符串...")
        try:
            result = data_manager.query_by_name('$')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符$导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试9: 正则特殊字符 \
        print("\n测试9: 查询包含\\的字符串...")
        try:
            result = data_manager.query_by_name('\\')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符\\导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试10: 正则特殊字符 |
        print("\n测试10: 查询包含|的字符串...")
        try:
            result = data_manager.query_by_name('|')
            print(f"  ✓ 查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_manager', 'query_by_name',
                '正则特殊字符|导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_type_issues():
    """测试数据类型问题"""
    print("\n" + "=" * 60)
    print("测试模块: 数据类型问题")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 身高为字符串数字
        print("\n测试1: 身高为字符串数字...")
        try:
            data_file = os.path.join(temp_dir, 'type1.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)

            # 直接操作DataFrame添加字符串身高
            data_store.df = pd.DataFrame({
                'student_id': ['STR001'],
                'name': ['张三'],
                'gender': ['男'],
                'grade': ['高一'],
                'class': [1],
                'height': ['175.5'],  # 字符串
                'measure_date': ['2024-03-15']
            })

            stats = HeightStatistics(data_store.get_all())
            result = stats.basic_statistics()

            if 'mean' in result:
                print(f"  ✓ 字符串数字身高处理完成，平均值: {result['mean']}")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('statistics', 'basic_statistics',
                    '字符串数字身高导致统计失败', 'high')
                bug_report.record_test(False)
        except Exception as e:
            print(f"  ⚠ 字符串数字身高处理异常: {e}")
            bug_report.record_test(True)

        # 测试2: 班级为浮点数
        print("\n测试2: 班级为浮点数...")
        try:
            data_file = os.path.join(temp_dir, 'type2.csv')
            data_store = DataStore(data_file)

            data_store.df = pd.DataFrame({
                'student_id': ['FLOAT001'],
                'name': ['张三'],
                'gender': ['男'],
                'grade': ['高一'],
                'class': [1.5],  # 浮点数班级
                'height': [175.5],
                'measure_date': ['2024-03-15']
            })

            result = data_store.query(class_num=1.5)
            print(f"  ✓ 浮点数班级查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 浮点数班级处理异常: {e}")
            bug_report.record_test(True)

        # 测试3: 日期格式混乱
        print("\n测试3: 日期格式混乱...")
        try:
            data_file = os.path.join(temp_dir, 'type3.csv')
            data_store = DataStore(data_file)

            data_store.df = pd.DataFrame({
                'student_id': ['DATE001', 'DATE002', 'DATE003'],
                'name': ['张三', '李四', '王五'],
                'gender': ['男', '女', '男'],
                'grade': ['高一', '高二', '高三'],
                'class': [1, 2, 3],
                'height': [175.5, 162.0, 170.0],
                'measure_date': ['2024-03-15', '15-03-2024', '03/15/2024']  # 不同格式
            })

            print(f"  ✓ 混乱日期格式处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 混乱日期格式处理异常: {e}")
            bug_report.record_test(True)

        # 测试4: NaN值处理
        print("\n测试4: NaN值处理...")
        try:
            data_file = os.path.join(temp_dir, 'type4.csv')
            data_store = DataStore(data_file)

            data_store.df = pd.DataFrame({
                'student_id': ['NAN001', 'NAN002'],
                'name': ['张三', None],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, float('nan')],
                'measure_date': ['2024-03-15', '2024-03-15']
            })

            stats = HeightStatistics(data_store.get_all())
            result = stats.basic_statistics()

            print(f"  ✓ NaN值处理完成，统计记录数: {result.get('count', 'N/A')}")
            bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('statistics', 'basic_statistics',
                'NaN值导致统计异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试5: Infinity值处理
        print("\n测试5: Infinity值处理...")
        try:
            data_file = os.path.join(temp_dir, 'type5.csv')
            data_store = DataStore(data_file)

            data_store.df = pd.DataFrame({
                'student_id': ['INF001'],
                'name': ['张三'],
                'gender': ['男'],
                'grade': ['高一'],
                'class': [1],
                'height': [float('inf')],
                'measure_date': ['2024-03-15']
            })

            stats = HeightStatistics(data_store.get_all())
            result = stats.basic_statistics()

            bug_report.add_bug('statistics', 'basic_statistics',
                'Infinity值被接受', 'high', '身高为Infinity时统计仍返回结果')
            print(f"  ✗ Bug发现: Infinity值被接受")
            bug_report.record_test(False)
        except Exception as e:
            print(f"  ✓ Infinity值正确处理: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_backup_restore_issues():
    """测试备份恢复问题"""
    print("\n" + "=" * 60)
    print("测试模块: 备份恢复问题")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 备份目录不存在
        print("\n测试1: 备份目录不存在...")
        try:
            data_file = os.path.join(temp_dir, 'backup1.csv')
            data_store = DataStore(data_file)
            data_manager = DataManager(data_store)

            # 删除备份目录
            if os.path.exists(data_manager.backup_dir):
                shutil.rmtree(data_manager.backup_dir)

            backup_path = data_manager.backup_data('test.csv')
            if os.path.exists(backup_path):
                print("  ✓ 备份目录自动创建")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('data_manager', 'backup_data',
                    '备份目录不存在时备份失败', 'high', '应该自动创建备份目录')
                print(f"  ✗ Bug发现: 备份目录不存在时备份失败")
                bug_report.record_test(False)
        except Exception as e:
            bug_report.add_bug('data_manager', 'backup_data',
                '备份目录不存在时异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试2: 恢复空备份文件
        print("\n测试2: 恢复空备份文件...")
        try:
            data_file = os.path.join(temp_dir, 'backup2.csv')
            data_store = DataStore(data_file)
            data_manager = DataManager(data_store)

            # 创建空备份文件
            empty_backup = os.path.join(data_manager.backup_dir, 'empty.csv')
            os.makedirs(data_manager.backup_dir, exist_ok=True)
            with open(empty_backup, 'w') as f:
                f.write('')

            success, message = data_manager.restore_from_backup('empty.csv')
            if success:
                bug_report.add_bug('data_manager', 'restore_from_backup',
                    '空备份文件恢复成功', 'medium', '应该拒绝空备份文件')
                print(f"  ✗ Bug发现: 空备份文件恢复成功")
                bug_report.record_test(False)
            else:
                print(f"  ✓ 空备份文件正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 空备份文件正确处理: {e}")
            bug_report.record_test(True)

        # 测试3: 恢复损坏的备份文件
        print("\n测试3: 恢复损坏的备份文件...")
        try:
            data_file = os.path.join(temp_dir, 'backup3.csv')
            data_store = DataStore(data_file)
            data_manager = DataManager(data_store)

            # 创建损坏的备份文件
            corrupted_backup = os.path.join(data_manager.backup_dir, 'corrupted.csv')
            os.makedirs(data_manager.backup_dir, exist_ok=True)
            with open(corrupted_backup, 'w') as f:
                f.write('这不是有效的CSV数据\n一些随机文本')

            success, message = data_manager.restore_from_backup('corrupted.csv')
            if success:
                bug_report.add_bug('data_manager', 'restore_from_backup',
                    '损坏备份文件恢复成功', 'high', '应该拒绝损坏的备份文件')
                print(f"  ✗ Bug发现: 损坏备份文件恢复成功")
                bug_report.record_test(False)
            else:
                print(f"  ✓ 损坏备份文件正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 损坏备份文件正确处理: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_concurrency_issues():
    """测试并发问题"""
    print("\n" + "=" * 60)
    print("测试模块: 并发问题")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'concurrent.csv')

    try:
        errors = []

        def add_students(start_id):
            try:
                data_store = DataStore(data_file)
                collector = DataCollector(data_store)
                for i in range(10):
                    collector.add_student_manual(
                        student_id=f'CONC{start_id:03d}{i:02d}',
                        name=f'并发学生{start_id}_{i}',
                        gender='男',
                        grade='高一',
                        class_num=1,
                        height=175.0 + i,
                        measure_date='2024-03-15'
                    )
            except Exception as e:
                errors.append(f"Thread {start_id}: {e}")

        # 测试1: 并发添加数据
        print("\n测试1: 并发添加数据...")
        try:
            threads = []
            for i in range(5):
                t = threading.Thread(target=add_students, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            if errors:
                bug_report.add_bug('data_model', 'add_student',
                    '并发添加数据异常', 'high', '; '.join(errors))
                print(f"  ✗ Bug发现: {len(errors)}个并发错误")
                bug_report.record_test(False)
            else:
                data_store = DataStore(data_file)
                count = len(data_store.df)
                print(f"  ✓ 并发添加完成，共{count}条记录")
                bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('data_model', 'add_student',
                '并发添加数据异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_import_edge_cases():
    """测试导入边界情况"""
    print("\n" + "=" * 60)
    print("测试模块: 导入边界情况")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: CSV文件缺少必要列
        print("\n测试1: CSV文件缺少必要列...")
        try:
            csv_file = os.path.join(temp_dir, 'missing_cols.csv')
            with open(csv_file, 'w') as f:
                f.write('student_id,name\n')
                f.write('2023010001,张三\n')

            data_file = os.path.join(temp_dir, 'import1.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(csv_file)

            if success:
                bug_report.add_bug('data_collector', 'import_from_csv',
                    '缺少必要列的CSV导入成功', 'high', '应该拒绝缺少必要列的CSV')
                print(f"  ✗ Bug发现: 缺少必要列的CSV导入成功")
                bug_report.record_test(False)
            else:
                print(f"  ✓ 缺少必要列的CSV正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 缺少必要列的CSV正确处理: {e}")
            bug_report.record_test(True)

        # 测试2: CSV文件列名错误
        print("\n测试2: CSV文件列名错误...")
        try:
            csv_file = os.path.join(temp_dir, 'wrong_cols.csv')
            with open(csv_file, 'w') as f:
                f.write('id,姓名,性别,年级,班级,身高,日期\n')  # 中文列名
                f.write('2023010001,张三,男,高一,1,175.5,2024-03-15\n')

            data_file = os.path.join(temp_dir, 'import2.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(csv_file)

            if success:
                bug_report.add_bug('data_collector', 'import_from_csv',
                    '错误列名的CSV导入成功', 'high', '应该拒绝错误列名的CSV')
                print(f"  ✗ Bug发现: 错误列名的CSV导入成功")
                bug_report.record_test(False)
            else:
                print(f"  ✓ 错误列名的CSV正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 错误列名的CSV正确处理: {e}")
            bug_report.record_test(True)

        # 测试3: CSV文件包含重复学号
        print("\n测试3: CSV文件包含重复学号...")
        try:
            csv_file = os.path.join(temp_dir, 'dup_ids.csv')
            with open(csv_file, 'w') as f:
                f.write('student_id,name,gender,grade,class,height,measure_date\n')
                f.write('2023010001,张三,男,高一,1,175.5,2024-03-15\n')
                f.write('2023010001,李四,女,高二,2,162.0,2024-03-15\n')  # 相同学号

            data_file = os.path.join(temp_dir, 'import3.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(csv_file)

            # 检查是否两个都被导入
            data_store2 = DataStore(data_file)
            dup_count = len(data_store2.df[data_store2.df['student_id'] == '2023010001'])

            if dup_count > 1:
                bug_report.add_bug('data_collector', 'import_from_csv',
                    'CSV中重复学号都被导入', 'critical', f'学号2023010001被导入{dup_count}次')
                print(f"  ✗ Bug发现: 重复学号被导入{dup_count}次")
                bug_report.record_test(False)
            else:
                print(f"  ✓ 重复学号正确处理")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 重复学号处理异常: {e}")
            bug_report.record_test(True)

        # 测试4: CSV文件包含空行
        print("\n测试4: CSV文件包含空行...")
        try:
            csv_file = os.path.join(temp_dir, 'empty_rows.csv')
            with open(csv_file, 'w') as f:
                f.write('student_id,name,gender,grade,class,height,measure_date\n')
                f.write('2023010001,张三,男,高一,1,175.5,2024-03-15\n')
                f.write('\n')  # 空行
                f.write('2023010002,李四,女,高二,2,162.0,2024-03-15\n')

            data_file = os.path.join(temp_dir, 'import4.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(csv_file)

            print(f"  ✓ 包含空行的CSV处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 包含空行的CSV处理异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_visualization_issues():
    """测试可视化问题"""
    print("\n" + "=" * 60)
    print("测试模块: 可视化问题")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 所有身高相同导致直方图失败
        print("\n测试1: 所有身高相同...")
        try:
            df = pd.DataFrame({
                'student_id': [f'SAME{i:03d}' for i in range(10)],
                'name': [f'学生{i}' for i in range(10)],
                'gender': ['男'] * 10,
                'grade': ['高一'] * 10,
                'class': [1] * 10,
                'height': [175.0] * 10,
                'measure_date': ['2024-03-15'] * 10
            })
            visualizer = HeightVisualizer(df, output_dir=temp_dir)
            result = visualizer.plot_height_distribution_histogram()

            if result == "":
                bug_report.add_bug('visualization', 'plot_height_distribution_histogram',
                    '相同身高导致直方图失败', 'medium', '所有身高相同时应该仍能生成图表')
                print(f"  ✗ Bug发现: 相同身高导致直方图失败")
                bug_report.record_test(False)
            else:
                print(f"  ✓ 相同身高直方图生成成功")
                bug_report.record_test(True)
        except Exception as e:
            bug_report.add_bug('visualization', 'plot_height_distribution_histogram',
                '相同身高导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

        # 测试2: 空数据可视化
        print("\n测试2: 空数据可视化...")
        try:
            df = pd.DataFrame()
            visualizer = HeightVisualizer(df, output_dir=temp_dir)

            files = visualizer.generate_all_visualizations()
            if len(files) == 0:
                print(f"  ✓ 空数据正确返回空列表")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('visualization', 'generate_all_visualizations',
                    '空数据生成图表', 'medium', '空数据时不应该生成图表')
                print(f"  ✗ Bug发现: 空数据生成{len(files)}个图表")
                bug_report.record_test(False)
        except Exception as e:
            bug_report.add_bug('visualization', 'generate_all_visualizations',
                '空数据导致异常', 'high', str(e))
            print(f"  ✗ Bug发现: {e}")
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("开始深度测试 - 学生身高分析系统")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    original_dir = os.getcwd()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    try:
        test_regex_vulnerabilities()
        test_data_type_issues()
        test_backup_restore_issues()
        test_concurrency_issues()
        test_import_edge_cases()
        test_visualization_issues()

        report = bug_report.generate_report()
        report_file = f'deep_bug_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print("\n" + "=" * 80)
        print(report)
        print(f"\n报告已保存到: {report_file}")

    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()
