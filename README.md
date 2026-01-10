# Mercedes W123 & W124 Diesel - Te Koop Overzicht

Geautomatiseerd systeem voor het dagelijks verzamelen en presenteren van Mercedes W123 en W124 diesel advertenties uit meerdere Europese landen.

## 📋 Overzicht

Dit systeem zoekt dagelijks naar Mercedes W123 en W124 diesels (bouwjaar 1980-1987) op diverse online markplaatsen in:
- 🇳🇱 Nederland
- 🇩🇪 Duitsland
- 🇧🇪 België
- 🇫🇷 Frankrijk
- 🇵🇱 Polen
- 🇨🇿 Tsjechië
- 🇦🇹 Oostenrijk

Het systeem presenteert de resultaten in een overzichtelijke webinterface met:
- **Top 100** advertenties van alle landen
- **Top 50** specifiek voor Nederland
- **Top 50** specifiek voor Duitsland
- Filtering op land
- Real-time statistieken

## 🚀 Installatie

### Vereisten
- Python 3.8 of hoger
- pip (Python package manager)

### Stappen

1. **Clone of download het project**
```bash
cd "D:\000 - DATA\DATA70 - Programming en Bots\20 - Claude Code\Projecten\04 - MB W124 Diesel zoeken"
```

2. **Installeer dependencies**
```bash
pip install -r requirements.txt
```

3. **Configuratie aanpassen (optioneel)**
Bewerk `config.py` om:
- Update tijd te wijzigen (standaard 06:00)
- Landen toe te voegen of te verwijderen
- Zoekparameters aan te passen

## 💻 Gebruik

### Volledige applicatie starten (Aanbevolen)
Start zowel de webserver als de dagelijkse scheduler:

```bash
python main.py
```

De webinterface is beschikbaar op: `http://localhost:5000`

### Alleen webserver
Als je alleen de webinterface wilt zonder automatische updates:

```bash
python main.py --web-only
```

### Eenmalige scrape
Om direct een keer te scrapen zonder scheduler:

```bash
python main.py --scrape-only
```

### Alleen scheduler
Om alleen de automatische dagelijkse scraper te draaien:

```bash
python main.py --scheduler-only
```

### Custom poort
Om een andere poort te gebruiken:

```bash
python main.py --port 8080
```

## 📁 Project Structuur

```
04 - MB W124 Diesel zoeken/
│
├── main.py                 # Hoofd applicatie
├── config.py              # Configuratie
├── database.py            # Database operaties
├── scrapers.py            # Web scrapers voor verschillende sites
├── scraper_manager.py     # Scraper coördinatie
├── scheduler.py           # Dagelijkse scheduler
├── web_app.py            # Flask web applicatie
├── requirements.txt       # Python dependencies
│
├── templates/
│   └── index.html        # HTML template
│
├── static/
│   ├── style.css         # CSS styling
│   └── script.js         # JavaScript functionaliteit
│
├── mercedes_diesel.db    # SQLite database (wordt automatisch aangemaakt)
└── README.md            # Deze file
```

## 🔧 Configuratie

### config.py
Pas de volgende instellingen aan naar wens:

```python
# Update tijd
UPDATE_TIME = "06:00"  # HH:MM formaat

# Bouwjaren
YEAR_FROM = 1980
YEAR_TO = 1987

# Landen en markplaatsen
MARKETPLACES = {
    'NL': {...},
    'DE': {...},
    # etc.
}

# Web server
FLASK_PORT = 5000
```

## 🌐 Online Hosting

Om de applicatie online beschikbaar te maken:

### Optie 1: PythonAnywhere (Gratis tier beschikbaar)

1. Maak een account op [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload bestanden via "Files" tab
3. Maak een nieuwe Web app (Flask)
4. Configureer de WSGI file
5. Start een scheduled task voor dagelijkse updates

### Optie 2: Heroku

```bash
# Installeer Heroku CLI
# Login en maak nieuwe app
heroku create mercedes-diesel-finder

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku master

# Configureer scheduler addon
heroku addons:create scheduler:standard
heroku addons:open scheduler
```

### Optie 3: DigitalOcean / Linode / AWS

1. Maak een VPS/Droplet aan
2. Installeer Python en dependencies
3. Configureer een systemd service voor auto-start
4. Gebruik nginx als reverse proxy
5. Configureer SSL met Let's Encrypt

### Optie 4: Docker (Aanbevolen voor productie)

Maak een `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "main.py"]
```

Build en run:

```bash
docker build -t mercedes-finder .
docker run -p 5000:5000 mercedes-finder
```

## 📊 Database

Het systeem gebruikt SQLite voor data opslag:

### Tabellen:
- **advertisements**: Alle auto advertenties
- **scrape_history**: Log van scrape sessies

### Database locatie:
`mercedes_diesel.db` (in project root)

### Handmatige database queries:
```bash
sqlite3 mercedes_diesel.db

# Bekijk actieve advertenties
SELECT * FROM advertisements WHERE is_active = 1;

# Bekijk scrape geschiedenis
SELECT * FROM scrape_history ORDER BY scrape_date DESC LIMIT 10;
```

## 🔍 Ondersteunde Websites

Momenteel worden de volgende sites gescraped:

- **AutoScout24** (NL, DE, BE)
- **Mobile.de** (DE)
- **Marktplaats.nl** (NL)
- **Kleinanzeigen** (DE)
- **2dehands.be** (BE)
- En meer...

## ⚠️ Belangrijke Opmerkingen

### Web Scraping Ethics
- Het systeem respecteert `robots.txt`
- Delay tussen requests (2 seconden standaard)
- User-agent identificatie
- Verantwoord gebruik van scrapers

### Rate Limiting
Sommige websites kunnen rate limiting toepassen. Als je geblokkeerd wordt:
- Verhoog de `REQUEST_DELAY` in `config.py`
- Gebruik een VPN
- Roteer user-agents

### Onderhoud
- Scrapers kunnen stuk gaan als websites hun layout wijzigen
- Controleer regelmatig de logs
- Update scrapers indien nodig in `scrapers.py`

## 🐛 Troubleshooting

### Geen data wordt verzameld
```bash
# Test scraper direct
python scraper_manager.py
```

### Database errors
```bash
# Reset database
rm mercedes_diesel.db
python main.py --scrape-only
```

### Port al in gebruik
```bash
# Gebruik andere poort
python main.py --port 8080
```

## 📝 Toekomstige Verbeteringen

- [ ] Email notificaties voor nieuwe advertenties
- [ ] Prijs tracking en alerts
- [ ] Meer gedetailleerde filters (prijs, km-stand)
- [ ] Foto's opslaan lokaal
- [ ] Export naar CSV/Excel
- [ ] Vergelijkingstool
- [ ] Favorieten systeem
- [ ] Selenium scraping voor JavaScript-heavy sites

## 📄 Licentie

Dit project is voor persoonlijk gebruik. Respecteer de terms of service van de gescrapte websites.

## 🤝 Contact

Voor vragen of suggesties, open een issue op GitHub.

---

**Let op**: Dit systeem is bedoeld voor persoonlijk gebruik. Gebruik het verantwoord en respecteer de robots.txt en terms of service van websites.
