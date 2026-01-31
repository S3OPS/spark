# Deployment Guide

## Production Deployment

### Overview
This guide covers deploying the Stealth AI Revenue System to production environments.

## Deployment Options

### Option 1: VPS Deployment (Recommended)

Best for: Full control, cost-effective

**Providers:**
- DigitalOcean ($5-10/month)
- Linode ($5-10/month)
- Vultr ($5-10/month)
- Hetzner ($4-8/month)

**Steps:**

1. **Set up VPS**
```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv git nginx

# Install Caddy (for HTTPS)
apt install -y caddy
```

2. **Clone and setup**
```bash
cd /opt
git clone https://github.com/S3OPS/spark.git
cd spark

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys
```

3. **Set up systemd services**

Create `/etc/systemd/system/stealth-api.service`:
```ini
[Unit]
Description=Stealth AI API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/spark
Environment="PATH=/opt/spark/venv/bin"
ExecStart=/opt/spark/venv/bin/python backend/api/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/stealth-scheduler.service`:
```ini
[Unit]
Description=Stealth AI Scheduler
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/spark
Environment="PATH=/opt/spark/venv/bin"
ExecStart=/opt/spark/venv/bin/python scripts/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Configure Caddy for HTTPS**

Edit `/etc/caddy/Caddyfile`:
```
yourdomain.com {
    reverse_proxy localhost:3000
}

api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

5. **Start services**
```bash
systemctl enable stealth-api
systemctl enable stealth-scheduler
systemctl start stealth-api
systemctl start stealth-scheduler

systemctl restart caddy
```

### Option 2: Railway.app (Easy, Free Tier)

1. **Create account** at railway.app
2. **Click "New Project"** → "Deploy from GitHub"
3. **Select repository**: S3OPS/spark
4. **Add environment variables** from `.env.example`
5. **Deploy**: Railway handles the rest

Railway will automatically:
- Install dependencies
- Run migrations
- Provide HTTPS domain
- Scale as needed

### Option 3: Heroku

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create Procfile**
```
web: python backend/api/main.py
worker: python scripts/scheduler.py
```

3. **Deploy**
```bash
heroku create stealth-ai-system
git push heroku main
heroku ps:scale web=1 worker=1
```

4. **Configure**
```bash
heroku config:set OPENAI_API_KEY=your-key
heroku config:set STRIPE_API_KEY=your-key
# ... other env vars
```

### Option 4: Docker Deployment

**Create `Dockerfile`:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "backend/api/main.py"]
```

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/stealth_ai.db
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: always

  scheduler:
    build: .
    command: python scripts/scheduler.py
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: always

  dashboard:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend/public:/usr/share/nginx/html
    restart: always
```

**Deploy:**
```bash
docker-compose up -d
```

## Production Configuration

### Environment Variables

**Required:**
```bash
# API
SECRET_KEY=generate-strong-random-key
DEBUG=False

# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Payment Processing
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Optional but recommended:**
```bash
# AI
OPENAI_API_KEY=sk-...

# Social Media
TWITTER_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...

# Email
SENDGRID_API_KEY=...
```

### Database Migration to PostgreSQL

For production, use PostgreSQL instead of SQLite:

1. **Install PostgreSQL**
```bash
apt install postgresql postgresql-contrib
```

2. **Create database**
```bash
sudo -u postgres psql
CREATE DATABASE stealth_ai;
CREATE USER stealth_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE stealth_ai TO stealth_user;
\q
```

3. **Update .env**
```bash
DATABASE_URL=postgresql://stealth_user:strong_password@localhost:5432/stealth_ai
```

4. **Update requirements.txt**
```bash
# Add
psycopg2-binary==2.9.9
```

5. **Migrate data** (if coming from SQLite)
```bash
pip install pgloader
pgloader sqlite://data/stealth_ai.db postgresql://user:pass@localhost/stealth_ai
```

## SSL/HTTPS Setup

### Using Caddy (Automatic)
Caddy automatically handles SSL certificates from Let's Encrypt.

### Using Certbot (Manual)
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

## Monitoring & Logging

### Set up logging
```bash
mkdir -p /var/log/stealth-ai
chown www-data:www-data /var/log/stealth-ai
```

Update services to log:
```ini
StandardOutput=append:/var/log/stealth-ai/api.log
StandardError=append:/var/log/stealth-ai/api.error.log
```

### Log rotation
Create `/etc/logrotate.d/stealth-ai`:
```
/var/log/stealth-ai/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

