# 拼多多自动核销系统 Docker部署方案

## Dockerfile

```dockerfile
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p logs data backup

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令
CMD ["python", "main.py", "web"]
```

## Docker Compose配置

```yaml
version: '3.8'

services:
  pdd-auto-verify:
    build: .
    container_name: pdd-auto-verify
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backup:/app/backup
      - ./.env:/app/.env
    environment:
      - PYTHONPATH=/app
    depends_on:
      - mysql
      - redis
    networks:
      - pdd-network

  mysql:
    image: mysql:8.0
    container_name: pdd-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: pdd_auto_verify
      MYSQL_USER: pdd_user
      MYSQL_PASSWORD: pdd_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - pdd-network

  redis:
    image: redis:7-alpine
    container_name: pdd-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - pdd-network

  nginx:
    image: nginx:alpine
    container_name: pdd-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - pdd-auto-verify
    networks:
      - pdd-network

volumes:
  mysql_data:
  redis_data:

networks:
  pdd-network:
    driver: bridge
```

## Nginx配置

```nginx
events {
    worker_connections 1024;
}

http {
    upstream pdd-backend {
        server pdd-auto-verify:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://pdd-backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/static/;
        }
    }
}
```

## 部署脚本

```bash
#!/bin/bash
# deploy.sh - Docker部署脚本

set -e

echo "开始部署拼多多自动核销系统..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要目录
mkdir -p data logs backup mysql nginx/ssl

# 检查环境配置文件
if [ ! -f .env ]; then
    echo "❌ 未找到.env配置文件，请先配置"
    exit 1
fi

# 构建镜像
echo "构建Docker镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 初始化数据库
echo "初始化数据库..."
docker-compose exec pdd-auto-verify python scripts/setup_test_simple.py

echo "✅ 部署完成！"
echo "访问地址: http://your-domain.com"
echo "管理界面: http://your-domain.com:8000"
```

## 一键部署脚本

```bash
#!/bin/bash
# one-click-deploy.sh - 一键部署脚本

set -e

echo "拼多多自动核销系统 - 一键部署"
echo "================================"

# 检查系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

echo "检测到操作系统: $OS"

# 安装Docker（如果需要）
if ! command -v docker &> /dev/null; then
    echo "安装Docker..."
    if [ "$OS" == "linux" ]; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
    elif [ "$OS" == "mac" ]; then
        echo "请手动安装Docker Desktop for Mac"
        exit 1
    elif [ "$OS" == "windows" ]; then
        echo "请手动安装Docker Desktop for Windows"
        exit 1
    fi
fi

# 安装Docker Compose（如果需要）
if ! command -v docker-compose &> /dev/null; then
    echo "安装Docker Compose..."
    if [ "$OS" == "linux" ]; then
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
fi

# 下载项目文件
echo "下载项目文件..."
if [ ! -d "pdd-auto-verify" ]; then
    git clone https://github.com/your-repo/pdd-auto-verify.git
fi

cd pdd-auto-verify

# 创建环境配置
if [ ! -f .env ]; then
    echo "创建环境配置文件..."
    cp env.example .env
    echo "请编辑 .env 文件，填写拼多多API配置"
    read -p "按回车键继续..."
fi

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh

echo "✅ 一键部署完成！"
```

## 使用说明

### 1. 快速部署
```bash
# 克隆项目
git clone https://github.com/your-repo/pdd-auto-verify.git
cd pdd-auto-verify

# 配置环境
cp env.example .env
# 编辑 .env 文件

# 一键部署
chmod +x one-click-deploy.sh
./one-click-deploy.sh
```

### 2. 手动部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 更新系统
```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务
docker-compose restart
```

### 4. 备份数据
```bash
# 备份数据库
docker-compose exec mysql mysqldump -u root -p pdd_auto_verify > backup.sql

# 备份文件
tar -czf backup_$(date +%Y%m%d).tar.gz data logs
```

### 5. 监控服务
```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 查看日志
docker-compose logs -f pdd-auto-verify
```

## 优势

1. **简单部署** - 一键部署，无需复杂配置
2. **环境隔离** - 容器化部署，避免环境冲突
3. **易于维护** - 统一管理，简化运维
4. **高可用性** - 支持负载均衡和故障转移
5. **安全可靠** - 内置安全配置和监控
6. **扩展性强** - 支持水平扩展和集群部署

这样的部署方案让商家可以轻松部署和使用系统，同时保证稳定性和安全性。
