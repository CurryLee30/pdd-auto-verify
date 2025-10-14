# 拼多多虚拟商品自动核销系统

## 项目结构
```
pdd-virtual-auto-verify/
├── config/                 # 配置文件
│   ├── __init__.py
│   ├── settings.py         # 系统配置
│   └── api_config.py       # API配置
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── api_client.py       # API客户端
│   ├── order_manager.py    # 订单管理
│   ├── verification.py     # 核销逻辑
│   └── exceptions.py       # 异常处理
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── database.py         # 数据库配置
│   ├── order.py           # 订单模型
│   └── product.py         # 商品模型
├── services/              # 业务服务
│   ├── __init__.py
│   ├── order_service.py   # 订单服务
│   ├── verification_service.py  # 核销服务
│   └── notification_service.py  # 通知服务
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── logger.py          # 日志工具
│   ├── validators.py      # 验证工具
│   └── helpers.py         # 辅助函数
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_api_client.py
│   ├── test_order_manager.py
│   └── test_verification.py
├── scripts/               # 脚本文件
│   ├── __init__.py
│   ├── start_monitor.py   # 启动监控脚本
│   └── manual_verify.py   # 手动核销脚本
├── .env.example           # 环境变量示例
├── .env                   # 环境变量（不提交到版本控制）
├── requirements.txt       # 依赖包
├── README.md             # 项目说明
└── main.py               # 主程序入口
```

## 主要功能

1. **订单监控**: 实时监控拼多多订单状态变化
2. **自动核销**: 根据订单信息自动执行核销操作
3. **异常处理**: 处理各种异常情况并记录日志
4. **状态同步**: 保持本地数据库与平台数据同步
5. **通知服务**: 核销结果通知和异常告警

## 技术栈

- Python 3.8+
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- Redis (缓存)
- Celery (异步任务)
- Loguru (日志)
- Pydantic (数据验证)

## 安装和使用

1. 安装依赖: `pip install -r requirements.txt`
2. 配置环境变量: 复制 `.env.example` 到 `.env` 并填写配置
3. 初始化数据库: `python scripts/init_db.py`
4. 启动服务: `python main.py`

## 注意事项

- 确保遵守拼多多平台规则和政策
- 定期更新API接口适配
- 做好数据备份和恢复机制
- 监控系统运行状态和性能指标
