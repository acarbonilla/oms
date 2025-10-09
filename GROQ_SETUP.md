# Groq Chatbot Setup Guide

Your OMS chatbot has been successfully migrated from DialoGPT to Groq! This provides better performance, reliability, and compatibility with Ubuntu production servers.

## 🎯 What Changed

- **Removed**: Heavy transformers, torch, and accelerate packages (~5GB)
- **Added**: Lightweight Groq API client (~1MB)
- **Benefits**: 
  - No local model downloading required
  - Faster response times (Groq uses LPU technology)
  - No GPU/CPU compatibility issues
  - Works perfectly on Ubuntu production servers
  - Much lower memory requirements

## 🚀 Setup Instructions

### 1. Get Your Groq API Key (Free)

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up or log in (free account available)
3. Go to "API Keys" section
4. Create a new API key
5. Copy the API key (starts with `gsk_...`)

**Free Tier Limits:**
- 30 requests per minute
- 6,000 requests per day
- More than enough for most use cases!

### 2. Add API Key to Your Environment

Add this line to your `.env` file:

```env
GROQ_API_KEY=gsk_your_api_key_here
```

**Example:**
```env
GROQ_API_KEY=gsk_1234567890abcdef1234567890abcdef
```

### 3. Install Dependencies

On your development machine (Windows):
```bash
.venv\Scripts\pip.exe install -r requirements.txt
```

On your production server (Ubuntu):
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
# Windows
.venv\Scripts\python.exe manage.py migrate chatbot

# Ubuntu
python manage.py migrate chatbot
```

### 5. Start Your Server

```bash
# Windows
.venv\Scripts\python.exe manage.py runserver

# Ubuntu (production)
gunicorn oms.wsgi:application --bind 0.0.0.0:8000
```

## ✅ Verification

1. Log in to your OMS system
2. Access the chatbot widget
3. Send a test message like: "How do I create a new facility?"
4. You should get an intelligent response powered by Groq

## 🔧 Available Models

The chatbot is configured to use `llama-3.3-70b-versatile` by default. Other available models:

- `llama-3.3-70b-versatile` (Default) - Best balance of speed and quality
- `mixtral-8x7b-32768` - Great for long context
- `llama-3.1-8b-instant` - Fastest responses
- `gemma2-9b-it` - Good for technical queries

To change the model, update it in the Django admin under "Chatbot Configuration".

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Make sure you added the API key to your `.env` file and restarted your Django server.

### Issue: "Rate limit exceeded"
**Solution:** You've hit the free tier limits. Wait a minute or upgrade your Groq plan.

### Issue: "Module not found: groq"
**Solution:** Run `pip install -r requirements.txt` again.

### Issue: Chatbot not responding
**Solution:** 
1. Check Django logs for errors
2. Verify your API key is correct
3. Ensure you have internet connectivity (Groq is API-based)

## 📊 Monitoring Usage

To monitor your Groq API usage:
1. Visit [https://console.groq.com](https://console.groq.com)
2. Go to "Usage" section
3. View requests, tokens, and rate limit status

## 🔐 Security Notes

- Never commit your `.env` file with the API key to Git
- Keep your API key secret
- Rotate your API key if it's ever exposed
- Use environment variables in production (don't hardcode)

## 🆘 Support

If you encounter any issues:
1. Check the Django logs: `tail -f logs/django.log`
2. Verify `.env` file is properly loaded
3. Test API key with a simple curl request:

```bash
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}], "model": "llama-3.3-70b-versatile"}'
```

## 📝 Next Steps

Your chatbot is now production-ready! It will:
- Answer questions about OMS features
- Provide guidance based on user roles and regions
- Help with facility management, activities, and assessments
- Offer contextual help from the knowledge base

Enjoy your faster, more reliable AI chatbot! 🎉

