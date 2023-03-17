import os
import face_recognition
from PIL import Image

def generate_thumbnail(image_path, output_folder, thumbnail_size=(128, 128)):
    """
    生成头像缩略图

    参数：
        - image_path: str，原始图片路径
        - output_folder: str，缩略图输出文件夹
        - thumbnail_size: tuple，缩略图大小，默认为 (128, 128)

    返回：
        - faces: list，人脸区域坐标列表
    """
    print('[IMAGE]'+image_path)
    # 读取图片
    image = face_recognition.load_image_file(image_path)

    # 检测图片中的人脸
    face_locations = face_recognition.face_locations(image)

    # 生成头像缩略图
    faces = []
    for i, face_location in enumerate(face_locations):
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        face_image = Image.fromarray(face_image)
        face_image = face_image.resize(thumbnail_size, Image.ANTIALIAS)

        # 将缩略图保存到文件
        filename = os.path.basename(image_path)
        basename, ext = os.path.splitext(filename)
        output_filename = f"{basename}_face_{i}{ext}"
        output_path = os.path.join(output_folder, output_filename)
        face_image.save(output_path)

        faces.append(face_location)

    return faces


# image_path = "/Users/lewaylee/Projects/grab-image/image-source/IMG_3204.jpeg"
# output_folder = "thumbnails"

# # 生成缩略图并获取人脸区域坐标
# faces = generate_thumbnail(image_path, output_folder, thumbnail_size=(128, 128))

# print(f"成功生成 {len(faces)} 张缩略图")
