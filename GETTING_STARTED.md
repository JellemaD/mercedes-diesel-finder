# Getting Started - Mercedes W123/W124 Diesel Finder

## ✅ Systeem Status

Je systeem is klaar voor gebruik!

### 🎯 Wat is er gebouwd?

Een volledig geautomatiseerd systeem dat **dagelijks om 06:00 uur** zoekt naar Mercedes W123 en W124 diesels (1980-1987) in:
- 🇳🇱 Nederland
- 🇩🇪 Duitsland
- 🇧🇪 België
- 🇫🇷 Frankrijk
- 🇵🇱 Polen
- 🇨🇿 Tsjechië
- 🇦🇹 Oostenrijk

Resultaten worden gepresenteerd in een moderne webinterface met filtering en statistieken.

---

## 🚀 Direct Starten

### Methode 1: Volledige Applicatie (Aanbevolen)

```bash
python main.py
```

Dit start:
- ✅ Webserver op http://localhost:5000
- ✅ Dagelijkse scheduler (scraped om 06:00)

### Methode 2: Alleen Webserver

```bash
python main.py --web-only
```

Alleen webserver, geen automatische updates.

### Methode 3: Eenmalige Scrape

```bash
python main.py --scrape-only
```

Scraped direct zonder webserver te starten.

---

## 🌐 Webinterface Gebruiken

1. Open je browser
2. Ga naar: **http://localhost:5000**
3. Gebruik de filterknoppen om te filteren op land
4. Klik op "Bekijk →" om naar de advertentie te gaan

### Features:

- **Top 100** - Beste advertenties van alle landen
- **Top 50 NL** - Nederlandse advertenties
- **Top 50 DE** - Duitse advertenties
- **Per land filteren** - Focus op specifiek land
- **Live statistieken** - Real-time overzicht
- **Auto-refresh** - Updates elke 5 minuten

---

## 📊 Demo Data

Het systeem heeft al **15 demo advertenties** in de database voor test doeleinden:

- 9x W123 modellen (300D, 300TD, 240D, Turbo)
- 5x W124 modellen (250D, 250TD, 300D, Turbo)

### Nieuwe scrape uitvoeren:

```bash
# Stop huidige server (Ctrl+C in terminal)
# Verwijder oude database
del mercedes_diesel.db  # Windows
# of: rm mercedes_diesel.db  # Mac/Linux

# Run nieuwe scrape
python main.py --scrape-only

# Start server opnieuw
python main.py
```

---

## ⚙️ Configuratie

Alle instellingen in **config.py**:

### Update Tijd Wijzigen

```python
UPDATE_TIME = "08:00"  # 8 uur 's ochtends
```

### Bouwjaar Aanpassen

```python
YEAR_FROM = 1975  # Vanaf 1975
YEAR_TO = 1987    # Tot en met 1987
```

### Poort Wijzigen

```python
FLASK_PORT = 8080  # Poort 8080 i.p.v. 5000
```

of via commandline:
```bash
python main.py --port 8080
```

---

## 📁 Project Bestanden

```
04 - MB W124 Diesel zoeken/
│
├── main.py                    # Start hier! Hoofdapplicatie
├── config.py                  # Configuratie (pas dit aan)
├── database.py                # Database operaties
├── scrapers.py                # Web scrapers
├── scraper_manager.py         # Scraper coördinatie
├── scheduler.py               # Dagelijkse scheduler
├── web_app.py                 # Flask webserver
│
├── demo_data.py               # Genereer test data
├── test_system.py             # Test het systeem
│
├── mercedes_diesel.db         # SQLite database (auto-generated)
│
├── templates/
│   └── index.html             # Webpagina
│
├── static/
│   ├── style.css              # Styling
│   └── script.js              # JavaScript
│
├── deployment/                # Voor online zetten
│   ├── DEPLOYMENT.md
│   ├── mercedes-finder.service
│   └── nginx.conf
│
├── README.md                  # Volledige documentatie
├── QUICKSTART.md              # Snelstart gids
└── PROJECT_STRUCTURE.md       # Code overzicht
```

---

## 🔧 Veelgebruikte Commands

### Test het systeem
```bash
python test_system.py
```

### Genereer demo data
```bash
python demo_data.py
```

### Check database
```bash
sqlite3 mercedes_diesel.db
SELECT COUNT(*) FROM advertisements;
.quit
```

