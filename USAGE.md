# 拼多多虚拟商品自动核销系统使用说明

## 系统概述

本系统是一个基于拼多多开放平台API的虚拟商品自动核销系统，能够自动监控订单状态、处理虚拟商品发货和核销操作。

## 主要功能

1. **订单监控**: 实时监控拼多多订单状态变化
2. **自动发货**: 自动发送虚拟商品信息给买家
3. **自动核销**: 根据订单信息自动执行核销操作
4. **异常处理**: 处理各种异常情况并记录日志
5. **状态同步**: 保持本地数据库与平台数据同步
6. **通知服务**: 核销结果通知和异常告警

## 安装和配置

### 1. 环境要求

- Python 3.8+
- 拼多多开放平台开发者账号
- 数据库（SQLite/MySQL/PostgreSQL）

### 2. 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd pdd-virtual-auto-verify

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化系统
python scripts/init.py

# 4. 配置环境变量
cp env.example .env
# 编辑 .env 文件，填写正确的配置信息
```

### 3. 环境配置

编辑 `.env` 文件，填写以下配置：

```env
# 拼多多开放平台配置
PDD_APP_ID=your_app_id
PDD_APP_SECRET=your_app_secret
PDD_ACCESS_TOKEN=your_access_token

# 数据库配置
DATABASE_URL=sqlite:///./pdd_auto_verify.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/pdd_auto_verify.log

# 系统配置
ORDER_CHECK_INTERVAL=60  # 订单检查间隔（秒）
MAX_RETRY_TIMES=3        # 最大重试次数

# 通知配置
NOTIFICATION_ENABLED=True
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_TO=admin@example.com
```

## 使用方法

### 1. 启动系统

```bash
# 启动定时任务（默认模式）
python main.py

# 启动订单监控
python main.py monitor

# 启动自动核销
python main.py verify

# 执行一次性任务（测试用）
python main.py once

# 启动Web服务器
python main.py web
```

### 2. Web API接口

启动Web服务器后，可以通过以下API接口进行操作：

#### 核销订单
```http
POST /verify
Content-Type: application/json

{
    "order_sn": "订单号",
    "verification_code": "核销码"
}
```

#### 获取订单列表
```http
GET /orders?page=1&page_size=20
```

#### 获取核销记录
```http
GET /verification-records?page=1&page_size=20
```

### 3. 手动核销

```python
from core.verification import VirtualGoodsVerifier

verifier = VirtualGoodsVerifier()
result = verifier.verify_order("订单号", "核销码")
print(result)
```

### 4. 批量核销

```python
from core.verification import VirtualGoodsVerifier

verifier = VirtualGoodsVerifier()
verification_list = [
    {"order_sn": "订单号1", "verification_code": "核销码1"},
    {"order_sn": "订单号2", "verification_code": "核销码2"}
]
result = verifier.batch_verify_orders(verification_list)
print(result)
```

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   拼多多平台    │    │   本地数据库    │    │   通知服务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API客户端      │    │   订单服务      │    │   邮件通知      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   订单管理器     │    │   核销服务      │    │   日志系统      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   自动核销器     │    │   异常处理      │    │   定时任务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 工作流程

1. **订单监控**: 系统定时检查拼多多平台的新订单
2. **订单处理**: 识别虚拟商品订单，保存到本地数据库
3. **自动发货**: 生成虚拟商品信息（卡密、兑换码等），发送给买家
4. **状态更新**: 更新订单状态为已发货
5. **自动核销**: 根据业务逻辑自动执行核销操作
6. **结果通知**: 发送核销结果通知

## 注意事项

### 1. 平台规则遵守

- 确保遵守拼多多平台规则和政策
- 虚拟商品必须符合平台要求
- 及时处理订单，避免超时

### 2. 安全考虑

- 妥善保管API密钥和访问令牌
- 定期备份数据库
- 监控系统运行状态

### 3. 性能优化

- 合理设置订单检查间隔
- 监控API调用频率限制
- 优化数据库查询性能

### 4. 异常处理

- 系统会自动重试失败的API调用
- 记录详细的错误日志
- 发送异常通知邮件

## 故障排除

### 1. API调用失败

- 检查API密钥和访问令牌是否正确
- 确认网络连接正常
- 查看API调用频率是否超限

### 2. 数据库连接失败

- 检查数据库配置是否正确
- 确认数据库服务是否运行
- 检查数据库权限设置

### 3. 邮件发送失败

- 检查SMTP服务器配置
- 确认邮箱账号和密码正确
- 检查防火墙设置

### 4. 订单处理异常

- 查看详细错误日志
- 检查订单状态是否正确
- 确认虚拟商品信息格式

## 技术支持

如遇到问题，请：

1. 查看系统日志文件
2. 检查配置文件设置
3. 参考API文档
4. 联系技术支持团队

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的订单监控和自动核销功能
- 提供Web API接口
- 支持邮件通知功能