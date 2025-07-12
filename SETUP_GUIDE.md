# 🚀 Complete Setup Guide - Advanced NER Suite

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8+ (recommended: 3.11)
- **RAM**: 8GB+ (for transformer models)
- **Storage**: 5GB+ free space
- **Internet**: Required for model downloads and Wikidata integration

### Check Your Python Version
```bash
python --version
# Should show Python 3.8 or higher
```

## 🔧 Installation Methods

### Method 1: Automated Setup (Recommended) ⭐

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/advanced-ner-suite
cd advanced-ner-suite
```

#### Step 2: Run Automated Setup
```bash
python setup.py
```
This will:
- Install all Python dependencies
- Download spaCy language models
- Create necessary directories
- Verify installation

#### Step 3: Launch Demo
```bash
streamlit run demo_all_features.py
```

### Method 2: Manual Setup

#### Step 1: Install Core Dependencies
```bash
pip install spacy textblob streamlit fastapi uvicorn pandas plotly
```

#### Step 2: Install Advanced Features
```bash
pip install transformers torch networkx wordcloud langdetect python-multipart
```

#### Step 3: Download Language Models
```bash
# Required (English)
python -m spacy download en_core_web_sm

# Optional (Additional Languages)
python -m spacy download es_core_news_sm  # Spanish
python -m spacy download fr_core_news_sm  # French
python -m spacy download de_core_news_sm  # German
```

#### Step 4: Create Directories
```bash
mkdir -p data models outputs logs
```

## 🎮 Running the Applications

### 1. 🌟 Complete Demo Suite
```bash
streamlit run demo_all_features.py
# Opens at: http://localhost:8502
```

### 2. 🔍 Individual Features

#### Basic NER Analysis
```bash
streamlit run web_app.py
# Opens at: http://localhost:8501
```

#### AI Knowledge Graph
```bash
streamlit run knowledge_graph_ner.py
# Opens at: http://localhost:8501
```

#### Confidence Analysis
```bash
streamlit run confidence_analyzer.py
# Opens at: http://localhost:8501
```

#### Collaborative Annotation
```bash
streamlit run collaborative_annotation.py
# Opens at: http://localhost:8501
```

#### Advanced Visualization
```bash
streamlit run advanced_visualization.py
# Opens at: http://localhost:8501
```

#### Multilingual Analysis
```bash
streamlit run multilingual_ner.py
# Opens at: http://localhost:8501
```

### 3. 🚀 Production API
```bash
python ner_api.py
# API at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

### 4. 📁 Batch Processing
```bash
# Single file
python batch_processor.py sample_document.txt

# Directory processing
python batch_processor.py ./documents/ --format csv --output results

# Help
python batch_processor.py --help
```

### 5. 🎯 Custom Training
```bash
python custom_entity_trainer.py
```

## ✅ Verification & Testing

### Test Basic Functionality
```bash
python test_ner.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Basic analysis
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Apple Inc. is based in California"}'
```

### Test Web Interface
1. Open http://localhost:8502
2. Enter sample text: "Apple Inc. was founded by Steve Jobs"
3. Click "Run Quick Analysis"
4. Verify entities are detected

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# Create .env file
echo "NER_MODEL_PATH=./models" > .env
echo "API_HOST=0.0.0.0" >> .env
echo "API_PORT=8000" >> .env
echo "LOG_LEVEL=INFO" >> .env
```

### Custom Model Path
```bash
export NER_MODEL_PATH="./custom_models"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. spaCy Model Not Found
```bash
# Error: Can't find model 'en_core_web_sm'
# Solution:
python -m spacy download en_core_web_sm
```

#### 2. Port Already in Use
```bash
# Error: Port 8501 is already in use
# Solution: Use different port
streamlit run demo_all_features.py --server.port 8502
```

#### 3. Memory Issues
```bash
# Error: Out of memory
# Solution: Reduce batch size or use smaller models
export MAX_BATCH_SIZE=10
```

#### 4. Transformer Model Download Issues
```bash
# If transformers fail to download
pip install --upgrade transformers torch
```

### Performance Optimization

#### For Low-Memory Systems
```python
# In your code, use smaller models
nlp = spacy.load('en_core_web_sm')  # Instead of large models
```

#### For Faster Processing
```bash
# Use CPU-only torch for faster startup
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## 📊 Usage Examples

### Quick Demo Text
```
Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Tim Cook became CEO in 2011, succeeding Steve Jobs. The company reported revenue of $394.3 billion in 2022.
```

### API Testing
```python
import requests

response = requests.post("http://localhost:8000/analyze", json={
    "text": "Microsoft was founded by Bill Gates in 1975",
    "include_sentiment": True
})

print(response.json())
```

### Batch Processing Example
```bash
# Create sample documents
echo "Google was founded by Larry Page and Sergey Brin" > doc1.txt
echo "Tesla is led by Elon Musk" > doc2.txt

# Process them
python batch_processor.py . --extensions .txt --format json
```

## 🎯 Next Steps

### 1. Explore Features
- Try all demo features
- Test different languages
- Upload your own documents
- Experiment with custom training

### 2. Integration
- Use the REST API in your applications
- Integrate with your existing workflows
- Set up batch processing for your documents

### 3. Customization
- Train custom entity models
- Add new entity types
- Customize the interface
- Deploy to production

## 📞 Getting Help

### If You Need Support:
1. Check this guide first
2. Look at the main README.md
3. Search GitHub issues
4. Create a new issue with:
   - Your system information
   - Error messages
   - Steps to reproduce

### System Information Template:
```
OS: [Windows/Mac/Linux]
Python Version: [3.x.x]
RAM: [XGB]
Error: [Full error message]
Steps: [What you were trying to do]
```

---

## 🎉 You're Ready!

Once setup is complete, you'll have access to:
- ✅ Advanced NER analysis
- ✅ AI-powered knowledge graphs
- ✅ Multi-model confidence scoring
- ✅ Real-time collaboration
- ✅ Interactive visualizations
- ✅ Production-ready API
- ✅ Multilingual support
- ✅ Batch processing capabilities

**Happy NLP Processing! 🚀**
