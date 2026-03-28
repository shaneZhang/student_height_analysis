#!/usr/bin/env python3
"""
高中学生身高情况统计分析系统
主程序入口
"""

import os
import sys
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_model import DataStore
from modules.data_collector import DataCollector, DataValidator
from modules.statistics import HeightStatistics
from modules.visualization import HeightVisualizer
from modules.data_manager import DataManager


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_menu():
    """打印主菜单"""
    print_header("高中学生身高情况统计分析系统")
    print("""
    1. 数据录入
    2. 数据导入
    3. 数据统计分析
    4. 数据可视化
    5. 数据查询
    6. 数据管理
    7. 生成报告
    8. 系统管理
    0. 退出系统
    """)


def data_entry_menu(collector: DataCollector):
    """数据录入菜单"""
    print_header("数据录入")

    print("请输入学生信息（输入空学号返回主菜单）：")

    while True:
        student_id = input("学号: ").strip()
        if not student_id:
            break

        name = input("姓名: ").strip()
        gender = input("性别 (男/女): ").strip()
        grade = input("年级 (高一/高二/高三): ").strip()

        try:
            class_num = int(input("班级: "))
            height = float(input("身高 (cm): "))
        except ValueError:
            print("错误: 班级和身高必须是数字")
            continue

        measure_date = input("测量日期 (YYYY-MM-DD，直接回车使用今天): ").strip()
        if not measure_date:
            measure_date = datetime.now().strftime('%Y-%m-%d')

        success, message = collector.add_student_manual(
            student_id, name, gender, grade, class_num, height, measure_date
        )

        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")


def data_import_menu(collector: DataCollector):
    """数据导入菜单"""
    print_header("数据导入")

    print("""
    1. 从CSV文件导入
    2. 从Excel文件导入
    3. 下载导入模板
    4. 预览导入文件
    0. 返回主菜单
    """)

    choice = input("请选择: ").strip()

    if choice == '1':
        file_path = input("请输入CSV文件路径: ").strip()
        if os.path.exists(file_path):
            success, message = collector.import_from_csv(file_path)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print(f"✗ 文件不存在: {file_path}")

    elif choice == '2':
        file_path = input("请输入Excel文件路径: ").strip()
        if os.path.exists(file_path):
            success, message = collector.import_from_excel(file_path)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print(f"✗ 文件不存在: {file_path}")

    elif choice == '3':
        template_path = input("请输入模板保存路径 (如: template.csv): ").strip()
        try:
            collector.save_template(template_path)
            print(f"✓ 模板已保存到: {template_path}")
        except Exception as e:
            print(f"✗ 保存模板失败: {e}")

    elif choice == '4':
        file_path = input("请输入文件路径: ").strip()
        if os.path.exists(file_path):
            preview_df, info = collector.preview_import(file_path)
            print(f"\n预览信息:\n{info}")
            if preview_df is not None and not preview_df.empty:
                print("\n前10行数据预览:")
                print(preview_df.to_string())
        else:
            print(f"✗ 文件不存在: {file_path}")


