# Project Structuur

Complete overzicht van alle bestanden en hun functie.

## 📁 Root Directory

```
04 - MB W124 Diesel zoeken/
│
├── 📄 main.py                     # Hoofdapplicatie entry point
├── 📄 config.py                   # Configuratie instellingen
├── 📄 database.py                 # Database operaties en queries
├── 📄 scrapers.py                 # Web scraper implementaties
├── 📄 scraper_manager.py          # Scraper coördinatie en management
├── 📄 scheduler.py                # Dagelijkse scheduling functionaliteit
├── 📄 web_app.py                  # Flask web applicatie en API
├── 📄 test_system.py              # Systeem test script
│
├── 📄 requirements.txt            # Python package dependencies
├── 📄 .gitignore                  # Git ignore regels
│
├── 📄 README.md                   # Hoofddocumentatie
├── 📄 QUICKSTART.md               # Snelstart gids
├── 📄 PROJECT_STRUCTURE.md        # Dit bestand
│
├── 📄 mercedes_diesel.db          # SQLite database (auto-generated)
│
├── 📁 templates/
│   └── 📄 index.html              # HTML hoofdpagina
│
├── 📁 static/
│   ├── 📄 style.css               # CSS styling
│   └── 📄 script.js               # JavaScript functionaliteit
│
└── 📁 deployment/
    ├── 📄 DEPLOYMENT.md           # Deployment instructies
    ├── 📄 mercedes-finder.service # Systemd service configuratie
    └── 📄 nginx.conf              # Nginx configuratie
```

---

## 📄 Bestand Details

### Core Application Files

#### `main.py`
**Doel:** Hoofdapplicatie launcher
**Functies:**
- Command-line interface voor verschillende run modes
- Start web server en/of scheduler
- Handelt command-line argumenten af

**Usage:**
```bash
python main.py                 # Full applicatie
python main.py --web-only      # Alleen webserver
python main.py --scrape-only   # Eenmalige scrape
```

---

#### `config.py`
**Doel:** Centrale configuratie
**Bevat:**
- Zoekparameters (modellen, jaren)
- Landen en marketplace URLs
- Scraping instellingen (delays, timeouts)
- Flask server instellingen

**Aanpasbaar:** ✅ Ja, pas aan voor custom settings

---

#### `database.py`
**Doel:** Database abstraction layer
**Klasse:** `Database`
**Functies:**
- Initialiseer database schema
- CRUD operaties voor advertenties
- Query functies voor top listings
- Scrape history logging
- Statistieken

**Database Schema:**
```sql
-- advertisements table
CREATE TABLE advertisements (
    id INTEGER PRIMARY KEY,
    external_id TEXT UNIQUE,
    model TEXT,
    year INTEGER,
    mileage INTEGER,
    price REAL,
    currency TEXT,
    location TEXT,
    country TEXT,
    source TEXT,
    source_url TEXT,
    title TEXT,
    description TEXT,
    image_url TEXT,
    date_added TIMESTAMP,
    date_updated TIMESTAMP,
    is_active BOOLEAN
);

-- scrape_history table
CREATE TABLE scrape_history (
    id INTEGER PRIMARY KEY,
    scrape_date TIMESTAMP,
    country TEXT,
    source TEXT,
    ads_found INTEGER,
    ads_new INTEGER,
    status TEXT
);
```

---

#### `scrapers.py`
**Doel:** Web scraping implementaties
**Klasses:**
- `BaseScraper` - Base class met gemeenschappelijke functionaliteit
- `AutoScout24Scraper` - Scraper voor AutoScout24 (NL/DE/BE)
- `MobileDeScraper` - Scraper voor Mobile.de (DE)
- `MarktplaatsScraper` - Scraper voor Marktplaats.nl (NL)

**Features:**
- Respecteert robots.txt
- Rate limiting
- User-agent rotation
- Error handling

---

