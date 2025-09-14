# Gen AI Integration Setup Guide

## 🚀 Overview

Your Adaptive Resource Forecast AI platform now includes advanced Gen AI capabilities that can be enabled by configuring API keys for OpenAI and/or Anthropic models. The system is designed to work perfectly without API keys using intelligent fallback mechanisms.

## ✅ Current Status

**Fallback Mode Active**: The system is currently running in fallback mode, which means:
- ✅ All core functionality works perfectly
- ✅ Rule-based intent recognition and response generation
- ✅ Full license management and reporting capabilities
- ✅ Original chat interface available at `/chat`
- ⚠️ Enhanced Gen AI features not available (requires API keys)

## 🔑 API Key Configuration

### Option 1: OpenAI API Key

1. **Get API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Sign up or log in to your account
   - Create a new API key
   - Copy the key (starts with `sk-`)

2. **Configure Environment Variable**:
   ```bash
   export OPENAI_API_KEY="sk-your-openai-api-key-here"
   ```

3. **Available Models**:
   - GPT-4 Turbo (best for complex analysis)
   - GPT-4 (excellent for detailed reports)
   - GPT-3.5 Turbo (fast for general queries)

### Option 2: Anthropic API Key

1. **Get API Key**:
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Sign up or log in to your account
   - Create a new API key
   - Copy the key (starts with `sk-ant-`)

2. **Configure Environment Variable**:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key-here"
   ```

3. **Available Models**:
   - Claude 3 Opus (superior reasoning)
   - Claude 3 Sonnet (balanced performance)
   - Claude 3 Haiku (ultra-fast responses)

### Option 3: Both APIs (Recommended)

For the best experience, configure both APIs:
```bash
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key-here"
```

## 🛠️ Setup Instructions

### Step 1: Get API Keys
Choose one or both providers and get your API keys as described above.

### Step 2: Set Environment Variables

**For macOS/Linux:**
```bash
# Add to your ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key-here"

# Reload your shell
source ~/.bashrc  # or source ~/.zshrc
```

**For Windows:**
```cmd
set OPENAI_API_KEY=sk-your-openai-api-key-here
set ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

**For Docker:**
```bash
docker run -e OPENAI_API_KEY="sk-your-key" -e ANTHROPIC_API_KEY="sk-ant-your-key" your-app
```

### Step 3: Restart Application
```bash
# Stop the current application (Ctrl+C)
# Then restart
python3 run.py
```

### Step 4: Verify Configuration
```bash
# Test the configuration
python3 test_fallback.py
```

## 🎯 Enhanced Features (With API Keys)

Once API keys are configured, you'll get access to:

### 🤖 Enhanced Chat Interface
- **URL**: http://localhost:8000/chat/enhanced
- **Features**: Natural language understanding, context awareness, personalized responses

### 🧠 Advanced Capabilities
- **Intelligent Intent Recognition**: Better understanding of complex queries
- **Natural Language Generation**: More human-like, engaging responses
- **Context-Aware Conversations**: Remembers user preferences and history
- **Advanced Analysis**: Deep insights powered by Gen AI reasoning
- **Custom Report Generation**: AI-generated reports tailored to specific teams

### 📊 Smart Query Examples
```
"I need to cut costs by 20%, what should I do?"
"Our CFO wants a board summary for next week"
"Why are our software costs increasing?"
"Optimize our license portfolio for maximum efficiency"
"Predict our software costs for next quarter"
```

## 🔧 API Endpoints

### Enhanced Chat API
- `POST /api/chat/enhanced` - Enhanced chat with Gen AI
- `GET /api/chat/enhanced/capabilities` - Check Gen AI status
- `GET /api/chat/enhanced/suggestions` - Get conversation starters
- `POST /api/chat/enhanced/analyze` - Gen AI-powered analysis
- `POST /api/chat/enhanced/generate-report` - AI-generated reports

### Status Check
```bash
curl http://localhost:8000/api/chat/enhanced/capabilities
```

## 💰 Cost Considerations

### OpenAI Pricing (Approximate)
- GPT-4 Turbo: ~$0.01-0.03 per 1K tokens
- GPT-4: ~$0.03-0.06 per 1K tokens  
- GPT-3.5 Turbo: ~$0.001-0.002 per 1K tokens

### Anthropic Pricing (Approximate)
- Claude 3 Opus: ~$0.015-0.075 per 1K tokens
- Claude 3 Sonnet: ~$0.003-0.015 per 1K tokens
- Claude 3 Haiku: ~$0.00025-0.00125 per 1K tokens

### Cost Optimization
- The system automatically selects the most cost-effective model for each task
- Fallback mechanisms ensure you only pay for what you use
- Simple queries use cheaper models, complex analysis uses premium models

## 🛡️ Security & Privacy

- API keys are stored as environment variables (not in code)
- No conversation data is sent to external services without your explicit request
- All data processing happens locally with your license data
- Gen AI is only used for response generation and analysis

## 🔄 Fallback Behavior

The system is designed to gracefully handle API key issues:

1. **No API Keys**: Uses rule-based fallback (current state)
2. **API Key Expired**: Automatically falls back to rule-based processing
3. **API Rate Limits**: Switches to alternative models or fallback
4. **Network Issues**: Continues with local processing

## 🧪 Testing

Run the test script to verify your configuration:
```bash
python3 test_fallback.py
```

Expected output with API keys configured:
```
Gen AI Available: True
Available Models: 2-6 (depending on which APIs you configured)
```

## 🆘 Troubleshooting

### Common Issues

1. **"API key not configured"**
   - Check environment variables are set correctly
   - Restart the application after setting variables
   - Verify API key format (OpenAI: `sk-...`, Anthropic: `sk-ant-...`)

2. **"Rate limit exceeded"**
   - Wait a few minutes and try again
   - Consider upgrading your API plan
   - The system will automatically fall back to rule-based processing

3. **"Model not available"**
   - Check if you have access to the specific model
   - Some models require special access (e.g., GPT-4)
   - The system will automatically select available alternatives

### Getting Help

- Check the application logs for detailed error messages
- Run `python3 test_fallback.py` to diagnose issues
- Verify API keys are valid and have sufficient credits

## 🎉 Ready to Go!

Once you've configured your API keys and restarted the application, you'll have access to:

- **Enhanced Chat Interface**: http://localhost:8000/chat/enhanced
- **Natural Language Queries**: Ask questions in plain English
- **Intelligent Analysis**: Get AI-powered insights and recommendations
- **Custom Reports**: Generate tailored reports for different teams
- **Advanced Features**: Context-aware conversations and personalized responses

The system will automatically use the best available model for each task, providing you with the most intelligent and cost-effective experience possible!

