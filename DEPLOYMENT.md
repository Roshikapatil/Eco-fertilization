# Deployment Guide - Crop Recommendation System

This guide covers different deployment options for the Crop Recommendation System backend.

## 🚀 Quick Deployment Options

### Option 1: Local Development Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp env_example.txt .env
# Edit .env with your configuration

# 3. Set up database
# Create MySQL database and user
mysql -u root -p
CREATE DATABASE crop_recommendation;
CREATE USER 'crop_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON crop_recommendation.* TO 'crop_user'@'localhost';
FLUSH PRIVILEGES;

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Train ML models
python ml/train.py

# 6. Create superuser
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

### Option 2: Docker Deployment

```bash
# 1. Build and start services
docker-compose up -d

# 2. Check logs
docker-compose logs -f

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Train ML models
docker-compose exec web python ml/train.py
```

### Option 3: Production Server Setup

#### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Python 3.9+
- MySQL 8.0+
- Nginx
- SSL certificate (for HTTPS)

#### Installation Steps

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.9 python3.9-venv python3-pip nginx mysql-server -y

# Install MySQL client
sudo apt install default-libmysqlclient-dev pkg-config -y
```

2. **Application Setup**
```bash
# Clone repository
git clone <your-repo-url> /opt/crop_recommendation
cd /opt/crop_recommendation

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Database Configuration**
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
CREATE DATABASE crop_recommendation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crop_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON crop_recommendation.* TO 'crop_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

4. **Environment Configuration**
```bash
# Create production environment file
sudo nano .env

# Add production settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_NAME=crop_recommendation
DB_USER=crop_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=3306
OPENWEATHER_API_KEY=your-openweather-api-key
```

5. **Application Configuration**
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Train ML models
python ml/train.py

# Create superuser
python manage.py createsuperuser
```

6. **Gunicorn Configuration**
```bash
# Create systemd service
sudo nano /etc/systemd/system/crop-recommendation.service
```

```ini
[Unit]
Description=Crop Recommendation System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/crop_recommendation
Environment="PATH=/opt/crop_recommendation/venv/bin"
ExecStart=/opt/crop_recommendation/venv/bin/gunicorn --config gunicorn.conf.py crop_recommendation.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Nginx Configuration**
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/crop-recommendation
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location /static/ {
        alias /opt/crop_recommendation/staticfiles/;
    }

    location /media/ {
        alias /opt/crop_recommendation/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

8. **Start Services**
```bash
# Enable and start services
sudo systemctl enable crop-recommendation
sudo systemctl start crop-recommendation
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status crop-recommendation
sudo systemctl status nginx
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | - | Yes |
| `DEBUG` | Debug mode | False | Yes |
| `ALLOWED_HOSTS` | Allowed hostnames | localhost | Yes |
| `DB_NAME` | Database name | crop_recommendation | Yes |
| `DB_USER` | Database user | root | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `DB_HOST` | Database host | localhost | Yes |
| `DB_PORT` | Database port | 3306 | Yes |
| `OPENWEATHER_API_KEY` | Weather API key | - | No |

### Database Configuration

#### MySQL Optimization
```sql
-- Add to my.cnf for better performance
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
query_cache_size = 64M
query_cache_type = 1
```

#### Indexes
The system automatically creates indexes on:
- `crop` field
- `season` field
- `created_at` field
- `location_name` field

### Performance Tuning

#### Gunicorn Workers
```python
# In gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
```

#### Django Settings
```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

## 📊 Monitoring and Logging

### Log Files
- Application logs: `logs/django.log`
- Gunicorn access: `logs/gunicorn_access.log`
- Gunicorn error: `logs/gunicorn_error.log`
- Nginx access: `/var/log/nginx/access.log`
- Nginx error: `/var/log/nginx/error.log`

### Health Checks
```bash
# API health check
curl http://your-domain.com/api/status/

# Database health check
python manage.py check --database default

# ML models health check
python -c "from recommendations.ml_predict import load_models; load_models()"
```

### Monitoring Commands
```bash
# Check service status
sudo systemctl status crop-recommendation

# View logs
sudo journalctl -u crop-recommendation -f

# Check database connections
mysql -u crop_user -p -e "SHOW PROCESSLIST;"

# Monitor disk usage
df -h
du -sh /opt/crop_recommendation/
```

## 🔒 Security Considerations

### SSL/TLS Configuration
1. Obtain SSL certificate (Let's Encrypt recommended)
2. Configure Nginx for HTTPS
3. Redirect HTTP to HTTPS
4. Set security headers

### Database Security
1. Use strong passwords
2. Limit database user privileges
3. Enable SSL for database connections
4. Regular security updates

### Application Security
1. Keep dependencies updated
2. Use environment variables for secrets
3. Enable Django security middleware
4. Regular security audits

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check MySQL status
sudo systemctl status mysql

# Test connection
mysql -u crop_user -p crop_recommendation

# Check Django database settings
python manage.py dbshell
```

#### ML Model Errors
```bash
# Retrain models
python ml/train.py

# Check model files
ls -la models/

# Test prediction
python -c "from recommendations.ml_predict import predict_recommendation; print(predict_recommendation({'crop': 'Rice', 'season': 'Monsoon', 'soil': 'Loamy', 'preference': 'Organic', 'latitude': 28.7041, 'longitude': 77.1025}))"
```

#### Performance Issues
```bash
# Check system resources
htop
iostat -x 1

# Check database performance
mysql -u root -p -e "SHOW PROCESSLIST;"

# Optimize database
python manage.py dbshell
OPTIMIZE TABLE recommendations_recommendation;
```

### Log Analysis
```bash
# Check error logs
tail -f logs/django.log | grep ERROR

# Check access patterns
tail -f logs/gunicorn_access.log

# Monitor database queries
tail -f logs/django.log | grep "SELECT\|INSERT\|UPDATE\|DELETE"
```

## 📈 Scaling Considerations

### Horizontal Scaling
1. Use load balancer (Nginx/HAProxy)
2. Multiple application servers
3. Database replication
4. Redis for caching

### Vertical Scaling
1. Increase server resources
2. Optimize database configuration
3. Use SSD storage
4. Increase memory for caching

### Caching Strategy
1. Redis for session storage
2. Database query caching
3. API response caching
4. Static file CDN

## 🔄 Backup and Recovery

### Database Backup
```bash
# Create backup
mysqldump -u crop_user -p crop_recommendation > backup_$(date +%Y%m%d).sql

# Restore backup
mysql -u crop_user -p crop_recommendation < backup_20240101.sql
```

### Application Backup
```bash
# Backup application files
tar -czf crop_recommendation_backup_$(date +%Y%m%d).tar.gz /opt/crop_recommendation/

# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz /opt/crop_recommendation/media/
```

### Automated Backups
```bash
# Create backup script
sudo nano /opt/backup_script.sh

# Add to crontab
crontab -e
0 2 * * * /opt/backup_script.sh
```

---

**For additional support, check the main README.md file or create an issue in the repository.**
