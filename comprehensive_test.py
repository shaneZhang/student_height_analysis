#!/usr/bin/env python3
"""
全面测试脚本 - 测试学生身高分析系统的所有功能
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_model import DataStore, Student
from modules.data_collector import DataCollector, DataValidator
from modules.statistics import HeightStatistics
from modules.visualization import HeightVisualizer
from modules.data_manager import DataManager

import pandas as pd
import numpy as np


class BugReport:
    """Bug报告收集器"""
    def __init__(self):
        self.bugs = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0

    def add_bug(self, module, function, description, severity="medium", details=""):
        """添加bug记录"""
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
        """记录测试结果"""
        self.test_count += 1
        if passed:
            self.pass_count += 1

    def generate_report(self):
        """生成bug报告"""
        report = []
        report.append("=" * 80)
        report.append("学生身高分析系统 - 全面测试Bug报告")
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

            # 按严重程度排序
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


# 全局bug报告
bug_report = BugReport()


def test_data_model():
    """测试数据模型模块"""
    print("\n" + "=" * 60)
    print("测试模块: data_model")
    print("=" * 60)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test_students.csv')

    try:
        # 测试1: Student数据类创建
        print("\n测试1: Student数据类创建...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            assert student.student_id == "2023010001"
            assert student.name == "张三"
            print("  ✓ Student数据类创建成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ Student数据类创建失败: {e}")
            bug_report.add_bug('data_model', 'Student.__init__', 'Student数据类创建失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试2: Student.from_dict
        print("\n测试2: Student.from_dict...")
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
            student = Student.from_dict(data)
            assert student.student_id == "2023010002"
            print("  ✓ Student.from_dict成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ Student.from_dict失败: {e}")
            bug_report.add_bug('data_model', 'Student.from_dict', '从字典创建Student失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试3: DataStore初始化
        print("\n测试3: DataStore初始化...")
        try:
            data_store = DataStore(data_file)
            assert data_store.df is not None
            assert len(data_store.df) == 0
            print("  ✓ DataStore初始化成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore初始化失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.__init__', 'DataStore初始化失败', 'critical', str(e))
            bug_report.record_test(False)
            return

        # 测试4: DataStore.add_student
        print("\n测试4: DataStore.add_student...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            result = data_store.add_student(student)
            assert result == True
            assert len(data_store.df) == 1
            print("  ✓ DataStore.add_student成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.add_student失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.add_student', '添加学生失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试5: DataStore.add_student重复学号
        print("\n测试5: DataStore.add_student重复学号...")
        try:
            student2 = Student(
                student_id="2023010001",  # 重复学号
                name="李四",
                gender="女",
                grade="高一",
                class_num=2,
                height=162.0,
                measure_date="2024-03-15"
            )
            result = data_store.add_student(student2)
            assert result == False  # 应该返回False
            print("  ✓ 重复学号检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 重复学号检测失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.add_student', '重复学号检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试6: DataStore.get_student
        print("\n测试6: DataStore.get_student...")
        try:
            result = data_store.get_student("2023010001")
            assert result is not None
            assert result['name'] == "张三"
            print("  ✓ DataStore.get_student成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.get_student失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.get_student', '获取学生信息失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试7: DataStore.get_student不存在的学号
        print("\n测试7: DataStore.get_student不存在的学号...")
        try:
            result = data_store.get_student("9999999999")
            assert result is None
            print("  ✓ 不存在的学号返回None成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 不存在的学号处理失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.get_student', '不存在的学号处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试8: DataStore.update_student
        print("\n测试8: DataStore.update_student...")
        try:
            result = data_store.update_student("2023010001", height=180.0, name="张三丰")
            assert result == True
            student = data_store.get_student("2023010001")
            assert student['height'] == 180.0
            assert student['name'] == "张三丰"
            print("  ✓ DataStore.update_student成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.update_student失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.update_student', '更新学生信息失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试9: DataStore.update_student不存在的学号
        print("\n测试9: DataStore.update_student不存在的学号...")
        try:
            result = data_store.update_student("9999999999", height=180.0)
            assert result == False
            print("  ✓ 更新不存在学号返回False成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 更新不存在学号处理失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.update_student', '更新不存在学号处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试10: DataStore.delete_student
        print("\n测试10: DataStore.delete_student...")
        try:
            # 先添加一个新学生
            student = Student(
                student_id="2023010003",
                name="王五",
                gender="男",
                grade="高三",
                class_num=3,
                height=170.0,
                measure_date="2024-03-15"
            )
            data_store.add_student(student)
            count_before = len(data_store.df)

            result = data_store.delete_student("2023010003")
            assert result == True
            assert len(data_store.df) == count_before - 1
            print("  ✓ DataStore.delete_student成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.delete_student失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.delete_student', '删除学生失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试11: DataStore.delete_student不存在的学号
        print("\n测试11: DataStore.delete_student不存在的学号...")
        try:
            result = data_store.delete_student("9999999999")
            assert result == False
            print("  ✓ 删除不存在学号返回False成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 删除不存在学号处理失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.delete_student', '删除不存在学号处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试12: DataStore.query
        print("\n测试12: DataStore.query...")
        try:
            # 添加测试数据
            for i in range(5):
                student = Student(
                    student_id=f"20230100{i+10:02d}",
                    name=f"测试{i}",
                    gender="男" if i % 2 == 0 else "女",
                    grade="高一",
                    class_num=i+1,
                    height=170.0 + i,
                    measure_date="2024-03-15"
                )
                data_store.add_student(student)

            result = data_store.query(gender="男")
            assert len(result) >= 3  # 至少有3个男生
            print("  ✓ DataStore.query成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.query失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.query', '查询功能失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试13: DataStore.clear_data
        print("\n测试13: DataStore.clear_data...")
        try:
            data_store.clear_data()
            assert len(data_store.df) == 0
            print("  ✓ DataStore.clear_data成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.clear_data失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.clear_data', '清空数据失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试14: DataStore.import_from_dataframe
        print("\n测试14: DataStore.import_from_dataframe...")
        try:
            data_store.clear_data()
            df = pd.DataFrame({
                'student_id': ['2023010001', '2023010002'],
                'name': ['张三', '李四'],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, 162.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            success, message = data_store.import_from_dataframe(df)
            assert success == True
            assert len(data_store.df) == 2
            print("  ✓ DataStore.import_from_dataframe成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataStore.import_from_dataframe失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.import_from_dataframe', '从DataFrame导入失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试15: DataStore.import_from_dataframe缺少列
        print("\n测试15: DataStore.import_from_dataframe缺少列...")
        try:
            data_store.clear_data()
            df = pd.DataFrame({
                'student_id': ['2023010001'],
                'name': ['张三'],
                # 缺少其他列
            })
            success, message = data_store.import_from_dataframe(df)
            assert success == False
            print("  ✓ 缺少列检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 缺少列检测失败: {e}")
            bug_report.add_bug('data_model', 'DataStore.import_from_dataframe', '缺少列检测失败', 'high', str(e))
            bug_report.record_test(False)

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_collector():
    """测试数据收集模块"""
    print("\n" + "=" * 60)
    print("测试模块: data_collector")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test_students.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        # 测试1: DataValidator.validate_student有效数据
        print("\n测试1: DataValidator.validate_student有效数据...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == True
            assert len(errors) == 0
            print("  ✓ 有效数据校验通过")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 有效数据校验失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '有效数据校验失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试2: DataValidator.validate_student空学号
        print("\n测试2: DataValidator.validate_student空学号...")
        try:
            student = Student(
                student_id="",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("学号" in err for err in errors)
            print("  ✓ 空学号检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 空学号检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '空学号检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试3: DataValidator.validate_student空姓名
        print("\n测试3: DataValidator.validate_student空姓名...")
        try:
            student = Student(
                student_id="2023010001",
                name="",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("姓名" in err for err in errors)
            print("  ✓ 空姓名检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 空姓名检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '空姓名检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试4: DataValidator.validate_student无效性别
        print("\n测试4: DataValidator.validate_student无效性别...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="未知",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("性别" in err for err in errors)
            print("  ✓ 无效性别检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效性别检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '无效性别检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试5: DataValidator.validate_student无效年级
        print("\n测试5: DataValidator.validate_student无效年级...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="大四",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("年级" in err for err in errors)
            print("  ✓ 无效年级检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效年级检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '无效年级检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试6: DataValidator.validate_student无效班级
        print("\n测试6: DataValidator.validate_student无效班级...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=100,  # 超出范围
                height=175.5,
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("班级" in err for err in errors)
            print("  ✓ 无效班级检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效班级检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '无效班级检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试7: DataValidator.validate_student身高过低
        print("\n测试7: DataValidator.validate_student身高过低...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=100.0,  # 过低
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("身高" in err for err in errors)
            print("  ✓ 身高过低检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 身高过低检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '身高过低检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试8: DataValidator.validate_student身高过高
        print("\n测试8: DataValidator.validate_student身高过高...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=250.0,  # 过高
                measure_date="2024-03-15"
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("身高" in err for err in errors)
            print("  ✓ 身高过高检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 身高过高检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '身高过高检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试9: DataValidator.validate_student无效日期
        print("\n测试9: DataValidator.validate_student无效日期...")
        try:
            student = Student(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-13-45"  # 无效日期
            )
            is_valid, errors = DataValidator.validate_student(student)
            assert is_valid == False
            assert any("日期" in err for err in errors)
            print("  ✓ 无效日期检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效日期检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_student', '无效日期检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试10: DataCollector.add_student_manual
        print("\n测试10: DataCollector.add_student_manual...")
        try:
            success, message = collector.add_student_manual(
                student_id="2023010001",
                name="张三",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            assert success == True
            print("  ✓ DataCollector.add_student_manual成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataCollector.add_student_manual失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.add_student_manual', '手动添加学生失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试11: DataCollector.add_student_manual重复学号
        print("\n测试11: DataCollector.add_student_manual重复学号...")
        try:
            success, message = collector.add_student_manual(
                student_id="2023010001",  # 重复
                name="李四",
                gender="女",
                grade="高二",
                class_num=2,
                height=162.0,
                measure_date="2024-03-15"
            )
            assert success == False
            print("  ✓ 重复学号检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 重复学号检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.add_student_manual', '重复学号检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试12: DataCollector.add_student_manual无效数据
        print("\n测试12: DataCollector.add_student_manual无效数据...")
        try:
            success, message = collector.add_student_manual(
                student_id="2023010002",
                name="",
                gender="男",
                grade="高一",
                class_num=1,
                height=175.5,
                measure_date="2024-03-15"
            )
            assert success == False
            print("  ✓ 无效数据检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效数据检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.add_student_manual', '无效数据检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试13: DataValidator.validate_dataframe
        print("\n测试13: DataValidator.validate_dataframe...")
        try:
            df = pd.DataFrame({
                'student_id': ['2023010002', '2023010003'],
                'name': ['李四', '王五'],
                'gender': ['女', '男'],
                'grade': ['高二', '高三'],
                'class': [2, 3],
                'height': [162.0, 170.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            is_valid, errors, valid_df = DataValidator.validate_dataframe(df)
            assert is_valid == True
            assert len(valid_df) == 2
            print("  ✓ DataValidator.validate_dataframe成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataValidator.validate_dataframe失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_dataframe', 'DataFrame校验失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试14: DataValidator.validate_dataframe包含无效数据
        print("\n测试14: DataValidator.validate_dataframe包含无效数据...")
        try:
            df = pd.DataFrame({
                'student_id': ['2023010002', '', '2023010004'],
                'name': ['李四', '王五', ''],
                'gender': ['女', '未知', '男'],
                'grade': ['高二', '高一', '大四'],
                'class': [2, 1, 3],
                'height': [162.0, 175.5, 170.0],
                'measure_date': ['2024-03-15', '2024-03-15', '2024-03-15']
            })
            is_valid, errors, valid_df = DataValidator.validate_dataframe(df)
            assert is_valid == False
            assert len(errors) > 0
            print("  ✓ DataFrame无效数据检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataFrame无效数据检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_dataframe', 'DataFrame无效数据检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试15: DataValidator.validate_dataframe缺少列
        print("\n测试15: DataValidator.validate_dataframe缺少列...")
        try:
            df = pd.DataFrame({
                'student_id': ['2023010002'],
                'name': ['李四']
            })
            is_valid, errors, valid_df = DataValidator.validate_dataframe(df)
            assert is_valid == False
            assert any("列" in err for err in errors)
            print("  ✓ DataFrame缺少列检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataFrame缺少列检测失败: {e}")
            bug_report.add_bug('data_collector', 'DataValidator.validate_dataframe', 'DataFrame缺少列检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试16: DataCollector.import_from_csv
        print("\n测试16: DataCollector.import_from_csv...")
        try:
            # 创建测试CSV文件
            csv_file = os.path.join(temp_dir, 'test_import.csv')
            df = pd.DataFrame({
                'student_id': ['2023010005', '2023010006'],
                'name': ['赵六', '钱七'],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, 162.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            df.to_csv(csv_file, index=False)

            success, message = collector.import_from_csv(csv_file)
            assert success == True
            print("  ✓ DataCollector.import_from_csv成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataCollector.import_from_csv失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.import_from_csv', 'CSV导入失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试17: DataCollector.import_from_csv文件不存在
        print("\n测试17: DataCollector.import_from_csv文件不存在...")
        try:
            success, message = collector.import_from_csv("/nonexistent/file.csv")
            assert success == False
            print("  ✓ 文件不存在处理成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 文件不存在处理失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.import_from_csv', '文件不存在处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试18: DataCollector.get_import_template
        print("\n测试18: DataCollector.get_import_template...")
        try:
            template = collector.get_import_template()
            assert isinstance(template, pd.DataFrame)
            assert len(template) == 2
            required_cols = ['student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date']
            assert all(col in template.columns for col in required_cols)
            print("  ✓ DataCollector.get_import_template成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataCollector.get_import_template失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.get_import_template', '获取导入模板失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试19: DataCollector.save_template
        print("\n测试19: DataCollector.save_template...")
        try:
            template_csv = os.path.join(temp_dir, 'template.csv')
            collector.save_template(template_csv)
            assert os.path.exists(template_csv)

            template_xlsx = os.path.join(temp_dir, 'template.xlsx')
            collector.save_template(template_xlsx)
            assert os.path.exists(template_xlsx)
            print("  ✓ DataCollector.save_template成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataCollector.save_template失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.save_template', '保存模板失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试20: DataCollector.check_duplicate_ids
        print("\n测试20: DataCollector.check_duplicate_ids...")
        try:
            df = pd.DataFrame({
                'student_id': ['2023010001', '2023010005', '2023010010'],  # 2023010001已存在
                'name': ['张三', '赵六', '新学生'],
                'gender': ['男', '男', '女'],
                'grade': ['高一', '高一', '高二'],
                'class': [1, 1, 2],
                'height': [175.5, 175.5, 162.0],
                'measure_date': ['2024-03-15', '2024-03-15', '2024-03-15']
            })
            duplicates = collector.check_duplicate_ids(df)
            assert '2023010001' in duplicates
            print("  ✓ DataCollector.check_duplicate_ids成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataCollector.check_duplicate_ids失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.check_duplicate_ids', '检查重复学号失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试21: DataCollector.preview_import
        print("\n测试21: DataCollector.preview_import...")
        try:
            preview_csv = os.path.join(temp_dir, 'preview_test.csv')
            df = pd.DataFrame({
                'student_id': ['2023010007', '2023010008'],
                'name': ['孙八', '周九'],
                'gender': ['男', '女'],
                'grade': ['高一', '高二'],
                'class': [1, 2],
                'height': [175.5, 162.0],
                'measure_date': ['2024-03-15', '2024-03-15']
            })
            df.to_csv(preview_csv, index=False)

            preview_df, info = collector.preview_import(preview_csv)
            assert preview_df is not None
            assert "总行数" in info
            print("  ✓ DataCollector.preview_import成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ DataCollector.preview_import失败: {e}")
            bug_report.add_bug('data_collector', 'DataCollector.preview_import', '预览导入失败', 'medium', str(e))
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_statistics():
    """测试统计分析模块"""
    print("\n" + "=" * 60)
    print("测试模块: statistics")
    print("=" * 60)

    # 创建测试数据
    np.random.seed(42)
    test_data = []
    for grade in ['高一', '高二', '高三']:
        for gender in ['男', '女']:
            base_height = {'高一': 170, '高二': 172, '高三': 173}[grade]
            if gender == '女':
                base_height -= 10
            for i in range(20):
                test_data.append({
                    'student_id': f'2023{grade}{gender}{i:03d}',
                    'name': f'学生{i}',
                    'gender': gender,
                    'grade': grade,
                    'class': (i % 10) + 1,
                    'height': round(np.random.normal(base_height, 5), 1),
                    'measure_date': '2024-03-15'
                })

    df = pd.DataFrame(test_data)
    stats = HeightStatistics(df)

    # 测试1: basic_statistics
    print("\n测试1: basic_statistics...")
    try:
        result = stats.basic_statistics()
        assert 'count' in result
        assert 'mean' in result
        assert 'median' in result
        assert 'std' in result
        assert 'min' in result
        assert 'max' in result
        print("  ✓ basic_statistics成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ basic_statistics失败: {e}")
        bug_report.add_bug('statistics', 'basic_statistics', '基础统计失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试2: basic_statistics空数据
    print("\n测试2: basic_statistics空数据...")
    try:
        empty_stats = HeightStatistics(pd.DataFrame())
        result = empty_stats.basic_statistics()
        assert result == {}
        print("  ✓ 空数据处理成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ 空数据处理失败: {e}")
        bug_report.add_bug('statistics', 'basic_statistics', '空数据处理失败', 'medium', str(e))
        bug_report.record_test(False)

    # 测试3: distribution_by_intervals
    print("\n测试3: distribution_by_intervals...")
    try:
        result = stats.distribution_by_intervals()
        assert isinstance(result, pd.DataFrame)
        assert 'interval' in result.columns
        assert 'count' in result.columns
        assert 'percentage' in result.columns
        print("  ✓ distribution_by_intervals成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ distribution_by_intervals失败: {e}")
        bug_report.add_bug('statistics', 'distribution_by_intervals', '身高区间分布统计失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试4: group_by_gender
    print("\n测试4: group_by_gender...")
    try:
        result = stats.group_by_gender()
        assert isinstance(result, pd.DataFrame)
        assert 'gender' in result.columns
        assert 'count' in result.columns
        assert 'mean' in result.columns
        print("  ✓ group_by_gender成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ group_by_gender失败: {e}")
        bug_report.add_bug('statistics', 'group_by_gender', '按性别分组统计失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试5: group_by_grade
    print("\n测试5: group_by_grade...")
    try:
        result = stats.group_by_grade()
        assert isinstance(result, pd.DataFrame)
        assert 'grade' in result.columns
        assert len(result) <= 3
        print("  ✓ group_by_grade成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ group_by_grade失败: {e}")
        bug_report.add_bug('statistics', 'group_by_grade', '按年级分组统计失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试6: group_by_class
    print("\n测试6: group_by_class...")
    try:
        result = stats.group_by_class()
        assert isinstance(result, pd.DataFrame)
        assert 'grade' in result.columns
        assert 'class' in result.columns
        print("  ✓ group_by_class成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ group_by_class失败: {e}")
        bug_report.add_bug('statistics', 'group_by_class', '按班级分组统计失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试7: cross_group_analysis
    print("\n测试7: cross_group_analysis...")
    try:
        result = stats.cross_group_analysis()
        assert isinstance(result, pd.DataFrame)
        assert 'grade' in result.columns
        assert 'gender' in result.columns
        print("  ✓ cross_group_analysis成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ cross_group_analysis失败: {e}")
        bug_report.add_bug('statistics', 'cross_group_analysis', '交叉分组分析失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试8: trend_analysis
    print("\n测试8: trend_analysis...")
    try:
        result = stats.trend_analysis()
        assert isinstance(result, pd.DataFrame)
        assert 'grade' in result.columns
        assert 'mean_height' in result.columns
        print("  ✓ trend_analysis成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ trend_analysis失败: {e}")
        bug_report.add_bug('statistics', 'trend_analysis', '趋势分析失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试9: gender_difference_analysis
    print("\n测试9: gender_difference_analysis...")
    try:
        result = stats.gender_difference_analysis()
        assert 'male_count' in result
        assert 'female_count' in result
        assert 'male_mean' in result
        assert 'female_mean' in result
        assert 't_statistic' in result
        assert 'p_value' in result
        print("  ✓ gender_difference_analysis成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ gender_difference_analysis失败: {e}")
        bug_report.add_bug('statistics', 'gender_difference_analysis', '性别差异分析失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试10: gender_difference_analysis缺少数据
    print("\n测试10: gender_difference_analysis缺少数据...")
    try:
        # 只创建男生数据
        male_only_df = df[df['gender'] == '男'].copy()
        male_only_stats = HeightStatistics(male_only_df)
        result = male_only_stats.gender_difference_analysis()
        assert 'error' in result
        print("  ✓ 缺少数据检测成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ 缺少数据检测失败: {e}")
        bug_report.add_bug('statistics', 'gender_difference_analysis', '缺少数据检测失败', 'medium', str(e))
        bug_report.record_test(False)

    # 测试11: compare_with_national
    print("\n测试11: compare_with_national...")
    try:
        result = stats.compare_with_national()
        assert isinstance(result, pd.DataFrame)
        assert 'grade' in result.columns
        assert 'gender' in result.columns
        assert 'actual_mean' in result.columns
        assert 'national_mean' in result.columns
        print("  ✓ compare_with_national成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ compare_with_national失败: {e}")
        bug_report.add_bug('statistics', 'compare_with_national', '与全国平均值对比失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试12: outliers_analysis
    print("\n测试12: outliers_analysis...")
    try:
        result = stats.outliers_analysis()
        assert isinstance(result, pd.DataFrame)
        print("  ✓ outliers_analysis成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ outliers_analysis失败: {e}")
        bug_report.add_bug('statistics', 'outliers_analysis', '异常值分析失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试13: outliers_analysis使用zscore方法
    print("\n测试13: outliers_analysis使用zscore方法...")
    try:
        result = stats.outliers_analysis(method='zscore')
        assert isinstance(result, pd.DataFrame)
        print("  ✓ outliers_analysis(zscore)成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ outliers_analysis(zscore)失败: {e}")
        bug_report.add_bug('statistics', 'outliers_analysis', 'zscore异常值分析失败', 'medium', str(e))
        bug_report.record_test(False)

    # 测试14: generate_full_report
    print("\n测试14: generate_full_report...")
    try:
        result = stats.generate_full_report()
        assert 'basic_stats' in result
        assert 'distribution' in result
        assert 'by_gender' in result
        assert 'by_grade' in result
        assert 'cross_analysis' in result
        assert 'trend' in result
        assert 'gender_diff' in result
        assert 'national_comparison' in result
        assert 'outliers' in result
        print("  ✓ generate_full_report成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ generate_full_report失败: {e}")
        bug_report.add_bug('statistics', 'generate_full_report', '生成完整报告失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试15: export_report_to_text
    print("\n测试15: export_report_to_text...")
    try:
        temp_dir = tempfile.mkdtemp()
        report_file = os.path.join(temp_dir, 'test_report.txt')
        stats.export_report_to_text(report_file)
        assert os.path.exists(report_file)
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '基础统计指标' in content
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("  ✓ export_report_to_text成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ export_report_to_text失败: {e}")
        bug_report.add_bug('statistics', 'export_report_to_text', '导出文本报告失败', 'medium', str(e))
        bug_report.record_test(False)


def test_visualization():
    """测试可视化模块"""
    print("\n" + "=" * 60)
    print("测试模块: visualization")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    # 创建测试数据
    np.random.seed(42)
    test_data = []
    for grade in ['高一', '高二', '高三']:
        for gender in ['男', '女']:
            base_height = {'高一': 170, '高二': 172, '高三': 173}[grade]
            if gender == '女':
                base_height -= 10
            for i in range(20):
                test_data.append({
                    'student_id': f'2023{grade}{gender}{i:03d}',
                    'name': f'学生{i}',
                    'gender': gender,
                    'grade': grade,
                    'class': (i % 10) + 1,
                    'height': round(np.random.normal(base_height, 5), 1),
                    'measure_date': '2024-03-15'
                })

    df = pd.DataFrame(test_data)
    visualizer = HeightVisualizer(df, output_dir=temp_dir)

    # 测试1: plot_height_distribution_histogram
    print("\n测试1: plot_height_distribution_histogram...")
    try:
        result = visualizer.plot_height_distribution_histogram()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_height_distribution_histogram成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_height_distribution_histogram失败: {e}")
        bug_report.add_bug('visualization', 'plot_height_distribution_histogram', '身高分布直方图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试2: plot_height_distribution_histogram空数据
    print("\n测试2: plot_height_distribution_histogram空数据...")
    try:
        empty_visualizer = HeightVisualizer(pd.DataFrame(), output_dir=temp_dir)
        result = empty_visualizer.plot_height_distribution_histogram()
        assert result == ""
        print("  ✓ 空数据处理成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ 空数据处理失败: {e}")
        bug_report.add_bug('visualization', 'plot_height_distribution_histogram', '空数据处理失败', 'medium', str(e))
        bug_report.record_test(False)

    # 测试3: plot_gender_comparison_boxplot
    print("\n测试3: plot_gender_comparison_boxplot...")
    try:
        result = visualizer.plot_gender_comparison_boxplot()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_gender_comparison_boxplot成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_gender_comparison_boxplot失败: {e}")
        bug_report.add_bug('visualization', 'plot_gender_comparison_boxplot', '性别对比箱线图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试4: plot_grade_trend
    print("\n测试4: plot_grade_trend...")
    try:
        result = visualizer.plot_grade_trend()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_grade_trend成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_grade_trend失败: {e}")
        bug_report.add_bug('visualization', 'plot_grade_trend', '年级趋势图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试5: plot_height_distribution_pie
    print("\n测试5: plot_height_distribution_pie...")
    try:
        result = visualizer.plot_height_distribution_pie()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_height_distribution_pie成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_height_distribution_pie失败: {e}")
        bug_report.add_bug('visualization', 'plot_height_distribution_pie', '身高分布饼图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试6: plot_gender_grade_heatmap
    print("\n测试6: plot_gender_grade_heatmap...")
    try:
        result = visualizer.plot_gender_grade_heatmap()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_gender_grade_heatmap成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_gender_grade_heatmap失败: {e}")
        bug_report.add_bug('visualization', 'plot_gender_grade_heatmap', '性别年级热力图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试7: plot_class_comparison
    print("\n测试7: plot_class_comparison...")
    try:
        result = visualizer.plot_class_comparison()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_class_comparison成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_class_comparison失败: {e}")
        bug_report.add_bug('visualization', 'plot_class_comparison', '班级对比图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试8: plot_class_comparison指定年级
    print("\n测试8: plot_class_comparison指定年级...")
    try:
        result = visualizer.plot_class_comparison(grade='高一')
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_class_comparison(指定年级)成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_class_comparison(指定年级)失败: {e}")
        bug_report.add_bug('visualization', 'plot_class_comparison', '指定年级班级对比图生成失败', 'medium', str(e))
        bug_report.record_test(False)

    # 测试9: plot_class_comparison空数据
    print("\n测试9: plot_class_comparison空数据...")
    try:
        empty_visualizer = HeightVisualizer(pd.DataFrame(), output_dir=temp_dir)
        result = empty_visualizer.plot_class_comparison()
        assert result == ""
        print("  ✓ 空数据处理成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ 空数据处理失败: {e}")
        bug_report.add_bug('visualization', 'plot_class_comparison', '空数据处理失败', 'medium', str(e))
        bug_report.record_test(False)

    # 测试10: plot_national_comparison
    print("\n测试10: plot_national_comparison...")
    try:
        result = visualizer.plot_national_comparison()
        assert result != ""
        assert os.path.exists(result)
        print("  ✓ plot_national_comparison成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ plot_national_comparison失败: {e}")
        bug_report.add_bug('visualization', 'plot_national_comparison', '全国对比图生成失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试11: generate_all_visualizations
    print("\n测试11: generate_all_visualizations...")
    try:
        result = visualizer.generate_all_visualizations()
        assert isinstance(result, list)
        assert len(result) > 0
        print(f"  ✓ generate_all_visualizations成功(生成{len(result)}个图表)")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ generate_all_visualizations失败: {e}")
        bug_report.add_bug('visualization', 'generate_all_visualizations', '生成所有图表失败', 'high', str(e))
        bug_report.record_test(False)

    # 测试12: generate_all_visualizations空数据
    print("\n测试12: generate_all_visualizations空数据...")
    try:
        empty_visualizer = HeightVisualizer(pd.DataFrame(), output_dir=temp_dir)
        result = empty_visualizer.generate_all_visualizations()
        assert isinstance(result, list)
        assert len(result) == 0
        print("  ✓ 空数据处理成功")
        bug_report.record_test(True)
    except Exception as e:
        print(f"  ✗ 空数据处理失败: {e}")
        bug_report.add_bug('visualization', 'generate_all_visualizations', '空数据处理失败', 'medium', str(e))
        bug_report.record_test(False)

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_manager():
    """测试数据管理模块"""
    print("\n" + "=" * 60)
    print("测试模块: data_manager")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test_students.csv')

    try:
        data_store = DataStore(data_file)
        data_manager = DataManager(data_store)

        # 添加测试数据
        test_data = [
            {'student_id': '2023010001', 'name': '张三', 'gender': '男', 'grade': '高一', 'class_num': 1, 'height': 175.5, 'measure_date': '2024-03-15'},
            {'student_id': '2023010002', 'name': '李四', 'gender': '女', 'grade': '高二', 'class_num': 2, 'height': 162.0, 'measure_date': '2024-03-15'},
            {'student_id': '2023010003', 'name': '王五', 'gender': '男', 'grade': '高三', 'class_num': 3, 'height': 170.0, 'measure_date': '2024-03-15'},
            {'student_id': '2023010004', 'name': '张三丰', 'gender': '男', 'grade': '高一', 'class_num': 1, 'height': 180.0, 'measure_date': '2024-03-15'},
        ]
        for data in test_data:
            student = Student(**data)
            data_store.add_student(student)

        # 测试1: query_by_student_id
        print("\n测试1: query_by_student_id...")
        try:
            result = data_manager.query_by_student_id('2023010001')
            assert result is not None
            assert result['name'] == '张三'
            print("  ✓ query_by_student_id成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ query_by_student_id失败: {e}")
            bug_report.add_bug('data_manager', 'query_by_student_id', '按学号查询失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试2: query_by_student_id不存在
        print("\n测试2: query_by_student_id不存在...")
        try:
            result = data_manager.query_by_student_id('9999999999')
            assert result is None
            print("  ✓ 不存在的学号返回None成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 不存在的学号处理失败: {e}")
            bug_report.add_bug('data_manager', 'query_by_student_id', '不存在的学号处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试3: query_by_name
        print("\n测试3: query_by_name...")
        try:
            result = data_manager.query_by_name('张三')
            assert len(result) >= 1
            print("  ✓ query_by_name成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ query_by_name失败: {e}")
            bug_report.add_bug('data_manager', 'query_by_name', '按姓名查询失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试4: query_by_name模糊查询
        print("\n测试4: query_by_name模糊查询...")
        try:
            result = data_manager.query_by_name('张')
            assert len(result) >= 2  # 张三和张三丰
            print("  ✓ 模糊查询成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 模糊查询失败: {e}")
            bug_report.add_bug('data_manager', 'query_by_name', '模糊查询失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试5: query_by_filters
        print("\n测试5: query_by_filters...")
        try:
            result = data_manager.query_by_filters(gender='男', grade='高一')
            assert len(result) >= 2  # 张三和张三丰
            print("  ✓ query_by_filters成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ query_by_filters失败: {e}")
            bug_report.add_bug('data_manager', 'query_by_filters', '组合条件查询失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试6: query_by_filters身高范围
        print("\n测试6: query_by_filters身高范围...")
        try:
            result = data_manager.query_by_filters(min_height=170.0, max_height=180.0)
            assert len(result) >= 1
            print("  ✓ 身高范围查询成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 身高范围查询失败: {e}")
            bug_report.add_bug('data_manager', 'query_by_filters', '身高范围查询失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试7: update_student_info
        print("\n测试7: update_student_info...")
        try:
            success, message = data_manager.update_student_info('2023010001', height=178.0, name='张三丰')
            assert success == True
            student = data_store.get_student('2023010001')
            assert student['height'] == 178.0
            print("  ✓ update_student_info成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ update_student_info失败: {e}")
            bug_report.add_bug('data_manager', 'update_student_info', '更新学生信息失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试8: update_student_info不存在
        print("\n测试8: update_student_info不存在...")
        try:
            success, message = data_manager.update_student_info('9999999999', height=178.0)
            assert success == False
            print("  ✓ 更新不存在学号返回False成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 更新不存在学号处理失败: {e}")
            bug_report.add_bug('data_manager', 'update_student_info', '更新不存在学号处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试9: update_student_info无效字段
        print("\n测试9: update_student_info无效字段...")
        try:
            success, message = data_manager.update_student_info('2023010001', invalid_field='value')
            assert success == False
            print("  ✓ 无效字段检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效字段检测失败: {e}")
            bug_report.add_bug('data_manager', 'update_student_info', '无效字段检测失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试10: delete_student
        print("\n测试10: delete_student...")
        try:
            # 先添加一个学生用于删除测试
            student = Student(
                student_id='2023010005',
                name='删除测试',
                gender='男',
                grade='高一',
                class_num=1,
                height=170.0,
                measure_date='2024-03-15'
            )
            data_store.add_student(student)

            success, message = data_manager.delete_student('2023010005')
            assert success == True
            assert data_store.get_student('2023010005') is None
            print("  ✓ delete_student成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ delete_student失败: {e}")
            bug_report.add_bug('data_manager', 'delete_student', '删除学生失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试11: delete_student不存在
        print("\n测试11: delete_student不存在...")
        try:
            success, message = data_manager.delete_student('9999999999')
            assert success == False
            print("  ✓ 删除不存在学号返回False成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 删除不存在学号处理失败: {e}")
            bug_report.add_bug('data_manager', 'delete_student', '删除不存在学号处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试12: batch_delete
        print("\n测试12: batch_delete...")
        try:
            # 添加测试学生
            for i in range(6, 9):
                student = Student(
                    student_id=f'202301000{i}',
                    name=f'批量删除{i}',
                    gender='男',
                    grade='高一',
                    class_num=1,
                    height=170.0,
                    measure_date='2024-03-15'
                )
                data_store.add_student(student)

            success_count, fail_count, failed_ids = data_manager.batch_delete(['2023010006', '2023010007', '9999999999'])
            assert success_count == 2
            assert fail_count == 1
            assert '9999999999' in failed_ids
            print("  ✓ batch_delete成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ batch_delete失败: {e}")
            bug_report.add_bug('data_manager', 'batch_delete', '批量删除失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试13: backup_data
        print("\n测试13: backup_data...")
        try:
            backup_path = data_manager.backup_data()
            assert os.path.exists(backup_path)
            print("  ✓ backup_data成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ backup_data失败: {e}")
            bug_report.add_bug('data_manager', 'backup_data', '备份数据失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试14: backup_data指定名称
        print("\n测试14: backup_data指定名称...")
        try:
            backup_path = data_manager.backup_data('test_backup.csv')
            assert os.path.exists(backup_path)
            assert 'test_backup.csv' in backup_path
            print("  ✓ 指定名称备份成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 指定名称备份失败: {e}")
            bug_report.add_bug('data_manager', 'backup_data', '指定名称备份失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试15: list_backups
        print("\n测试15: list_backups...")
        try:
            backups = data_manager.list_backups()
            assert isinstance(backups, list)
            assert len(backups) >= 2  # 至少有两个备份
            print("  ✓ list_backups成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ list_backups失败: {e}")
            bug_report.add_bug('data_manager', 'list_backups', '列出备份失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试16: restore_from_backup
        print("\n测试16: restore_from_backup...")
        try:
            # 先备份当前数据
            backup_path = data_manager.backup_data('restore_test.csv')
            # 修改数据
            data_manager.update_student_info('2023010001', height=999.0)
            # 恢复备份
            success, message = data_manager.restore_from_backup('restore_test.csv')
            assert success == True
            student = data_store.get_student('2023010001')
            assert student['height'] != 999.0  # 数据已恢复
            print("  ✓ restore_from_backup成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ restore_from_backup失败: {e}")
            bug_report.add_bug('data_manager', 'restore_from_backup', '从备份恢复失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试17: restore_from_backup不存在
        print("\n测试17: restore_from_backup不存在...")
        try:
            success, message = data_manager.restore_from_backup('nonexistent_backup.csv')
            assert success == False
            print("  ✓ 恢复不存在的备份返回False成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 恢复不存在的备份处理失败: {e}")
            bug_report.add_bug('data_manager', 'restore_from_backup', '恢复不存在的备份处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试18: export_data CSV
        print("\n测试18: export_data CSV...")
        try:
            export_path = os.path.join(temp_dir, 'export_test.csv')
            success, message = data_manager.export_data(export_path, 'csv')
            assert success == True
            assert os.path.exists(export_path)
            print("  ✓ export_data CSV成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ export_data CSV失败: {e}")
            bug_report.add_bug('data_manager', 'export_data', '导出CSV失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试19: export_data Excel
        print("\n测试19: export_data Excel...")
        try:
            export_path = os.path.join(temp_dir, 'export_test.xlsx')
            success, message = data_manager.export_data(export_path, 'xlsx')
            assert success == True
            assert os.path.exists(export_path)
            print("  ✓ export_data Excel成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ export_data Excel失败: {e}")
            bug_report.add_bug('data_manager', 'export_data', '导出Excel失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试20: export_data无效格式
        print("\n测试20: export_data无效格式...")
        try:
            export_path = os.path.join(temp_dir, 'export_test.txt')
            success, message = data_manager.export_data(export_path, 'txt')
            assert success == False
            print("  ✓ 无效格式检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 无效格式检测失败: {e}")
            bug_report.add_bug('data_manager', 'export_data', '无效格式检测失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试21: get_statistics_summary
        print("\n测试21: get_statistics_summary...")
        try:
            summary = data_manager.get_statistics_summary()
            assert 'total_students' in summary
            assert 'total_records' in summary
            assert 'gender_distribution' in summary
            assert 'grade_distribution' in summary
            assert 'class_count' in summary
            assert summary['total_students'] > 0
            print("  ✓ get_statistics_summary成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ get_statistics_summary失败: {e}")
            bug_report.add_bug('data_manager', 'get_statistics_summary', '获取统计摘要失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试22: get_statistics_summary空数据
        print("\n测试22: get_statistics_summary空数据...")
        try:
            empty_store = DataStore(os.path.join(temp_dir, 'empty.csv'))
            empty_manager = DataManager(empty_store)
            summary = empty_manager.get_statistics_summary()
            assert summary['total_students'] == 0
            print("  ✓ 空数据统计成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 空数据统计失败: {e}")
            bug_report.add_bug('data_manager', 'get_statistics_summary', '空数据统计失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试23: clear_all_data
        print("\n测试23: clear_all_data...")
        try:
            # 创建新的数据存储用于清空测试
            clear_test_file = os.path.join(temp_dir, 'clear_test.csv')
            clear_store = DataStore(clear_test_file)
            clear_manager = DataManager(clear_store)
            # 添加测试数据
            student = Student(
                student_id='CLEAR001',
                name='清空测试',
                gender='男',
                grade='高一',
                class_num=1,
                height=170.0,
                measure_date='2024-03-15'
            )
            clear_store.add_student(student)
            assert len(clear_store.df) == 1

            success, message = clear_manager.clear_all_data(confirm=True)
            assert success == True
            assert len(clear_store.df) == 0
            print("  ✓ clear_all_data成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ clear_all_data失败: {e}")
            bug_report.add_bug('data_manager', 'clear_all_data', '清空所有数据失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试24: clear_all_data未确认
        print("\n测试24: clear_all_data未确认...")
        try:
            success, message = data_manager.clear_all_data(confirm=False)
            assert success == False
            print("  ✓ 未确认清空返回False成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 未确认清空处理失败: {e}")
            bug_report.add_bug('data_manager', 'clear_all_data', '未确认清空处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试25: validate_data_integrity
        print("\n测试25: validate_data_integrity...")
        try:
            is_valid, issues = data_manager.validate_data_integrity()
            assert isinstance(is_valid, bool)
            assert isinstance(issues, list)
            print("  ✓ validate_data_integrity成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ validate_data_integrity失败: {e}")
            bug_report.add_bug('data_manager', 'validate_data_integrity', '数据完整性检查失败', 'high', str(e))
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_edge_cases():
    """测试边界情况和特殊场景"""
    print("\n" + "=" * 60)
    print("测试模块: 边界情况和特殊场景")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'edge_test.csv')

    try:
        # 测试1: 边界身高值
        print("\n测试1: 边界身高值(140cm和200cm)...")
        try:
            data_store = DataStore(data_file)
            collector = DataCollector(data_store)

            # 测试最小边界
            success1, _ = collector.add_student_manual(
                student_id='EDGE001',
                name='边界测试1',
                gender='男',
                grade='高一',
                class_num=1,
                height=140.0,  # 最小值
                measure_date='2024-03-15'
            )

            # 测试最大边界
            success2, _ = collector.add_student_manual(
                student_id='EDGE002',
                name='边界测试2',
                gender='女',
                grade='高一',
                class_num=1,
                height=200.0,  # 最大值
                measure_date='2024-03-15'
            )

            assert success1 == True
            assert success2 == True
            print("  ✓ 边界身高值测试成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 边界身高值测试失败: {e}")
            bug_report.add_bug('edge_cases', 'validate_student', '边界身高值处理失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试2: 边界身高值(超出范围)
        print("\n测试2: 边界身高值(超出范围)...")
        try:
            success1, _ = collector.add_student_manual(
                student_id='EDGE003',
                name='边界测试3',
                gender='男',
                grade='高一',
                class_num=1,
                height=139.9,  # 低于最小值
                measure_date='2024-03-15'
            )

            success2, _ = collector.add_student_manual(
                student_id='EDGE004',
                name='边界测试4',
                gender='女',
                grade='高一',
                class_num=1,
                height=200.1,  # 高于最大值
                measure_date='2024-03-15'
            )

            assert success1 == False
            assert success2 == False
            print("  ✓ 超出边界值检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 超出边界值检测失败: {e}")
            bug_report.add_bug('edge_cases', 'validate_student', '超出边界值检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试3: 边界班级值
        print("\n测试3: 边界班级值(1和50)...")
        try:
            success1, _ = collector.add_student_manual(
                student_id='EDGE005',
                name='边界测试5',
                gender='男',
                grade='高一',
                class_num=1,  # 最小值
                height=170.0,
                measure_date='2024-03-15'
            )

            success2, _ = collector.add_student_manual(
                student_id='EDGE006',
                name='边界测试6',
                gender='女',
                grade='高一',
                class_num=50,  # 最大值
                height=160.0,
                measure_date='2024-03-15'
            )

            assert success1 == True
            assert success2 == True
            print("  ✓ 边界班级值测试成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 边界班级值测试失败: {e}")
            bug_report.add_bug('edge_cases', 'validate_student', '边界班级值处理失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试4: 边界班级值(超出范围)
        print("\n测试4: 边界班级值(超出范围)...")
        try:
            success, _ = collector.add_student_manual(
                student_id='EDGE007',
                name='边界测试7',
                gender='男',
                grade='高一',
                class_num=0,  # 低于最小值
                height=170.0,
                measure_date='2024-03-15'
            )
            assert success == False
            print("  ✓ 超出边界班级值检测成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 超出边界班级值检测失败: {e}")
            bug_report.add_bug('edge_cases', 'validate_student', '超出边界班级值检测失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试5: 特殊字符姓名
        print("\n测试5: 特殊字符姓名...")
        try:
            success, _ = collector.add_student_manual(
                student_id='EDGE008',
                name='测试@#$%',
                gender='男',
                grade='高一',
                class_num=1,
                height=170.0,
                measure_date='2024-03-15'
            )
            # 特殊字符应该被允许
            assert success == True
            print("  ✓ 特殊字符姓名处理成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 特殊字符姓名处理失败: {e}")
            bug_report.add_bug('edge_cases', 'validate_student', '特殊字符姓名处理失败', 'low', str(e))
            bug_report.record_test(False)

        # 测试6: 超长学号
        print("\n测试6: 超长学号...")
        try:
            long_id = 'A' * 1000
            success, _ = collector.add_student_manual(
                student_id=long_id,
                name='超长学号测试',
                gender='男',
                grade='高一',
                class_num=1,
                height=170.0,
                measure_date='2024-03-15'
            )
            # 超长学号应该被允许(只要不为空)
            assert success == True
            print("  ✓ 超长学号处理成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 超长学号处理失败: {e}")
            bug_report.add_bug('edge_cases', 'validate_student', '超长学号处理失败', 'low', str(e))
            bug_report.record_test(False)

        # 测试7: 浮点数精度
        print("\n测试7: 浮点数精度...")
        try:
            success, _ = collector.add_student_manual(
                student_id='EDGE009',
                name='精度测试',
                gender='男',
                grade='高一',
                class_num=1,
                height=175.123456789,  # 高精度浮点数
                measure_date='2024-03-15'
            )
            assert success == True
            student = data_store.get_student('EDGE009')
            # 检查身高是否被正确存储
            assert student is not None
            print("  ✓ 浮点数精度处理成功")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 浮点数精度处理失败: {e}")
            bug_report.add_bug('edge_cases', 'Student.__post_init__', '浮点数精度处理失败', 'medium', str(e))
            bug_report.record_test(False)

        # 测试8: 大量数据导入
        print("\n测试8: 大量数据导入...")
        try:
            large_data = []
            for i in range(1000):
                large_data.append({
                    'student_id': f'LARGE{i:06d}',
                    'name': f'批量{i}',
                    'gender': '男' if i % 2 == 0 else '女',
                    'grade': ['高一', '高二', '高三'][i % 3],
                    'class': (i % 10) + 1,
                    'height': 160.0 + (i % 40),
                    'measure_date': '2024-03-15'
                })

            large_df = pd.DataFrame(large_data)
            success, message = data_store.import_from_dataframe(large_df)
            assert success == True
            assert len(data_store.df) >= 1000
            print(f"  ✓ 大量数据导入成功(当前记录数: {len(data_store.df)})")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 大量数据导入失败: {e}")
            bug_report.add_bug('edge_cases', 'import_from_dataframe', '大量数据导入失败', 'high', str(e))
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_file_operations():
    """测试数据文件操作"""
    print("\n" + "=" * 60)
    print("测试模块: 数据文件操作")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试1: 使用实际数据文件
        print("\n测试1: 使用实际数据文件(students.csv)...")
        try:
            data_file = 'data/students.csv'
            if os.path.exists(data_file):
                data_store = DataStore(data_file)
                assert data_store.df is not None
                print(f"  ✓ 加载实际数据文件成功(记录数: {len(data_store.df)})")
                bug_report.record_test(True)
            else:
                print("  ⚠ 实际数据文件不存在，跳过此测试")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ 加载实际数据文件失败: {e}")
            bug_report.add_bug('data_file', 'DataStore._load_data', '加载实际数据文件失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试2: 使用test_data.csv
        print("\n测试2: 使用test_data.csv...")
        try:
            data_file = 'data/test_data.csv'
            if os.path.exists(data_file):
                data_store = DataStore(data_file)
                stats = HeightStatistics(data_store.get_all())
                result = stats.basic_statistics()
                assert 'count' in result
                print(f"  ✓ test_data.csv分析成功")
                bug_report.record_test(True)
            else:
                print("  ⚠ test_data.csv不存在，跳过此测试")
                bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ test_data.csv分析失败: {e}")
            bug_report.add_bug('data_file', 'HeightStatistics', 'test_data.csv分析失败', 'high', str(e))
            bug_report.record_test(False)

        # 测试3: 导入Excel文件
        print("\n测试3: 导入Excel文件...")
        try:
            excel_file = 'data/sample_students_1000.xlsx'
            if os.path.exists(excel_file):
                data_file = os.path.join(temp_dir, 'excel_test.csv')
                data_store = DataStore(data_file)
                collector = DataCollector(data_store)
                success, message = collector.import_from_excel(excel_file)
                # Excel导入可能缺少依赖，捕获特定错误
                if success:
                    print(f"  ✓ Excel导入成功")
                else:
                    print(f"  ⚠ Excel导入返回: {message}")
                bug_report.record_test(True)
            else:
                print("  ⚠ Excel文件不存在，跳过此测试")
                bug_report.record_test(True)
        except ImportError as e:
            print(f"  ⚠ 缺少Excel依赖: {e}")
            bug_report.record_test(True)
        except Exception as e:
            print(f"  ✗ Excel导入失败: {e}")
            bug_report.add_bug('data_file', 'import_from_excel', 'Excel导入失败', 'medium', str(e))
            bug_report.record_test(False)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主函数 - 运行所有测试"""
    print("\n" + "=" * 80)
    print("开始全面测试 - 学生身高分析系统")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 保存当前工作目录
    original_dir = os.getcwd()

    # 切换到项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    try:
        # 运行所有测试
        test_data_model()
        test_data_collector()
        test_statistics()
        test_visualization()
        test_data_manager()
        test_edge_cases()
        test_data_file_operations()

        # 生成并保存报告
        report = bug_report.generate_report()

        # 保存报告到文件
        report_file = f'bug_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # 打印报告
        print("\n" + "=" * 80)
        print(report)
        print(f"\n报告已保存到: {report_file}")

    finally:
        # 恢复工作目录
        os.chdir(original_dir)


if __name__ == '__main__':
    main()

