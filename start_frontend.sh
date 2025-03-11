#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 确保前端目录存在
if [ ! -d "frontend" ]; then
  echo -e "${RED}错误：frontend目录不存在${NC}"
  exit 1
fi

# 切换到项目根目录确保路径正确
cd "$(dirname "$0")"

# 如果前端目录中没有node_modules，初始化前端
if [ ! -d "frontend/node_modules" ]; then
  echo -e "${GREEN}初始化前端...${NC}"
  cd frontend
  
  if [ ! -f "package.json" ]; then
    echo -e "${RED}错误：package.json不存在，请确保前端配置正确${NC}"
    exit 1
  fi
  
  echo -e "${GREEN}安装前端依赖，请稍候...${NC}"
  npm install
  if [ $? -ne 0 ]; then
    echo -e "${RED}错误：npm install 失败，请检查错误信息${NC}"
    exit 1
  fi
  cd ..
fi

# 启动前端开发服务器
echo -e "${GREEN}启动前端开发服务器...${NC}"
cd frontend
npm start

# 这个脚本不会返回，除非用户按Ctrl+C 