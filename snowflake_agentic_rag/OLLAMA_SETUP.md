# Ollama Setup Guide for Healthcare RAG System

Ollama provides a reliable local LLM fallback when cloud APIs fail. This guide helps you set up Ollama as your primary or backup AI provider.

## 🚀 Quick Setup

### 1. Install Ollama

**macOS:**
```bash
# Download and install from https://ollama.ai
# Or use Homebrew:
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai and run the installer.

### 2. Start Ollama Service

```bash
# Start Ollama (runs on http://localhost:11434)
ollama serve
```

### 3. Pull a Medical-Friendly Model

```bash
# Recommended: Llama 3.2 (good balance of performance and medical knowledge)
ollama pull llama3.2

# Alternative: Smaller model for lower-end hardware
ollama pull llama3.2:1b

# Alternative: Larger model for better performance (if you have 16GB+ RAM)
ollama pull llama3.1:8b
```

### 4. Test the Setup

```bash
# Test that Ollama is working
curl http://localhost:11434/api/tags

# Test a simple medical query
ollama run llama3.2 "What are the symptoms of diabetes?"
```

## 🏥 Healthcare-Optimized Configuration

### Recommended Models for Medical Use

1. **llama3.2** (Default) - Best balance for medical queries
2. **llama3.1:8b** - Better medical knowledge, needs more RAM
3. **codellama** - Good for medical coding/analysis tasks

### Model Selection

```bash
# For general medical questions (recommended)
ollama pull llama3.2

# For detailed medical analysis (if you have 16GB+ RAM)
ollama pull llama3.1:8b

# For medical coding and data analysis
ollama pull codellama
```

## 🔧 Integration with Healthcare RAG

The system automatically detects and uses Ollama when:

1. **Ollama is running** on `http://localhost:11434`
2. **Cloud APIs fail** (automatic fallback)
3. **No cloud API keys** are configured (primary option)

### Priority Order

1. **Ollama (Local)** - Most reliable, always available
2. **DeepSeek** - Usually reliable cloud option
3. **OpenAI GPT-4** - High quality but can have issues
4. **Google Gemini** - Requires project setup (currently disabled)

## 🛠️ Troubleshooting

### Ollama Not Starting

```bash
# Check if Ollama is running
ps aux | grep ollama

# Kill existing processes
pkill ollama

# Restart Ollama
ollama serve
```

### Model Not Found

```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3.2

# Test the model
ollama run llama3.2 "Hello"
```

### Memory Issues

```bash
# Use smaller model
ollama pull llama3.2:1b

# Or adjust model parameters
ollama run llama3.2 --memory 4GB
```

### Port Conflicts

```bash
# Check what's using port 11434
lsof -i :11434

# Start Ollama on different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

## 📊 Performance Optimization

### Hardware Requirements

- **Minimum**: 8GB RAM, 4GB free disk space
- **Recommended**: 16GB RAM, 10GB free disk space
- **Optimal**: 32GB RAM, SSD storage

### Model Performance

| Model | RAM Required | Speed | Medical Knowledge |
|-------|-------------|-------|------------------|
| llama3.2:1b | 4GB | Fast | Good |
| llama3.2 | 8GB | Medium | Very Good |
| llama3.1:8b | 16GB | Slower | Excellent |

### Optimization Tips

```bash
# Preload model for faster responses
ollama run llama3.2 --keep-alive 24h

# Adjust context window for longer conversations
ollama run llama3.2 --ctx-size 4096
```

## 🔒 Security Considerations

### Local Benefits

- **No data leaves your machine**
- **No API key management**
- **No rate limiting**
- **Always available**

### Network Security

```bash
# Bind to localhost only (default)
OLLAMA_HOST=127.0.0.1:11434 ollama serve

# Or bind to specific interface
OLLAMA_HOST=192.168.1.100:11434 ollama serve
```

## 🚀 Advanced Usage

### Custom Medical Models

```bash
# Create a custom medical assistant
ollama create medical-assistant -f Modelfile

# Example Modelfile content:
# FROM llama3.2
# SYSTEM "You are a medical research assistant. Always provide evidence-based responses and include appropriate medical disclaimers."
```

### API Integration

```python
import requests

# Direct API call to Ollama
response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'llama3.2',
    'prompt': 'What are the symptoms of diabetes?',
    'stream': False
})

print(response.json()['response'])
```

## 📚 Additional Resources

- **Ollama Documentation**: https://ollama.ai/docs
- **Model Library**: https://ollama.ai/library
- **GitHub Repository**: https://github.com/ollama/ollama
- **Community Discord**: https://discord.gg/ollama

## 🆘 Getting Help

If you encounter issues:

1. **Check Ollama logs**: `ollama logs`
2. **Restart the service**: `ollama serve`
3. **Update Ollama**: Download latest from https://ollama.ai
4. **Check system resources**: Ensure sufficient RAM/disk space

The Healthcare RAG system will automatically fall back to Ollama when cloud APIs fail, ensuring your medical AI assistant is always available.