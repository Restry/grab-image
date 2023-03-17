import os
from PIL import Image
import face_recognition

def get_face_locations(image_path):
    """获取图片中的人脸位置"""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return face_locations

def save_face_images(image_path, face_locations, output_folder):
    """保存人脸图片"""
    image = Image.open(image_path)
    # 生成头像缩略图
    faces = []
    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_image = image.crop((left, top, right, bottom))
        # 使用原始图片文件名加上人脸位置作为新的文件名
        file_name = os.path.splitext(os.path.basename(image_path))[0] + \
                    '=={}_{}_{}_{}.png'.format(top, right, bottom, left)
        file_path = os.path.join(output_folder, file_name)
        face_image.save(file_path, quality=50, optimize=True) # 设置quality和optimize参数来压缩图片

        faces.append(file_name)

    return faces