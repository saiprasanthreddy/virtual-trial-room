# 🚀 DEPLOYMENT GUIDE

## Deploying Your Virtual Trial Room

This guide covers various deployment options for your application.

---

## 🏠 Local Development

Already covered in QUICKSTART.md, but as a reminder:

```bash
python app.py
```

Access at: `http://localhost:5000`

---

## ☁️ Cloud Deployment Options

### 1. Heroku (Easiest)

#### Setup:
```bash
# Install Heroku CLI
# Create Procfile
echo "web: python app.py" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Initialize git
git init
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key_here

# Deploy
git add .
git commit -m "Deploy virtual trial room"
git push heroku main
```

#### Update app.py for Heroku:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

### 2. Google Cloud Platform (GCP)

#### Setup app.yaml:
```yaml
runtime: python311

env_variables:
  GEMINI_API_KEY: "your_key_here"

handlers:
- url: /static
  static_dir: static
  
- url: /.*
  script: auto
```

#### Deploy:
```bash
gcloud app deploy
```

---

### 3. AWS (Elastic Beanstalk)

#### Create .ebextensions/python.config:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
```

#### Deploy:
```bash
eb init -p python-3.11 your-app-name
eb create your-env-name
eb setenv GEMINI_API_KEY=your_key_here
eb deploy
```

---

### 4. DigitalOcean App Platform

1. Connect your GitHub repository
2. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python app.py`
3. Add environment variable: `GEMINI_API_KEY`
4. Deploy!

---

### 5. Render (Simple & Free Tier Available)

#### Create render.yaml:
```yaml
services:
  - type: web
    name: virtual-trial-room
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

#### Deploy:
1. Push to GitHub
2. Connect to Render
3. Add environment variables
4. Deploy!

---

### 6. Railway (Modern & Easy)

1. Push code to GitHub
2. Connect repository to Railway
3. Add `GEMINI_API_KEY` environment variable
4. Deploy automatically

---

## 🐳 Docker Deployment

### Create Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Create docker-compose.yml:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - .:/app
```

### Deploy:
```bash
docker-compose up -d
```

---

## 🔒 Production Considerations

### 1. Security

#### Update app.py:
```python
# Add production settings
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Add CORS if needed
from flask_cors import CORS
CORS(app)

# Add rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
```

### 2. Environment Variables
Never commit your `.env` file. Always use:
- Heroku Config Vars
- AWS Secrets Manager
- GCP Secret Manager
- Railway/Render environment variables

### 3. Error Handling
Add better error pages:
```python
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
```

### 4. Logging
Add production logging:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

### 5. HTTPS
Most platforms provide free HTTPS:
- Heroku: Automatic
- Vercel: Automatic
- Railway: Automatic
- Others: Use Let's Encrypt

---

## 📊 Performance Optimization

### 1. Caching
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def cached_function():
    pass
```

### 2. CDN for Static Files
Move CSS/JS to CDN for faster loading:
- Cloudflare
- AWS CloudFront
- Google Cloud CDN

### 3. Image Optimization
```python
from PIL import Image

def optimize_image(image):
    # Resize if too large
    if image.width > 1920:
        ratio = 1920 / image.width
        new_size = (1920, int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    return image
```

### 4. Async Processing
For 360° generation, consider using:
- Celery for background tasks
- Redis for job queue
- Webhook notifications

---

## 🔍 Monitoring

### Add Health Check:
```python
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200
```

### Monitoring Services:
- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **Datadog**: Full stack monitoring
- **Google Analytics**: User analytics

---

## 💾 Database (Optional)

If you want to save user sessions:

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_url = db.Column(db.String(500))
```

---

## 🎯 Recommended Setup for Hackathon Demo

For fastest deployment during a hackathon:

1. **Railway** or **Render** (Free tier available)
2. Push code to GitHub
3. Connect and deploy in minutes
4. Share the live URL

### Quick Deploy Script:
```bash
# Add all files
git add .
git commit -m "Ready for deployment"
git push origin main

# Use Railway CLI
railway login
railway init
railway up
```

---

## 📱 Custom Domain

Most platforms support custom domains:

1. Purchase domain (Namecheap, Google Domains)
2. Add CNAME record pointing to your app
3. Configure SSL certificate (usually automatic)

Example:
```
your-tryon-app.com → your-app.railway.app
```

---

## ✅ Pre-Deployment Checklist

- [ ] Test locally thoroughly
- [ ] Set all environment variables
- [ ] Update `app.py` with production settings
- [ ] Test image upload limits
- [ ] Test API error handling
- [ ] Check mobile responsiveness
- [ ] Test on different browsers
- [ ] Set up error logging
- [ ] Configure SSL/HTTPS
- [ ] Test 360° generation
- [ ] Check API rate limits
- [ ] Add health check endpoint

---

## 🚨 Common Issues

### Issue: "Application failed to start"
**Solution**: Check Python version matches requirements

### Issue: "API key not found"
**Solution**: Verify environment variables are set

### Issue: "File upload too large"
**Solution**: Configure MAX_CONTENT_LENGTH

### Issue: "Timeout on 360° generation"
**Solution**: Increase timeout limits in platform settings

---

## 📞 Support

For deployment issues:
- Check platform documentation
- Review application logs
- Test locally first
- Verify environment variables
- Check API quotas

---

## 🎉 Success!

Once deployed, your Virtual Trial Room will be accessible worldwide!

Share your live demo URL and impress everyone with your premium AI fashion platform! 🚀

---

*Remember: Always keep your API keys secure and never commit them to version control!*
