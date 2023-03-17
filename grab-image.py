import exifread
from geopy.geocoders import Nominatim
from cachetools import TTLCache, cached
import csv
import os
import concurrent.futures
import multiprocessing
from face_detect import generate_thumbnail

geolocator = Nominatim(user_agent="image_location_parser")

def get_gps_info(file):
    with open(file, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        lat_ref = tags['GPS GPSLatitudeRef'].printable
        lon_ref = tags['GPS GPSLongitudeRef'].printable
        lat = tags['GPS GPSLatitude'].values
        lon = tags['GPS GPSLongitude'].values
        latitude = lat[0].numerator / lat[0].denominator + \
            lat[1].numerator / lat[1].denominator / 60 + \
            lat[2].numerator / lat[2].denominator / 3600
        longitude = lon[0].numerator / lon[0].denominator + \
            lon[1].numerator / lon[1].denominator / 60 + \
            lon[2].numerator / lon[2].denominator / 3600
        if lat_ref == 'S':
            latitude = -latitude
        if lon_ref == 'W':
            longitude = -longitude
        return latitude, longitude

def get_location_from_gps_info(file):
    try:
        lat, lon = get_gps_info(file)
        
        # 保留三位小数
        lat = round(lat, 3)
        lon = round(lon, 3)
        cache_key = f"{lat},{lon}"
        # 查看缓存是否存在
        if cache_key in get_location_from_gps_info.cache:
            # 显示缓存的数量
            print(f"当前缓存中有 {len(get_location_from_gps_info.cache)} 个位置信息")
            return get_location_from_gps_info.cache[cache_key]

        location = geolocator.reverse(cache_key, language='zh-CN', timeout=1000)
        print(location)
        address = location.address
        get_location_from_gps_info.cache[cache_key] = address
    except Exception as e:
        print(f"[GPS]Error: {e}")
        address = ""
    return address

get_location_from_gps_info.cache = {}

def analyze_image_file(file):
    try:
        with open(file, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            create_time = tags['EXIF DateTimeOriginal'].printable
            location = get_location_from_gps_info(file)
            print(f"[FILE]{file}: {create_time} - {location}")
            # face_location = generate_thumbnail(os.path.abspath(file), "thumbnails", thumbnail_size=(128, 128))
            return [os.path.basename(file), location, create_time, os.path.abspath(file)]
    except Exception as e:
        print(f"[ANA]Error: {e}")
        return None

def analyze_images(dir_path):
    data = []
    count = 0  # 用于记录已处理的照片数量
    with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        image_files = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                    image_files.append(os.path.join(root, file))
        results = executor.map(analyze_image_file, image_files)
        for result in results:
            if result is not None:
                data.append(result)
                count += 1
                if count == 50:
                    # 当处理的照片数量达到50时，将处理结果写入CSV文件
                    sorted_data = sorted(data, key=lambda x: x[2], reverse=True)
                    with open('./image_info.csv', 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        for row in sorted_data:
                            writer.writerow(row)
                    data = []
                    count = 0
    if count > 0:
        # 处理剩余的照片
        sorted_data = sorted(data, key=lambda x: x[2], reverse=True)
        with open('./image_info.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in sorted_data:
                writer.writerow(row)




if __name__ == '__main__':
    analyze_images('./source')



# 显示所有缓存的图片GPS坐标
print("缓存中的GPS坐标:")
for gps in get_location_from_gps_info.cache:
    print(gps)