#!/bin/bash

# 存储当前日期和时间
current_datetime=$(date +%Y%m%d_%H%M)

# 创建备份目录
mkdir -p bak/bak_$current_datetime

# 复制所有文件到备份目录
cp -r Dockerfile app bak run.sh Readme.md bak/bak_$current_datetime

# 如果不存在db，创建app/hotel.db文件
if [ ! -f app/hotel.db ]; then
    mkdir -p app
    touch app/hotel.db
fi

# 更新代码（确保取消下面一行的注释以启用git pull）
# git pull || { echo 'git pull failed'; exit 1; }

# 准备docker环境
sudo docker stop ptest 2>/dev/null || true
sudo docker rm ptest 2>/dev/null || true
sudo docker rmi flask-app 2>/dev/null || true

sudo docker build -t flask-app -f ./Dockerfile . || { echo 'docker build failed'; exit 1; }
sudo docker run -dti --name ptest -p 5001:5000 -v ./app:/app flask-app || { echo 'docker run failed'; exit 1; }
