# A股智能助手 - 部署指南

## 📋 目录

- [快速开始](#快速开始)
- [本地部署](#本地部署)
- [Docker部署](#docker部署)
- [GitHub Actions部署](#github-actions部署)
- [配置说明](#配置说明)
- [使用手册](#使用手册)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 方式一：GitHub Actions（推荐）

GitHub Actions是最简单的部署方式，零成本，无需服务器。

#### 步骤1：Fork仓库

1. 访问你的GitHub仓库
2. 点击右上角的 `Fork` 按钮
3. 等待Fork完成

#### 步骤2：配置Secrets

1. 进入你的仓库：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`
2. 添加以下Secrets：

| Secret名称 | 说明 | 必填 | 示例 |
|------------|------|------|--------|
| `GEMINI_API_KEY` | Google AI API Key | ✅ | `AIzaSy...` |
| `OPENAI_API_KEY` | OpenAI兼容API Key | 可选 | `sk-...` |
| `OPENAI_BASE_URL` | OpenAI兼容API地址 | 可选 | `https://api.deepseek.com/v1` |
| `OPENAI_MODEL` | 模型名称 | 可选 | `deepseek-chat` |
| `STOCK_LIST` | 自选股代码 | ✅ | `600519,000001,300260` |
| `WECHAT_WEBHOOK_URL` | 企业微信Webhook URL | 可选 | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...` |
| `FEISHU_WEBHOOK_URL` | 飞书Webhook URL | 可选 | `https://open.feishu.cn/open-apis/bot/v2/hook/...` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 可选 | `123456789:ABC...` |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 可选 | `123456789` |
| `EMAIL_SENDER` | 发件人邮箱 | 可选 | `your@email.com` |
| `EMAIL_PASSWORD` | 邮箱授权码 | 可选 | `your_password` |
| `EMAIL_RECEIVERS` | 收件人邮箱 | 可选 | `receiver@email.com` |

**注意：**
- `GEMINI_API_KEY` 和 `OPENAI_API_KEY` 至少配置一个
- `STOCK_LIST` 是必填的
- 其他都是可选的，根据需要配置

#### 步骤3：启用Actions

1. 进入 `Actions` 标签页
2. 找到 `每日股票分析` 工作流
3. 点击 `I understand my workflows, go ahead and enable them`
4. 等待工作流自动运行

#### 步骤4：手动触发

1. 进入 `Actions` 标签页
2. 找到 `每日股票分析` 工作流
3. 点击 `Run workflow` 按钮
4. 选择分支：`main`
5. 点击 `Run workflow` 按钮

#### 工作流说明

- **自动触发**：每个工作日 18:00（北京时间）自动执行
- **手动触发**：可以随时手动触发分析
- **参数说明**：
  - `stock_list`：自选股代码列表（逗号分隔）
  - `run_backtest`：是否运行回测（默认false）
  - `notify`：是否发送推送通知（默认true）

---

### 方式二：本地部署

#### 步骤1：安装依赖

```bash
# 克隆仓库
git clone <your-repo-url>
cd <your-repo-name>

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2：配置环境变量

创建 `.env` 文件：

```bash
# AI配置（至少配置一个）
GEMINI_API_KEY=your_gemini_api_key
# 或者
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 自选股配置
STOCK_LIST=600519,000001,300260

# 推送配置（可选）
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
EMAIL_SENDER=your@email.com
EMAIL_PASSWORD=your_password
EMAIL_RECEIVERS=receiver@email.com
```

#### 步骤3：运行应用

```bash
# 正常运行（PyQt5桌面模式）
python main.py

# Web界面模式
python main.py --webui

# 仅Web服务模式
python main.py --webui-only

# 定时任务模式
python main.py --schedule
```

---

### 方式三：Docker部署

#### 步骤1：构建镜像

```bash
# 构建镜像
docker build -t aistock-assistant .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  aistock-assistant
```

#### 步骤2：Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  aistock:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
    restart: unless-stopped
```

运行：

```bash
docker-compose up -d
```

---

## ⚙️ 配置说明

### AI模型配置

#### OpenAI兼容（推荐）

支持以下API提供商：
- DeepSeek（推荐）：https://platform.deepseek.com/
- 通义千问：https://dashscope.aliyun.com/
- 硅基流动：https://cloud.siliconflow.cn/
- 火山云：https://ark.cn/zh/product/DeepSeek
- 其他OpenAI兼容API
- 硅基流动：https://cloud.siliconflow.cn/
- 火山云：https://ark.cn/zh/product/DeepSeek
- 其他OpenAI兼容API

### 数据源配置

系统支持多源数据策略，优先级如下：

1. **AkShare**（优先级0）- 默认启用
2. **Pytdx**（优先级1）- 默认启用
3. **EastMoney**（优先级2）- 默认启用
4. **Mock**（优先级3）- 默认启用

在 `config.json` 中配置：

```json
{
  "data_sources": {
    "akshare": {
      "enabled": true,
      "priority": 0
    },
    "pytdx": {
      "enabled": true,
      "priority": 1,
      "server_host": "111.229.247.189",
      "server_port": 7709,
      "max_retries": 3,
      "retry_delay": 2
    },
    "eastmoney": {
      "enabled": true,
      "priority": 2
    },
    "mock": {
      "enabled": true,
      "priority": 3
    }
  }
}
```

### 推送配置

支持多渠道推送，在 `config.json` 中配置：

```json
{
  "notification": {
    "enabled": true,
    "channels": {
      "wechat": {
        "enabled": true,
        "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
        "msg_type": "markdown"
      },
      "feishu": {
        "enabled": false,
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
        "msg_type": "card"
      },
      "telegram": {
        "enabled": false,
        "bot_token": "xxx",
        "chat_id": "xxx"
      },
      "email": {
        "enabled": false,
        "sender": "your@email.com",
        "password": "xxx",
        "receivers": "receiver@email.com"
      }
    }
  }
}
```

### 回测配置

在 `config.json` 中配置：

```json
{
  "backtest": {
    "enabled": true,
    "eval_window_days": 10,
    "min_age_days": 14,
    "limit": 200
  }
}
```

---

## 📖 使用手册

### 命令行参数

```bash
# 帮助信息
python main.py --help

# 正常运行（PyQt5桌面模式）
python main.py

# Web界面模式
python main.py --webui

# 仅Web服务模式
python main.py --webui-only

# 定时任务模式
python main.py --schedule

# 运行回测
python main.py --backtest

# 指定股票分析
python main.py --stocks 600519,000001

# 禁用推送通知
python main.py --no-notify

# 单股推送模式（每分析完一只立即推送）
python main.py --single-notify
```

### Web界面功能

访问 `http://localhost:8000` 可以使用Web界面，功能包括：

1. **仪表盘** - 查看系统状态、数据源状态、推送状态
2. **自选股管理** - 添加/删除自选股
3. **股票分析** - 手动触发股票分析
4. **分析历史** - 查看历史分析记录
5. **回测管理** - 查看回测结果
6. **配置管理** - 配置AI模型、数据源、推送渠道
7. **推送历史** - 查看推送历史记录

### 多智能体分析

系统支持四个智能体同时分析：

1. **市场分析师** - 分析市场趋势、板块轮动、资金流向
2. **技术分析师** - 分析技术指标（MA、MACD、RSI、KDJ、BOLL、ATR、CCI、OBV）和K线形态
3. **基本面分析师** - 分析估值、盈利能力、成长能力、财务健康度
4. **新闻分析师** - 分析舆情情绪、新闻搜索、新闻影响

每个智能体独立分析，最终由协调器整合结果，提供综合投资建议。

### 回测功能

系统支持自动回测历史分析结果，计算：

- **方向准确率** - 预测方向与实际方向的一致性
- **止盈命中率** - 达到目标价的比例
- **止损命中率** - 触发止损的比例
- **综合评分** - 加权计算的整体表现评分

### 推送功能

支持多渠道推送：

1. **企业微信** - 支持Markdown和文本格式
2. **飞书** - 支持富文本和卡片消息
3. **Telegram** - 支持Bot API
4. **邮件** - 支持SMTP协议

推送系统支持队列和重试机制，确保消息可靠送达。

---

## 🔧 常见问题

### Q1：如何获取AI API Key？

**A：** Gemini（免费）
1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 创建新项目
3. 选择 "Get API Key"
4. 复制 API Key 到 `.env` 文件

**B：** OpenAI兼容**
1. 访问对应API提供商官网
2. 注册账号并获取API Key
3. 复制 API Key 和 Base URL 到 `.env` 文件

### Q2：如何配置自选股？

**A：** GitHub Actions
在仓库设置中添加 `STOCK_LIST` Secret

**B：** 本地部署
在 `.env` 文件中设置 `STOCK_LIST=600519,000001,300260`

**C：** Web界面
在Web界面的"自选股管理"页面添加股票

### Q3：推送不工作？

**A：** 检查配置
1. 确认 `.env` 文件中的推送配置正确
2. 检查Webhook URL是否正确
3. 查看日志文件排查问题

**B：** 测试推送
1. 使用测试工具测试Webhook URL
2. 检查推送是否成功

### Q4：如何查看日志？

**A：** GitHub Actions
1. 进入 `Actions` 标签页
2. 点击对应的工作流
3. 查看运行日志

**B：** 本地部署
1. 查看控制台输出
2. 查看日志文件（如果配置了日志文件）

### Q5：如何切换数据源？

**A：** 配置文件
在 `config.json` 中修改 `data_sources` 配置，禁用/启用对应数据源

**B：** 环境变量
在 `.env` 文件中设置对应的环境变量

### Q6：如何启用/禁用推送？

**A：** 配置文件
在 `config.json` 中修改 `notification.enabled` 为 `true` 或 `false`

**B：** 环境变量
在 `.env` 文件中设置对应的环境变量

---

## 🎯 核心特性

### 100%保留原有功能

- ✅ **个人化知识库** - 完整保留，支持分类、标签、搜索
- ✅ **AI记忆系统** - 完整保留，支持多轮对话
- ✅ **PyQt5界面** - 完整保留，桌面应用体验

### 新增功能

- ✅ **多源数据策略** - AkShare、Pytdx、EastMoney、Mock，自动降级
- ✅ **多智能体分析** - 市场、技术、基本面、新闻四维度
- ✅ **多渠道推送** - 企业微信、飞书、Telegram、邮件
- ✅ **回测系统** - 自动评估历史分析准确率
- ✅ **Web界面** - 配置管理、任务监控
- ✅ **GitHub Actions** - 零成本自动化部署
- ✅ **Docker支持** - 容器化部署

### 部署方式对比

| 特性 | 原项目 | 集成后 |
|------|--------|--------|
| 数据层 | pytdx（不稳定） | 多源策略（AkShare优先级0） |
| AI分析 | 单一AI分析 | 多智能体（市场+技术+基本面+新闻） |
| 推送 | 无 | 多渠道推送（企业微信+飞书+Telegram+邮件） |
| 回测 | 无 | 完整回测系统（方向胜率+止盈止损命中率） |
| 部署 | 本地运行 | GitHub Actions + Docker支持 |
| 知识库 | 保留 | 100%保留并增强 |
| AI记忆 | 保留 | 100%保留并增强 |

---

## 📞 技术支持

### 系统要求

- **Python版本**：3.10+
- **操作系统**：Windows / Linux / macOS
- **内存**：建议 4GB+
- **网络**：需要访问互联网（数据源、AI API、推送）

### 依赖说明

主要依赖：

- **数据源**：akshare、pytdx、requests
- **AI**：openai、google-generativeai
- **推送**：requests
- **Web框架**：fastapi、uvicorn
- **数据处理**：pandas、numpy
- **其他**：python-dotenv、schedule

---

## 🎉 开始使用

恭喜！你的A股智能助手已经升级完成，现在可以开始使用了。

建议从[快速开始](#快速开始)选择合适的部署方式，按照[配置说明](#配置说明)进行配置。

祝你投资顺利！
