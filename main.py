import csv
import math
import os
from multiprocessing import Pool, cpu_count
from metadata import get_metadata
from face import get_face_locations, save_face_images

from utils import save_to_sqlite, generate_thumbnail, get_processed_files, process_address
import argparse


def process_image(image_path, output_folder):
    try:
        # 获取图片元数据
        metadata = get_metadata(image_path)
        image_name = os.path.basename(image_path)
        # 创建输出目录
        output_path = os.path.join(
            output_folder, metadata['year'], metadata['month'])
        os.makedirs(output_path, exist_ok=True)

        # 生成缩略图
        thumbnail_path = generate_thumbnail(image_path, output_path)

        # 获取人脸位置并保存人脸图片
        face_locations = get_face_locations(image_path)
        face_paths = []
        if face_locations:
            face_output_path = os.path.join(output_path, 'face')
            os.makedirs(face_output_path, exist_ok=True)
            face_paths = save_face_images(
                image_path, face_locations, face_output_path)

        # 保存原始图片地址和缩略图地址以及人脸图片地址到CSV文件中
        save_to_sqlite(metadata, image_path, thumbnail_path,
                       ','.join(face_paths), output_folder)
        print('Processed image:', image_name)
        print(' - Taken time:', metadata['taken_time'])

    except Exception as e:
        print('Error processing image:', image_path)
        print(' -', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process images in a directory.')
    parser.add_argument('input_folder', default='./source',
                        help='Input folder path')
    parser.add_argument('output_folder', default='./output',
                        help='Output folder path')
    parser.add_argument('--skip-dirs', default=None,
                        help='Folders to skip during processing')
    parser.add_argument('--max-cpu-ratio', type=float,
                        default=0.7, help='Maximum CPU ratio for pool size')
    args = parser.parse_args()

    skip_dirs_params = os.environ.get('SKIP_DIRS', args.skip_dirs)
    skip_dirs = []
    if skip_dirs_params:
        skip_dirs = skip_dirs_params.split(',')
    max_cpu_ratio = float(os.environ.get('MAX_CPU_RATIO', args.max_cpu_ratio))

    input_folder = args.input_folder
    output_folder = args.output_folder
    print('[max cpu ratio]:', max_cpu_ratio)

    # 获取已处理的文件列表
    processed_files = get_processed_files(output_folder)
    print('[Processed files]:', len(processed_files))
    # 进程池大小
    pool_size = math.ceil(int(cpu_count() * max_cpu_ratio))
    print('[Pool size]:', pool_size)
    # 要跳过的目录
    print('[Skip directories]:', skip_dirs)

    with Pool(pool_size) as pool:

        for root, dirs, files in os.walk(input_folder):
            # 检查是否需要跳过该目录
            skip_dir = any([d in root for d in skip_dirs])
            if skip_dir:
                print('Skip directory:', root)
                continue
            for file in files:
                if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                    # 如果已处理过该文件，则跳过
                    if os.path.join(root, file) in processed_files:
                        print('Skip file:', file)
                        continue
                    # 处理图片
                    image_path = os.path.join(root, file)
                    print('[Process image]:', image_path)
                    pool.apply_async(process_image, args=(
                        image_path, output_folder))
                    
        # 使用pool.map()方法将任务分配给不同的进程，并等待结果返回
        pool.map(process_address, os.path.join(output_folder,  'imagedb.db'))

        pool.close()
        pool.join()
