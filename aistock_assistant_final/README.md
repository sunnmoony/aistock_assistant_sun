# A股智能助手

一个基于PyQt5的A股智能分析助手，集成实时行情、AI分析、知识库等功能。

## 功能特性

- 📊 **实时行情** - 支持多种数据源（AkShare、通达信、Tushare等）
- 🤖 **AI助手** - 集成多种AI模型（DeepSeek、OpenAI等）
- 📚 **知识库** - 投资知识管理和文档管理
- 📈 **技术分析** - K线图、技术指标分析
- 🔔 **智能提醒** - 价格预警、新闻推送

## 安装

### 环境要求

- Python 3.8+
- Windows/Linux/macOS

### 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制配置文件模板：
```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml`，填入您的API密钥：
```yaml
ai:
  api_key: 'YOUR_API_KEY_HERE'
  
data_sources:
  tushare:
    api_key: 'YOUR_TUSHARE_API_KEY_HERE'
    
search:
  bocha_api_keys:
    - 'YOUR_BOCHA_API_KEY_HERE'
```

## 运行

```bash
python main.py
```

或使用批处理文件（Windows）：
```bash
check_and_run.bat
```

## 数据源

支持以下数据源：

- **AkShare** - 免费开源的金融数据接口
- **通达信** - 通达信行情接口
- **Tushare** - 金融数据接口（需要API密钥）
- **博查** - 搜索API（需要API密钥）
- **Mock** - 模拟数据（用于测试）

## AI模型

支持以下AI模型：

- **DeepSeek** - 深度求索AI模型
- **OpenAI** - GPT系列模型
- **硅基流动** - SiliconFlow API

## 项目结构

```
aistock_assistant_final/
├── core/                    # 核心模块
│   ├── data_providers/      # 数据提供者
│   ├── data_manager.py      # 数据管理器
│   ├── ai_engine.py         # AI引擎
│   └── ...
├── ui/                      # UI模块
│   ├── pages/               # 页面
│   ├── components/          # 组件
│   └── main_window.py       # 主窗口
├── models/                  # 数据模型
├── config.yaml              # 配置文件
├── main.py                  # 入口文件
└── requirements.txt         # 依赖列表
```

## 技术栈

- **PyQt5** - GUI框架
- **AkShare** - 金融数据接口
- **Pytdx** - 通达信接口
- **APScheduler** - 任务调度
- **Pandas** - 数据处理

## 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。使用本软件进行投资决策的风险由用户自行承担。

## 联系方式

如有问题或建议，请提交 Issue。
