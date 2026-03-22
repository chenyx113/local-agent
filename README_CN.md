# Ollama Web Chat Service

一个基于Ollama的智能聊天服务，支持本地模型聊天和Tavily实时搜索功能。

## 🚀 功能特性

- **多模型支持**：自动检测并支持所有本地Ollama模型
- **智能搜索**：集成Tavily API，自动判断是否需要实时信息搜索
- **流式响应**：AI回复实时显示，提供流畅的对话体验
- **Web界面**：现代化的网页聊天界面，支持移动端
- **动态模型列表**：实时查询可用模型，每30秒自动刷新
- **对话历史**：完整的对话历史管理和清空功能

## 📋 系统要求

- **Python**: 3.8+
- **Ollama**: 本地安装并运行
- **操作系统**: Linux, macOS, Windows

## 🔧 环境搭建

### 1. 安装Ollama

首先确保您已经安装并运行了Ollama：

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载并安装: https://ollama.com/download
```

### 2. 安装Python依赖

```bash
# 克隆项目
git clone <repository-url>
cd deep-research

# 安装Python依赖
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install flask ollama tavily-python
```

### 3. 安装模型（可选）

```bash
# 安装推荐模型
ollama pull qwen3.5:2b
ollama pull qwen3:4b
ollama pull llama3.2

# 查看已安装模型
ollama list
```

## 📦 项目结构

```
deep-research/
├── app.py                    # Flask后端服务
├── ollama_chat.py           # 命令行聊天程序
├── ollama_chat_simple.py    # 简单测试程序
├── templates/
│   └── index.html           # Web界面模板
├── static/                  # 静态资源（可选）
│   ├── css/
│   └── js/
├── README.md               # 项目文档
└── requirements.txt        # Python依赖
```

## 🏃‍♂️ 运行方式

### 方式一：Web界面（推荐）

```bash
# 启动Web服务
python app.py

# 访问网页
# 打开浏览器访问: http://localhost:5000
```

**功能说明：**
- 自动检测可用模型并显示在左侧
- 支持模型切换
- 流式AI回复显示
- 支持Tavily智能搜索
- 响应式设计，支持移动端

### 方式二：命令行界面

```bash
# 使用默认模型
python ollama_chat.py

# 指定模型
python ollama_chat.py qwen3:4b
```

**功能说明：**
- 交互式命令行聊天
- 支持模型选择
- 实时流式输出
- 支持对话历史管理

### 方式三：简单测试

```bash
python ollama_chat_simple.py
```

**功能说明：**
- 单次消息测试
- 快速验证模型可用性
- 简单的API调用示例

## ⚙️ 配置说明

### Tavily API配置

如需启用实时搜索功能，请配置Tavily API密钥：

```bash
# 设置环境变量
export TAVILY_API_KEY="your_tavily_api_key_here"

# 或在.bashrc/.zshrc中永久设置
echo 'export TAVILY_API_KEY="your_tavily_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Tavily API密钥获取：**
1. 访问 [Tavily AI](https://tavily.com/)
2. 注册账号并获取API密钥
3. 按照上述方式配置环境变量

### 模型配置

系统会自动检测所有已安装的Ollama模型。您也可以手动指定模型：

```python
# 在代码中指定默认模型
chat_client = OllamaChat(model_name="qwen3.5:2b")
```

## 🎯 使用指南

### Web界面使用

1. **启动服务**：`python app.py`
2. **访问网页**：打开浏览器访问 `http://localhost:5000`
3. **选择模型**：在左侧模型列表中选择要使用的模型
4. **开始聊天**：在底部输入框输入消息并发送
5. **智能搜索**：当询问实时信息时，系统会自动进行搜索

### 命令行使用

1. **启动程序**：`python ollama_chat.py`
2. **选择模型**：程序会显示可用模型列表，选择或输入模型名称
3. **开始聊天**：输入消息，AI会实时回复
4. **管理对话**：
   - 输入 `clear` 清空对话历史
   - 输入 `exit` 退出程序

### 智能搜索功能

系统会自动判断是否需要实时搜索：

**会触发搜索的查询：**
- 包含时效性关键词：`latest`, `recent`, `current`, `today`, `now`
- 天气查询：`weather`, `temperature`, `what is the weather`
- 股票价格：`stock price`, `current price`
- 新闻事件：`news`, `latest news`, `what happened`
- 当前日期相关：包含当前年份或日期的查询

**不会触发搜索的查询：**
- 一般性问题：`How to write Python?`
- 编程帮助：`Debug this code`
- 闲聊对话：`Tell me a joke`

## 🛠️ 开发说明

### 后端API

主要API接口：

- `GET /` - Web界面
- `GET /api/models` - 获取可用模型列表
- `POST /api/set_model` - 设置当前模型
- `POST /api/chat` - 发送聊天消息（支持流式响应）
- `POST /api/clear` - 清空对话历史
- `GET /api/status` - 获取当前状态

### 前端技术栈

- **HTML5** - 页面结构
- **CSS3** - 样式设计（响应式布局）
- **JavaScript (ES6+)** - 交互逻辑
- **Fetch API** - 与后端通信
- **Server-Sent Events** - 流式响应处理

### 核心功能实现

1. **模型检测**：通过 `ollama list` API动态获取
2. **流式响应**：使用 `stream=True` 参数实现实时输出
3. **智能搜索**：基于关键词和模式匹配判断搜索需求
4. **上下文管理**：维护完整的对话历史

## 🐛 故障排除

### 常见问题

**Q: Ollama未运行**
```
Error: Failed to connect to Ollama
```
**A:** 确保Ollama正在运行：
```bash
ollama serve
```

**Q: 模型未找到**
```
Model 'xxx' not found
```
**A:** 安装所需模型：
```bash
ollama pull model_name
```

**Q: Tavily搜索失败**
```
TAVILY_API_KEY not found
```
**A:** 配置Tavily API密钥环境变量

**Q: 端口被占用**
```
Address already in use
```
**A:** 修改 `app.py` 中的端口号：
```python
app.run(host='0.0.0.0', port=5001)  # 改为其他端口
```

### 调试模式

启动调试模式查看详细日志：

```bash
# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=1

# 启动服务
python app.py
```

## 📊 性能优化

### 模型选择建议

- **快速响应**：qwen3:0.6b, qwen3.5:0.8b
- **平衡性能**：qwen3:4b, qwen3.5:2b
- **高质量**：llama3.2, qwen2.5-coder:3b

### 配置优化

在 `app.py` 中调整模型参数：

```python
options={
    'num_ctx': 4096,      # 上下文窗口大小
    'num_predict': 2048,  # 最大生成token数
    'temperature': 0.7,   # 创造力水平
    'top_p': 0.9,         # 核采样参数
    'repeat_penalty': 1.1 # 重复惩罚
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Ollama](https://ollama.com/) - 本地AI模型运行时
- [Tavily AI](https://tavily.com/) - 实时搜索API
- [Flask](https://flask.palletsprojects.com/) - Web框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 项目讨论区

---

**享受智能聊天的乐趣！** 🤖✨