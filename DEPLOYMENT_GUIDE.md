# 🚀 Deployment Guide - Render Hosting

## 🌐 Deploy Your Advanced NER Suite to Render

### 📋 Prerequisites
- GitHub account
- Render account (free tier available)
- Your NER project code

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your GitHub Repository

1. **Create a new GitHub repository** (or use existing one)
2. **Push your NER project** to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - Advanced NER Suite"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/advanced-ner-suite.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Render

#### Option A: Using Render Dashboard (Recommended)

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**

   ```
   Name: advanced-ner-suite
   Environment: Python 3
   Build Command: pip install -r requirements-render.txt && python -m spacy download en_core_web_sm
   Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```

5. **Set Environment Variables:**
   ```
   PYTHON_VERSION=3.11.6
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_SERVER_ENABLE_CORS=false
   ```

6. **Click "Create Web Service"**

#### Option B: Using render.yaml (Infrastructure as Code)

1. **Use the provided `render.yaml`** file in your repository
2. **Go to Render Dashboard** → **"New +"** → **"Blueprint"**
3. **Connect your repository** and Render will automatically use the `render.yaml` configuration

### Step 3: Monitor Deployment

1. **Watch the build logs** in Render dashboard
2. **Wait for deployment** (usually 5-10 minutes)
3. **Access your live app** at the provided URL (e.g., `https://your-app-name.onrender.com`)

## 📊 Deployment Options Comparison

### 🆓 Free Tier (Perfect for Demo)
- **RAM**: 512 MB
- **CPU**: Shared
- **Build Time**: 15 minutes max
- **Sleep**: After 15 minutes of inactivity
- **Custom Domain**: Not included
- **Perfect for**: Portfolio, demos, testing

### 💰 Paid Tiers (Production Ready)
- **RAM**: 1GB - 32GB
- **CPU**: Dedicated
- **Build Time**: No limits
- **Sleep**: Never sleeps
- **Custom Domain**: Included
- **Perfect for**: Production apps, business use

## 🔧 Optimization for Render

### Memory Optimization
The deployment files include optimizations for Render's free tier:

1. **Lighter Dependencies**: CPU-only PyTorch, optimized packages
2. **Model Caching**: spaCy models cached after first load
3. **Streamlit Config**: Optimized for cloud deployment
4. **Error Handling**: Graceful fallbacks for missing features

### Performance Tips

1. **Use Caching**: 
   ```python
   @st.cache_resource
   def load_model():
       return spacy.load('en_core_web_sm')
   ```

2. **Optimize Imports**: Only import what you need
3. **Lazy Loading**: Load heavy features only when needed
4. **Error Handling**: Provide fallbacks for resource-intensive features

## 🐛 Troubleshooting

### Common Issues

#### 1. Build Timeout
```
Error: Build exceeded time limit
```
**Solution**: Use `requirements-render.txt` with optimized dependencies

#### 2. Memory Issues
```
Error: Process killed (out of memory)
```
**Solution**: 
- Use CPU-only PyTorch
- Implement lazy loading
- Consider upgrading to paid tier

#### 3. spaCy Model Not Found
```
Error: Can't find model 'en_core_web_sm'
```
**Solution**: Ensure build command includes:
```bash
python -m spacy download en_core_web_sm
```

#### 4. Port Issues
```
Error: Port binding failed
```
**Solution**: Use `$PORT` environment variable:
```bash
streamlit run app.py --server.port $PORT
```

### Debug Commands

```bash
# Check logs in Render dashboard
# Or use Render CLI
render logs -s your-service-name

# Test locally before deployment
streamlit run app.py --server.port 8080 --server.headless true
```

## 🌟 Post-Deployment

### 1. Test Your Deployment
- ✅ Visit your live URL
- ✅ Test basic NER functionality
- ✅ Try different features
- ✅ Check export functionality
- ✅ Test on mobile devices

### 2. Custom Domain (Paid Plans)
```
1. Go to Render Dashboard
2. Select your service
3. Go to "Settings" → "Custom Domains"
4. Add your domain
5. Update DNS records
```

### 3. Monitoring & Analytics
- **Render Metrics**: Built-in monitoring
- **Google Analytics**: Add tracking code
- **Error Tracking**: Implement Sentry or similar

### 4. Scaling Options
- **Vertical Scaling**: Upgrade RAM/CPU
- **Horizontal Scaling**: Multiple instances
- **Database**: Add PostgreSQL for collaboration features

## 📈 Production Enhancements

### Security
```python
# Add API keys for external services
WIKIDATA_API_KEY = os.environ.get('WIKIDATA_API_KEY')

# Implement rate limiting
@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_text(text):
    # Your analysis code
    pass
```

### Performance
```python
# Use Redis for caching (paid plans)
import redis
r = redis.from_url(os.environ.get('REDIS_URL'))

# Implement background processing
from celery import Celery
app = Celery('ner_tasks')
```

### Monitoring
```python
# Add health checks
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now()}

# Add metrics
import prometheus_client
```

## 🎯 Success Checklist

- [ ] Repository pushed to GitHub
- [ ] Render service created and deployed
- [ ] Live URL accessible
- [ ] Basic NER functionality working
- [ ] Export buttons functional
- [ ] Mobile-responsive design
- [ ] Error handling working
- [ ] Performance acceptable
- [ ] Custom domain configured (if needed)
- [ ] Monitoring set up

## 🔗 Useful Links

- **Render Documentation**: https://render.com/docs
- **Streamlit Deployment**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Your Live App**: `https://your-app-name.onrender.com`

---

## 🎉 Congratulations!

Your Advanced NER Suite is now live on the internet! 🌐

**Share your live demo URL with:**
- Potential employers
- Colleagues and friends
- Social media
- Your portfolio/resume

**Your project is now accessible worldwide!** 🚀
