#!/usr/bin/env python3
"""快速测试修复的bug"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_model import DataStore, Student
from modules.data_collector import DataCollector, DataValidator
from modules.data_manager import DataManager
from modules.statistics import HeightStatistics

import pandas as pd
import numpy as np

def test_duplicate_student_id():
    """测试Bug #1: CSV导入重复学号"""
    print("\n=== 测试Bug #1: CSV导入重复学号 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)

        # 创建包含重复学号的DataFrame
        df = pd.DataFrame({
            'student_id': ['2023010001', '2023010001', '2023010002'],
            'name': ['张三', '张三重复', '李四'],
            'gender': ['男', '男', '女'],
            'grade': ['高一', '高一', '高二'],
            'class': [1, 1, 2],
            'height': [175.5, 176.0, 162.0],
            'measure_date': ['2024-03-15', '2024-03-15', '2024-03-15']
        })

        success, message = data_store.import_from_dataframe(df)
        if not success and '重复学号' in message:
            print("✓ Bug #1 已修复: 检测到CSV内部重复学号")
            return True
        else:
            print(f"✗ Bug #1 未修复: {message}")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_regex_vulnerability():
    """测试Bug #3: 正则表达式漏洞"""
    print("\n=== 测试Bug #3: 正则表达式漏洞 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        # 添加测试数据
        collector.add_student_manual('REG001', '张三', '男', '高一', 1, 175.5, '2024-03-15')

        data_manager = DataManager(data_store)

        # 测试正则特殊字符
        special_chars = ['*', '+', '?', '[', '(', '{', '^', '$', '\\', '|']
        all_passed = True

        for char in special_chars:
            try:
                result = data_manager.query_by_name(char)
                print(f"  ✓ 字符 '{char}' 查询成功")
            except Exception as e:
                print(f"  ✗ 字符 '{char}' 查询失败: {e}")
                all_passed = False

        if all_passed:
            print("✓ Bug #3 已修复: 正则特殊字符不再导致异常")
        return all_passed
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_backup_directory():
    """测试Bug #4: 备份目录不存在时异常"""
    print("\n=== 测试Bug #4: 备份目录不存在时异常 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)
        data_manager = DataManager(data_store)

        # 删除备份目录
        if os.path.exists(data_manager.backup_dir):
            shutil.rmtree(data_manager.backup_dir)

        try:
            backup_path = data_manager.backup_data('test.csv')
            if os.path.exists(backup_path):
                print("✓ Bug #4 已修复: 备份目录自动创建")
                return True
            else:
                print("✗ Bug #4 未修复: 备份文件未创建")
                return False
        except Exception as e:
            print(f"✗ Bug #4 未修复: {e}")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_corrupted_backup():
    """测试Bug #5: 损坏备份文件恢复成功"""
    print("\n=== 测试Bug #5: 损坏备份文件恢复成功 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)
        data_manager = DataManager(data_store)

        # 创建损坏的备份文件
        os.makedirs(data_manager.backup_dir, exist_ok=True)
        corrupted_backup = os.path.join(data_manager.backup_dir, 'corrupted.csv')
        with open(corrupted_backup, 'w') as f:
            f.write('这不是有效的CSV数据\n一些随机文本')

        success, message = data_manager.restore_from_backup('corrupted.csv')
        if not success:
            print(f"✓ Bug #5 已修复: 损坏备份文件被拒绝 - {message}")
            return True
        else:
            print("✗ Bug #5 未修复: 损坏备份文件被成功恢复")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_infinity_value():
    """测试Bug #7: Infinity值被接受"""
    print("\n=== 测试Bug #7: Infinity值被接受 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)

        # 直接创建包含Infinity的DataFrame
        data_store.df = pd.DataFrame({
            'student_id': ['INF001', 'INF002'],
            'name': ['张三', '李四'],
            'gender': ['男', '女'],
            'grade': ['高一', '高二'],
            'class': [1, 2],
            'height': [175.5, float('inf')],
            'measure_date': ['2024-03-15', '2024-03-15']
        })

        stats = HeightStatistics(data_store.get_all())
        result = stats.basic_statistics()

        # 检查是否过滤了Infinity
        if result.get('count') == 1 and result.get('max', 0) < 1000:
            print("✓ Bug #7 已修复: Infinity值被正确过滤")
            return True
        else:
            print(f"✗ Bug #7 未修复: 统计结果包含Infinity - {result}")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_future_date():
    """测试Bug #11: 未来日期被接受"""
    print("\n=== 测试Bug #11: 未来日期被接受 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        success, message = collector.add_student_manual(
            'FUT001', '测试', '男', '高一', 1, 175.5, future_date
        )

        if not success and '未来' in message:
            print("✓ Bug #11 已修复: 未来日期被正确拒绝")
            return True
        else:
            print(f"✗ Bug #11 未修复: 未来日期被接受 - {message}")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_early_date():
    """测试Bug #12: 极早日期被接受"""
    print("\n=== 测试Bug #12: 极早日期被接受 ===")
    temp_dir = tempfile.mkdtemp()
    data_file = os.path.join(temp_dir, 'test.csv')

    try:
        data_store = DataStore(data_file)
        collector = DataCollector(data_store)

        success, message = collector.add_student_manual(
            'EAR001', '测试', '男', '高一', 1, 175.5, '1900-01-01'
        )

        if not success and '2000' in message:
            print("✓ Bug #12 已修复: 极早日期被正确拒绝")
            return True
        else:
            print(f"✗ Bug #12 未修复: 极早日期被接受 - {message}")
            return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    print("=" * 60)
    print("学生身高分析系统 - Bug修复验证测试")
    print("=" * 60)

    results = []
    results.append(("Bug #1: CSV导入重复学号", test_duplicate_student_id()))
    results.append(("Bug #3: 正则表达式漏洞", test_regex_vulnerability()))
    results.append(("Bug #4: 备份目录不存在", test_backup_directory()))
    results.append(("Bug #5: 损坏备份文件", test_corrupted_backup()))
    results.append(("Bug #7: Infinity值处理", test_infinity_value()))
    results.append(("Bug #11: 未来日期", test_future_date()))
    results.append(("Bug #12: 极早日期", test_early_date()))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 个测试通过")

if __name__ == '__main__':
    main()
