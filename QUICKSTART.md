# Quick Start Guide

Snel aan de slag met de Mercedes W123/W124 Diesel Finder in 5 minuten!

## 🚀 Snelle Installatie

### 1. Python Installeren (als nog niet geïnstalleerd)

**Windows:**
- Download Python 3.10+ van [python.org](https://www.python.org/downloads/)
- Vink "Add Python to PATH" aan tijdens installatie

**Verificatie:**
```bash
python --version
# Moet Python 3.8 of hoger zijn
```

### 2. Dependencies Installeren

Open Command Prompt of Terminal in de project folder:

```bash
# Navigeer naar project folder
cd "D:\000 - DATA\DATA70 - Programming en Bots\20 - Claude Code\Projecten\04 - MB W124 Diesel zoeken"

# Installeer packages
pip install -r requirements.txt
```

### 3. Start de Applicatie

```bash
python main.py
```

**Dat is alles!** 🎉

De applicatie is nu beschikbaar op: **http://localhost:5000**

---

## 📱 Gebruik

### Webinterface Openen

Open je browser en ga naar:
```
http://localhost:5000
```

### Filters Gebruiken

Klik op de landenknoppen om te filteren:
- **Alle landen (Top 100)** - Beste 100 advertenties
- **🇳🇱 Nederland (Top 50)** - Top 50 uit Nederland
- **🇩🇪 Duitsland (Top 50)** - Top 50 uit Duitsland
- **🇧🇪 België** - Advertenties uit België
- etc.

### Dagelijkse Updates

De applicatie scraped automatisch elke dag om **06:00 uur**.

---

## ⚙️ Configuratie Aanpassen

Bewerk `config.py` voor:

### Update Tijd Wijzigen
```python
UPDATE_TIME = "08:00"  # Bijvoorbeeld 8 uur 's ochtends
```

### Bouwjaar Range Aanpassen
```python
YEAR_FROM = 1978  # Start jaar
YEAR_TO = 1990    # Eind jaar
```

### Landen Toevoegen/Verwijderen
Zie de `MARKETPLACES` dictionary in `config.py`

---

## 🔧 Commando's

### Volledige Applicatie
```bash
python main.py
```
Start webserver + dagelijkse scheduler

### Alleen Webserver
```bash
python main.py --web-only
```
Start alleen de website (geen auto-updates)

### Eenmalige Scrape
```bash
python main.py --scrape-only
```
Scraped direct, zonder webserver of scheduler

### Custom Poort
```bash
python main.py --port 8080
```
Start op poort 8080 i.p.v. 5000

---

## 📊 Data Locatie

### Database
Alle data wordt opgeslagen in:
```
mercedes_diesel.db
```

### Database Resetten
```bash
# Stop applicatie (Ctrl+C)
# Verwijder database
rm mercedes_diesel.db

# Nieuwe scrape
python main.py --scrape-only
```

---

## 🐛 Veel Voorkomende Problemen

### "pip niet gevonden"
```bash
# Gebruik python -m pip
python -m pip install -r requirements.txt
```

### "Poort al in gebruik"
```bash
# Gebruik andere poort
python main.py --port 8080
```

### "Module niet gevonden"
```bash
# Installeer opnieuw
pip install -r requirements.txt --force-reinstall
```

### Geen advertenties gevonden
```bash
# Check internet connectie
# Run handmatige scrape met debug
python scraper_manager.py
```

### Applicatie crashed
```bash
# Check error message
# Vaak rate limiting van websites
# Verhoog REQUEST_DELAY in config.py
```

---

## 💡 Tips

### Eerste Gebruik
Bij eerste keer opstarten:
1. Laat applicatie 2-3 minuten draaien
2. Database wordt automatisch aangemaakt
3. Eerste scrape kan 5-10 minuten duren
4. Refresh browser om data te zien

### Performance
- Eerste scrape duurt lang (alle landen)
- Daarna sneller (alleen nieuwe/gewijzigde ads)
- Database groeit langzaam over tijd

### Beste Resultaten
- Laat scheduler draaien voor dagelijkse updates
- Check 's morgens na 06:00 voor nieuwe ads
- Gebruik filters voor sneller overzicht

---

## 🌐 Online Zetten

Wil je de applicatie online beschikbaar maken?

### Snelste optie: PythonAnywhere
1. Account op [pythonanywhere.com](https://www.pythonanywhere.com) (gratis)
2. Upload bestanden
3. Configure web app
4. Klaar!

Zie `deployment/DEPLOYMENT.md` voor gedetailleerde instructies.

---

## 📖 Meer Informatie

- **README.md** - Volledige documentatie
- **config.py** - Alle configuratie opties
- **deployment/DEPLOYMENT.md** - Deployment guides

---

## ❓ Hulp Nodig?

### Logs Bekijken
Applicatie print status in terminal/command prompt

### Test Scraper
```bash
python scraper_manager.py
```

### Test Database
```bash
sqlite3 mercedes_diesel.db
SELECT COUNT(*) FROM advertisements;
.quit
```

---

## 🎯 Volgende Stappen

1. ✅ Installeer dependencies
2. ✅ Start applicatie
3. ✅ Open browser (localhost:5000)
4. ✅ Wacht op eerste scrape (of run --scrape-only)
5. ✅ Bekijk resultaten!
6. 📱 Optioneel: Zet online

**Veel plezier met het vinden van je Mercedes!** 🚗💨
