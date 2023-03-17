# 设置基础镜像
FROM animcogn/face_recognition

ENV MAX_CPU_RATIO=0.7
ENV SKIP_DIRS=''

# 设置工作目录
WORKDIR /app

# 复制代码到镜像中
COPY . .

# 安装依赖项
RUN pip install --upgrade pip
# RUN apt-get update && apt-get install -y build-essential cmake
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 运行命令
CMD ["python", "main.py" , "./source", "./output"]
