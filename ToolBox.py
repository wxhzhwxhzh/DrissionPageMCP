# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sqlite3
import json
import os

def save_dict_to_sqlite(data, db_path='data.db', table_name='my_table'):
    """
    将字典或JSON字符串保存到SQLite数据库中。
    
    参数:
        data (dict or list of dict or str): 字典、列表字典，或JSON字符串。
        db_path (str): SQLite 数据库文件路径。
        table_name (str): 要创建的表名。
    """
    # 如果是 JSON 字符串，则解析为 Python 对象
    if isinstance(data, str):
        data = json.loads(data)
    
    # 如果是单个字典，则转成列表
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("输入必须是字典、字典列表，或 JSON 字符串。")

    # 提取字段名（以第一个字典为准）
    columns = data[0].keys()
    
    # 构建字段定义
    col_defs = ', '.join([f'"{col}" TEXT' for col in columns])

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建表（如果不存在）
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    cursor.execute(f'CREATE TABLE "{table_name}" ({col_defs})')

    # 插入数据
    placeholders = ', '.join(['?' for _ in columns])
    insert_query = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders})'
    for row in data:
        values = tuple(str(row.get(col, '')) for col in columns)
        cursor.execute(insert_query, values)

    # 提交并关闭连接
    conn.commit()
    conn.close()

    return (f"数据已保存到 {db_path} 的表 {table_name} 中。")
