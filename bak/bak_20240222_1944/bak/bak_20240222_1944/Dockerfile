# 使用官方Python运行时作为父镜像
FROM python:3.8-slim
 
# 设置工作目录为/app
WORKDIR /app

# 将当前目录内容映射到容器的/app目录
ADD ./app /app

# 使端口80可供此容器外的环境使用
EXPOSE 80

# 定义环境变量
ENV NAME World

# 下载依赖库
RUN pip install --no-cache-dir -r requirements.txt --index-url="https://pypi.mirrors.ustc.edu.cn/simple/"

# 在容器启动时运行app.py
CMD ["python", "app.py"]


# # # 构建Docker镜像
# docker build -t flask-app .

# # 运行Docker容器
# docker run -p 5000:5001 flask-app
