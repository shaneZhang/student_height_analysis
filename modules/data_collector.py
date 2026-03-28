import pandas as pd
from datetime import datetime
from typing import Tuple, List, Optional
from .data_model import Student, DataStore


class DataValidator:
    """数据校验器"""

    MIN_HEIGHT = 140.0
    MAX_HEIGHT = 200.0
    VALID_GENDERS = ['男', '女']
    VALID_GRADES = ['高一', '高二', '高三']

    @classmethod
    def validate_student(cls, student: Student) -> Tuple[bool, List[str]]:
        """校验学生数据"""
        errors = []

        if not student.student_id or not str(student.student_id).strip():
            errors.append("学号不能为空")

        if not student.name or not str(student.name).strip():
            errors.append("姓名不能为空")

        if student.gender not in cls.VALID_GENDERS:
            errors.append(f"性别必须是: {', '.join(cls.VALID_GENDERS)}")

        if student.grade not in cls.VALID_GRADES:
            errors.append(f"年级必须是: {', '.join(cls.VALID_GRADES)}")

        if not isinstance(student.class_num, int) or student.class_num < 1 or student.class_num > 50:
            errors.append("班级必须是1-50之间的整数")

        if not isinstance(student.height, (int, float)):
            errors.append("身高必须是数字")
        elif student.height < cls.MIN_HEIGHT or student.height > cls.MAX_HEIGHT:
            errors.append(f"身高必须在{cls.MIN_HEIGHT}cm到{cls.MAX_HEIGHT}cm之间")

        try:
            measure_date = datetime.strptime(student.measure_date, '%Y-%m-%d')
            today = datetime.now()

            # 检查未来日期
            if measure_date > today:
                errors.append("测量日期不能是未来日期")

            # 检查极早日期（早于2000年）
            if measure_date.year < 2000:
                errors.append("测量日期不能早于2000年")
        except ValueError:
            errors.append("测量日期格式错误，应为YYYY-MM-DD")

        return len(errors) == 0, errors

    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame]:
        """校验DataFrame数据"""
        errors = []
        valid_rows = []

        required_columns = ['student_id', 'name', 'gender', 'grade', 'class', 'height', 'measure_date']

        for col in required_columns:
            if col not in df.columns:
                errors.append(f"缺少必要列: {col}")
                return False, errors, pd.DataFrame()

        for idx, row in df.iterrows():
            row_errors = []

            if pd.isna(row['student_id']) or str(row['student_id']).strip() == '':
                row_errors.append(f"第{idx+1}行: 学号不能为空")

            if pd.isna(row['name']) or str(row['name']).strip() == '':
                row_errors.append(f"第{idx+1}行: 姓名不能为空")

            if str(row['gender']) not in cls.VALID_GENDERS:
                row_errors.append(f"第{idx+1}行: 性别必须是男或女")

            if str(row['grade']) not in cls.VALID_GRADES:
                row_errors.append(f"第{idx+1}行: 年级必须是高一、高二或高三")

            try:
                height = float(row['height'])
                if height < cls.MIN_HEIGHT or height > cls.MAX_HEIGHT:
                    row_errors.append(f"第{idx+1}行: 身高必须在{cls.MIN_HEIGHT}cm到{cls.MAX_HEIGHT}cm之间")
            except (ValueError, TypeError):
                row_errors.append(f"第{idx+1}行: 身高必须是有效数字")

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_rows.append(row)

        valid_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=df.columns)
        return len(errors) == 0, errors, valid_df


class DataCollector:
    """数据收集器"""

    def __init__(self, data_store: DataStore):
        self.data_store = data_store
        self.validator = DataValidator()

    def add_student_manual(self, student_id: str, name: str, gender: str,
                          grade: str, class_num: int, height: float,
                          measure_date: str = None) -> Tuple[bool, str]:
        """手动添加单个学生"""
        if measure_date is None:
            measure_date = datetime.now().strftime('%Y-%m-%d')

        try:
            student = Student(
                student_id=str(student_id).strip(),
                name=str(name).strip(),
                gender=str(gender).strip(),
                grade=str(grade).strip(),
                class_num=int(class_num),
                height=float(height),
                measure_date=measure_date
            )
        except (ValueError, TypeError) as e:
            return False, f"数据格式错误: {str(e)}"

        is_valid, errors = self.validator.validate_student(student)
        if not is_valid:
            return False, f"数据校验失败: {'; '.join(errors)}"

        if student.student_id in self.data_store.df['student_id'].values:
            return False, f"学号 {student.student_id} 已存在"

        success = self.data_store.add_student(student)
        if success:
            return True, f"学生 {student.name} 添加成功"
        else:
            return False, "添加失败"

    def import_from_csv(self, file_path: str) -> Tuple[bool, str]:
        """从CSV文件导入"""
        try:
            df = pd.read_csv(file_path)
            return self._import_dataframe(df, file_path)
        except Exception as e:
            return False, f"读取CSV文件失败: {str(e)}"

    def import_from_excel(self, file_path: str, sheet_name: str = 0) -> Tuple[bool, str]:
        """从Excel文件导入"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return self._import_dataframe(df, file_path)
        except Exception as e:
            return False, f"读取Excel文件失败: {str(e)}"

    def _import_dataframe(self, df: pd.DataFrame, source: str) -> Tuple[bool, str]:
        """从DataFrame导入数据"""
        is_valid, errors, valid_df = self.validator.validate_dataframe(df)

        if valid_df.empty:
            return False, f"没有有效的数据可导入。错误: {'; '.join(errors[:5])}"

        success, message = self.data_store.import_from_dataframe(valid_df)

        if errors:
            message += f"\n警告: 发现 {len(errors)} 个错误，部分数据未导入"

        return success, message

    def get_import_template(self) -> pd.DataFrame:
        """获取导入模板"""
        template_data = {
            'student_id': ['2023010101', '2023010102'],
            'name': ['张三', '李四'],
            'gender': ['男', '女'],
            'grade': ['高一', '高二'],
            'class': [1, 2],
            'height': [175.5, 162.0],
            'measure_date': ['2024-03-15', '2024-03-15']
        }
        return pd.DataFrame(template_data)

    def save_template(self, file_path: str):
        """保存导入模板"""
        template = self.get_import_template()
        if file_path.endswith('.csv'):
            template.to_csv(file_path, index=False)
        else:
            template.to_excel(file_path, index=False)

    def check_duplicate_ids(self, df: pd.DataFrame) -> List[str]:
        """检查重复的学号"""
        existing_ids = set(self.data_store.df['student_id'].values)
        new_ids = set(df['student_id'].astype(str).values)
        return list(existing_ids & new_ids)

    def preview_import(self, file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
        """预览导入数据"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            is_valid, errors, valid_df = self.validator.validate_dataframe(df)

            preview_info = f"总行数: {len(df)}, 有效行数: {len(valid_df)}, 错误数: {len(errors)}"
            if errors:
                preview_info += f"\n前5个错误: {'; '.join(errors[:5])}"

            duplicates = self.check_duplicate_ids(df)
            if duplicates:
                preview_info += f"\n重复学号: {', '.join(duplicates[:10])}"

            return valid_df.head(10), preview_info

        except Exception as e:
            return None, f"预览失败: {str(e)}"
