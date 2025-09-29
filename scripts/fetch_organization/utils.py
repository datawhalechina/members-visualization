from datetime import datetime
from pathlib import Path


def ensure_dir_and_write_file(file_path, data):
    print(f'写入文件: {file_path}')
    """确保目录存在并写入文件"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)


# 根据月份获取过去12个月的数据，比如2025-1,2025-2等
def get_object_by_month_key(month_object, month_count=12):
    result = {}
    month_key = []
    # 获取当前日期
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # 计算过去n个月
    for _ in range(month_count):
        # 添加当前月份（需要先减后加，因为是获取过去的月份）
        month_key.append(f"{current_year}-{current_month}")

        # 计算上一个月
        current_month -= 1
        if current_month < 1:
            current_month = 12
            current_year -= 1

    # 反转列表，使月份按时间先后顺序排列
    month_key.reverse()

    for month in month_key:
        result[month] = month_object.get(month, 0)
    return result
