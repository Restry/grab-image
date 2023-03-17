from datetime import datetime
import os
import csv
from PIL import Image
import csv
from dateutil.parser import parse
import sqlite3
from geopy.geocoders import Nominatim


def get_timestamp_from_path(path):
    for substring in path.split('_'):
        try:
            timestamp = parse(substring, fuzzy=True)
            return timestamp
        except ValueError:
            pass
    return None


def extract_timestamp(path):
    timestamp = get_timestamp_from_path(path)
    if timestamp:
        return (timestamp)
    else:
        print('No timestamp found in path')
    # # 定义匹配时间戳的正则表达式
    # pattern = r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})'

    # # 从文件名中提取时间戳
    # match = re.search(pattern, path)
    # if match:
    #     year, month, day, hour, minute, second = map(int, match.groups())
    #     timestamp = datetime(year, month, day, hour, minute, second)
    #     return timestamp
    # else:
    #     return None


def generate_thumbnail(image_path, output_path):
    # 生成缩略图
    image = Image.open(image_path)
    width, height = image.size
    new_width = 680
    new_height = int(height * new_width / width)
    image.thumbnail((new_width, new_height))
    # 获取图片的文件名和扩展名
    file_path, file_name = os.path.split(image_path)
    name, ext = os.path.splitext(file_name)
    thumbnail_path = os.path.join(output_path, name + '_thumbnail'+ext)

    # 检查文件是否存在，如果不存在则保存并压缩
    if not os.path.isfile(thumbnail_path):
        # 设置quality和optimize参数来压缩图片
        image.save(thumbnail_path, quality=50, optimize=True)

    return thumbnail_path


def save_to_sqlite(metadata, image_path, thumbnail_path, face_paths, output_folder):
    # 连接到 SQLite 数据库（如果数据库不存在，它会被创建）
    conn = sqlite3.connect(os.path.join(output_folder, 'imagedb.db'))
    c = conn.cursor()

    # 插入数据
    data = (str(metadata['taken_time']), str(metadata['make']), str(metadata['model']),
            metadata['latitude'], metadata['longitude'], '', image_path, thumbnail_path, face_paths)
    c.execute('INSERT INTO images (taken_time, make, model, latitude, longitude,\
               address, image_path, thumbnail_path, face_paths) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

    # 提交更改并关闭连接
    conn.commit()
    conn.close()


def get_processed_files(output_folder):
    """
    获取已处理的文件列表
    """
    processed_files = set()

    # 连接到 SQLite 数据库（如果数据库不存在，它会被创建）
    conn = sqlite3.connect(os.path.join(output_folder, 'imagedb.db'))
    c = conn.cursor()

    # 检查表是否存在，如果不存在则创建一个新表
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taken_time TEXT,
            make TEXT,
            model TEXT,
            latitude REAL,
            longitude REAL,
            address TEXT,
            image_path TEXT,
            thumbnail_path TEXT,
            face_paths TEXT
        )
     ''')

    # 查询已处理的文件列表
    for row in c.execute('SELECT image_path FROM images'):
        processed_files.add(row[0])

     # 关闭连接
    conn.close()

    return processed_files


def process_address(db_file):
    # 创建一个地理编码器对象
    geolocator = Nominatim(user_agent="image_location_parser")

    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # 查询数据
    rows = c.execute('SELECT * FROM images WHERE address IS NULL').fetchall()
    print(f"Found {len(rows)} rows to process...")

    # 遍历每一行数据
    for row in rows:
        data = dict(zip(('id', 'taken_time', 'make', 'model', 'latitude', 'longitude',
                         'address', 'image_path', 'thumbnail_path', 'face_paths'), row))
        # 根据latitude和longitude字段获取真实地址
        location = geolocator.reverse(
            f"{data['latitude']}, {data['longitude']}")
        data["address"] = location.address

        # 更新数据
        c.execute('UPDATE images SET address=? WHERE id=?',
                  (data["address"], data["id"]))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()
