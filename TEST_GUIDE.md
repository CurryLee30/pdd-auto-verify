# 测试环境使用说明

## 快速开始

### 1. 设置测试环境

```bash
# 运行测试环境设置脚本
python scripts/setup_test.py
```

这个脚本会自动：
- 创建测试环境配置文件
- 安装依赖包
- 初始化数据库
- 创建必要目录

### 2. 启动测试模式

```bash
# 交互式测试模式
python scripts/test_mode.py

# 或者运行完整测试
python scripts/test_mode.py full
```

## 测试环境特性

### 🎯 模拟API客户端

测试环境使用 `MockPddAPIClient` 模拟真实的拼多多API，包括：

- **订单管理**: 获取订单列表、订单详情、更新订单状态
- **商品管理**: 获取商品列表、商品详情、更新库存
- **核销功能**: 虚拟商品核销、获取核销记录
- **发货功能**: 订单发货、确认订单

### 📊 测试数据生成

系统会自动生成测试数据：

- **测试订单**: 10个模拟订单（可配置）
- **测试商品**: 5个虚拟商品
- **核销记录**: 部分订单的核销记录

### 🔧 测试功能

#### 1. 订单监控测试
```bash
python scripts/test_mode.py monitor
```

测试功能：
- 获取待处理订单
- 处理虚拟商品订单
- 自动发货功能

#### 2. 核销功能测试
```bash
python scripts/test_mode.py verify
```

测试功能：
- 单个订单核销
- 批量订单核销
- 核销记录查询

#### 3. API客户端测试
```bash
python scripts/test_mode.py api
```

测试功能：
- 订单列表API
- 商品列表API
- 核销记录API

#### 4. 完整测试
```bash
python scripts/test_mode.py full
```

运行所有测试功能。

## 测试数据说明

### 订单数据格式
```json
{
    "order_sn": "TEST20241201001",
    "buyer_id": "buyer_0001",
    "buyer_name": "测试买家1",
    "order_status": 1,
    "pay_time": "2024-12-01 10:00:00",
    "order_amount": 29.99,
    "goods_list": [
        {
            "goods_id": "goods_1",
            "goods_name": "测试虚拟商品1",
            "goods_type": 1,
            "quantity": 1,
            "price": 29.99
        }
    ]
}
```

### 核销码格式
- 长度：16位
- 字符：大写字母和数字
- 示例：`A1B2C3D4E5F6G7H8`

## 配置说明

### 测试环境配置 (.env)
```env
# 测试模式开关
TEST_MODE=True
DEBUG=True

# 测试数据配置
TEST_ORDER_COUNT=10
TEST_VERIFICATION_CODE_LENGTH=16

# 数据库配置（测试数据库）
DATABASE_URL=sqlite:///./test_pdd_auto_verify.db

# 日志配置
LOG_LEVEL=DEBUG
LOG_FILE=logs/test_pdd_auto_verify.log
```

## 交互式测试菜单

运行 `python scripts/test_mode.py` 后，会显示以下菜单：

```
==================================================
拼多多自动核销系统 - 测试模式
==================================================
1. 设置测试环境
2. 测试订单监控
3. 测试核销功能
4. 测试API客户端
5. 运行完整测试
6. 清除测试数据
0. 退出
==================================================
```

## Web API测试

启动Web服务器进行API测试：

```bash
python main.py web
```

访问 `http://localhost:8000` 查看API文档。

### 测试API接口

#### 核销订单
```bash
curl -X POST "http://localhost:8000/verify" \
     -H "Content-Type: application/json" \
     -d '{"order_sn": "TEST20241201001", "verification_code": "A1B2C3D4E5F6G7H8"}'
```

#### 获取订单列表
```bash
curl "http://localhost:8000/orders?page=1&page_size=10"
```

#### 获取核销记录
```bash
curl "http://localhost:8000/verification-records?page=1&page_size=10"
```

## 注意事项

### 1. 测试数据隔离
- 测试数据使用 `TEST` 前缀标识
- 不会影响生产数据
- 可以随时清除测试数据

### 2. 模拟行为
- API调用有模拟延迟（0.1-0.5秒）
- 核销成功率设置为75%
- 所有API响应都是模拟的

### 3. 数据库
- 使用独立的测试数据库
- 每次测试可以重新生成数据
- 支持SQLite，无需额外配置

### 4. 日志
- 测试模式使用DEBUG级别日志
- 所有操作都有详细记录
- 日志文件：`logs/test_pdd_auto_verify.log`

## 故障排除

### 1. 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### 2. 数据库初始化失败
```bash
# 删除现有数据库文件
rm test_pdd_auto_verify.db

# 重新初始化
python scripts/setup_test.py
```

### 3. 测试数据问题
```bash
# 清除测试数据
python scripts/test_mode.py clear

# 重新生成测试数据
python scripts/test_mode.py setup
```

## 开发建议

1. **先运行完整测试**：了解系统整体功能
2. **使用交互式模式**：逐步测试各个功能
3. **查看日志输出**：了解系统运行状态
4. **修改测试数据**：调整 `TEST_ORDER_COUNT` 等参数
5. **扩展测试功能**：在 `MockPddAPIClient` 中添加更多模拟行为

测试环境已经准备就绪，您可以开始验证系统功能了！
