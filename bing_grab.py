# 导入所需的库
import os
import csv
import exifread
from PIL import Image
from PIL.ExifTags import TAGS
# 定义一个函数，用于遍历指定文件夹下所有目录层级的图片，并根据拍摄时间分类创建文件夹存放，并将元数据写入csv文件中
def analyze_and_write_metadata(folder, csv_file):
    # 打开csv文件，以写入模式
    with open(csv_file, 'w') as f:
        # 创建一个csv写入对象
        writer = csv.writer(f)
        # 写入csv文件的表头，包括图片名、地理位置、拍摄时间、设备制造商、设备型号等信息
        writer.writerow(['Image Name', 'GPS Info', 'DateTimeOriginal', 'Make', 'Model'])
        # 遍历指定文件夹下所有目录层级的文件和子文件夹
        for root, dirs, files in os.walk(folder):
            # 遍历每个文件
            for file in files:
                # 获取文件的扩展名
                ext = os.path.splitext(file)[1].lower()
                # 如果文件的扩展名是图片类型，继续后面的操作
                if ext in ['.jpg','.jpeg', '.png', '.gif']:
                    # 获取文件的完整路径
                    path = os.path.join(root, file)
                    # 打开图片文件
                    image = Image.open(path)
                    # 获取图片的元数据
                    exif = image.getexif()
                    # 创建一个空字典，用于存储元数据
                    metadata = {}
                    # 遍历元数据中的每个标签和值
                    for tag, value in exif.items():
                        # 获取标签的名称
                        tag_name = TAGS.get(tag, tag)
                        # 将标签和值添加到字典中
                        metadata[tag_name] = value
                    # 从字典中提取需要的信息，如果不存在则返回None
                    image_name = file
                    gps_info = metadata.get('GPSInfo', None)
                    date_time = metadata.get('DateTimeOriginal', None)
                    make = metadata.get('Make', None)
                    model = metadata.get('Model', None)
                    print('[EXT]',image_name, gps_info, date_time, make, model)
                    # 将信息写入csv文件中的一行
                    writer.writerow([image_name, gps_info, date_time, make, model])
                    # 如果文件有拍摄时间，根据该值创建一个新的子文件夹，并将文件移动到该子文件夹中
                    if date_time:
                        new_dir = os.path.join(folder, date_time[:7])
                        # 如果该子文件夹不存在，创建它
                        if not os.path.exists(new_dir):
                            os.mkdir(new_dir)
                        # 将文件移动到该子文件夹中
                        os.rename(path, os.path.join(new_dir, file))
                        # 生成缩略图，并添加_thumbnail后缀到原图名
                        make_thumbnail(os.path.join(new_dir, file))

# 定义一个函数，用于生成缩略图，并添加_thumbnail后缀到原图名
def make_thumbnail(path):
    # 打开图片文件
    im = Image.open(path)
    # 获取图片的宽度和高度
    width, height = im.size
    # 如果图片的宽度大于680，生成宽度为680的缩略图，保持高宽比
    if width > 680:
        im.thumbnail((680, height * 680 // width))
        # 获取图片的文件名和扩展名
        name, ext = os.path.splitext(path)
        # 保存缩略图，添加_thumbnail后缀到原图名
        im.save(name + '_thumbnail' + ext)

# 调用函数，遍历指定文件夹下所有目录层级的图片，并根据拍摄时间分类创建文件夹存放，并将元数据写入csv文件中
analyze_and_write_metadata('./source', './metadata.csv')