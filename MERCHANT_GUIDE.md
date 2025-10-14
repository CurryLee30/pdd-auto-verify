# 商家使用指南

## 部署方案

### 方案一：云端部署（推荐）

#### 1. 服务器要求
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 50GB以上
- **网络**: 稳定的网络连接
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+

#### 2. 部署步骤

```bash
# 1. 安装Python环境
sudo apt update
sudo apt install python3.8 python3.8-pip python3.8-venv

# 2. 创建应用目录
sudo mkdir -p /opt/pdd-auto-verify
sudo chown $USER:$USER /opt/pdd-auto-verify
cd /opt/pdd-auto-verify

# 3. 上传代码
# 将项目文件上传到服务器

# 4. 安装依赖
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. 配置环境
cp test.env.example .env
# 编辑 .env 文件，填写真实配置

# 6. 初始化数据库
python scripts/setup_test_simple.py

# 7. 启动服务
python main.py
```

#### 3. 使用Docker部署（更简单）

```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py", "web"]
```

```bash
# 构建镜像
docker build -t pdd-auto-verify .

# 运行容器
docker run -d \
  --name pdd-auto-verify \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  pdd-auto-verify
```

### 方案二：本地部署

#### 1. Windows环境
```batch
# 1. 安装Python 3.8+
# 2. 下载项目文件
# 3. 解压到本地目录
# 4. 运行安装脚本
python scripts/setup_test_simple.py
# 5. 启动服务
python main.py
```

#### 2. 创建Windows服务
```batch
# 使用NSSM创建Windows服务
nssm install PddAutoVerify "C:\Python38\python.exe" "C:\path\to\main.py"
nssm start PddAutoVerify
```

## 商家配置流程

### 1. 拼多多开放平台申请

#### 步骤1：注册开发者账号
1. 访问 [拼多多开放平台](https://open.pinduoduo.com/)
2. 注册开发者账号
3. 完成实名认证

#### 步骤2：创建应用
1. 登录开发者后台
2. 创建新应用
3. 选择应用类型：**商家应用**
4. 填写应用信息：
   - 应用名称：虚拟商品自动核销系统
   - 应用描述：自动处理虚拟商品订单和核销
   - 回调地址：`http://your-domain.com/callback`

#### 步骤3：申请API权限
需要申请以下API权限：
- `pdd.order.list.get` - 获取订单列表
- `pdd.order.detail.get` - 获取订单详情
- `pdd.order.goods.send` - 订单发货
- `pdd.virtual.goods.verify` - 虚拟商品核销
- `pdd.goods.list.get` - 获取商品列表

#### 步骤4：获取密钥
1. 在应用详情页面获取：
   - `App ID`
   - `App Secret`
2. 通过授权获取：
   - `Access Token`

### 2. 系统配置

#### 配置文件设置
编辑 `.env` 文件：

```env
# 拼多多开放平台配置
PDD_APP_ID=your_real_app_id
PDD_APP_SECRET=your_real_app_secret
PDD_ACCESS_TOKEN=your_real_access_token
PDD_REDIRECT_URI=http://your-domain.com/callback

# 生产环境配置
TEST_MODE=False
DEBUG=False

# 数据库配置（生产环境建议使用MySQL）
DATABASE_URL=mysql://username:password@localhost:3306/pdd_auto_verify

# 系统配置
ORDER_CHECK_INTERVAL=60  # 订单检查间隔（秒）
MAX_RETRY_TIMES=3        # 最大重试次数

# 通知配置
NOTIFICATION_ENABLED=True
EMAIL_SMTP_SERVER=smtp.your-provider.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-email-password
EMAIL_TO=admin@your-domain.com
```

## 商家使用流程

### 1. 系统启动

#### 方式一：命令行启动
```bash
# 启动定时任务（推荐）
python main.py

# 启动Web管理界面
python main.py web
```

#### 方式二：Web界面管理
访问 `http://your-domain.com:8000` 进入管理界面

### 2. 商品管理

#### 上架虚拟商品
1. 在拼多多商家后台创建虚拟商品
2. 设置商品类型为虚拟商品
3. 配置商品信息：
   - 商品名称
   - 价格
   - 库存
   - 商品描述

#### 系统自动识别
- 系统会自动识别虚拟商品订单
- 根据商品类型自动处理

### 3. 订单处理流程

#### 自动处理流程
1. **订单监控** - 系统每60秒检查一次新订单
2. **订单识别** - 自动识别虚拟商品订单
3. **自动发货** - 生成卡密/兑换码并发送给买家
4. **状态更新** - 更新订单状态为已发货
5. **自动核销** - 根据业务规则自动核销

#### 手动处理
- 通过Web界面查看订单状态
- 手动核销特定订单
- 批量处理订单

### 4. 核销管理

#### 自动核销
- 系统根据预设规则自动核销
- 支持多种核销方式：
  - 时间触发
  - 条件触发
  - 手动触发

#### 核销记录
- 查看所有核销记录
- 导出核销报告
- 异常处理记录

## 监控和维护

### 1. 系统监控

#### 日志监控
```bash
# 查看实时日志
tail -f logs/pdd_auto_verify.log

# 查看错误日志
grep ERROR logs/pdd_auto_verify.log
```

#### 性能监控
- CPU使用率
- 内存使用率
- 数据库连接数
- API调用频率

### 2. 数据备份

#### 数据库备份
```bash
# MySQL备份
mysqldump -u username -p pdd_auto_verify > backup_$(date +%Y%m%d).sql

# SQLite备份
cp pdd_auto_verify.db backup_$(date +%Y%m%d).db
```

#### 配置文件备份
```bash
# 备份配置文件
cp .env backup/.env_$(date +%Y%m%d)
```

### 3. 故障处理

#### 常见问题
1. **API调用失败**
   - 检查网络连接
   - 验证API密钥
   - 查看API调用频率限制

2. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接配置
   - 检查数据库权限

3. **订单处理异常**
   - 查看详细错误日志
   - 检查订单状态
   - 验证商品配置

## 商家培训

### 1. 基础培训
- 系统功能介绍
- 基本操作流程
- 常见问题处理

### 2. 高级培训
- 自定义核销规则
- 批量操作技巧
- 性能优化建议

### 3. 技术支持
- 在线文档
- 视频教程
- 技术支持群

## 收费模式

### 1. 软件授权费
- 一次性授权费用
- 包含基础功能
- 提供技术支持

### 2. 服务费
- 按订单数量收费
- 按处理时间收费
- 按功能模块收费

### 3. 定制开发
- 个性化需求开发
- 集成第三方系统
- 特殊功能定制

## 安全保障

### 1. 数据安全
- 数据加密存储
- 定期安全备份
- 访问权限控制

### 2. API安全
- 密钥安全管理
- 请求签名验证
- 频率限制保护

### 3. 系统安全
- 定期安全更新
- 漏洞扫描检测
- 安全日志监控

## 售后服务

### 1. 技术支持
- 7x24小时技术支持
- 远程协助服务
- 问题快速响应

### 2. 系统维护
- 定期系统检查
- 性能优化建议
- 功能更新升级

### 3. 培训服务
- 新用户培训
- 功能更新培训
- 最佳实践分享

这样的部署和使用方案可以让商家轻松使用系统，同时保证稳定性和安全性。