### Bekijk actieve advertenties
```bash
sqlite3 mercedes_diesel.db
SELECT model, year, location, price FROM advertisements WHERE is_active=1;
.quit
```

---

## 🐛 Problemen Oplossen

### Poort al in gebruik
```bash
python main.py --port 8080
```

### Packages missen
```bash
pip install -r requirements.txt
```

### Database errors
```bash
# Reset database
del mercedes_diesel.db
python demo_data.py  # Maak nieuwe met demo data
```

### Browser toont geen data
1. Check of server draait (zie terminal output)
2. Refresh browser (Ctrl+F5)
3. Check browser console (F12) voor errors
4. Verify database heeft data: `python demo_data.py`

### Scraper werkt niet
- Check internet connectie
- Website kan rate limiting toepassen
- Verhoog `REQUEST_DELAY` in config.py
- Sommige websites blokkeren scrapers

---

## 🌐 Online Zetten

### Opties:

1. **PythonAnywhere** (Gratis!)
   - Gemakkelijkste optie
   - Gratis tier beschikbaar
   - Zie: `deployment/DEPLOYMENT.md`

2. **Heroku**
   - Ook gratis tier
   - Git-based deployment
   - Zie: `deployment/DEPLOYMENT.md`

3. **VPS** (DigitalOcean, Linode, etc.)
   - Volledige controle
   - Vanaf $5/maand
   - Nginx + Systemd setup
   - Zie: `deployment/DEPLOYMENT.md`

4. **Docker**
   - Makkelijk te deployen overal
   - Docker Compose setup
   - Zie: `deployment/DEPLOYMENT.md`

---

## 📈 Volgende Stappen

### Basis Gebruik:
1. ✅ Start applicatie: `python main.py`
2. ✅ Open browser: http://localhost:5000
3. ✅ Bekijk demo advertenties
4. ✅ Test filtering
5. ✅ Laat draaien voor dagelijkse updates om 06:00

### Geavanceerd:
1. ⚙️ Pas configuratie aan in `config.py`
2. 🌐 Zet online (zie deployment folder)
3. 🔧 Customize frontend (templates/static)
4. 📊 Analyseer data in database
5. 🚀 Voeg nieuwe scrapers toe

---

## 📚 Documentatie

- **README.md** - Volledige documentatie
- **QUICKSTART.md** - 5-minuten setup
- **PROJECT_STRUCTURE.md** - Code architectuur
- **deployment/DEPLOYMENT.md** - Online deployment

---

## 💡 Tips

### Beste Resultaten:
- Laat scheduler 24/7 draaien voor dagelijkse updates
- Check resultaten 's ochtends na 06:00
- Gebruik Top 50 NL/DE voor beste Nederlandse en Duitse aanbod
- Filter op land voor specifieke markten

### Performance:
- Eerste scrape duurt 5-10 minuten (alle landen)
- Daarna sneller (alleen nieuwe/updates)
- Database groeit geleidelijk
- Auto-refresh in browser elke 5 minuten

### Scraping Ethics:
- Systeem respecteert robots.txt
- 2 seconden delay tussen requests
- Proper user-agent identificatie
- Verantwoord gebruik

---

## ✅ Checklist

- [x] Python 3.8+ geïnstalleerd
- [x] Dependencies geïnstalleerd (`pip install -r requirements.txt`)
- [x] System test passed (`python test_system.py`)
- [x] Demo data geladen (`python demo_data.py`)
- [x] Webserver draait (`python main.py`)
- [x] Browser werkt (http://localhost:5000)
- [ ] Configuratie aangepast naar wens
- [ ] Online deployment (optioneel)

---

## 🎉 Je bent klaar!

Het systeem is volledig operationeel. Veel succes met het vinden van je ideale Mercedes W123 of W124!

### Huidige Status:
- ✅ Webserver: http://localhost:5000
- ✅ Demo data: 15 advertenties
- ✅ Scheduler: Actief (06:00 dagelijks)
- ✅ Database: mercedes_diesel.db

### Quick Access:
```bash
# Start alles
python main.py

# Open browser
start http://localhost:5000  # Windows
# of: open http://localhost:5000  # Mac
# of: xdg-open http://localhost:5000  # Linux
```

---

**Vragen? Check README.md of PROJECT_STRUCTURE.md voor meer details!**
