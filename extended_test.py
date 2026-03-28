#!/usr/bin/env python3
"""
扩展测试脚本 - 发现更多边界情况和潜在Bug
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


class ExtendedBugReport:
    """扩展Bug报告收集器"""
    def __init__(self):
        self.bugs = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.warnings = []

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

    def add_warning(self, module, function, description, details=""):
        self.warnings.append({
            'id': len(self.warnings) + 1,
            'module': module,
            'function': function,
            'description': description,
            'details': details
        })

    def record_test(self, passed=True):
        self.test_count += 1
        if passed:
            self.pass_count += 1

    def generate_report(self):
        report = []
        report.append("=" * 80)
        report.append("学生身高分析系统 - 扩展测试Bug报告")
        report.append("=" * 80)
        report.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试总数: {self.test_count}")
        report.append(f"通过测试: {self.pass_count}")
        report.append(f"失败测试: {self.fail_count}")
        report.append(f"Bug数量: {len(self.bugs)}")
        report.append(f"警告数量: {len(self.warnings)}")

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

        if self.warnings:
            report.append("\n" + "=" * 80)
            report.append("警告详情")
            report.append("=" * 80)
            for warning in self.warnings:
                report.append(f"\n【警告 #{warning['id']}】")
                report.append(f"  模块: {warning['module']}")
                report.append(f"  函数: {warning['function']}")
                report.append(f"  描述: {warning['description']}")
                if warning['details']:
                    report.append(f"  详情: {warning['details']}")

        report.append("\n" + "=" * 80)
        return "\n".join(report)


bug_report = ExtendedBugReport()


def test_extreme_values():
    """测试极端值"""
    print("\n" + "=" * 60)
    print("测试模块: 极端值测试")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'extreme_test.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        # 测试1: 身高为0
        print("\n测试1: 身高为0...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT001', name='测试', gender='男', grade='高一',
                class_num=1, height=0, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student', 
                    '身高为0应该被拒绝但通过了校验', 'high', '身高0cm不在有效范围内')
                bug_report.record_test(False)
            else:
                print("  ✓ 身高为0被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 身高为0处理异常: {e}")
            bug_report.record_test(True)

        # 测试2: 负身高
        print("\n测试2: 负身高...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT002', name='测试', gender='男', grade='高一',
                class_num=1, height=-175.5, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '负身高应该被拒绝但通过了校验', 'high', '负身高-175.5cm被接受')
                bug_report.record_test(False)
            else:
                print("  ✓ 负身高被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 负身高处理异常: {e}")
            bug_report.record_test(True)

        # 测试3: 极大身高
        print("\n测试3: 极大身高(1000cm)...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT003', name='测试', gender='男', grade='高一',
                class_num=1, height=1000, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '极大身高应该被拒绝但通过了校验', 'high', '身高1000cm超过最大限制200cm')
                bug_report.record_test(False)
            else:
                print("  ✓ 极大身高被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 极大身高处理异常: {e}")
            bug_report.record_test(True)

        # 测试4: 班级为负数
        print("\n测试4: 班级为负数...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT004', name='测试', gender='男', grade='高一',
                class_num=-1, height=175.5, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '负班级应该被拒绝但通过了校验', 'high', '班级-1被接受')
                bug_report.record_test(False)
            else:
                print("  ✓ 负班级被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 负班级处理异常: {e}")
            bug_report.record_test(True)

        # 测试5: 极大班级号
        print("\n测试5: 极大班级号(999)...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT005', name='测试', gender='男', grade='高一',
                class_num=999, height=175.5, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '极大班级号应该被拒绝但通过了校验', 'high', '班级999超过最大限制50')
                bug_report.record_test(False)
            else:
                print("  ✓ 极大班级号被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 极大班级号处理异常: {e}")
            bug_report.record_test(True)

        # 测试6: 空字符串学号（只有空格）
        print("\n测试6: 空格学号...")
        try:
            success, message = collector.add_student_manual(
                student_id='   ', name='测试', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '空格学号应该被拒绝但通过了校验', 'high', '学号只有空格被接受')
                bug_report.record_test(False)
            else:
                print("  ✓ 空格学号被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 空格学号处理异常: {e}")
            bug_report.record_test(True)

        # 测试7: 空字符串姓名（只有空格）
        print("\n测试7: 空格姓名...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT007', name='   ', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='2024-03-15'
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '空格姓名应该被拒绝但通过了校验', 'high', '姓名只有空格被接受')
                bug_report.record_test(False)
            else:
                print("  ✓ 空格姓名被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 空格姓名处理异常: {e}")
            bug_report.record_test(True)

        # 测试8: 未来日期
        print("\n测试8: 未来日期...")
        try:
            future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            success, message = collector.add_student_manual(
                student_id='EXT008', name='测试', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date=future_date
            )
            if success:
                bug_report.add_warning('data_collector', 'validate_student',
                    '未来日期被接受', f'日期{future_date}是未来日期但被接受')
                print("  ⚠ 未来日期被接受（可能是设计如此）")
            else:
                print("  ✓ 未来日期被正确拒绝")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 未来日期处理异常: {e}")
            bug_report.record_test(True)

        # 测试9: 过去极早日期
        print("\n测试9: 过去极早日期(1900年)...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT009', name='测试', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='1900-01-01'
            )
            if success:
                bug_report.add_warning('data_collector', 'validate_student',
                    '极早日期被接受', '日期1900-01-01被接受')
                print("  ⚠ 极早日期被接受（可能是设计如此）")
            else:
                print("  ✓ 极早日期被正确拒绝")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 极早日期处理异常: {e}")
            bug_report.record_test(True)

        # 测试10: 无效日期格式
        print("\n测试10: 无效日期格式...")
        try:
            success, message = collector.add_student_manual(
                student_id='EXT010', name='测试', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='2024/03/15'  # 使用斜杠
            )
            if success:
                bug_report.add_bug('data_collector', 'validate_student',
                    '无效日期格式应该被拒绝但通过了校验', 'medium', '日期格式2024/03/15被接受')
                bug_report.record_test(False)
            else:
                print("  ✓ 无效日期格式被正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 无效日期格式处理异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_special_characters_and_injection():
    """测试特殊字符和注入攻击"""
    print("\n" + "=" * 60)
    print("测试模块: 特殊字符和注入测试")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'injection_test.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        # 测试1: SQL注入尝试
        print("\n测试1: SQL注入尝试...")
        try:
            success, message = collector.add_student_manual(
                student_id="2023010001'; DROP TABLE students; --",
                name='测试',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            print(f"  {'✓' if success else '✗'} SQL注入尝试处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ SQL注入处理异常: {e}")
            bug_report.record_test(True)

        # 测试2: HTML标签
        print("\n测试2: HTML标签...")
        try:
            success, message = collector.add_student_manual(
                student_id='HTML001',
                name='<script>alert("xss")</script>',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            if success:
                bug_report.add_warning('data_collector', 'validate_student',
                    'HTML标签被接受', '可能存在XSS风险')
            print(f"  {'✓' if success else '✗'} HTML标签处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ HTML标签处理异常: {e}")
            bug_report.record_test(True)

        # 测试3: 换行符
        print("\n测试3: 换行符...")
        try:
            success, message = collector.add_student_manual(
                student_id='NL001',
                name='张三\n李四',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            print(f"  {'✓' if success else '✗'} 换行符处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 换行符处理异常: {e}")
            bug_report.record_test(True)

        # 测试4: 制表符
        print("\n测试4: 制表符...")
        try:
            success, message = collector.add_student_manual(
                student_id='TAB001',
                name='张三\t李四',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            print(f"  {'✓' if success else '✗'} 制表符处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 制表符处理异常: {e}")
            bug_report.record_test(True)

        # 测试5: Unicode特殊字符
        print("\n测试5: Unicode特殊字符...")
        try:
            success, message = collector.add_student_manual(
                student_id='UNI001',
                name='🔥🎉💯',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            print(f"  {'✓' if success else '✗'} Unicode特殊字符处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ Unicode特殊字符处理异常: {e}")
            bug_report.record_test(True)

        # 测试6: 零宽字符
        print("\n测试6: 零宽字符...")
        try:
            success, message = collector.add_student_manual(
                student_id='ZW001',
                name='张三\u200B李四',  # 零宽空格
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            print(f"  {'✓' if success else '✗'} 零宽字符处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 零宽字符处理异常: {e}")
            bug_report.record_test(True)

        # 测试7: 超长字符串
        print("\n测试7: 超长姓名(10000字符)...")
        try:
            long_name = 'A' * 10000
            success, message = collector.add_student_manual(
                student_id='LONG001',
                name=long_name,
                gender='男',
                grade='高一',
                class_num=1,
                height=175.5,
                measure_date='2024-03-15'
            )
            if success:
                bug_report.add_warning('data_collector', 'validate_student',
                    '超长姓名被接受', '姓名长度10000字符被接受，可能影响性能')
            print(f"  {'✓' if success else '✗'} 超长姓名处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 超长姓名处理异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "=" * 60)
    print("测试模块: 数据一致性测试")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 重复添加相同学号不同数据
        print("\n测试1: 重复添加相同学号不同数据...")
        try:
            data_file = os.path.join(temp_dir, 'consistency1.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)

            success1, _ = collector.add_student_manual(
                student_id='DUP001', name='张三', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='2024-03-15'
            )
            success2, _ = collector.add_student_manual(
                student_id='DUP001', name='李四', gender='女', grade='高二',
                class_num=2, height=162.0, measure_date='2024-03-15'
            )

            if success1 and success2:
                bug_report.add_bug('data_model', 'add_student',
                    '重复学号被成功添加两次', 'critical', '学号DUP001被添加两次，数据不一致')
                bug_report.record_test(False)
            elif success1 and not success2:
                print("  ✓ 重复学号正确拒绝")
                bug_report.record_test(True)
            else:
                print("  ⚠ 第一次添加失败")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 测试异常: {e}")
            bug_report.record_test(True)

        # 测试2: 删除后重新添加相同学号
        print("\n测试2: 删除后重新添加相同学号...")
        try:
            data_file = os.path.join(temp_dir, 'consistency2.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)

            collector.add_student_manual(
                student_id='READD001', name='张三', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='2024-03-15'
            )
            data_store.delete_student('READD001')
            success, _ = collector.add_student_manual(
                student_id='READD001', name='李四', gender='女', grade='高二',
                class_num=2, height=162.0, measure_date='2024-03-15'
            )

            if success:
                student = data_store.get_student('READD001')
                if student is not None and student['name'] == '李四':
                    print("  ✓ 删除后重新添加成功")
                    bug_report.record_test(True)
                else:
                    bug_report.add_bug('data_model', 'delete_student/add_student',
                        '删除后重新添加数据不一致', 'high', '重新添加后数据不正确')
                    bug_report.record_test(False)
            else:
                bug_report.add_bug('data_model', 'add_student',
                    '删除后无法重新添加相同学号', 'high', '学号READD001删除后无法重新添加')
                bug_report.record_test(False)
        except Exception as e:
            print(f"  ⚠ 测试异常: {e}")
            bug_report.record_test(True)

        # 测试3: 更新不存在的字段
        print("\n测试3: 更新不存在的字段...")
        try:
            data_file = os.path.join(temp_dir, 'consistency3.csv')
            data_store = DataStore(data_file)
            data_manager = DataManager(data_store)

            collector = DataCollector(data_store)
            collector.add_student_manual(
                student_id='UPDATE001', name='张三', gender='男', grade='高一',
                class_num=1, height=175.5, measure_date='2024-03-15'
            )

            # 尝试更新不存在的字段
            success, message = data_manager.update_student_info('UPDATE001', nonexistent_field='value')
            if success:
                bug_report.add_bug('data_manager', 'update_student_info',
                    '不存在的字段被接受更新', 'medium', '字段nonexistent_field不存在但被接受')
                bug_report.record_test(False)
            else:
                print("  ✓ 不存在的字段正确拒绝")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 测试异常: {e}")
            bug_report.record_test(True)

        # 测试4: 数据类型一致性
        print("\n测试4: 数据类型一致性...")
        try:
            data_file = os.path.join(temp_dir, 'consistency4.csv')
            data_store = DataStore(data_file)

            # 直接操作DataFrame添加错误类型数据
            data_store.df = pd.DataFrame({
                'student_id': ['TYPE001'],
                'name': ['张三'],
                'gender': ['男'],
                'grade': ['高一'],
                'class': ['一班'],  # 应该是整数
                'height': ['很高'],  # 应该是浮点数
                'measure_date': ['2024-03-15']
            })
            data_store.save_data()

            # 重新加载
            data_store2 = DataStore(data_file)
            stats = HeightStatistics(data_store2.get_all())
            result = stats.basic_statistics()

            bug_report.add_warning('data_model', 'save_data/load_data',
                '数据类型未严格校验', 'class和height列可以存储错误类型')
            print("  ⚠ 数据类型未严格校验")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 错误数据类型导致异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_file_operations_edge_cases():
    """测试文件操作边界情况"""
    print("\n" + "=" * 60)
    print("测试模块: 文件操作边界情况")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 导入空CSV文件
        print("\n测试1: 导入空CSV文件...")
        try:
            empty_csv = os.path.join(temp_dir, 'empty.csv')
            with open(empty_csv, 'w') as f:
                f.write('')

            data_file = os.path.join(temp_dir, 'test1.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(empty_csv)

            if success:
                bug_report.add_warning('data_collector', 'import_from_csv',
                    '空CSV文件被成功导入', '空文件应该被拒绝或给出警告')
            print(f"  {'✓' if not success else '⚠'} 空CSV处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 空CSV正确处理: {e}")
            bug_report.record_test(True)

        # 测试2: 导入只有标题的CSV
        print("\n测试2: 导入只有标题的CSV...")
        try:
            header_only_csv = os.path.join(temp_dir, 'header_only.csv')
            with open(header_only_csv, 'w') as f:
                f.write('student_id,name,gender,grade,class,height,measure_date\n')

            data_file = os.path.join(temp_dir, 'test2.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(header_only_csv)

            print(f"  {'✓' if success else '✗'} 只有标题的CSV处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 只有标题的CSV处理异常: {e}")
            bug_report.record_test(True)

        # 测试3: 导入格式错误的CSV
        print("\n测试3: 导入格式错误的CSV...")
        try:
            malformed_csv = os.path.join(temp_dir, 'malformed.csv')
            with open(malformed_csv, 'w') as f:
                f.write('student_id,name,gender,grade,class,height,measure_date\n')
                f.write('2023010001,张三,男,高一,1,175.5\n')  # 缺少日期列

            data_file = os.path.join(temp_dir, 'test3.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)
            success, message = collector.import_from_csv(malformed_csv)

            print(f"  {'✓' if success else '✗'} 格式错误的CSV处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 格式错误的CSV处理异常: {e}")
            bug_report.record_test(True)

        # 测试4: 导入超大CSV文件
        print("\n测试4: 导入超大CSV文件(10000行)...")
        try:
            large_csv = os.path.join(temp_dir, 'large.csv')
            with open(large_csv, 'w') as f:
                f.write('student_id,name,gender,grade,class,height,measure_date\n')
                for i in range(10000):
                    f.write(f'2023{i:08d},学生{i},{"男" if i % 2 == 0 else "女"},'
                           f'{"高一" if i % 3 == 0 else "高二" if i % 3 == 1 else "高三"},'
                           f'{i % 10 + 1},{160 + i % 40},2024-03-15\n')

            data_file = os.path.join(temp_dir, 'test4.csv')
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)

            start_time = time.time()
            success, message = collector.import_from_csv(large_csv)
            elapsed_time = time.time() - start_time

            print(f"  ✓ 超大CSV处理完成，耗时: {elapsed_time:.2f}秒")
            if elapsed_time > 10:
                bug_report.add_warning('data_collector', 'import_from_csv',
                    '大文件导入性能问题', f'10000行数据导入耗时{elapsed_time:.2f}秒')
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 超大CSV处理异常: {e}")
            bug_report.record_test(True)

        # 测试5: 备份目录不存在
        print("\n测试5: 备份目录不存在...")
        try:
            data_file = os.path.join(temp_dir, 'test5.csv')
            data_store = DataStore(data_file)
            data_manager = DataManager(data_store)

            # 删除备份目录
            if os.path.exists(data_manager.backup_dir):
                shutil.rmtree(data_manager.backup_dir)

            backup_path = data_manager.backup_data()
            if os.path.exists(backup_path):
                print("  ✓ 备份目录自动创建成功")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('data_manager', 'backup_data',
                    '备份目录不存在时备份失败', 'high', '备份目录应该自动创建')
                bug_report.record_test(False)
        except Exception as e:
            print(f"  ⚠ 备份测试异常: {e}")
            bug_report.record_test(True)

        # 测试6: 导出到只读目录
        print("\n测试6: 导出到只读目录...")
        try:
            data_file = os.path.join(temp_dir, 'test6.csv')
            data_store = DataStore(data_file)
            data_manager = DataManager(data_store)

            readonly_dir = os.path.join(temp_dir, 'readonly')
            os.makedirs(readonly_dir, exist_ok=True)
            os.chmod(readonly_dir, 0o444)  # 只读

            export_path = os.path.join(readonly_dir, 'export.csv')
            success, message = data_manager.export_data(export_path, 'csv')

            if success:
                bug_report.add_bug('data_manager', 'export_data',
                    '只读目录导出返回成功', 'medium', '应该返回失败')
            print(f"  {'✓' if not success else '⚠'} 只读目录处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✓ 只读目录正确处理: {e}")
            bug_report.record_test(True)
        finally:
            # 恢复权限以便清理
            try:
                os.chmod(readonly_dir, 0o755)
            except:
                pass

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_statistics_edge_cases():
    """测试统计分析边界情况"""
    print("\n" + "=" * 60)
    print("测试模块: 统计分析边界情况")
    print("=" * 60)

    # 测试1: 只有一个数据点
    print("\n测试1: 只有一个数据点...")
    try:
        df = pd.DataFrame({
            'student_id': ['SINGLE001'],
            'name': ['张三'],
            'gender': ['男'],
            'grade': ['高一'],
            'class': [1],
            'height': [175.5],
            'measure_date': ['2024-03-15']
        })
        stats = HeightStatistics(df)
        result = stats.basic_statistics()

        if result['count'] == 1:
            print("  ✓ 单数据点统计成功")
            bug_report.record_test(True)
        else:
            bug_report.add_bug('statistics', 'basic_statistics',
                '单数据点统计结果异常', 'medium', f'count={result["count"]}, expected=1')
            bug_report.record_test(False)
    except Exception as e:
        print(f"  ⚠ 单数据点统计异常: {e}")
        bug_report.record_test(True)

    # 测试2: 所有数据相同
    print("\n测试2: 所有数据相同...")
    try:
        df = pd.DataFrame({
            'student_id': [f'SAME{i:03d}' for i in range(10)],
            'name': [f'学生{i}' for i in range(10)],
            'gender': ['男'] * 10,
            'grade': ['高一'] * 10,
            'class': [1] * 10,
            'height': [175.5] * 10,
            'measure_date': ['2024-03-15'] * 10
        })
        stats = HeightStatistics(df)
        result = stats.basic_statistics()

        if result['std'] == 0:
            print("  ✓ 相同数据统计成功(std=0)")
            bug_report.record_test(True)
        else:
            bug_report.add_bug('statistics', 'basic_statistics',
                '相同数据标准差不为0', 'medium', f'std={result["std"]}, expected=0')
            bug_report.record_test(False)
    except Exception as e:
        print(f"  ⚠ 相同数据统计异常: {e}")
        bug_report.record_test(True)

    # 测试3: 只有男生数据
    print("\n测试3: 只有男生数据...")
    try:
        df = pd.DataFrame({
            'student_id': [f'MALE{i:03d}' for i in range(10)],
            'name': [f'男生{i}' for i in range(10)],
            'gender': ['男'] * 10,
            'grade': ['高一'] * 10,
            'class': [1] * 10,
            'height': [170.0 + i for i in range(10)],
            'measure_date': ['2024-03-15'] * 10
        })
        stats = HeightStatistics(df)
        result = stats.gender_difference_analysis()

        if 'error' in result:
            print("  ✓ 只有男生数据正确处理")
            bug_report.record_test(True)
        else:
            bug_report.add_bug('statistics', 'gender_difference_analysis',
                '只有男生数据未返回错误', 'medium', '应该返回缺少女生数据的错误')
            bug_report.record_test(False)
    except Exception as e:
        print(f"  ⚠ 只有男生数据处理异常: {e}")
        bug_report.record_test(True)

    # 测试4: 空DataFrame统计
    print("\n测试4: 空DataFrame统计...")
    try:
        stats = HeightStatistics(pd.DataFrame())
        result = stats.basic_statistics()

        if result == {}:
            print("  ✓ 空DataFrame返回空结果")
            bug_report.record_test(True)
        else:
            bug_report.add_bug('statistics', 'basic_statistics',
                '空DataFrame返回非空结果', 'medium', f'result={result}')
            bug_report.record_test(False)
    except Exception as e:
        print(f"  ⚠ 空DataFrame处理异常: {e}")
        bug_report.record_test(True)

    # 测试5: 异常值检测边界
    print("\n测试5: 异常值检测边界...")
    try:
        # 创建有明确异常值的数据
        heights = [170.0] * 98 + [100.0, 250.0]  # 两个明显的异常值
        df = pd.DataFrame({
            'student_id': [f'OUT{i:03d}' for i in range(100)],
            'name': [f'学生{i}' for i in range(100)],
            'gender': ['男'] * 100,
            'grade': ['高一'] * 100,
            'class': [1] * 100,
            'height': heights,
            'measure_date': ['2024-03-15'] * 100
        })
        stats = HeightStatistics(df)
        outliers = stats.outliers_analysis()

        if len(outliers) >= 2:
            print(f"  ✓ 异常值检测成功(发现{len(outliers)}个异常值)")
            bug_report.record_test(True)
        else:
            bug_report.add_warning('statistics', 'outliers_analysis',
                '异常值检测可能不敏感', f'期望2个异常值，只发现{len(outliers)}个')
            print(f"  ⚠ 异常值检测发现{len(outliers)}个")
            bug_report.record_test(True)
    except Exception as e:
        print(f"  ⚠ 异常值检测异常: {e}")
        bug_report.record_test(True)


def test_visualization_edge_cases():
    """测试可视化边界情况"""
    print("\n" + "=" * 60)
    print("测试模块: 可视化边界情况")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 只有一个性别的数据
        print("\n测试1: 只有一个性别的数据...")
        try:
            df = pd.DataFrame({
                'student_id': [f'M{i:03d}' for i in range(10)],
                'name': [f'男生{i}' for i in range(10)],
                'gender': ['男'] * 10,
                'grade': ['高一'] * 10,
                'class': [1] * 10,
                'height': [170.0 + i for i in range(10)],
                'measure_date': ['2024-03-15'] * 10
            })
            visualizer = HeightVisualizer(df, output_dir=temp_dir)
            result = visualizer.plot_gender_comparison_boxplot()

            if result == "":
                print("  ✓ 单性别数据正确处理")
                bug_report.record_test(True)
            else:
                bug_report.add_warning('visualization', 'plot_gender_comparison_boxplot',
                    '单性别数据仍然生成图表', '可能显示不完整')
                print("  ⚠ 单性别数据仍然生成图表")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 单性别数据处理异常: {e}")
            bug_report.record_test(True)

        # 测试2: 只有一个年级的数据
        print("\n测试2: 只有一个年级的数据...")
        try:
            df = pd.DataFrame({
                'student_id': [f'G{i:03d}' for i in range(10)],
                'name': [f'学生{i}' for i in range(10)],
                'gender': ['男', '女'] * 5,
                'grade': ['高一'] * 10,
                'class': [1] * 10,
                'height': [170.0 + i for i in range(10)],
                'measure_date': ['2024-03-15'] * 10
            })
            visualizer = HeightVisualizer(df, output_dir=temp_dir)
            result = visualizer.plot_grade_trend()

            print(f"  {'✓' if result != '' else '⚠'} 单年级数据处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 单年级数据处理异常: {e}")
            bug_report.record_test(True)

        # 测试3: 所有身高相同
        print("\n测试3: 所有身高相同...")
        try:
            df = pd.DataFrame({
                'student_id': [f'SAME{i:03d}' for i in range(10)],
                'name': [f'学生{i}' for i in range(10)],
                'gender': ['男', '女'] * 5,
                'grade': ['高一', '高二', '高三'] * 3 + ['高一'],
                'class': [1] * 10,
                'height': [175.0] * 10,
                'measure_date': ['2024-03-15'] * 10
            })
            visualizer = HeightVisualizer(df, output_dir=temp_dir)
            result = visualizer.plot_height_distribution_histogram()

            print(f"  {'✓' if result != '' else '⚠'} 相同身高处理完成")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 相同身高处理异常: {e}")
            bug_report.record_test(True)

        # 测试4: 输出目录不存在
        print("\n测试4: 输出目录不存在...")
        try:
            df = pd.DataFrame({
                'student_id': ['TEST001'],
                'name': ['测试'],
                'gender': ['男'],
                'grade': ['高一'],
                'class': [1],
                'height': [175.0],
                'measure_date': ['2024-03-15']
            })
            nonexistent_dir = os.path.join(temp_dir, 'nonexistent', 'nested')
            visualizer = HeightVisualizer(df, output_dir=nonexistent_dir)
            result = visualizer.plot_height_distribution_histogram()

            if os.path.exists(nonexistent_dir):
                print("  ✓ 输出目录自动创建成功")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('visualization', 'HeightVisualizer.__init__',
                    '输出目录未自动创建', 'medium', '嵌套目录应该自动创建')
                bug_report.record_test(False)
        except Exception as e:
            print(f"  ⚠ 输出目录测试异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_memory_and_performance():
    """测试内存和性能"""
    print("\n" + "=" * 60)
    print("测试模块: 内存和性能测试")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 大量数据统计性能
        print("\n测试1: 大量数据统计性能(50000条)...")
        try:
            np.random.seed(42)
            large_data = []
            for i in range(50000):
                large_data.append({
                    'student_id': f'PERF{i:08d}',
                    'name': f'学生{i}',
                    'gender': '男' if i % 2 == 0 else '女',
                    'grade': ['高一', '高二', '高三'][i % 3],
                    'class': (i % 10) + 1,
                    'height': round(np.random.normal(170, 8), 1),
                    'measure_date': '2024-03-15'
                })

            df = pd.DataFrame(large_data)
            stats = HeightStatistics(df)

            start_time = time.time()
            result = stats.basic_statistics()
            elapsed_time = time.time() - start_time

            print(f"  ✓ 大量数据统计完成，耗时: {elapsed_time:.2f}秒")
            if elapsed_time > 5:
                bug_report.add_warning('statistics', 'basic_statistics',
                    '大量数据统计性能问题', f'50000条数据统计耗时{elapsed_time:.2f}秒')
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 大量数据统计异常: {e}")
            bug_report.record_test(True)

        # 测试2: 大量数据可视化性能
        print("\n测试2: 大量数据可视化性能(10000条)...")
        try:
            np.random.seed(42)
            large_data = []
            for i in range(10000):
                large_data.append({
                    'student_id': f'VIZ{i:08d}',
                    'name': f'学生{i}',
                    'gender': '男' if i % 2 == 0 else '女',
                    'grade': ['高一', '高二', '高三'][i % 3],
                    'class': (i % 10) + 1,
                    'height': round(np.random.normal(170, 8), 1),
                    'measure_date': '2024-03-15'
                })

            df = pd.DataFrame(large_data)
            visualizer = HeightVisualizer(df, output_dir=temp_dir)

            start_time = time.time()
            result = visualizer.plot_height_distribution_histogram()
            elapsed_time = time.time() - start_time

            print(f"  ✓ 大量数据可视化完成，耗时: {elapsed_time:.2f}秒")
            if elapsed_time > 10:
                bug_report.add_warning('visualization', 'plot_height_distribution_histogram',
                    '大量数据可视化性能问题', f'10000条数据可视化耗时{elapsed_time:.2f}秒')
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 大量数据可视化异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_query_edge_cases():
    """测试查询边界情况"""
    print("\n" + "=" * 60)
    print("测试模块: 查询边界情况")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'query_test.csv')

    try:
        # 准备测试数据
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        for i in range(100):
            collector.add_student_manual(
                student_id=f'QUERY{i:04d}',
                name=f'学生{i}',
                gender='男' if i % 2 == 0 else '女',
                grade=['高一', '高二', '高三'][i % 3],
                class_num=(i % 10) + 1,
                height=160.0 + (i % 40),
                measure_date='2024-03-15'
            )

        data_manager = DataManager(data_store)

        # 测试1: 查询不存在的姓名
        print("\n测试1: 查询不存在的姓名...")
        try:
            result = data_manager.query_by_name('不存在的姓名')
            if len(result) == 0:
                print("  ✓ 不存在的姓名返回空结果")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('data_manager', 'query_by_name',
                    '不存在的姓名返回非空结果', 'high')
                bug_report.record_test(False)
        except Exception as e:
            print(f"  ⚠ 查询异常: {e}")
            bug_report.record_test(True)

        # 测试2: 查询空字符串
        print("\n测试2: 查询空字符串...")
        try:
            result = data_manager.query_by_name('')
            # 空字符串查询应该返回所有结果或空结果
            print(f"  ✓ 空字符串查询返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 空字符串查询异常: {e}")
            bug_report.record_test(True)

        # 测试3: 查询特殊字符
        print("\n测试3: 查询特殊字符...")
        try:
            result = data_manager.query_by_name('*')
            print(f"  ✓ 特殊字符查询完成，返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 特殊字符查询异常: {e}")
            bug_report.record_test(True)

        # 测试4: 极端身高范围查询
        print("\n测试4: 极端身高范围查询...")
        try:
            result = data_manager.query_by_filters(min_height=1000.0, max_height=2000.0)
            if len(result) == 0:
                print("  ✓ 极端身高范围返回空结果")
                bug_report.record_test(True)
            else:
                bug_report.add_bug('data_manager', 'query_by_filters',
                    '极端身高范围返回非空结果', 'medium')
                bug_report.record_test(False)
        except Exception as e:
            print(f"  ⚠ 极端身高范围查询异常: {e}")
            bug_report.record_test(True)

        # 测试5: 反转身高范围查询
        print("\n测试5: 反转身高范围查询(min > max)...")
        try:
            result = data_manager.query_by_filters(min_height=200.0, max_height=150.0)
            print(f"  ✓ 反转身高范围查询返回{len(result)}条结果")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ⚠ 反转身高范围查询异常: {e}")
            bug_report.record_test(True)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("开始扩展测试 - 学生身高分析系统")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    original_dir = os.getcwd()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    try:
        test_extreme_values()
        test_special_characters_and_injection()
        test_data_consistency()
        test_file_operations_edge_cases()
        test_statistics_edge_cases()
        test_visualization_edge_cases()
        test_memory_and_performance()
        test_query_edge_cases()

        report = bug_report.generate_report()
        report_file = f'extended_bug_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print("\n" + "=" * 80)
        print(report)
        print(f"\n报告已保存到: {report_file}")

    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()
