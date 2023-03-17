import sqlite3
import csv

# 连接到 SQLite 数据库（如果数据库不存在，它会被创建）
conn = sqlite3.connect('database.db')
c = conn.cursor()

# 从 CSV 文件中读取数据
with open('./output/metadata.csv', 'r') as f:
    reader = csv.reader(f)
    headers = next(reader)  # 读取标题行
    headers = [h.replace(' ', '_') for h in headers]  # 将空格替换为下划线（SQLite 列名不能包含空格）
    
    # 创建一个新表（使用 CSV 文件中的标题行作为列名，并添加一个名为 id 的自增列）
    c.execute(f'CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT, {", ".join(headers)})')
    
    # 将数据插入到表中
    for row in reader:
        c.execute(f'INSERT INTO images ({", ".join(headers)}) VALUES ({", ".join(["?"] * len(headers))})', row)

# 提交更改并关闭连接
conn.commit()
conn.close()