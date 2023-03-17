import exifread
from datetime import datetime


def get_gps_info(tags):
    try:
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
    except Exception as e:
        print('[GSP]Error:', e)
        return 0, 0

# 获取图片元数据


def get_metadata(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    # 获取拍摄时间和设备信息
    taken_time = tags.get('Image DateTime', None)  # 尝试获取拍摄时间
    if taken_time is not None:  # 如果存在拍摄时间
        taken_time = datetime.strptime(
            str(taken_time), '%Y:%m:%d %H:%M:%S')  # 转换为日期和时间对象
        year = taken_time.strftime('%Y')
        month = taken_time.strftime('%m')
    else:  # 如果不存在拍摄时间
        modified_time = tags.get('FileModifyDate', None)  # 尝试获取修改时间
        if modified_time is not None:  # 如果存在修改时间
            modified_time = datetime.strptime(
                str(modified_time), '%Y:%m:%d %H:%M:%S%z')  # 转换为日期和时间对象，注意有时区信息
            year = modified_time.strftime('%Y')
            month = modified_time.strftime('%m')
        else:  # 如果不存在修改时间
            digitized_time = tags.get(
                'EXIF DateTimeDigitized', None)  # 尝试获取数字化时间
            if digitized_time is not None:  # 如果存在数字化时间
                digitized_time = datetime.strptime(
                    str(digitized_time), '%Y:%m:%d %H:%M:%S')  # 转换为日期和时间对象
                year = digitized_time.strftime('%Y')
                month = digitized_time.strftime('%m')
            else:  # 如果都不存在，则设置为未知值
                year = 'unknown'
                month = 'unknown'
    make = tags.get('Image Make', 'unknown')
    model = tags.get('Image Model', 'unknown')
    # 获取地理位置信息

    latitude, longitude = get_gps_info(tags)

    return {
        'taken_time': taken_time,
        'year': year,
        'month': month,
        'make': make,
        'model': model,
        'latitude': latitude,
        'longitude': longitude
    }