def statistics_menu(data_store: DataStore):
    """统计分析菜单"""
    print_header("数据统计分析")

    df = data_store.get_all()
    if df.empty:
        print("暂无数据，请先录入或导入数据")
        return

    stats = HeightStatistics(df)

    print("""
    1. 基础统计指标
    2. 身高区间分布
    3. 按性别统计
    4. 按年级统计
    5. 交叉分组统计
    6. 年级趋势分析
    7. 性别差异分析
    8. 与全国平均对比
    9. 异常值分析
    10. 完整统计报告
    0. 返回主菜单
    """)

    choice = input("请选择: ").strip()

    if choice == '1':
        result = stats.basic_statistics()
        print("\n基础统计指标:")
        for key, value in result.items():
            print(f"  {key}: {value}")

    elif choice == '2':
        result = stats.distribution_by_intervals()
        print("\n身高区间分布:")
        print(result.to_string(index=False))

    elif choice == '3':
        result = stats.group_by_gender()
        print("\n按性别统计:")
        print(result.to_string(index=False))

    elif choice == '4':
        result = stats.group_by_grade()
        print("\n按年级统计:")
        print(result.to_string(index=False))

    elif choice == '5':
        result = stats.cross_group_analysis()
        print("\n交叉分组统计:")
        print(result.to_string(index=False))

    elif choice == '6':
        result = stats.trend_analysis()
        print("\n年级趋势分析:")
        print(result.to_string(index=False))

    elif choice == '7':
        result = stats.gender_difference_analysis()
        print("\n性别差异分析:")
        for key, value in result.items():
            print(f"  {key}: {value}")

    elif choice == '8':
        result = stats.compare_with_national()
        print("\n与全国平均值对比:")
        print(result.to_string(index=False))

    elif choice == '9':
        result = stats.outliers_analysis()
        print("\n异常值分析:")
        if result.empty:
            print("未发现异常值")
        else:
            print(result.to_string())

    elif choice == '10':
        report = stats.generate_full_report()
        print("\n完整统计报告已生成")

        # 保存文本报告
        report_path = f'reports/statistics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        stats.export_report_to_text(report_path)
        print(f"报告已保存到: {report_path}")


def visualization_menu(data_store: DataStore):
    """数据可视化菜单"""
    print_header("数据可视化")

    df = data_store.get_all()
    if df.empty:
        print("暂无数据，请先录入或导入数据")
        return

    visualizer = HeightVisualizer(df)

    print("""
    1. 生成所有图表
    2. 身高分布直方图
    3. 男女生对比箱线图
    4. 年级趋势图
    5. 身高分布饼图
    6. 性别-年级热力图
    7. 班级对比图
    8. 全国对比图
    0. 返回主菜单
    """)

    choice = input("请选择: ").strip()

    if choice == '1':
        print("正在生成所有图表...")
        files = visualizer.generate_all_visualizations()
        print(f"✓ 已生成 {len(files)} 个图表:")
        for f in files:
            print(f"  - {f}")

    elif choice == '2':
        path = visualizer.plot_height_distribution_histogram()
        print(f"✓ 图表已保存: {path}")

    elif choice == '3':
        path = visualizer.plot_gender_comparison_boxplot()
        print(f"✓ 图表已保存: {path}")

    elif choice == '4':
        path = visualizer.plot_grade_trend()
        print(f"✓ 图表已保存: {path}")

    elif choice == '5':
        path = visualizer.plot_height_distribution_pie()
        print(f"✓ 图表已保存: {path}")

    elif choice == '6':
        path = visualizer.plot_gender_grade_heatmap()
        print(f"✓ 图表已保存: {path}")

    elif choice == '7':
        grade = input("请输入年级 (高一/高二/高三，直接回车查看全部): ").strip()
        grade = grade if grade else None
        path = visualizer.plot_class_comparison(grade=grade)
        print(f"✓ 图表已保存: {path}")

    elif choice == '8':
        path = visualizer.plot_national_comparison()
        print(f"✓ 图表已保存: {path}")


