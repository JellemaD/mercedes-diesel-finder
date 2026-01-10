# Deployment Instructies

Deze guide helpt je om de Mercedes Finder applicatie online te zetten.

## Optie 1: Ubuntu/Debian VPS (Aanbevolen voor productie)

### Stap 1: Server voorbereiden

```bash
# Update systeem
sudo apt update && sudo apt upgrade -y

# Installeer vereiste packages
sudo apt install -y python3 python3-pip python3-venv nginx git

# Maak applicatie directory
sudo mkdir -p /opt/mercedes-finder
sudo chown $USER:$USER /opt/mercedes-finder
```

### Stap 2: Applicatie installeren

```bash
# Clone of upload bestanden
cd /opt/mercedes-finder
# Upload bestanden via SCP of git clone

# Maak virtual environment
python3 -m venv venv
source venv/bin/activate

# Installeer dependencies
pip install -r requirements.txt
```

### Stap 3: Systemd service configureren

```bash
# Kopieer service file
sudo cp deployment/mercedes-finder.service /etc/systemd/system/

# Pas service file aan indien nodig
sudo nano /etc/systemd/system/mercedes-finder.service

# Enable en start service
sudo systemctl daemon-reload
sudo systemctl enable mercedes-finder
sudo systemctl start mercedes-finder

# Controleer status
sudo systemctl status mercedes-finder
```

### Stap 4: Nginx configureren

```bash
# Kopieer nginx configuratie
sudo cp deployment/nginx.conf /etc/nginx/sites-available/mercedes-finder

# Pas domein aan
sudo nano /etc/nginx/sites-available/mercedes-finder

# Enable site
sudo ln -s /etc/nginx/sites-available/mercedes-finder /etc/nginx/sites-enabled/

# Test configuratie
sudo nginx -t

# Herstart nginx
sudo systemctl restart nginx
```

### Stap 5: SSL Certificaat (Let's Encrypt)

```bash
# Installeer certbot
sudo apt install certbot python3-certbot-nginx

# Verkrijg certificaat (vervang example.com met je domein)
sudo certbot --nginx -d mercedes-finder.example.com

# Certificaat auto-renewal is standaard ingeschakeld
```

### Stap 6: Firewall configureren

```bash
# UFW firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## Optie 2: Docker Deployment

### Stap 1: Maak Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installeer dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer applicatie
COPY . .

# Expose poort
EXPOSE 5000

# Start applicatie
CMD ["python", "main.py"]
```

### Stap 2: Docker Compose

Maak `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mercedes-finder:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./mercedes_diesel.db:/app/mercedes_diesel.db
    restart: unless-stopped
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./static:/app/static:ro
    depends_on:
      - mercedes-finder
    restart: unless-stopped
```

### Stap 3: Build en Run

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Bekijk logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Optie 3: Heroku Deployment

### Stap 1: Voorbereiden

Maak `Procfile`:
```
web: python main.py --web-only
worker: python main.py --scheduler-only
```

Maak `runtime.txt`:
```
python-3.10.11
```

### Stap 2: Deploy

```bash
# Login
heroku login

# Maak app
heroku create mercedes-finder

# Deploy
git init
git add .
git commit -m "Initial deployment"
git push heroku main

# Schakel worker dyno in
heroku ps:scale worker=1

# Bekijk logs
heroku logs --tail
```

### Stap 3: Scheduler addon

```bash
# Installeer scheduler
heroku addons:create scheduler:standard

# Open scheduler dashboard
heroku addons:open scheduler

# Voeg job toe: python scraper_manager.py
# Frequentie: Daily at 06:00 AM
```

---

## Optie 4: PythonAnywhere (Gratis tier)

