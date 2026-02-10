# 🚀 Deployment Guide - DocuMind AI

This guide covers deploying DocuMind AI to Streamlit Cloud and other platforms.

---

## 📋 Prerequisites

1. **Groq API Key**
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create a new API key
   - Free tier includes generous limits

2. **GitHub Account**
   - Required for Streamlit Cloud deployment
   - Repository must be public or you need Streamlit Cloud Pro

3. **Streamlit Cloud Account**
   - Sign up at [share.streamlit.io](https://share.streamlit.io)
   - Free tier available

---

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Repository

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/documind-ai.git
git push -u origin main
```

2. **Verify Files**
Ensure these files are in your repository:
- `app.py` (main application)
- `requirements.txt` (dependencies)
- `.streamlit/config.toml` (Streamlit configuration)
- `README.md` (documentation)

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"

2. **Configure Deployment**
   - Repository: `yourusername/documind-ai`
   - Branch: `main`
   - Main file path: `app.py`

3. **Advanced Settings**
   - Python version: `3.11`
   - Click "Deploy"

### Step 3: Configure Secrets

1. **In Streamlit Cloud Dashboard**
   - Go to your app
   - Click "Settings" → "Secrets"

2. **Add Secrets** (copy from `.streamlit/secrets.toml.example`):
```toml
GROQ_API_KEY = "your_actual_groq_key_here"
DEFAULT_MODEL = "gemma2-9b-it"
PREMIUM_MODEL = "llama-3.1-70b-versatile"
FAST_MODEL = "llama-3.1-8b-instant"
MAX_FILE_SIZE_MB = 50
MAX_PAGES = 1000
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
ENABLE_MULTI_DOCUMENT = true
ENABLE_SEARCH_AGENT = true
ENABLE_VERSION_COMPARISON = true
ENABLE_EXPORT = true
```

3. **Save** and wait for app to restart

### Step 4: Verify Deployment

1. Your app will be available at:
   `https://yourusername-documind-ai-app-xxxxx.streamlit.app`

2. Test by:
   - Uploading a sample PDF
   - Generating summaries
   - Testing export functionality

---

## 🐳 Docker Deployment (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/processed data/summaries

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t documind-ai .

# Run container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key_here \
  documind-ai
```

---

## ☁️ AWS Deployment

### Using EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t2.medium or larger
   - Configure security group (port 8501)

2. **SSH and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone repository
git clone https://github.com/yourusername/documind-ai.git
cd documind-ai

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_key_here

# Run app
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

3. **Use PM2 for Process Management**
```bash
# Install Node.js and PM2
sudo apt install nodejs npm -y
sudo npm install -g pm2

# Start app with PM2
pm2 start "streamlit run app.py" --name documind-ai
pm2 save
pm2 startup
```

### Using ECS (Docker)

1. Push Docker image to ECR
2. Create ECS task definition
3. Configure service and load balancer
4. Set environment variables in task definition

---

## 🔧 Environment Configuration

### For Production

Update `.env` or Streamlit secrets:

```env
# Production Settings
DEFAULT_MODEL=gemma2-9b-it
PREMIUM_MODEL=llama-3.1-70b-versatile

# Increase limits for production
MAX_FILE_SIZE_MB=100
MAX_PAGES=2000
CHUNK_SIZE=1500

# Enable all features
ENABLE_MULTI_DOCUMENT=true
ENABLE_SEARCH_AGENT=true
ENABLE_VERSION_COMPARISON=true
ENABLE_EXPORT=true

# Optional: Analytics
ENABLE_ANALYTICS=true
```

---

## 📊 Monitoring

### Streamlit Cloud

- Built-in analytics in dashboard
- View usage metrics
- Monitor errors and crashes

### Custom Monitoring (Optional)

Add to `requirements.txt`:
```
sentry-sdk==1.40.5
```

In `app.py`:
```python
import sentry_sdk

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0
    )
```

---

## 🔒 Security Best Practices

1. **Never commit API keys**
   - Use environment variables
   - Use Streamlit secrets
   - Add `.env` to `.gitignore`

2. **Rate Limiting**
   - Configure in `config/settings.py`
   - Set daily limits per user

3. **Input Validation**
   - File size limits enforced
   - File type validation
   - Sanitize user inputs

4. **HTTPS Only**
   - Streamlit Cloud provides SSL
   - Use Let's Encrypt for self-hosted

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**2. "API key not found"**
```bash
# Check environment variables
echo $GROQ_API_KEY

# Or check Streamlit secrets
streamlit secrets list
```

**3. "Out of memory"**
```bash
# For large documents, increase server resources
# Or reduce chunk_size and max_pages settings
```

**4. Streamlit Cloud deployment fails**
- Check Python version (must be 3.11+)
- Verify all files are committed
- Check requirements.txt formatting
- Review deployment logs

---

## 📈 Scaling

### Horizontal Scaling

For high traffic:

1. **Load Balancer**
   - Use nginx or AWS ALB
   - Distribute across multiple instances

2. **Caching**
   - Implement Redis for summaries
   - Cache processed documents

3. **Database**
   - Move from SQLite to PostgreSQL
   - Use for user data and history

### Performance Optimization

```python
# In settings.py
ENABLE_CACHE = True
CACHE_TTL_HOURS = 24

# Use faster models for high throughput
DEFAULT_MODEL = "llama-3.1-8b-instant"
```

---

## 🔄 Updates and Maintenance

### Updating the App

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart app
# Streamlit Cloud: automatic
# Self-hosted: pm2 restart documind-ai
```

### Database Migrations

```bash
# When adding database features
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [GitHub Issues](https://github.com/yourusername/documind-ai/issues)
3. Join our [Discord community](https://discord.gg/documind)
4. Email: support@documind.ai

---

## ✅ Deployment Checklist

- [ ] Groq API key obtained
- [ ] Repository pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] Secrets configured
- [ ] App deployed successfully
- [ ] Sample document tested
- [ ] All summary levels working
- [ ] Export functionality verified
- [ ] Error handling tested
- [ ] Documentation updated
- [ ] Monitoring configured (optional)

---

**Happy Deploying! 🚀**