#### `scraper_manager.py`
**Doel:** Scraper orchestration
**Klasse:** `ScraperManager`
**Functies:**
- Coördineert alle scrapers
- Itereren over landen en sites
- Database updates
- Logging en error handling

**Run standalone:**
```bash
python scraper_manager.py
```

---

#### `scheduler.py`
**Doel:** Dagelijkse scraping scheduler
**Klasse:** `DailyScheduler`
**Functies:**
- Schedule dagelijkse scrapes (06:00)
- Run scraper op schema
- Print statistieken
- Continue process

**Configureerbaar:** Update tijd in `config.py`

---

#### `web_app.py`
**Doel:** Flask web application
**Routes:**
- `GET /` - Hoofdpagina
- `GET /api/listings` - Alle listings (met filters)
- `GET /api/listings/top` - Top 100
- `GET /api/listings/nl` - Top 50 NL
- `GET /api/listings/de` - Top 50 DE
- `GET /api/statistics` - Statistieken

**Filters:**
- `format_price` - Format prijzen
- `format_mileage` - Format kilometers
- `format_date` - Format datums

---

#### `test_system.py`
**Doel:** System verification
**Tests:**
- Python imports
- Database operaties
- Configuratie
- Scrapers
- Web app
- Templates en static files

**Usage:**
```bash
python test_system.py
```

---

### Frontend Files

#### `templates/index.html`
**Doel:** HTML hoofdpagina
**Bevat:**
- Header met titel en info
- Statistieken cards
- Filterknoppen
- Tabellen voor advertenties (W123, W124, All)
- Footer

**Gebruikt:** Jinja2 templating

---

#### `static/style.css`
**Doel:** CSS styling
**Features:**
- Responsive design
- Gradient achtergronden
- Card layouts
- Tabel styling
- Hover effecten
- Mobile optimalisatie

**Frameworks:** Geen, pure CSS

---

#### `static/script.js`
**Doel:** Frontend JavaScript
**Functies:**
- API calls naar backend
- Tabel rendering
- Filtering logic
- Statistieken updates
- Auto-refresh (5 min)
- Country flags

**Dependencies:** Geen, vanilla JavaScript

---

### Documentation Files

#### `README.md`
**Doel:** Hoofd documentatie
**Bevat:**
- Project overzicht
- Installatie instructies
- Gebruik
- Configuratie
- Deployment opties
- Troubleshooting

**Voor:** Developers en eindgebruikers

---

#### `QUICKSTART.md`
**Doel:** Snelstart gids
**Bevat:**
- 5-minuten setup
- Quick commands
- Common issues
- Tips

**Voor:** Nieuwe gebruikers die snel willen starten

---

#### `PROJECT_STRUCTURE.md`
**Doel:** Dit bestand!
**Bevat:**
- Alle bestanden en hun functie
- Code structuur
- Architectuur overzicht

**Voor:** Developers die de codebase willen begrijpen

---

### Deployment Files

#### `deployment/DEPLOYMENT.md`
**Doel:** Gedetailleerde deployment guides
**Bevat:**
- VPS deployment (Ubuntu/Debian)
- Docker deployment
- Heroku deployment
- PythonAnywhere deployment
- Monitoring en onderhoud

**Voor:** Production deployment

---

#### `deployment/mercedes-finder.service`
**Doel:** Systemd service definitie
**Voor:** Linux servers
**Features:**
- Auto-start on boot
- Auto-restart on crash
- Logging
- Security settings

---

#### `deployment/nginx.conf`
**Doel:** Nginx reverse proxy configuratie
**Features:**
- SSL/HTTPS
- Static file serving
- Proxy to Flask
- Gzip compression
- Security headers

---

### Configuration Files

#### `requirements.txt`
**Doel:** Python dependencies
**Packages:**
```
beautifulsoup4==4.12.2
requests==2.31.0
selenium==4.16.0
schedule==1.2.0
flask==3.0.0
pandas==2.1.4
python-dotenv==1.0.0
lxml==4.9.3
fake-useragent==1.4.0
webdriver-manager==4.0.1
```

