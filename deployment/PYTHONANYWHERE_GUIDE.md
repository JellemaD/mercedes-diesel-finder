# PythonAnywhere Deployment Guide

Complete stap-voor-stap gids om Mercedes Finder op PythonAnywhere te deployen (GRATIS!)

## 📋 Vereisten

- PythonAnywhere account (gratis tier is voldoende)
- Project bestanden (gezipt of via git)

---

## 🚀 Stap 1: Account Aanmaken

1. Ga naar [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Klik op "Pricing & signup"
3. Kies "Create a Beginner account" (GRATIS)
4. Vul je gegevens in en bevestig email

**Gratis tier limiet:**
- 1 web app
- 512MB opslag
- Dagelijks 100 seconden CPU tijd
- 1 scheduled task

---

## 📁 Stap 2: Bestanden Uploaden

### Optie A: Via Web Interface (Gemakkelijkst)

1. Log in op PythonAnywhere
2. Ga naar het **"Files"** tab
3. Klik op **"Upload a file"**
4. Upload een ZIP van het project
5. Open een **Bash console** (van het Dashboard)
6. Unzip het bestand:
   ```bash
   cd ~
   unzip mercedes-finder.zip -d mercedes-finder
   cd mercedes-finder
   ```

### Optie B: Via Git (Aanbevolen)

1. Open een **Bash console**
2. Clone het repository:
   ```bash
   cd ~
   git clone https://github.com/jouw-username/mercedes-finder.git
   cd mercedes-finder
   ```

### Optie C: Directe Upload per Bestand

1. Ga naar **"Files"** tab
2. Navigeer naar `/home/yourusername/`
3. Maak nieuwe directory: `mercedes-finder`
4. Upload elk bestand handmatig

---

## 🔧 Stap 3: Dependencies Installeren

Open een **Bash console** en run:

```bash
cd ~/mercedes-finder

# Installeer packages
pip3 install --user -r requirements.txt

# Dit duurt 2-3 minuten
```

**Controleer installatie:**
```bash
python3 test_system.py
```

Alle tests moeten PASSED zijn! ✅

---

## 🌐 Stap 4: Web App Configureren

### 4.1 Nieuwe Web App Aanmaken

1. Ga naar het **"Web"** tab
2. Klik **"Add a new web app"**
3. Kies je domein: `yourusername.pythonanywhere.com`
4. Klik **"Next"**
5. Selecteer **"Flask"**
6. Kies **"Python 3.10"** (of nieuwer)
7. Flask app path: `/home/yourusername/mercedes-finder/web_app.py`
8. Klik **"Next"**

### 4.2 WSGI File Configureren

1. In het **"Web"** tab, scroll naar **"Code"** sectie
2. Klik op de WSGI configuration file link
   - Bijvoorbeeld: `/var/www/yourusername_pythonanywhere_com_wsgi.py`
3. **Verwijder alle bestaande code**
4. Plak deze code:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/mercedes-finder'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import Flask app
from web_app import app as application
```

5. **Vervang `yourusername`** met je PythonAnywhere username!
6. Klik **"Save"**

### 4.3 Working Directory Instellen

1. Scroll naar **"Code"** sectie in Web tab
2. Bij **"Working directory"** vul in:
   ```
   /home/yourusername/mercedes-finder
   ```
3. Vervang `yourusername` met jouw username

### 4.4 Static Files Configureren

1. Scroll naar **"Static files"** sectie
2. Voeg toe:
   - URL: `/static`
   - Directory: `/home/yourusername/mercedes-finder/static`

### 4.5 Reload Web App

1. Scroll helemaal naar boven
2. Klik de groene knop **"Reload yourusername.pythonanywhere.com"**
3. Wacht 5-10 seconden

---

## 🎉 Stap 5: Testen

### 5.1 Open Je Website

Ga naar: `https://yourusername.pythonanywhere.com`

Je zou nu de Mercedes Finder interface moeten zien! 🚗

### 5.2 Demo Data Laden

Als de pagina leeg is, laad demo data:

1. Open een **Bash console**
2. Run:
   ```bash
   cd ~/mercedes-finder
   python3 demo_data.py
   ```
3. Refresh je browser

Nu zie je 15 demo advertenties!

---

## ⏰ Stap 6: Dagelijkse Scraping Configureren

### 6.1 Scheduled Task Aanmaken

1. Ga naar het **"Tasks"** tab
2. Scroll naar **"Scheduled tasks"**
3. Bij "Daily (UTC time)" vul in:
   - **Time:** `05:00` (UTC is 1 uur eerder dan NL, dus 05:00 = 06:00 NL tijd)
   - **Command:**
     ```bash
     /home/yourusername/mercedes-finder/scraper_manager.py
     ```
4. Klik **"Create"**

**Let op:** Gratis accounts hebben max 100 seconden CPU per dag. Een volledige scrape kan langer duren, dus mogelijk moet je:
- Minder landen scrapen
- Alleen NL en DE scrapen
- Of upgraden naar betaald account

### 6.2 Test Scheduled Task

Run handmatig in Bash console:
```bash
cd ~/mercedes-finder
python3 scraper_manager.py
```

Dit scraped nu en vult de database!

---

## 🔍 Stap 7: Monitoring en Logs

### Error Logs Bekijken

1. Ga naar **"Web"** tab
2. Scroll naar **"Log files"**
3. Klik op **"error log"** link
4. Check voor errors

### Server Logs

Ook in **"Log files"** sectie:
- **access log** - Wie bezoekt je site
- **error log** - Python errors en crashes

### Bash Console Logs

In je Bash console zie je output van scripts die je draait.

---

## ⚙️ Configuratie Aanpassen

### Update Tijd Wijzigen

1. Edit `config.py` via Files tab
2. Wijzig `UPDATE_TIME = "06:00"`
3. Reload web app

### Landen Beperken (CPU Besparen)

Edit `config.py` en verwijder landen:

```python
MARKETPLACES = {
    'NL': {...},  # Houd Nederland
    'DE': {...},  # Houd Duitsland
    # Commentaar de rest uit om CPU te besparen:
    # 'BE': {...},
    # 'FR': {...},
}
```

---

## 🐛 Troubleshooting

### Website toont error page

**Check WSGI file:**
1. Ga naar Web tab
2. Click WSGI config file
3. Verify pad klopt: `/home/YOURUSERNAME/mercedes-finder`
4. Verify je hebt `yourusername` vervangen
5. Save en Reload

**Check error log:**
1. Web tab → Log files → error log
2. Lees laatste error
3. Fix het probleem
4. Reload web app

### Geen data op website

**Load demo data:**
```bash
cd ~/mercedes-finder
python3 demo_data.py
```

### ImportError of ModuleNotFoundError

**Reinstall packages:**
```bash
cd ~/mercedes-finder
pip3 install --user -r requirements.txt --force-reinstall
```

### "Could not import Flask"

**Wrong Python version in WSGI:**
1. Check WSGI file heeft juiste imports
2. Reload web app
3. Check error log

### Scheduled task werkt niet

**Check command:**
- Moet volledige pad zijn
- Of: `cd /home/yourusername/mercedes-finder && python3 scraper_manager.py`

**Check CPU limits:**
- Gratis account: 100 sec/dag
- Volledige scrape kan langer duren
- Beperk landen in config.py

### Database errors

**Reset database:**
```bash
cd ~/mercedes-finder
rm mercedes_diesel.db
python3 demo_data.py
```

---

## 📊 Performance Tips

### Reduce CPU Usage

1. **Beperk landen** in config.py tot NL en DE
2. **Verhoog delay** tussen requests:
   ```python
   REQUEST_DELAY = 5  # Was 2, nu 5 seconden
   ```
3. **Scrape minder frequent** - bijvoorbeeld om de 2 dagen

### Optimize Database

In Bash console:
```bash
cd ~/mercedes-finder
sqlite3 mercedes_diesel.db "VACUUM;"
```

---

## 💰 Upgraden (Optioneel)

Als je meer CPU tijd nodig hebt:

**Hacker Plan - $5/maand:**
- Meer CPU tijd
- Meer opslag
- Meer scheduled tasks
- Snellere performance

Ga naar: Account → Plans & Pricing

---

## 🔐 Security

### HTTPS

PythonAnywhere biedt automatisch HTTPS aan via:
- `https://yourusername.pythonanywhere.com`

Geen configuratie nodig! ✅

### Custom Domain (Betaald)

Met betaald account kun je eigen domein gebruiken:
- `mercedes-finder.jouwdomein.nl`

---

## 📝 Checklist Deployment

- [ ] PythonAnywhere account aangemaakt
- [ ] Bestanden geupload
- [ ] Dependencies geïnstalleerd (`pip3 install`)
- [ ] Test gedraaid (`python3 test_system.py`)
- [ ] Demo data geladen (`python3 demo_data.py`)
- [ ] Web app aangemaakt
- [ ] WSGI file geconfigureerd
- [ ] Working directory ingesteld
- [ ] Static files geconfigureerd
- [ ] Web app gereload
- [ ] Website getest (https://yourusername.pythonanywhere.com)
- [ ] Scheduled task aangemaakt (optioneel)
- [ ] Error logs gecontroleerd

---

## 🎯 Quick Commands Reference

```bash
# Navigeer naar project
cd ~/mercedes-finder

# Test systeem
python3 test_system.py

# Demo data laden
python3 demo_data.py

# Handmatige scrape
python3 scraper_manager.py

# Database bekijken
sqlite3 mercedes_diesel.db
SELECT COUNT(*) FROM advertisements;
.quit

# Dependencies installeren
pip3 install --user -r requirements.txt

# Check Flask
python3 -c "from web_app import app; print('Flask OK')"
```

---

## 🌐 Je Live URL

Na deployment is je site beschikbaar op:

```
https://yourusername.pythonanywhere.com
```

Vervang `yourusername` met je PythonAnywhere username.

**Voorbeeld:**
- Username: `mercedesfan`
- URL: `https://mercedesfan.pythonanywhere.com`

---

## 📧 Support

**PythonAnywhere Help:**
- Forum: https://www.pythonanywhere.com/forums/
- Help: https://help.pythonanywhere.com/

**Project Issues:**
- Check README.md
- Check error logs
- Review DEPLOYMENT.md

---

## ✅ Success!

Je Mercedes Finder is nu live op het internet! 🎉

**Share de link:**
```
https://yourusername.pythonanywhere.com
```

**Geniet van je dagelijkse Mercedes overzicht!** 🚗💨

---

**Extra:** Wil je een custom domein of meer CPU? Upgrade naar Hacker plan ($5/maand)
