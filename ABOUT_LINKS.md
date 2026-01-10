# Over de Links in het Systeem

## 🔗 Twee Soorten Links

Het systeem bevat twee soorten "advertenties":

### 1. Direct Zoeklinks (✅ ALTIJD WERKEND)

Dit zijn links naar zoekresultaat-pagina's op markplaatsen:
- **AutoScout24.nl** - Alle W123 diesels in NL
- **AutoScout24.de** - Alle W123/W124 diesels in DE
- **Mobile.de** - Alle Mercedes diesels 1980-1987
- **Marktplaats.nl** - W123 en W124 zoekresultaten
- **2dehands.be** - Mercedes zoekresultaten België
- **LeBonCoin.fr** - Mercedes zoekresultaten Frankrijk

**Voordeel:**
- ✅ Links werken ALTIJD
- ✅ Tonen actuele advertenties
- ✅ Geen scraping nodig

**Nadeel:**
- ⚠️ Toont zoekpagina i.p.v. specifieke auto
- ⚠️ Geen prijs/km-stand in database

---

### 2. Demo Advertenties (Voorbeeld Data)

Dit zijn fictieve advertenties met realistische data:
- Hebben prijs, km-stand, jaar, locatie
- Links zijn placeholder URLs
- Bedoeld om UI te demonstreren

**Voordeel:**
- ✅ Laat zien hoe interface werkt
- ✅ Toont statistieken

**Nadeel:**
- ⚠️ Links werken mogelijk niet
- ⚠️ Data is fictief

---

## 🚀 Echte Advertenties Krijgen

### Optie 1: Gebruik Zoeklinks (Aanbevolen)

De 8 zoeklinks in de database zijn **volledig werkend** en tonen altijd actuele advertenties!

Klik op:
- "AutoScout24 - Nederland" → Zie alle W123 diesels
- "Mobile.de - Duitsland" → Zie alle Mercedes diesels
- etc.

**Dit werkt perfect!** ✅

---

### Optie 2: Echte Scraping (Geavanceerd)

Om individuele advertenties te scrapen:

#### Uitdaging:
1. **JavaScript rendering** - Veel sites gebruiken React/Vue
2. **Rate limiting** - Sites blokkeren bots
3. **Layout changes** - HTML structuur verandert vaak
4. **Captcha** - Anti-bot bescherming

#### Oplossingen:

**A) Selenium Browser Automation**
```python
# Voeg toe aan scrapers.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
# Scrape pagina's
```

**B) API Gebruik** (Beste optie)
Sommige sites hebben publieke API's:
- AutoScout24 heeft partner API
- Mobile.de heeft affiliate programma
- Marktplaats heeft RSS feeds

**C) Proxies & Rotation**
```python
# Gebruik rotating proxies
# Wissel user-agents
# Voeg random delays toe
```

---

## 💡 Waarom Zoeklinks Beter Zijn

### Voor gebruikers:
✅ Altijd up-to-date advertenties
✅ Geen verouderde listings
✅ Geen gebroken links
✅ Direct naar marketplace

### Voor het systeem:
✅ Geen scraping errors
✅ Geen rate limiting
✅ Geen onderhoud
✅ Geen legal issues

---

## 🔧 Links Updaten

### Nieuwe zoeklink toevoegen:

Edit `simple_scraper.py`:

```python
links.append({
    'external_id': 'search_new_site',
    'model': 'W123',
    'year': None,
    'mileage': None,
    'price': None,
    'currency': 'EUR',
    'location': 'Land',
    'country': 'XX',
    'source': 'Website',
    'source_url': 'https://www.example.com/search?q=mercedes+w123',
    'title': 'Zoekresultaten op Website',
    'description': 'Beschrijving',
    'image_url': ''
})
```

Run:
```bash
python simple_scraper.py
```

---

## 🎯 Aanbevolen Aanpak

### Voor Demo/Testing:
```bash
# Database met zoeklinks + demo data
python simple_scraper.py
python demo_data.py
```

### Voor Productie:
```bash
# Alleen werkende zoeklinks
rm mercedes_diesel.db
python simple_scraper.py
```

Gebruikers klikken op links → Gaan naar marketplace → Zien actuele advertenties ✅

---

## 📊 Huidige Database Status

Na `simple_scraper.py` + `demo_data.py`:

```
Totaal: 22 advertenties

Werkende zoeklinks: 8
- AutoScout24 NL
- AutoScout24 DE
- AutoScout24 BE
- Mobile.de DE
- Marktplaats NL (W123)
- Marktplaats NL (W124)
- 2dehands.be BE
- LeBonCoin FR

Demo data: 14
- 9x W123 (met fake data)
- 5x W124 (met fake data)
```

---

## 🚀 Verbeteren: Echte Scraping

Als je echte individuele advertenties wilt:

### 1. Install Selenium
```bash
pip install selenium webdriver-manager
```

### 2. Update scrapers.py
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scrape_with_selenium(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    # Wait for JavaScript
    time.sleep(3)
    # Extract data
    listings = driver.find_elements(By.CLASS_NAME, "listing")
    # ... parse
    driver.quit()
```

### 3. Verhoog Delays
```python
# config.py
REQUEST_DELAY = 10  # 10 seconden tussen requests
```

### 4. Use Proxies (Optioneel)
```python
from fake_useragent import UserAgent
# Rotate IPs and user-agents
```

---

## ✅ Conclusie

**Huidige oplossing met zoeklinks werkt perfect voor:**
- ✅ Altijd actuele resultaten
- ✅ Geen technische problemen
- ✅ Gemakkelijk onderhoud
- ✅ Legaal en ethisch

**Echte scraping is mogelijk maar:**
- ⚠️ Technisch complex
- ⚠️ Maintenance overhead
- ⚠️ Kan geblokkeerd worden
- ⚠️ Legal grey area

**Aanbeveling:**
Gebruik de **zoeklinks aanpak** - Het werkt, het is simpel, en gebruikers krijgen altijd de nieuwste advertenties!

---

Voor vragen: zie PROJECT_STRUCTURE.md of GETTING_STARTED.md