---

#### `.gitignore`
**Doel:** Git ignore regels
**Ignores:**
- Python cache files
- Virtual environments
- Database files
- IDE files
- OS files
- Logs

---

### Generated Files

#### `mercedes_diesel.db`
**Type:** SQLite database
**Auto-generated:** Ja, bij eerste run
**Bevat:**
- Alle advertenties
- Scrape geschiedenis

**Backup:** Aanbevolen dagelijks

---

## 🏗️ Architectuur

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                    (Application Entry)                      │
└───────────────┬─────────────────────┬───────────────────────┘
                │                     │
                ▼                     ▼
    ┌───────────────────┐  ┌──────────────────────┐
    │   scheduler.py    │  │     web_app.py       │
    │   (Daily Cron)    │  │   (Flask Server)     │
    └─────────┬─────────┘  └──────────┬───────────┘
              │                       │
              ▼                       │
    ┌──────────────────────┐          │
    │ scraper_manager.py   │          │
    │  (Orchestration)     │          │
    └─────────┬────────────┘          │
              │                       │
              ▼                       │
    ┌──────────────────────┐          │
    │    scrapers.py       │          │
    │  (Web Scrapers)      │          │
    └─────────┬────────────┘          │
              │                       │
              └───────┬───────────────┘
                      ▼
            ┌──────────────────┐
            │   database.py    │
            │   (SQLite DB)    │
            └──────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ mercedes_diesel  │
            │      .db         │
            └──────────────────┘
```

### Data Flow

1. **Scheduler** triggers scrape at 06:00
2. **ScraperManager** loops through countries/sites
3. **Scrapers** fetch and parse listings
4. **Database** stores/updates advertisements
5. **Web App** serves data via API
6. **Frontend** displays data to user

---

## 🔄 Workflow

### Daily Scraping Workflow

```
06:00 → Scheduler activates
     → ScraperManager starts
     → For each country:
         → For each marketplace:
             → Scraper fetches listings
             → Parse HTML
             → Extract data
             → Save to database
         → Update statistics
         → Log results
     → Mark inactive ads
     → Complete
```

### User Request Workflow

```
User opens website
     → Browser loads index.html
     → JavaScript loads
     → API call to /api/listings/top
     → Database query
     → Return JSON
     → JavaScript renders tables
     → Display to user
```

---

## 🛠️ Customization Points

### Eenvoudig aan te passen:

1. **config.py**
   - Update tijd
   - Zoekparameters
   - Landen

2. **static/style.css**
   - Kleuren
   - Layout
   - Styling

3. **templates/index.html**
   - Teksten
   - Structuur

### Gevorderd:

1. **scrapers.py**
   - Nieuwe scrapers toevoegen
   - Parsing logic aanpassen

2. **database.py**
   - Schema wijzigen
   - Query's optimaliseren

3. **web_app.py**
   - Nieuwe API endpoints
   - Filters toevoegen

---

## 📚 Lees Volgorde

Voor nieuwe developers:

1. **QUICKSTART.md** - Setup en eerste run
2. **README.md** - Algemeen overzicht
3. **PROJECT_STRUCTURE.md** - Dit bestand (architectuur)
4. **config.py** - Begrijp configuratie
5. **database.py** - Begrijp data model
6. **scrapers.py** - Begrijp scraping logic
7. **web_app.py** - Begrijp API
8. **deployment/DEPLOYMENT.md** - Production setup

---

## ✅ Checklist voor Contributions

Bij het toevoegen van features:

- [ ] Code gedocumenteerd
- [ ] Error handling toegevoegd
- [ ] Test gedraaid met test_system.py
- [ ] README.md bijgewerkt
- [ ] Config opties toegevoegd aan config.py
- [ ] Database migratie (indien nodig)
- [ ] Frontend aangepast (indien nodig)

---

Voor meer informatie, zie README.md of QUICKSTART.md
