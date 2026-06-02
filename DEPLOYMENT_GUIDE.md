# Deployment Guide

**Production Deployment for AI Chatbot**

---

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Security review completed
- [ ] Environment variables configured
- [ ] Database backups in place
- [ ] Monitoring/logging set up
- [ ] Rate limiting enabled
- [ ] CORS configured
- [ ] API documentation reviewed
- [ ] Error handling tested
- [ ] Load testing completed

---

## Phase 1: Security Hardening

### 1.1 Environment Variables

**Never commit secrets!** Use environment variables:

```bash
# .env (never commit)
NVIDIA_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DATABASE_URL=postgresql://...
SECRET_KEY=random_secret_for_signing
JWT_SECRET=secret_for_jwt_tokens
```

### 1.2 API Keys

Where to get keys:
- **NVIDIA:** https://build.nvidia.com/
- **Anthropic:** https://console.anthropic.com/
- **Database:** Your cloud provider (AWS, GCP, Azure, etc.)

### 1.3 HTTPS Enforcement

```python
# In main.py
from fastapi.middleware.https import HTTPSMiddleware

app.add_middleware(HTTPSMiddleware, redirect=True)
```

### 1.4 CORS Configuration

```python
# Restrict to your domain only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 1.5 Security Headers

```python
# Add to responses
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Phase 2: Rate Limiting & Validation

### 2.1 Enable Rate Limiting

```python
from app.middleware.rate_limiter import RateLimitMiddleware, get_rate_limiter

limiter = get_rate_limiter()
app.add_middleware(RateLimitMiddleware, limiter=limiter)
```

**Settings:**
- 60 requests per minute per IP
- Adjustable in `middleware/rate_limiter.py`

### 2.2 Input Validation

```python
from app.utils.validation import validate_message, sanitize_string

# Automatically validated by Pydantic models
# Additional validation available:
safe_message = validate_message(user_input)
```

### 2.3 Error Handling

Always return consistent error format:

```json
{
  "error": "Error message",
  "detail": "Additional details",
  "code": "ERROR_CODE"
}
```

Never expose:
- ❌ Stack traces
- ❌ SQL queries
- ❌ Internal file paths
- ❌ API key fragments

---

## Phase 3: Database Setup (Optional)

For production, you'll want to persist:
- User conversations
- Rate limit data
- Error logs
- Analytics

### 3.1 PostgreSQL Setup

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### 3.2 Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE chatbot_db;

# Create user
CREATE USER chatbot WITH PASSWORD 'secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot;
```

### 3.3 Set Database URL

```bash
# In .env
DATABASE_URL=postgresql://chatbot:secure_password@localhost:5432/chatbot_db
```

---

## Phase 4: Cloud Deployment

### Option A: Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set NVIDIA_API_KEY=your_key
heroku config:set DATABASE_URL=postgresql://...

# Deploy
git push heroku main

# View logs
heroku logs -t
```

### Option B: AWS

```bash
# Using Elastic Beanstalk
eb init -p python-3.11 your-app-name

# Create environment
eb create production-env

# Set environment variables
eb setenv NVIDIA_API_KEY=your_key

# Deploy
eb deploy

# View logs
eb logs
```

### Option C: Google Cloud

```bash
# Using Cloud Run
gcloud run deploy your-app-name \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars NVIDIA_API_KEY=your_key
```

### Option D: DigitalOcean

```bash
# Using Docker
# Create Dockerfile
docker build -t chatbot .

# Push to registry
docker tag chatbot:latest your-registry/chatbot:latest
docker push your-registry/chatbot:latest

# Deploy to DigitalOcean App Platform
# Use the dashboard or:
doctl apps create --spec app.yaml
```

---

## Phase 5: Monitoring & Logging

### 5.1 Application Monitoring

Add error tracking (choose one):

**Sentry** (recommended for production)
```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/123",
    environment="production",
    traces_sample_rate=1.0
)
```

**Datadog**
```python
from datadog import api
api.api_key = "your_key"
```

### 5.2 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/chatbot.log'),
        logging.StreamHandler()
    ]
)
```

### 5.3 Performance Monitoring

```python
# Add timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.url.path} took {process_time:.3f}s")
    return response
```

---

## Phase 6: Scaling Considerations

### 6.1 Load Balancing

For multiple backend instances:

```yaml
# nginx.conf
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

### 6.2 Caching

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

FastAPICache2.init(RedisBackend(url="redis://localhost"), 
                   prefix="fastapi-cache")

