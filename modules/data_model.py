from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
import pandas as pd


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

    def __init__(self, data_file: str = 'data/students.csv'):
        self.data_file = data_file
        self.df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self):
        """加载数据"""
        try:
            self.df = pd.read_csv(self.data_file)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=[
                'student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date'
            ])

    def save_data(self):
        """保存数据到文件"""
        self.df.to_csv(self.data_file, index=False)

    def get_all(self) -> pd.DataFrame:
        """获取所有数据"""
        return self.df.copy()

    def add_student(self, student: Student) -> bool:
        """添加学生"""
        if student.student_id in self.df['student_id'].values:
            return False

        new_row = pd.DataFrame([student.to_dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_data()
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
            result = result[result['name'].str.contains(filters['name'], na=False)]

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
        """从DataFrame导入数据"""
        required_columns = ['student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date']

        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            return False, f"缺少必要列: {missing}"

        success_count = 0
        skip_count = 0

        for _, row in df.iterrows():
            student = Student(
                student_id=str(row['student_id']),
                name=str(row['name']),
                gender=str(row['gender']),
                grade=str(row['grade']),
                class_num=int(row['class']),
                height=float(row['height']),
                measure_date=str(row['measure_date'])
            )

            if self.add_student(student):
                success_count += 1
            else:
                skip_count += 1

        return True, f"导入成功: {success_count}条, 跳过重复: {skip_count}条"