### Monitoring tools
- **Uptime monitoring**: UptimeRobot (free)
- **Error tracking**: Sentry
- **Analytics**: Self-hosted dashboard
- **Server metrics**: Netdata

## Backup Strategy

### Automated daily backups
```bash
# Create backup script
cat > /opt/backup-stealth.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/stealth-ai"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump stealth_ai > $BACKUP_DIR/db_$DATE.sql

# Backup data files
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/spark/data

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/backup-stealth.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/backup-stealth.sh
```

### Off-site backups
Use rsync or rclone to sync to:
- S3
- BackBlaze B2
- Google Drive
- Dropbox

## Security Hardening

### Firewall
```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Fail2ban
```bash
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### Regular updates
```bash
# Create update script
cat > /opt/update-stealth.sh << 'EOF'
#!/bin/bash
cd /opt/spark
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl restart stealth-api
systemctl restart stealth-scheduler
EOF
```

## Performance Optimization

### Use Redis for caching
```bash
apt install redis-server
pip install redis
```

Update `.env`:
```bash
REDIS_URL=redis://localhost:6379/0
```

### Database optimization
```sql
-- Add indexes
CREATE INDEX idx_signals_score ON signals(overall_score DESC);
CREATE INDEX idx_offers_status ON micro_offers(status);
CREATE INDEX idx_analytics_offer ON analytics(offer_id);
CREATE INDEX idx_revenue_offer ON revenue(offer_id);
```

### Enable gzip compression
In Caddy:
```
encode gzip
```

## Scaling Strategy

### Vertical Scaling
- Start: 1 GB RAM, 1 CPU ($5/mo)
- Growth: 2 GB RAM, 2 CPU ($10/mo)
- Scale: 4 GB RAM, 4 CPU ($20/mo)

### Horizontal Scaling
1. Add load balancer
2. Multiple API instances
3. Separate scheduler server
4. Database replication

### CDN for static assets
- Cloudflare (free)
- BunnyCDN
- AWS CloudFront

## Post-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database initialized
- [ ] SSL certificates installed
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Firewall rules set
- [ ] Test all endpoints
- [ ] Test payment processing
- [ ] Test automation scheduler
- [ ] Verify domain DNS
- [ ] Set up alerts
- [ ] Document deployment
- [ ] Create rollback plan

## Troubleshooting Production Issues

### Service won't start
```bash
systemctl status stealth-api
journalctl -u stealth-api -n 50
```

### Database connection issues
```bash
# Test connection
psql -U stealth_user -h localhost stealth_ai

# Check permissions
SELECT * FROM pg_stat_activity;
```

### High memory usage
```bash
# Monitor
htop
free -m

# Optimize
# Reduce concurrent workers
# Add swap space
# Upgrade server
```

### API slow response
```bash
# Check logs
tail -f /var/log/stealth-ai/api.log

# Profile slow endpoints
# Add caching
# Optimize database queries
```

## Rollback Procedure

```bash
# Stop services
systemctl stop stealth-api stealth-scheduler

# Restore from backup
pg_restore -d stealth_ai backups/db_YYYYMMDD.sql
tar -xzf backups/data_YYYYMMDD.tar.gz -C /

# Revert code
cd /opt/spark
git reset --hard PREVIOUS_COMMIT

# Restart
systemctl start stealth-api stealth-scheduler
```

## Maintenance Windows

Schedule weekly maintenance:
- Day: Sunday 2-4 AM (low traffic)
- Tasks: Updates, backups verification, optimization
- Duration: Max 2 hours
- Notification: Email subscribers 24h advance
