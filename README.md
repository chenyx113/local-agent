# Ollama Web Chat Service

An intelligent chat service based on Ollama, supporting local model chat and Tavily real-time search functionality.

<img width="1150" height="781" alt="image" src="https://github.com/user-attachments/assets/f3603ccf-e21a-4544-ac5b-9299913d6afe" />


## 🚀 Features

- **Multi-Model Support**: Automatically detects and supports all local Ollama models
- **Smart Search**: Integrated Tavily API, automatically determines if real-time information search is needed
- **Streaming Response**: Real-time AI response display for smooth conversation experience
- **Web Interface**: Modern web chat interface, mobile-friendly
- **Dynamic Model List**: Real-time query of available models, auto-refresh every 30 seconds
- **Conversation History**: Complete conversation history management and clearing
- **Intelligent Skills System**: Advanced skill-based architecture with LLM-powered routing
- **Smart Skill Routing**: Uses LLM to analyze queries and intelligently select the most appropriate skill

## 📋 System Requirements

- **Python**: 3.8+
- **Ollama**: Locally installed and running
- **Operating System**: Linux, macOS, Windows

## 🔧 Environment Setup

### 1. Install Ollama

First, ensure you have installed and running Ollama:

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download and install: https://ollama.com/download
```

### 2. Install Python Dependencies

```bash
# Clone the project
git clone <repository-url>
cd deep-research

# Install Python dependencies
pip install -r requirements.txt
```

Or install manually:

```bash
pip install flask ollama tavily-python
```

### 3. Install Models (Optional)

```bash
# Install recommended models
ollama pull qwen3.5:2b
ollama pull qwen3:4b
ollama pull llama3.2

# View installed models
ollama list
```

## 📦 Project Structure

```
local-agent/
├── app.py                    # Flask backend service with skills system
├── ollama_chat.py           # Command-line chat program
├── ollama_chat_simple.py    # Simple test program
├── templates/
│   └── index.html           # Web interface template with dynamic parameter configuration
├── skills/                  # Skills system directory
│   ├── README.md            # Skills system documentation
│   ├── list_files.md/py     # File listing skill
│   ├── read_file.md/py      # File reading skill
│   ├── write_file.md/py     # File writing skill
│   ├── search_files.md/py   # File content search skill
│   ├── execute_command.md/py # Shell command execution skill
│   ├── tavily_search.md/py  # Real-time web search skill
│   └── route_skill.md/py    # Intelligent skill routing skill
├── static/                  # Static resources (optional)
│   ├── css/
│   └── js/
├── README.md               # Project documentation
├── README_CN.md            # Chinese documentation
└── requirements.txt        # Python dependencies
```

## 🏃‍♂️ Running Methods

### Method 1: Web Interface (Recommended)

```bash
# Start web service
python app.py

# Access web page
# Open browser and visit: http://localhost:5000
```

**Features:**
- Automatically detects available models and displays them on the left
- Supports model switching
- Streaming AI response display
- Supports Tavily smart search
- Responsive design, mobile-friendly

### Method 2: Command Line Interface

```bash
# Use default model
python ollama_chat.py

# Specify model
python ollama_chat.py qwen3:4b
```

**Features:**
- Interactive command-line chat
- Supports model selection
- Real-time streaming output
- Supports conversation history management

### Method 3: Simple Test

```bash
python ollama_chat_simple.py
```

**Features:**
- Single message test
- Quick verification of model availability
- Simple API call example

## ⚙️ Configuration

### Tavily API Configuration

To enable real-time search functionality, configure Tavily API key:

```bash
# Set environment variable
export TAVILY_API_KEY="your_tavily_api_key_here"

