#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 确保后端目录存在
if [ ! -d "backend" ]; then
  echo -e "${RED}错误：backend目录不存在${NC}"
  exit 1
fi

# 确保输出目录存在
mkdir -p output/web_generated

# 安装后端依赖
echo -e "${GREEN}安装后端依赖...${NC}"
pip install fastapi uvicorn python-multipart

# 检查依赖安装是否成功
if [ $? -ne 0 ]; then
  echo -e "${RED}错误：安装依赖失败${NC}"
  exit 1
fi

# 处理端口8080冲突
echo -e "${YELLOW}检查端口8080是否被占用...${NC}"
PORT_PID=$(lsof -ti :8080 2>/dev/null)
if [ -n "$PORT_PID" ]; then
  echo -e "${YELLOW}端口8080被进程 $PORT_PID 占用，尝试终止...${NC}"
  kill -9 $PORT_PID 2>/dev/null
  sleep 1
  
  # 再次检查端口是否已释放
  PORT_PID=$(lsof -ti :8080 2>/dev/null)
  if [ -n "$PORT_PID" ]; then
    echo -e "${RED}无法释放端口8080，请手动终止占用该端口的进程${NC}"
    echo -e "${YELLOW}您可以运行: ${NC}lsof -i :8080${YELLOW} 查看占用端口的进程${NC}"
    echo -e "${YELLOW}然后运行: ${NC}kill -9 进程ID${YELLOW} 终止进程${NC}"
    exit 1
  else
    echo -e "${GREEN}端口8080已成功释放${NC}"
  fi
else
  echo -e "${GREEN}端口8080可用${NC}"
fi

# 切换到项目根目录确保路径正确
cd "$(dirname "$0")"

# 启动后端服务器
echo -e "${GREEN}启动后端服务器...${NC}"
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# 这个脚本不会返回，除非用户按Ctrl+C 