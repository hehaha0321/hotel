#!/bin/bash 
#
# 先备份当前目录下的所有文件 到 bak/bak_{date}_{time} 目录下 
# 如果不存在bak/bak_{date}_{time} 目录 创建 bak/bak_{date}_{time} 目录
[ ! -d bak/bak_$(date +%Y%m%d_%H%M%S) ] && mkdir -r bak/bak_$(date +%Y%m%d_%H%M%S)
cp -r * bak/bak_$(date +%Y%m%d_%H%M%S)

# 如果不存在db 创建 app/hotel.db 文件 
if [ ! -f app/hotel.db ]; then
    touch app/hotel.db
fi

