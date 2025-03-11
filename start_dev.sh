#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 输出带颜色的信息
info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 确保输出目录存在
mkdir -p output/web_generated
info "已创建输出目录: output/web_generated"

# 安装后端依赖
info "安装后端依赖..."
pip install fastapi uvicorn python-multipart

# 确保前端公共目录存在
mkdir -p frontend/public
info "已确保frontend/public目录存在"

# 启动后端服务器（后台运行）
info "启动后端服务器..."
cd backend || { error "backend目录不存在"; exit 1; }

if [ ! -f "main.py" ]; then
  error "main.py文件不存在，请确保backend目录结构正确"
  exit 1
fi

uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

if [ -z "$BACKEND_PID" ]; then
  error "后端服务器启动失败"
  exit 1
else
  info "后端服务器已启动，PID: $BACKEND_PID"
fi

# 检查前端目录结构
if [ ! -d "frontend/src" ]; then
  error "frontend/src目录不存在，请检查项目结构"
  exit 1
fi

# 如果前端目录中没有node_modules，初始化前端
if [ ! -d "frontend/node_modules" ]; then
  info "初始化前端..."
  cd frontend || { error "frontend目录不存在"; exit 1; }
  
  if [ ! -f "package.json" ]; then
    error "package.json不存在，请确保前端配置正确"
    exit 1
  fi
  
  info "安装前端依赖，请稍候..."
  npm install
  if [ $? -ne 0 ]; then
    error "npm install 失败，请检查错误信息"
    exit 1
  fi
  cd ..
fi

# 启动前端开发服务器
info "启动前端开发服务器..."
cd frontend || { error "frontend目录不存在"; exit 1; }
npm start

# 当前端服务器退出时，杀死后端进程
info "清理进程..."
kill $BACKEND_PID
info "已停止后端服务器" 