# Or permanently set in .bashrc/.zshrc
echo 'export TAVILY_API_KEY="your_tavily_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Get Tavily API Key:**
1. Visit [Tavily AI](https://tavily.com/)
2. Register account and get API key
3. Configure environment variable as shown above

### Model Configuration

The system automatically detects all installed Ollama models. You can also manually specify models:

```python
# Specify default model in code
chat_client = OllamaChat(model_name="qwen3.5:2b")
```

## 🎯 Usage Guide

### Web Interface Usage

1. **Start Service**: `python app.py`
2. **Access Web**: Open browser and visit `http://localhost:5000`
3. **Select Model**: Choose the model to use from the model list on the left
4. **Start Chat**: Enter message in the input box at the bottom and send
5. **Smart Search**: When asking for real-time information, the system will automatically search

### Command Line Usage

1. **Start Program**: `python ollama_chat.py`
2. **Select Model**: Program displays available model list, select or enter model name
3. **Start Chat**: Enter message, AI will respond in real-time
4. **Manage Conversation**:
   - Enter `clear` to clear conversation history
   - Enter `exit` to exit program

### Intelligent Skills System

The system uses LLM-powered skill routing to intelligently handle different types of queries:

#### File System Operations
- **List Files**: "List files in /home/user/documents" → `list_files` skill
- **Read Files**: "Read the content of config.json" → `read_file` skill
- **Write Files**: "Create a new file called notes.txt" → `write_file` skill
- **Search Files**: "Search for TODO comments in the codebase" → `search_files` skill

#### System Operations
- **Execute Commands**: "Run 'ls -la' command" → `execute_command` skill
- **System Info**: "Get system information" → `get_system_info` skill

#### Real-time Information
- **Latest News**: "What are the latest developments in AI?" → `tavily_search` skill
- **Weather**: "What's the current weather in New York?" → `tavily_search` skill
- **Stock Prices**: "What's the stock price of Apple?" → `tavily_search` skill

#### Smart Routing
The system automatically analyzes your query and selects the most appropriate skill:
- Uses LLM to understand query intent
- Considers conversation context
- Provides confidence scores for skill selection
- Falls back to keyword-based routing if needed

### Smart Search Function

The system automatically determines if real-time search is needed:

**Queries that trigger search:**
- Contains timeliness keywords: `latest`, `recent`, `current`, `today`, `now`
- Weather queries: `weather`, `temperature`, `what is the weather`
- Stock prices: `stock price`, `current price`
- News events: `news`, `latest news`, `what happened`
- Current date related: queries containing current year or date

**Queries that don't trigger search:**
- General questions: `How to write Python?`
- Programming help: `Debug this code`
- Casual chat: `Tell me a joke`

## 🛠️ Development Notes

### Backend API

Main API endpoints:

- `GET /` - Web interface
- `GET /api/models` - Get available model list
- `POST /api/set_model` - Set current model
- `POST /api/chat` - Send chat message (supports streaming response)
- `POST /api/clear` - Clear conversation history
- `GET /api/status` - Get current status
- `GET /api/skills` - Get available skills list
- `POST /api/skill/<skill_name>` - Execute specific skill

### Skills System Architecture

The system implements a sophisticated skill-based architecture with intelligent routing:

#### Skill Routing Logic

1. **Primary Analysis**: `route_skill` uses LLM to analyze user queries
2. **Confidence Scoring**: Each skill selection includes a confidence score (0.0-1.0)
3. **Context Awareness**: Considers conversation history for better decisions
4. **Fallback Mechanism**: Keyword-based routing if LLM analysis fails
5. **Multi-skill Support**: Complex queries can trigger multiple skills sequentially

#### Skill Activation Patterns

**File System Skills**:
- `list_files`: "list files", "show files", "what files", "ls ", "dir "
- `read_file`: "read file", "show content", "cat ", "head ", "tail "
- `write_file`: "write file", "create file", "echo ", "touch "
- `search_files`: "search file", "find file", "grep ", "rgrep "

**System Skills**:
- `execute_command`: "run command", "execute command", "cd ", "mkdir ", "rm "

**Real-time Information Skills**:
- `tavily_search`: "latest", "recent", "current", "weather", "stock", "news"

### Frontend Tech Stack

- **HTML5** - Page structure
- **CSS3** - Style design (responsive layout)
- **JavaScript (ES6+)** - Interactive logic
- **Fetch API** - Communication with backend
- **Server-Sent Events** - Streaming response handling

### Core Function Implementation

1. **Model Detection**: Dynamically obtain through `ollama list` API
2. **Streaming Response**: Use `stream=True` parameter for real-time output
3. **Smart Search**: Determine search needs based on keyword and pattern matching
4. **Context Management**: Maintain complete conversation history
5. **Skill Execution**: Intelligent routing and execution of appropriate skills

## 🐛 Troubleshooting

### Common Issues

**Q: Ollama not running**
```
Error: Failed to connect to Ollama
```
**A:** Ensure Ollama is running:
```bash
ollama serve
```

**Q: Model not found**
```
Model 'xxx' not found
```
**A:** Install required model:
```bash
ollama pull model_name
```

**Q: Tavily search failed**
```
TAVILY_API_KEY not found
```
**A:** Configure Tavily API key environment variable

**Q: Port already in use**
```
Address already in use
```
**A:** Modify port number in `app.py`:
```python
app.run(host='0.0.0.0', port=5001)  # Change to other port
```

### Debug Mode

Start debug mode to view detailed logs:

```bash
# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start service
python app.py
```

## 📊 Performance Optimization

### Model Selection Recommendations

- **Fast Response**: qwen3:0.6b, qwen3.5:0.8b
- **Balanced Performance**: qwen3:4b, qwen3.5:2b
- **High Quality**: llama3.2, qwen2.5-coder:3b

### Configuration Optimization

Adjust model parameters in `app.py`:

```python
options={
    'num_ctx': 4096,      # Context window size
    'num_predict': 2048,  # Max tokens to generate
    'temperature': 0.7,   # Creativity level
    'top_p': 0.9,         # Nucleus sampling parameter
    'repeat_penalty': 1.1 # Repetition penalty
}
```

## 🤝 Contribution Guide

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) - Local AI model runtime
- [Tavily AI](https://tavily.com/) - Real-time search API
- [Flask](https://flask.palletsprojects.com/) - Web framework

## 📞 Contact

For questions or suggestions, please contact via:

- Submit Issue
- Send email
- Project discussion area

---

**Enjoy the fun of intelligent chat!** 🤖✨
