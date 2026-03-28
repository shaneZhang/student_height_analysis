from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
import pandas as pd
import threading
import os
import tempfile


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
        """转换为字典 - 使用一致的字段名: class_num (避免与Python关键字冲突)"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'grade': self.grade,
            'class_num': self.class_num,
            'height': self.height,
            'measure_date': self.measure_date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """从字典创建对象 - 支持两种字段名"""
        # 支持两种字段名以保持向后兼容
        class_num = data.get('class_num', data.get('class'))
        return cls(
            student_id=data['student_id'],
            name=data['name'],
            gender=data['gender'],
            grade=data['grade'],
            class_num=class_num,
            height=data['height'],
            measure_date=data['measure_date']
        )


class DataStore:
    """数据存储管理类 - 使用单例模式确保数据一致性"""

    # 单例实例缓存: {data_file: instance}
    _instances = {}
    _instance_lock = threading.Lock()  # 单例创建锁

    def __new__(cls, data_file: str = 'data/students.csv'):
        """单例模式 - 每个文件路径只有一个DataStore实例"""
        with cls._instance_lock:
            if data_file not in cls._instances:
                instance = super().__new__(cls)
                instance.data_file = data_file
                instance.df: Optional[pd.DataFrame] = None
                instance._lock = threading.Lock()  # 每个实例自己的锁（不再需要类级别锁）
                instance._load_data()
                cls._instances[data_file] = instance
            return cls._instances[data_file]

    def _load_data(self):
        """加载数据 - 支持两种列名以保持向后兼容"""
        try:
            self.df = pd.read_csv(self.data_file)
            # 规范化列名
            self._normalize_columns()
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=[
                'student_id', 'name', 'gender', 'grade', 'class_num', 'height', 'measure_date'
            ])
        except pd.errors.EmptyDataError:
            # 文件为空，创建空DataFrame
            self.df = pd.DataFrame(columns=[
                'student_id', 'name', 'gender', 'grade', 'class_num', 'height', 'measure_date'
            ])

    def _normalize_columns(self):
        """规范化列名 - 处理class/class_num列名不一致问题"""
        if self.df is None:
            return
        # 支持两种列名: class 或 class_num
        if 'class' in self.df.columns and 'class_num' not in self.df.columns:
            self.df = self.df.rename(columns={'class': 'class_num'})

    def _save_data_internal(self):
        """内部保存数据 - 假设已经持有锁，避免死锁"""
        # 先写入临时文件，然后原子重命名，避免并发读取时读到损坏的文件
        temp_dir = os.path.dirname(self.data_file) or '.'
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            dir=temp_dir,
            delete=False,
            newline=''
        ) as tmp:
            self.df.to_csv(tmp, index=False)
            tmp_path = tmp.name
        
        # 原子重命名
        os.replace(tmp_path, self.data_file)
    
    def save_data(self):
        """保存数据到文件 - 使用原子写入避免并发读写时的文件损坏"""
        with self._lock:
            self._save_data_internal()

    def get_all(self) -> pd.DataFrame:
        """获取所有数据"""
        return self.df.copy()

    def add_student(self, student: Student) -> bool:
        """添加学生"""
        with self._lock:
            if student.student_id in self.df['student_id'].values:
                return False

            new_row = pd.DataFrame([student.to_dict()])
            
            # 修复FutureWarning: 确保DataFrame不为空时再进行concat
            if self.df.empty:
                self.df = new_row
            else:
                # 确保列一致
                new_row = new_row.reindex(columns=self.df.columns)
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                
            self._save_data_internal()
            return True

    def update_student(self, student_id: str, **kwargs) -> bool:
        """更新学生信息"""
        with self._lock:
            if student_id not in self.df['student_id'].values:
                return False

            idx = self.df[self.df['student_id'] == student_id].index[0]
            for key, value in kwargs.items():
                if key in self.df.columns:
                    self.df.at[idx, key] = value

            self._save_data_internal()
            return True

    def delete_student(self, student_id: str) -> bool:
        """删除学生"""
        with self._lock:
            if student_id not in self.df['student_id'].values:
                return False

            self.df = self.df[self.df['student_id'] != student_id].reset_index(drop=True)
            self._save_data_internal()
            return True

    def get_student(self, student_id: str) -> Optional[pd.Series]:
        """获取单个学生信息 - 确保student_id类型匹配"""
        # 将DataFrame中的student_id转换为字符串以匹配查询类型
        result = self.df[self.df['student_id'].astype(str) == str(student_id)]
        if len(result) > 0:
            return result.iloc[0]
        return None

    def query(self, **filters) -> pd.DataFrame:
        """条件查询"""
        import re
        result = self.df.copy()

        if 'gender' in filters and filters['gender']:
            result = result[result['gender'] == filters['gender']]

        if 'grade' in filters and filters['grade']:
            result = result[result['grade'] == filters['grade']]

        if 'class_num' in filters and filters['class_num']:
            result = result[result['class_num'] == filters['class_num']]

        if 'name' in filters and filters['name']:
            # 转义正则表达式特殊字符
            escaped_name = re.escape(filters['name'])
            result = result[result['name'].str.contains(escaped_name, na=False, regex=True)]

        if 'min_height' in filters and filters['min_height']:
            result = result[result['height'] >= filters['min_height']]

        if 'max_height' in filters and filters['max_height']:
            result = result[result['height'] <= filters['max_height']]

        return result

    def clear_data(self):
        """清空所有数据"""
        with self._lock:
            self.df = pd.DataFrame(columns=[
                'student_id', 'name', 'gender', 'grade', 'class_num', 'height', 'measure_date'
            ])
            self._save_data_internal()

    def import_from_dataframe(self, df: pd.DataFrame) -> tuple:
        """从DataFrame导入数据 - 优化性能版本"""
        # 支持两种列名: class 或 class_num
        df = df.copy()
        if 'class' in df.columns and 'class_num' not in df.columns:
            df = df.rename(columns={'class': 'class_num'})
        
        required_columns = ['student_id', 'name', 'gender', 'grade', 'class_num', 'height', 'measure_date']

        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            return False, f"缺少必要列: {missing}"

        # 检查CSV内部是否有重复学号
        duplicate_in_csv = df[df.duplicated('student_id', keep=False)]
        if not duplicate_in_csv.empty:
            duplicate_ids = duplicate_in_csv['student_id'].unique()
            return False, f"CSV文件内部存在重复学号: {', '.join(map(str, duplicate_ids))}"

        with self._lock:
            # 检查与现有数据的重复
            existing_ids = set(self.df['student_id'].values)
            new_df = df[~df['student_id'].astype(str).isin(existing_ids)].copy()
            
            # 转换数据类型确保一致
            new_df['student_id'] = new_df['student_id'].astype(str)
            new_df['name'] = new_df['name'].astype(str)
            new_df['gender'] = new_df['gender'].astype(str)
            new_df['grade'] = new_df['grade'].astype(str)
            new_df['class_num'] = new_df['class_num'].astype(int)
            new_df['height'] = new_df['height'].astype(float)
            new_df['measure_date'] = new_df['measure_date'].astype(str)
            
            skip_count = len(df) - len(new_df)
            
            if not new_df.empty:
                if self.df.empty:
                    self.df = new_df
                else:
                    # 确保列一致
                    new_df = new_df.reindex(columns=self.df.columns)
                    self.df = pd.concat([self.df, new_df], ignore_index=True)
                self._save_data_internal()
            
            success_count = len(new_df)

        return True, f"导入成功: {success_count}条, 跳过重复: {skip_count}条"