def query_menu(data_manager: DataManager):
    """数据查询菜单"""
    print_header("数据查询")

    print("""
    1. 按学号查询
    2. 按姓名查询
    3. 组合条件查询
    4. 查看数据概览
    0. 返回主菜单
    """)

    choice = input("请选择: ").strip()

    if choice == '1':
        student_id = input("请输入学号: ").strip()
        result = data_manager.query_by_student_id(student_id)
        if result is not None:
            print("\n查询结果:")
            print(result)
        else:
            print(f"未找到学号 {student_id} 的记录")

    elif choice == '2':
        name = input("请输入姓名（支持模糊查询）: ").strip()
        result = data_manager.query_by_name(name)
        if not result.empty:
            print(f"\n找到 {len(result)} 条记录:")
            print(result.to_string())
        else:
            print(f"未找到姓名包含 '{name}' 的记录")

    elif choice == '3':
        print("请输入查询条件（直接回车跳过该条件）:")
        gender = input("性别 (男/女): ").strip()
        grade = input("年级 (高一/高二/高三): ").strip()

        class_num = input("班级: ").strip()
        class_num = int(class_num) if class_num else None

        min_height = input("最小身高: ").strip()
        min_height = float(min_height) if min_height else None

        max_height = input("最大身高: ").strip()
        max_height = float(max_height) if max_height else None

        result = data_manager.query_by_filters(
            gender=gender or None,
            grade=grade or None,
            class_num=class_num,
            min_height=min_height,
            max_height=max_height
        )

        if not result.empty:
            print(f"\n找到 {len(result)} 条记录:")
            print(result.to_string())
        else:
            print("未找到符合条件的记录")

    elif choice == '4':
        summary = data_manager.get_statistics_summary()
        print("\n数据概览:")
        for key, value in summary.items():
            print(f"  {key}: {value}")


def data_management_menu(data_manager: DataManager):
    """数据管理菜单"""
    print_header("数据管理")

    print("""
    1. 修改学生信息
    2. 删除学生记录
    3. 导出数据
    4. 数据备份
    5. 查看备份列表
    6. 从备份恢复
    7. 数据完整性检查
    0. 返回主菜单
    """)

    choice = input("请选择: ").strip()

    if choice == '1':
        student_id = input("请输入要修改的学号: ").strip()
        print("请输入要修改的字段（直接回车跳过）:")

        updates = {}
        name = input("姓名: ").strip()
        if name:
            updates['name'] = name

        gender = input("性别 (男/女): ").strip()
        if gender:
            updates['gender'] = gender

        grade = input("年级 (高一/高二/高三): ").strip()
        if grade:
            updates['grade'] = grade

        class_str = input("班级: ").strip()
        if class_str:
            updates['class'] = int(class_str)

        height_str = input("身高: ").strip()
        if height_str:
            updates['height'] = float(height_str)

        if updates:
            success, message = data_manager.update_student_info(student_id, **updates)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print("没有要修改的字段")

    elif choice == '2':
        student_id = input("请输入要删除的学号: ").strip()
        confirm = input(f"确认删除学号 {student_id} 的记录? (yes/no): ").strip().lower()
        if confirm == 'yes':
            success, message = data_manager.delete_student(student_id)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print("已取消删除")

    elif choice == '3':
        file_path = input("请输入导出文件路径: ").strip()
        format_type = input("格式 (csv/excel): ").strip().lower()
        success, message = data_manager.export_data(file_path, format_type)
        print(f"{'✓' if success else '✗'} {message}")

    elif choice == '4':
        backup_path = data_manager.backup_data()
        print(f"✓ 数据已备份到: {backup_path}")

    elif choice == '5':
        backups = data_manager.list_backups()
        if backups:
            print("\n备份列表:")
            for i, backup in enumerate(backups, 1):
                print(f"  {i}. {backup}")
        else:
            print("暂无备份")

    elif choice == '6':
        backups = data_manager.list_backups()
        if not backups:
            print("暂无备份")
            return

        print("\n备份列表:")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. {backup}")

        try:
            idx = int(input("请选择要恢复的备份编号: ")) - 1
            if 0 <= idx < len(backups):
                confirm = input("恢复将覆盖当前数据，是否继续? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    success, message = data_manager.restore_from_backup(backups[idx])
                    print(f"{'✓' if success else '✗'} {message}")
            else:
                print("无效的编号")
        except ValueError:
            print("请输入有效的数字")

    elif choice == '7':
        is_valid, issues = data_manager.validate_data_integrity()
        if is_valid:
            print("✓ 数据完整性检查通过")
        else:
            print("✗ 发现以下问题:")
            for issue in issues:
                print(f"  - {issue}")


def system_menu(data_store: DataStore, data_manager: DataManager):
    """系统管理菜单"""
    print_header("系统管理")

    print("""
    1. 查看系统信息
    2. 清空所有数据
    3. 初始化示例数据
    0. 返回主菜单
    """)

    choice = input("请选择: ").strip()

    if choice == '1':
        print("\n系统信息:")
        print(f"  数据文件: {data_store.data_file}")
        print(f"  记录数量: {len(data_store.df)}")
        print(f"  备份目录: {data_manager.backup_dir}")

    elif choice == '2':
        confirm = input("警告: 此操作将删除所有数据! 输入 'DELETE' 确认: ").strip()
        if confirm == 'DELETE':
            success, message = data_manager.clear_all_data(confirm=True)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print("已取消")

    elif choice == '3':
        confirm = input("将生成示例数据，是否继续? (yes/no): ").strip().lower()
        if confirm == 'yes':
            generate_sample_data(data_store)


def generate_sample_data(data_store: DataStore, count: int = 200):
    """生成示例数据"""
    import random
    from modules.data_model import Student

    first_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
                   '勇', '艳', '杰', '娟', '涛', '明', '超', '秀', '霞', '平']
    last_names = ['张', '王', '李', '刘', '陈', '杨', '黄', '赵', '周', '吴',
                  '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']

    grades = ['高一', '高二', '高三']
    genders = ['男', '女']

    success_count = 0

    for i in range(count):
        grade = random.choice(grades)
        gender = random.choice(genders)
        class_num = random.randint(1, 10)

        # 根据年级和性别设置基础身高
        base_heights = {
            '高一': {'男': 170, '女': 160},
            '高二': {'男': 172, '女': 161},
            '高三': {'男': 173, '女': 162}
        }

        base_height = base_heights[grade][gender]
        height = random.gauss(base_height, 6)  # 正态分布
        height = round(max(145, min(195, height)), 1)

        name = random.choice(last_names) + random.choice(first_names)
        student_id = f"2023{grades.index(grade)+1}{class_num:02d}{i+1:03d}"
        measure_date = "2024-03-15"

        student = Student(
            student_id=student_id,
            name=name,
            gender=gender,
            grade=grade,
            class_num=class_num,
            height=height,
            measure_date=measure_date
        )

        if data_store.add_student(student):
            success_count += 1

    print(f"✓ 成功生成 {success_count} 条示例数据")


