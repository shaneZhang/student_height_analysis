import pandas as pd
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import shutil
import os


class DataManager:
    """数据管理器 - 提供查询和维护功能"""

    def __init__(self, data_store):
        self.data_store = data_store
        self.backup_dir = 'data/backups'
        os.makedirs(self.backup_dir, exist_ok=True)

    def query_by_student_id(self, student_id: str) -> Optional[pd.Series]:
        """按学号查询"""
        return self.data_store.get_student(student_id)

    def query_by_name(self, name: str) -> pd.DataFrame:
        """按姓名模糊查询"""
        return self.data_store.query(name=name)

    def query_by_filters(self, gender: Optional[str] = None,
                        grade: Optional[str] = None,
                        class_num: Optional[int] = None,
                        min_height: Optional[float] = None,
                        max_height: Optional[float] = None) -> pd.DataFrame:
        """多条件组合查询"""
        return self.data_store.query(
            gender=gender,
            grade=grade,
            class_num=class_num,
            min_height=min_height,
            max_height=max_height
        )

    def update_student_info(self, student_id: str, **kwargs) -> Tuple[bool, str]:
        """更新学生信息"""
        if student_id not in self.data_store.df['student_id'].values:
            return False, f"学号 {student_id} 不存在"

        allowed_fields = ['name', 'gender', 'grade', 'class', 'height', 'measure_date']

        for key in kwargs:
            if key not in allowed_fields:
                return False, f"不允许修改字段: {key}"

        success = self.data_store.update_student(student_id, **kwargs)
        if success:
            return True, f"学号 {student_id} 信息更新成功"
        else:
            return False, "更新失败"

    def delete_student(self, student_id: str) -> Tuple[bool, str]:
        """删除学生记录"""
        if student_id not in self.data_store.df['student_id'].values:
            return False, f"学号 {student_id} 不存在"

        success = self.data_store.delete_student(student_id)
        if success:
            return True, f"学号 {student_id} 已删除"
        else:
            return False, "删除失败"

    def batch_delete(self, student_ids: List[str]) -> Tuple[int, int, List[str]]:
        """批量删除"""
        success_count = 0
        failed_ids = []

        for student_id in student_ids:
            success, _ = self.delete_student(student_id)
            if success:
                success_count += 1
            else:
                failed_ids.append(student_id)

        return success_count, len(failed_ids), failed_ids

    def backup_data(self, backup_name: Optional[str] = None) -> str:
        """备份数据"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        os.makedirs(self.backup_dir, exist_ok=True)
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        self.data_store.df.to_csv(backup_path, index=False)
        return backup_path

    def list_backups(self) -> List[str]:
        """列出所有备份"""
        if not os.path.exists(self.backup_dir):
            return []
        return sorted([f for f in os.listdir(self.backup_dir) if f.endswith('.csv')])

    def restore_from_backup(self, backup_name: str) -> Tuple[bool, str]:
        """从备份恢复"""
        backup_path = os.path.join(self.backup_dir, backup_name)

        if not os.path.exists(backup_path):
            return False, f"备份文件 {backup_name} 不存在"

        try:
            df = pd.read_csv(backup_path, dtype={'student_id': str, 'class': int})
            
            if df.empty:
                return False, "备份文件为空"
            
            required_columns = ['student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"备份文件缺少必要列: {missing_columns}"

            self.backup_data(f"auto_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

            self.data_store.df = df
            self.data_store.save_data()

            return True, f"已从备份 {backup_name} 恢复数据"
        except pd.errors.EmptyDataError:
            return False, "备份文件为空或格式错误"
        except pd.errors.ParserError:
            return False, "备份文件格式错误，无法解析"
        except Exception as e:
            return False, f"恢复失败: {str(e)}"

    def export_data(self, file_path: str, format: str = 'csv') -> Tuple[bool, str]:
        """导出数据"""
        try:
            if format.lower() == 'csv':
                self.data_store.df.to_csv(file_path, index=False)
            elif format.lower() in ['excel', 'xlsx']:
                self.data_store.df.to_excel(file_path, index=False)
            else:
                return False, f"不支持的格式: {format}"

            return True, f"数据已导出到 {file_path}"
        except Exception as e:
            return False, f"导出失败: {str(e)}"

    def get_statistics_summary(self) -> Dict:
        """获取数据概览统计"""
        df = self.data_store.df

        if df.empty:
            return {
                'total_students': 0,
                'total_records': 0,
                'gender_distribution': {},
                'grade_distribution': {},
                'class_count': 0
            }

        gender_dist = df['gender'].value_counts().to_dict()
        grade_dist = df['grade'].value_counts().to_dict()

        return {
            'total_students': len(df),
            'total_records': len(df),
            'gender_distribution': gender_dist,
            'grade_distribution': grade_dist,
            'class_count': df.groupby(['grade', 'class']).size().shape[0]
        }

    def clear_all_data(self, confirm: bool = False) -> Tuple[bool, str]:
        """清空所有数据（危险操作）"""
        if not confirm:
            return False, "请设置 confirm=True 确认清空所有数据"

        # 先备份
        self.backup_data(f"auto_backup_before_clear_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        self.data_store.clear_data()
        return True, "所有数据已清空（已自动备份）"

    def validate_data_integrity(self) -> Tuple[bool, List[str]]:
        """数据完整性检查"""
        df = self.data_store.df
        issues = []

        if df.empty:
            return True, []

        # 检查必填字段
        for col in ['student_id', 'name', 'gender', 'grade', 'class', 'height']:
            if col not in df.columns:
                issues.append(f"缺少必要列: {col}")
            else:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    issues.append(f"列 '{col}' 有 {null_count} 个空值")

        # 检查重复学号
        duplicates = df[df.duplicated('student_id', keep=False)]
        if not duplicates.empty:
            dup_ids = duplicates['student_id'].unique()
            issues.append(f"发现重复学号: {', '.join(map(str, dup_ids[:10]))}")

        # 检查身高范围
        invalid_heights = df[(df['height'] < 140) | (df['height'] > 200)]
        if not invalid_heights.empty:
            issues.append(f"发现 {len(invalid_heights)} 条身高异常记录")

        # 检查性别值
        invalid_genders = df[~df['gender'].isin(['男', '女'])]
        if not invalid_genders.empty:
            issues.append(f"发现 {len(invalid_genders)} 条性别值异常记录")

        # 检查年级值
        invalid_grades = df[~df['grade'].isin(['高一', '高二', '高三'])]
        if not invalid_grades.empty:
            issues.append(f"发现 {len(invalid_grades)} 条年级值异常记录")

        return len(issues) == 0, issues
