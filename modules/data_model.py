from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
import pandas as pd
import threading
import fcntl
import os


@dataclass
class Student:
    """学生数据模型"""
    student_id: str
    name: str
    gender: str
    grade: str
    class_num: int
    height: float
    measure_date: str

    def __post_init__(self):
        """数据后处理，确保数据格式正确"""
        self.gender = self.gender.strip()
        self.grade = self.grade.strip()
        self.height = float(self.height)
        self.class_num = int(self.class_num)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'grade': self.grade,
            'class': self.class_num,
            'height': self.height,
            'measure_date': self.measure_date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """从字典创建对象"""
        return cls(
            student_id=data['student_id'],
            name=data['name'],
            gender=data['gender'],
            grade=data['grade'],
            class_num=data['class'],
            height=data['height'],
            measure_date=data['measure_date']
        )


class DataStore:
    """数据存储管理类"""

    _instances = {}
    _lock = threading.Lock()
    _file_lock = threading.Lock()

    def __new__(cls, data_file: str = 'data/students.csv'):
        # 基于文件路径的单例模式 - 使用类级别的锁确保线程安全
        with cls._lock:
            abs_path = os.path.abspath(data_file)
            if abs_path not in cls._instances:
                instance = super().__new__(cls)
                # 在锁内完成所有初始化，确保其他线程获取时已经初始化完成
                instance._data_file_path = abs_path
                instance.data_file = data_file
                instance.df: Optional[pd.DataFrame] = None
                instance._load_data()
                cls._instances[abs_path] = instance
            return cls._instances[abs_path]

    def __init__(self, data_file: str = 'data/students.csv'):
        # 初始化已在__new__中完成，这里不需要做任何事情
        pass

    def _load_data(self):
        """加载数据"""
        try:
            # 使用dtype参数确保student_id被读取为字符串
            self.df = pd.read_csv(self.data_file, dtype={'student_id': str})
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=[
                'student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date'
            ])
            # 设置student_id列的类型为字符串
            self.df['student_id'] = self.df['student_id'].astype(str)

    def save_data(self):
        """保存数据到文件 - 线程安全"""
        with self._file_lock:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file) if os.path.dirname(self.data_file) else '.', exist_ok=True)
            # 使用文件锁防止并发写入问题
            with open(self.data_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                self.df.to_csv(f, index=False)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def get_all(self) -> pd.DataFrame:
        """获取所有数据"""
        return self.df.copy()

    def add_student(self, student: Student) -> bool:
        """添加学生 - 线程安全"""
        with self._file_lock:
            # 重新加载数据以确保数据最新
            self._load_data()

            if student.student_id in self.df['student_id'].values:
                return False

            new_row = pd.DataFrame([student.to_dict()])

            # 处理空DataFrame的情况，避免FutureWarning
            if self.df.empty:
                self.df = new_row
            else:
                self.df = pd.concat([self.df, new_row], ignore_index=True)

            # 直接保存，不再调用save_data避免死锁
            os.makedirs(os.path.dirname(self.data_file) if os.path.dirname(self.data_file) else '.', exist_ok=True)
            with open(self.data_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                self.df.to_csv(f, index=False)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return True

    def update_student(self, student_id: str, **kwargs) -> bool:
        """更新学生信息"""
        if student_id not in self.df['student_id'].values:
            return False

        idx = self.df[self.df['student_id'] == student_id].index[0]
        for key, value in kwargs.items():
            if key in self.df.columns:
                self.df.at[idx, key] = value

        self.save_data()
        return True

    def delete_student(self, student_id: str) -> bool:
        """删除学生"""
        if student_id not in self.df['student_id'].values:
            return False

        self.df = self.df[self.df['student_id'] != student_id].reset_index(drop=True)
        self.save_data()
        return True

    def get_student(self, student_id: str) -> Optional[pd.Series]:
        """获取单个学生信息"""
        result = self.df[self.df['student_id'] == student_id]
        if result.empty:
            return None
        return result.iloc[0]

    def query(self, **filters) -> pd.DataFrame:
        """条件查询"""
        result = self.df.copy()

        if 'gender' in filters and filters['gender']:
            result = result[result['gender'] == filters['gender']]

        if 'grade' in filters and filters['grade']:
            result = result[result['grade'] == filters['grade']]

        if 'class_num' in filters and filters['class_num']:
            result = result[result['class'] == filters['class_num']]

        if 'name' in filters and filters['name']:
            import re
            escaped_name = re.escape(filters['name'])
            result = result[result['name'].str.contains(escaped_name, na=False, regex=True)]

        if 'min_height' in filters and filters['min_height']:
            result = result[result['height'] >= filters['min_height']]

        if 'max_height' in filters and filters['max_height']:
            result = result[result['height'] <= filters['max_height']]

        return result

    def clear_data(self):
        """清空所有数据"""
        self.df = pd.DataFrame(columns=[
            'student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date'
        ])
        self.save_data()

    def import_from_dataframe(self, df: pd.DataFrame) -> tuple:
        """从DataFrame导入数据 - 优化性能"""
        required_columns = ['student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date']

        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            return False, f"缺少必要列: {missing}"

        # 检查CSV内部是否有重复学号
        duplicate_in_csv = df[df.duplicated('student_id', keep=False)]
        if not duplicate_in_csv.empty:
            dup_ids = duplicate_in_csv['student_id'].unique()
            return False, f"CSV文件内部存在重复学号: {list(dup_ids)}"

        with self._file_lock:
            # 重新加载数据以确保数据最新
            self._load_data()

            # 获取已存在的学号集合，用于快速查找
            existing_ids = set(self.df['student_id'].values) if not self.df.empty else set()

            # 准备新数据
            new_rows = []
            success_count = 0
            skip_count = 0

            for _, row in df.iterrows():
                student_id = str(row['student_id'])
                if student_id in existing_ids:
                    skip_count += 1
                    continue

                new_rows.append({
                    'student_id': student_id,
                    'name': str(row['name']),
                    'gender': str(row['gender']),
                    'grade': str(row['grade']),
                    'class': int(row['class']),
                    'height': float(row['height']),
                    'measure_date': str(row['measure_date'])
                })
                existing_ids.add(student_id)
                success_count += 1

            # 批量添加新数据
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                if self.df.empty:
                    self.df = new_df
                else:
                    self.df = pd.concat([self.df, new_df], ignore_index=True)
                # 直接保存，不再调用save_data避免死锁
                os.makedirs(os.path.dirname(self.data_file) if os.path.dirname(self.data_file) else '.', exist_ok=True)
                with open(self.data_file, 'w') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    self.df.to_csv(f, index=False)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return True, f"导入成功: {success_count}条, 跳过重复: {skip_count}条"
