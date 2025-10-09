# AI Chatbot Training Guide

## Overview

Your OMS chatbot now has advanced AI training capabilities! You can train the AI to better understand your specific operations management system and provide more accurate, contextual responses.

## Training Methods

### 1. **Automatic Training** (Recommended)
The AI automatically learns from every conversation and improves over time. The more you use the chatbot, the smarter it gets!

### 2. **Manual Training via Admin Panel**
1. Go to Django Admin → Chatbot Configuration
2. Click "Train AI" button
3. The system will collect conversation data and train a new model
4. View training statistics with the "Stats" button

### 3. **Command Line Training**
```bash
# Train with last 30 days of conversation data
python manage.py train_chatbot

# Train with custom days
python manage.py train_chatbot --days 60

# Collect data only (no training)
python manage.py train_chatbot --collect-only

# View training statistics
python manage.py train_chatbot --stats

# Evaluate existing model
python manage.py train_chatbot --evaluate-only /path/to/model
```

## Training Features

### 🧠 **Smart Data Collection**
- Automatically collects high-quality conversation pairs
- Filters out low-quality responses
- Includes OMS-specific training examples
- Tracks response quality scores

### 📊 **Performance Tracking**
- Quality scores for each bot response (0-1 scale)
- Training statistics dashboard
- Model evaluation with test queries
- Response quality trends

### 🎯 **Context-Aware Training**
- Learns from user roles (AM, EMP, EV)
- Understands regional differences (C2, Danao, Mindanao)
- Incorporates OMS-specific terminology
- Adapts to your workflow patterns

## Training Process

1. **Data Collection**: Gathers conversations from the last 30 days
2. **Quality Filtering**: Removes low-quality responses
3. **Dataset Creation**: Formats data for AI training
4. **Model Fine-tuning**: Trains the DialoGPT model
5. **Evaluation**: Tests model performance
6. **Deployment**: Saves trained model for use

## Quality Metrics

- **High Quality (0.7-1.0)**: ✅ Excellent responses
- **Medium Quality (0.5-0.7)**: ⚠️ Good responses, room for improvement
- **Low Quality (0.0-0.5)**: ❌ Poor responses, training needed

## Training Tips

### 📈 **Improve Training Data**
- Use the chatbot regularly
- Ask specific OMS-related questions
- Provide feedback on responses
- Use different user roles and regions

### 🔄 **Regular Training**
- Train weekly for active systems
- Train monthly for moderate usage
- Train when adding new features
- Train after major OMS updates

### 📝 **Best Practices**
- Ask varied questions about facilities, activities, and reports
- Use natural language, not just keywords
- Include context in your questions
- Test different user scenarios

## Advanced Features

### 🎛️ **Custom Training Parameters**
- Adjust training epochs
- Modify batch sizes
- Set custom output directories
- Configure evaluation metrics

### 📁 **Training Data Management**
- Automatic data collection and storage
- Manual data export/import
- Training history tracking
- Model version management

### 🔍 **Monitoring & Analytics**
- Real-time quality scoring
- Training progress tracking
- Performance comparison
- Usage analytics

## Troubleshooting

### Common Issues

**No Training Data Found**
- Solution: Use the chatbot more frequently to generate conversation data

**Low Quality Scores**
- Solution: Train more frequently or review conversation patterns

**Training Fails**
- Solution: Check system resources and dependencies

**Model Performance Issues**
- Solution: Collect more diverse training data or adjust parameters

### System Requirements

- **Memory**: 8GB+ RAM recommended for training
- **Storage**: 2GB+ free space for models
- **GPU**: Optional but recommended for faster training
- **Dependencies**: All training packages included in requirements.txt

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Training Data**:
   - Use the chatbot for a few days
   - Ask various OMS-related questions
   - Ensure different user roles interact

3. **Run First Training**:
   ```bash
   python manage.py train_chatbot --stats
   python manage.py train_chatbot
   ```

4. **Monitor Progress**:
   - Check Django Admin for quality scores
   - Review training statistics regularly
   - Retrain as needed

## Support

For training issues or questions:
- Check Django Admin → Chatbot Configuration → Training Stats
- Review training logs in the console
- Monitor response quality scores
- Adjust training parameters as needed

---

**Remember**: The more you use the chatbot, the smarter it becomes! 🚀