### Stap 1: Account aanmaken
1. Ga naar [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Maak gratis account

### Stap 2: Upload bestanden
1. Ga naar "Files" tab
2. Upload alle project bestanden
3. Of gebruik git clone

### Stap 3: Web app configureren
1. Ga naar "Web" tab
2. Klik "Add a new web app"
3. Kies "Flask"
4. Kies Python 3.10
5. Set working directory: `/home/username/mercedes-finder`

### Stap 4: WSGI configureren

Bewerk WSGI file (`/var/www/username_pythonanywhere_com_wsgi.py`):

```python
import sys
path = '/home/username/mercedes-finder'
if path not in sys.path:
    sys.path.append(path)

from web_app import app as application
```

### Stap 5: Scheduled tasks
1. Ga naar "Tasks" tab
2. Voeg toe: `python /home/username/mercedes-finder/scraper_manager.py`
3. Tijd: 06:00 UTC

---

## Monitoring en Onderhoud

### Logs bekijken

```bash
# Systemd service logs
sudo journalctl -u mercedes-finder -f

# Nginx logs
sudo tail -f /var/log/nginx/mercedes-finder-error.log
sudo tail -f /var/log/nginx/mercedes-finder-access.log
```

### Database backup

```bash
# Maak backup script
cat > /opt/mercedes-finder/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/mercedes-finder/backups"
mkdir -p $BACKUP_DIR
cp /opt/mercedes-finder/mercedes_diesel.db $BACKUP_DIR/mercedes_diesel_$DATE.db
# Verwijder backups ouder dan 30 dagen
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
EOF

chmod +x /opt/mercedes-finder/backup.sh

# Voeg toe aan crontab
crontab -e
# Voeg toe: 0 3 * * * /opt/mercedes-finder/backup.sh
```

### Update applicatie

```bash
cd /opt/mercedes-finder
git pull  # of upload nieuwe bestanden

# Herstart service
sudo systemctl restart mercedes-finder
```

### Monitoring met Systemd

```bash
# Status checken
sudo systemctl status mercedes-finder

# Auto-restart bij crash is al geconfigureerd in service file
# Check crash logs:
sudo journalctl -u mercedes-finder --since "1 hour ago"
```

---

## Troubleshooting

### Service start niet
```bash
# Check logs
sudo journalctl -u mercedes-finder -n 50

# Check permissies
ls -la /opt/mercedes-finder
sudo chown -R www-data:www-data /opt/mercedes-finder
```

### Nginx errors
```bash
# Test configuratie
sudo nginx -t

# Check error log
sudo tail -f /var/log/nginx/error.log
```

### Database locked
```bash
# Stop service
sudo systemctl stop mercedes-finder

# Check en repareer database
sqlite3 /opt/mercedes-finder/mercedes_diesel.db "PRAGMA integrity_check;"

# Start service
sudo systemctl start mercedes-finder
```

### Poort al in gebruik
```bash
# Check welk proces poort 5000 gebruikt
sudo lsof -i :5000

# Pas poort aan in config.py of gebruik andere poort
```

---

## Security Best Practices

1. **Firewall**: Alleen poort 80, 443 en SSH open
2. **SSL**: Gebruik altijd HTTPS in productie
3. **Updates**: Regelmatig systeem en dependencies updaten
4. **Backups**: Dagelijkse database backups
5. **Monitoring**: Log monitoring en alerting instellen
6. **Rate Limiting**: Nginx rate limiting configureren
7. **User Permissions**: Draai service met beperkte rechten

---

## Performance Optimizatie

### Nginx caching

Voeg toe aan nginx.conf:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=mercedes_cache:10m inactive=60m;
proxy_cache_key "$scheme$request_method$host$request_uri";

location /api/ {
    proxy_cache mercedes_cache;
    proxy_cache_valid 200 5m;
    # ... rest van proxy configuratie
}
```

### Database optimizatie

```bash
# Vacuum database regelmatig
sqlite3 /opt/mercedes-finder/mercedes_diesel.db "VACUUM;"

# Voeg toe aan crontab (weekly)
0 2 * * 0 sqlite3 /opt/mercedes-finder/mercedes_diesel.db "VACUUM;"
```

---

Voor meer hulp, zie de main README.md of open een issue op GitHub.