@cached(namespace="tools", expire=3600)
async def get_tools():
    # This endpoint is cached for 1 hour
    ...
```

### 6.3 Database Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

---

## Phase 7: Backup & Disaster Recovery

### 7.1 Database Backups

```bash
# Daily backup script
#!/bin/bash
pg_dump -U chatbot chatbot_db | \
  gzip > /backups/chatbot_db_$(date +%Y%m%d_%H%M%S).sql.gz

# Keep last 30 days
find /backups -name "chatbot_db_*.sql.gz" -mtime +30 -delete
```

### 7.2 Application Backups

```bash
# Backup code and config
tar -czf /backups/app_$(date +%Y%m%d).tar.gz /app

# Store on S3 or external service
aws s3 cp /backups/app_*.tar.gz s3://your-bucket/backups/
```

### 7.3 Recovery Plan

1. Restore database from backup
2. Restore application code
3. Verify checksums
4. Run smoke tests
5. Monitor for errors

---

## Production Checklist (Final)

### Security
- [ ] All secrets in environment variables
- [ ] HTTPS enabled
- [ ] CORS restricted to known domains
- [ ] Rate limiting enabled
- [ ] Input validation strict
- [ ] Security headers added
- [ ] API key rotation plan in place

### Monitoring
- [ ] Error tracking (Sentry/Datadog)
- [ ] Application logs
- [ ] Performance monitoring
- [ ] Database monitoring
- [ ] Uptime monitoring

### Scaling
- [ ] Load balancer configured
- [ ] Database connection pooling
- [ ] Caching layer implemented
- [ ] CDN for static assets

### Backup & Recovery
- [ ] Database backups automated
- [ ] Application backups automated
- [ ] Recovery plan tested
- [ ] Disaster recovery plan documented

### Testing
- [ ] Load testing passed
- [ ] Security testing passed
- [ ] Smoke tests automated
- [ ] Integration tests passing

### Documentation
- [ ] API documentation complete
- [ ] Deployment steps documented
- [ ] Runbook for troubleshooting
- [ ] Team trained on operations

---

## Troubleshooting

### High Memory Usage

```python
# Check if tools are leaking memory
import tracemalloc
tracemalloc.start()

# ... run some requests ...

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024}MB")
print(f"Peak: {peak / 1024 / 1024}MB")
```

### Slow Responses

```python
# Enable timing in logs
import time

@app.middleware("http")
async def log_timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    if process_time > 1.0:  # Log slow requests
        logger.warning(f"Slow request: {request.url.path} took {process_time:.3f}s")
    return response
```

### Rate Limiting Too Aggressive

```python
# Adjust in middleware/rate_limiter.py
limiter = RateLimiter(
    requests_per_minute=120,  # Increase from 60
    burst_size=20
)
```

---

## Going Live Checklist

Before flipping the switch:

1. ✅ All tests passing
2. ✅ Security review complete
3. ✅ Load testing successful
4. ✅ Monitoring configured
5. ✅ Backup system tested
6. ✅ Team trained
7. ✅ Rollback plan ready
8. ✅ Status page configured
9. ✅ Support team briefed
10. ✅ Marketing/comms ready

---

## Post-Launch Monitoring

First 48 hours (critical):
- Monitor error rates
- Check latency/performance
- Verify rate limiting
- Monitor database performance
- Check API key usage

First week:
- Analyze usage patterns
- Optimize hot paths
- Review security logs
- Gather user feedback

Ongoing:
- Weekly performance review
- Monthly security review
- Quarterly architecture review
- Annual capacity planning

---

## Support & Escalation

**Critical Issues (Page On-Call):**
- Service completely down
- Data corruption
- Security breach
- Massive error spike

**High Priority (4 hour response):**
- Performance degradation > 50%
- Error rate > 5%
- Rate limiting blocking legitimate users

**Normal (24 hour response):**
- Feature requests
- Documentation updates
- Minor optimizations

---

## Next Steps

1. Choose cloud provider (Heroku, AWS, GCP, etc.)
2. Set up database (PostgreSQL recommended)
3. Configure monitoring (Sentry, Datadog, etc.)
4. Set up CI/CD pipeline
5. Run security audit
6. Load test the system
7. Train operations team
8. Plan launch date
9. Schedule post-launch review
10. Celebrate! 🚀

---

**Remember:** A well-deployed system is worth 10x the code quality. Take deployment seriously!