def main():
    """主函数"""
    # 确保目录存在
    os.makedirs('data', exist_ok=True)
    os.makedirs('reports', exist_ok=True)

    # 初始化组件
    data_store = DataStore('data/students.csv')
    collector = DataCollector(data_store)
    data_manager = DataManager(data_store)

    print(f"\n欢迎使用高中学生身高情况统计分析系统")
    print(f"当前数据记录数: {len(data_store.df)}")

    while True:
        print_menu()
        choice = input("请选择功能 (0-8): ").strip()

        if choice == '0':
            print("\n感谢使用，再见！")
            break

        elif choice == '1':
            data_entry_menu(collector)

        elif choice == '2':
            data_import_menu(collector)

        elif choice == '3':
            statistics_menu(data_store)

        elif choice == '4':
            visualization_menu(data_store)

        elif choice == '5':
            query_menu(data_manager)

        elif choice == '6':
            data_management_menu(data_manager)

        elif choice == '7':
            print_header("生成报告")
            df = data_store.get_all()
            if df.empty:
                print("暂无数据")
                continue

            stats = HeightStatistics(df)
            visualizer = HeightVisualizer(df)

            # 生成统计报告
            report_path = f'reports/full_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            stats.export_report_to_text(f'{report_path}.txt')

            # 生成图表
            files = visualizer.generate_all_visualizations()

            print(f"✓ 报告已生成:")
            print(f"  - 统计报告: {report_path}.txt")
            print(f"  - 图表文件: {len(files)} 个")

        elif choice == '8':
            system_menu(data_store, data_manager)

        else:
            print("无效的选择，请重新输入")


if __name__ == '__main__':
    main()
