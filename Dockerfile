# 使用官方Python运行时作为父镜像
FROM python:3.8-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录内容复制到位于/app中的容器中
COPY . /app

# 使端口80可供此容器外的环境使用
EXPOSE 80

# 定义环境变量
ENV NAME World

# 在容器启动时运行app.py
CMD ["/app/run.sh"]


# # # 构建Docker镜像
# docker build -t flask-app .

# # 运行Docker容器
# docker run -p 5000:5001 flask-app
