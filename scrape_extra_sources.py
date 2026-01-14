"""
Scrape extra sources: AutoScout24, eBay.de, Gaspedaal.nl, 2dehands.be
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from database import Database

# WebDriver manager for Selenium
def get_chrome_service():
    """Get a fresh Chrome service for each scraper session"""
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        return Service(ChromeDriverManager().install())
    except ImportError:
        return None

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,de;q=0.8,en;q=0.7',
}

CLASSIC_KEYWORDS = ['w123', 'w124', 'w115', '200-280-w123', '200-280-w124', '200-280-w115',
                    'w123-combi', 'w124-combi', '200-serie', '300-serie', '200-500']
DIESEL_KEYWORDS = ['200d', '240d', '250d', '300d', '300td', '200 d', '240 d', '250 d', '300 d',
                   '200-d', '240-d', '250-d', '300-d', '240-td', '300-td', '-d-', 'diesel', 'turbo-d']
MODERN_KEYWORDS = ['v-klasse', 'v klasse', 'vito', 'sprinter', 'amg line', 'amg paket', '4matic',
                   'g-klasse', 'glc', 'gle', 'gla', 'glb', 'cls', 'cla', 'hybrid', 'eq',
                   'e-klasse', 'c-klasse', 'a-klasse', 'b-klasse', 's-klasse', 'sl-klasse']
# Benzine modellen uitsluiten (E = Einspritzung = benzine)
BENZINE_KEYWORDS = ['200e', '230e', '260e', '280e', '300e', '320e', '200 e', '230 e', '260 e', '280 e', '300 e', '320 e',
                    'benzine', 'petrol', 'gasoline']


def is_classic_diesel(title, year=None, url=''):
    """Check if this is a classic W123/W124 diesel (oldtimer <= 1987)"""
    # Combine title and URL for matching
    combined = (title or '').lower() + ' ' + (url or '').lower()

    if not combined.strip():
        return False

    # Must be a classic model (W123, W124, W115, 200-serie, etc.)
    is_classic = any(kw in combined for kw in CLASSIC_KEYWORDS)
    # Must be diesel
    is_diesel = any(kw in combined for kw in DIESEL_KEYWORDS)
    # Must NOT be a modern model
    is_modern = any(kw in combined for kw in MODERN_KEYWORDS)
    is_benzine = any(kw in combined for kw in BENZINE_KEYWORDS)
    # Only oldtimers: max year 1987 for road tax exemption
    year_ok = year is None or (year and year <= 1987)

    return is_classic and is_diesel and not is_modern and not is_benzine and year_ok


def extract_price(text):
    if not text:
        return None
    if isinstance(text, dict):
        text = text.get('priceFormatted', str(text))
    clean = re.sub(r'[€$£\s.]', '', str(text))
    clean = clean.replace(',', '.')
    match = re.search(r'\d+\.?\d*', clean)
    return float(match.group()) if match else None


def extract_year(text):
    """Extract year from text, supporting multiple formats:
    - Plain year: 1986
    - Erstzulassung format: EZ 02/1986, Erstzulassung 02/1986
    - Date format: 02/1986, 1986-02
    - Registration: firstRegistration: 1986
    """
    if not text:
        return None

    text = str(text)

    # Format: EZ 02/1986 or Erstzulassung 02/1986 or 02/1986
    ez_match = re.search(r'(?:EZ|Erstzulassung|Bj\.?|Baujahr)?\s*(\d{1,2})[/.-]?(19[789]\d|199[0-7])', text, re.IGNORECASE)
    if ez_match:
        return int(ez_match.group(2))

    # Format: 1986-02 (ISO-like)
    iso_match = re.search(r'(19[789]\d|199[0-7])[/-]\d{1,2}', text)
    if iso_match:
        return int(iso_match.group(1))

    # Plain year: 1986
    plain_match = re.search(r'(19[789]\d|199[0-7])', text)
    return int(plain_match.group()) if plain_match else None


def extract_mileage(text):
    if not text:
        return None
    match = re.search(r'(\d[\d.]*)\s*km', str(text).lower())
    if match:
        return int(match.group(1).replace('.', ''))
    return None


def scrape_autoscout24_json(country='de'):
    """Scrape AutoScout24 using __NEXT_DATA__ JSON"""
    print(f"\n{'='*50}")
    print(f"SCRAPING AUTOSCOUT24.{country.upper()} (JSON)")
    print("="*50)

    results = []
    base_url = f'https://www.autoscout24.{country}'

    # Country-specific settings
    country_names = {'de': 'Deutschland', 'nl': 'Nederland', 'be': 'België', 'fr': 'France', 'at': 'Österreich'}
    country_codes = {'de': 'DE', 'nl': 'NL', 'be': 'BE', 'fr': 'FR', 'at': 'AT'}

    # Search URLs for diesel oldtimers (max 1987 for road tax exemption)
    search_urls = [
        f'{base_url}/lst/mercedes-benz?fregfrom=1976&fregto=1987&fuel=D&sort=standard&desc=0&ustate=N%2CU',
        f'{base_url}/lst/mercedes-benz/200-serie?fregfrom=1976&fregto=1987&fuel=D',
    ]

    for search_url in search_urls:
        print(f"\nFetching: {search_url[:60]}...")

        try:
            response = requests.get(search_url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                print(f"  Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find __NEXT_DATA__ JSON
            next_data = soup.find('script', id='__NEXT_DATA__')
            if not next_data:
                print("  No __NEXT_DATA__ found")
                continue

            data = json.loads(next_data.string)
            props = data.get('props', {})
            page_props = props.get('pageProps', {})
            listings = page_props.get('listings', [])

            print(f"  Found {len(listings)} listings in JSON")

            for listing in listings:
                try:
                    # Extract vehicle info
                    vehicle = listing.get('vehicle', {})
                    tracking = listing.get('tracking', {})

                    # URL
                    url_path = listing.get('url', '')
                    ad_url = base_url + url_path if url_path.startswith('/') else url_path

                    # Build title from URL if empty
                    title = vehicle.get('title', '') or tracking.get('make', '') + ' ' + tracking.get('model', '')
                    if not title.strip():
                        # Extract title from URL: /angebote/mercedes-benz-240-d-w123... -> Mercedes-Benz 240 D W123
                        url_parts = url_path.replace('/angebote/', '').replace('-', ' ').title()
                        title = url_parts.split('?')[0][:60]

                    # Filter: only classic diesel (check URL too)
                    if not is_classic_diesel(title, url=url_path):
                        continue

                    # Get details
                    price_info = listing.get('price', {})
                    price = extract_price(price_info)

                    # Try multiple year sources
                    year = tracking.get('firstRegistrationYear')
                    if not year:
                        # Check firstRegistration field (format: "02/1986")
                        first_reg = vehicle.get('firstRegistration') or tracking.get('firstRegistration', '')
                        year = extract_year(first_reg)
                    if not year:
                        # Try title and description
                        year = extract_year(title) or extract_year(vehicle.get('description', ''))
                    mileage = tracking.get('mileage') or vehicle.get('mileage')
                    if isinstance(mileage, str):
                        mileage = extract_mileage(mileage)

                    location = listing.get('seller', {}).get('city', country_names.get(country, country))

                    # ID
                    id_match = re.search(r'/([a-f0-9-]{20,})', url_path)
                    external_id = id_match.group(1) if id_match else url_path.split('/')[-1]

                    # Image
                    images = listing.get('images', [])
                    image_url = images[0] if images else ''

                    # Model
                    model = 'W123/W124'
                    title_lower = title.lower()
                    if 'w123' in title_lower or '240d' in title_lower:
                        model = 'W123'
                    elif 'w124' in title_lower or '250d' in title_lower:
                        model = 'W124'

                    ad = {
                        'external_id': f'as24_{country}_{external_id}',
                        'model': model,
                        'year': year,
                        'mileage': mileage,
                        'price': price,
                        'currency': 'EUR',
                        'location': location,
                        'country': country_codes.get(country, country.upper()),
                        'source': 'AutoScout24',
                        'source_url': ad_url,
                        'title': title,
                        'description': '',
                        'image_url': image_url
                    }

                    # Avoid duplicates
                    if not any(r['external_id'] == ad['external_id'] for r in results):
                        results.append(ad)
                        print(f"  + {title[:45]}...")

                except Exception as e:
                    continue

            time.sleep(1)

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal from AutoScout24.{country}: {len(results)}")
    return results


def scrape_ebay_motors():
    """Scrape eBay.de Motors using Selenium"""
    print(f"\n{'='*50}")
    print("SCRAPING EBAY.DE MOTORS (Selenium)")
    print("="*50)

    results = []

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium niet geinstalleerd, skip eBay.de")
        return results

    # Setup headless Chrome
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        chrome_service = get_chrome_service()
        driver = webdriver.Chrome(service=chrome_service, options=options) if chrome_service else webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)

        search_terms = ['mercedes+w123+diesel', 'mercedes+w124+diesel', 'mercedes+240d']

        for term in search_terms:
            url = f'https://www.ebay.de/sch/9801/i.html?_nkw={term}&_sop=10&LH_ItemCondition=3000'
            print(f"\nSearching: {term}")

            try:
                driver.get(url)
                time.sleep(4)

                # Find listing items - eBay uses li[data-viewport] for results
                items = driver.find_elements(By.CSS_SELECTOR, 'li[data-viewport]')
                print(f"  Found {len(items)} items")

                for item in items[:20]:
                    try:
                        # Title - try multiple selectors
                        title = ''
                        for selector in ['[class*="title"]', 'h3', 'span[role="heading"]']:
                            title_elems = item.find_elements(By.CSS_SELECTOR, selector)
                            for t in title_elems:
                                text = t.text.strip()
                                if text and len(text) > 10:
                                    title = text
                                    break
                            if title:
                                break

                        if not title or 'shop on ebay' in title.lower():
                            continue

                        if not is_classic_diesel(title):
                            continue

                        # Link - find /itm/ links
                        ad_url = ''
                        link_elems = item.find_elements(By.TAG_NAME, 'a')
                        for link in link_elems:
                            href = link.get_attribute('href') or ''
                            if '/itm/' in href and 'ebay.de' in href:
                                ad_url = href
                                break

                        if not ad_url:
                            continue

                        # ID from URL
                        id_match = re.search(r'/itm/(\d+)', ad_url)
                        external_id = id_match.group(1) if id_match else str(hash(ad_url))[:10]

                        # Price - try multiple selectors
                        price = None
                        for price_selector in ['[class*="price"]', '[class*="Price"]', 'span[class*="EUR"]']:
                            price_elems = item.find_elements(By.CSS_SELECTOR, price_selector)
                            for pe in price_elems:
                                text = pe.text.strip()
                                if text and ('€' in text or 'EUR' in text or re.search(r'\d', text)):
                                    price = extract_price(text)
                                    if price:
                                        break
                            if price:
                                break

                        # Year
                        year = extract_year(title)

                        # Model
                        model = 'W123/W124'
                        if 'w123' in title.lower() or '240d' in title.lower():
                            model = 'W123'
                        elif 'w124' in title.lower():
                            model = 'W124'

                        ad = {
                            'external_id': f'ebay_de_{external_id}',
                            'model': model,
                            'year': year,
                            'mileage': None,
                            'price': price,
                            'currency': 'EUR',
                            'location': 'Deutschland',
                            'country': 'DE',
                            'source': 'eBay.de',
                            'source_url': ad_url,
                            'title': title,
                            'description': '',
                            'image_url': ''
                        }

                        if not any(r['external_id'] == ad['external_id'] for r in results):
                            results.append(ad)
                            print(f"  + {title[:45]}...")

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"  Error: {e}")

        driver.quit()

    except Exception as e:
        print(f"  Selenium error: {e}")

    print(f"\nTotal from eBay.de: {len(results)}")
    return results


def scrape_gaspedaal():
    """Scrape Gaspedaal.nl using Selenium"""
    print(f"\n{'='*50}")
    print("SCRAPING GASPEDAAL.NL (Selenium)")
    print("="*50)

    results = []

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium niet geinstalleerd, skip Gaspedaal.nl")
        return results

    # Setup headless Chrome
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        chrome_service = get_chrome_service()
        driver = webdriver.Chrome(service=chrome_service, options=options) if chrome_service else webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)

        # Gaspedaal.nl search URLs - try different formats
        search_urls = [
            'https://www.gaspedaal.nl/mercedes-benz?q=w123+diesel',
            'https://www.gaspedaal.nl/mercedes-benz?q=w124+diesel',
            'https://www.gaspedaal.nl/mercedes-benz?q=240d',
            'https://www.gaspedaal.nl/zoeken?q=mercedes+w123',
            'https://www.gaspedaal.nl/zoeken?q=mercedes+240d',
        ]

        for url in search_urls:
            print(f"\nFetching: {url[:55]}...")

            try:
                driver.get(url)
                time.sleep(5)  # Gaspedaal needs time to load JavaScript content

                # Find listing items - Gaspedaal uses different structures
                listings = driver.find_elements(By.CSS_SELECTOR, '[class*="listing"], [class*="Listing"], [class*="result"], [class*="car"], article, .occasion')
                print(f"  Found {len(listings)} potential items")

                for listing in listings[:25]:
                    try:
                        # Get all text to help with debugging
                        full_text = listing.text.strip()
                        if not full_text or len(full_text) < 10:
                            continue

                        # Title - try multiple selectors
                        title = ''
                        for selector in ['h2', 'h3', '[class*="title"]', '[class*="Title"]', 'a[href*="/auto/"], a[href*="-mercedes"]']:
                            elems = listing.find_elements(By.CSS_SELECTOR, selector)
                            for elem in elems:
                                text = elem.text.strip()
                                if text and len(text) > 5:
                                    title = text
                                    break
                            if title:
                                break

                        # If no title found, try first line of full text
                        if not title:
                            title = full_text.split('\n')[0][:80]

                        if not title or not is_classic_diesel(title):
                            continue

                        # Link - look for auto/occasion links
                        ad_url = ''
                        link_elems = listing.find_elements(By.TAG_NAME, 'a')
                        for link in link_elems:
                            href = link.get_attribute('href') or ''
                            if href and ('gaspedaal.nl' in href or href.startswith('/')) and ('/auto/' in href or '/occasion/' in href or '-mercedes' in href):
                                ad_url = href if href.startswith('http') else 'https://www.gaspedaal.nl' + href
                                break

                        if not ad_url:
                            continue

                        # ID from URL
                        id_match = re.search(r'/(\d+)', ad_url)
                        external_id = id_match.group(1) if id_match else str(hash(ad_url))[:10]

                        # Price
                        price = None
                        price_elems = listing.find_elements(By.CSS_SELECTOR, '[class*="price"], [class*="Price"]')
                        if price_elems:
                            price = extract_price(price_elems[0].text)

                        # Year
                        year = extract_year(title)

                        # Model
                        model = 'W123/W124'
                        if 'w123' in title.lower() or '240d' in title.lower():
                            model = 'W123'
                        elif 'w124' in title.lower():
                            model = 'W124'

                        ad = {
                            'external_id': f'gaspedaal_{external_id}',
                            'model': model,
                            'year': year,
                            'mileage': None,
                            'price': price,
                            'currency': 'EUR',
                            'location': 'Nederland',
                            'country': 'NL',
                            'source': 'Gaspedaal.nl',
                            'source_url': ad_url,
                            'title': title,
                            'description': '',
                            'image_url': ''
                        }

                        if not any(r['external_id'] == ad['external_id'] for r in results):
                            results.append(ad)
                            print(f"  + {title[:45]}...")

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"  Error: {e}")

        driver.quit()

    except Exception as e:
        print(f"  Selenium error: {e}")

    print(f"\nTotal from Gaspedaal.nl: {len(results)}")
    return results


def scrape_2dehands():
    """Scrape 2dehands.be using Selenium (JavaScript rendering)"""
    print(f"\n{'='*50}")
    print("SCRAPING 2DEHANDS.BE (Selenium)")
    print("="*50)

    results = []

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium niet geinstalleerd. Installeer met: pip install selenium")
        return results

    # Setup headless Chrome
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        chrome_service = get_chrome_service()
        driver = webdriver.Chrome(service=chrome_service, options=options) if chrome_service else webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)

        # 2dehands - search in auto category only
        search_urls = [
            # Direct auto category searches - these are most reliable
            'https://www.2dehands.be/l/auto-s/mercedes-benz/',
        ]

        for url in search_urls:
            print(f"\nFetching: {url[:60]}...")

            try:
                driver.get(url)
                time.sleep(4)

                # Scroll down to load more listings (lazy loading)
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                # Find listing items - 2dehands uses various classes containing 'Listing'
                listings = driver.find_elements(By.CSS_SELECTOR, '[class*="Listing"], [class*="listing"], article, li[class*="result"]')
                print(f"  Found {len(listings)} potential listings (after scroll)")

                for listing in listings[:30]:
                    try:
                        # Get full text of listing element
                        full_text = listing.text.strip()

                        # Title - try multiple selectors
                        title = ''
                        for title_sel in ['h3', '[class*="title"]', '[class*="Title"]', 'a[href*="/v/"]']:
                            elems = listing.find_elements(By.CSS_SELECTOR, title_sel)
                            for elem in elems:
                                text = elem.text.strip()
                                if text and len(text) > 5:
                                    title = text
                                    break
                            if title:
                                break

                        # If no title found, use first line of full text
                        if not title and full_text:
                            title = full_text.split('\n')[0][:80]

                        # Check for classic diesel - also check full listing text
                        if not is_classic_diesel(title) and not is_classic_diesel(full_text):
                            continue

                        # Link - look for /v/auto-s/ links only (cars, not parts)
                        ad_url = ''
                        link_elems = listing.find_elements(By.CSS_SELECTOR, 'a[href*="/v/auto-s/"]')
                        if link_elems:
                            ad_url = link_elems[0].get_attribute('href') or ''
                        else:
                            # Try any link with /v/auto
                            all_links = listing.find_elements(By.TAG_NAME, 'a')
                            for link in all_links:
                                href = link.get_attribute('href') or ''
                                if '/v/auto-s/' in href or ('/v/auto' in href and 'onderdelen' not in href):
                                    ad_url = href
                                    break

                        if not ad_url or 'onderdelen' in ad_url:
                            continue

                        # Price - try multiple selectors
                        price = None
                        for price_sel in ['[class*="price"]', '[class*="Price"]', '[data-testid*="price"]']:
                            price_elems = listing.find_elements(By.CSS_SELECTOR, price_sel)
                            for pe in price_elems:
                                text = pe.text.strip()
                                if text and ('€' in text or re.search(r'\d', text)):
                                    price = extract_price(text)
                                    if price:
                                        break
                            if price:
                                break

                        # ID from URL - handles /v/auto/m12345/ and /a/something/ formats
                        id_match = re.search(r'/(?:v|a)/[^/]+/m?(\d+)', ad_url)
                        if not id_match:
                            id_match = re.search(r'/([^/]+)/?$', ad_url)
                        external_id = id_match.group(1) if id_match else str(hash(ad_url))[:10]

                        # Year from title
                        year = extract_year(title)

                        # Model
                        model = 'W123/W124'
                        if 'w123' in title.lower() or '240d' in title.lower():
                            model = 'W123'
                        elif 'w124' in title.lower():
                            model = 'W124'

                        ad = {
                            'external_id': f'2dehands_{external_id}',
                            'model': model,
                            'year': year,
                            'mileage': None,
                            'price': price,
                            'currency': 'EUR',
                            'location': 'België',
                            'country': 'BE',
                            'source': '2dehands.be',
                            'source_url': ad_url,
                            'title': title,
                            'description': '',
                            'image_url': ''
                        }

                        if not any(r['external_id'] == ad['external_id'] for r in results):
                            results.append(ad)
                            print(f"  + {title[:45]}...")

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"  Error: {e}")

        driver.quit()

    except Exception as e:
        print(f"  Selenium error: {e}")

    print(f"\nTotal from 2dehands.be: {len(results)}")
    return results


def add_search_links(db):
    """Add search links for eBay.de, Gaspedaal.nl, 2dehands.be"""
    print("\nAdding search links...")

    links = [
        # eBay.de
        {
            'external_id': 'search_ebay_de_w123',
            'model': 'W123',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Duitsland',
            'country': 'DE',
            'source': 'eBay.de',
            'source_url': 'https://www.ebay.de/sch/9801/i.html?_nkw=mercedes+w123+diesel&_sop=10',
            'title': 'Zoek Mercedes W123 Diesel op eBay.de',
            'description': 'eBay Duitsland auto advertenties',
            'image_url': ''
        },
        {
            'external_id': 'search_ebay_de_w124',
            'model': 'W124',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Duitsland',
            'country': 'DE',
            'source': 'eBay.de',
            'source_url': 'https://www.ebay.de/sch/9801/i.html?_nkw=mercedes+w124+diesel&_sop=10',
            'title': 'Zoek Mercedes W124 Diesel op eBay.de',
            'description': 'eBay Duitsland auto advertenties',
            'image_url': ''
        },
        # Gaspedaal.nl
        {
            'external_id': 'search_gaspedaal_w123',
            'model': 'W123',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Nederland',
            'country': 'NL',
            'source': 'Gaspedaal.nl',
            'source_url': 'https://www.gaspedaal.nl/mercedes-benz?q=w123+diesel',
            'title': 'Zoek Mercedes W123 Diesel op Gaspedaal.nl',
            'description': 'Gaspedaal Nederland auto advertenties',
            'image_url': ''
        },
        {
            'external_id': 'search_gaspedaal_w124',
            'model': 'W124',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Nederland',
            'country': 'NL',
            'source': 'Gaspedaal.nl',
            'source_url': 'https://www.gaspedaal.nl/mercedes-benz?q=w124+diesel',
            'title': 'Zoek Mercedes W124 Diesel op Gaspedaal.nl',
            'description': 'Gaspedaal Nederland auto advertenties',
            'image_url': ''
        },
        # 2dehands.be
        {
            'external_id': 'search_2dehands_w123',
            'model': 'W123',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'België',
            'country': 'BE',
            'source': '2dehands.be',
            'source_url': 'https://www.2dehands.be/q/mercedes+w123+diesel/',
            'title': 'Zoek Mercedes W123 Diesel op 2dehands.be',
            'description': '2dehands België auto advertenties',
            'image_url': ''
        },
        {
            'external_id': 'search_2dehands_w124',
            'model': 'W124',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'België',
            'country': 'BE',
            'source': '2dehands.be',
            'source_url': 'https://www.2dehands.be/q/mercedes+w124+diesel/',
            'title': 'Zoek Mercedes W124 Diesel op 2dehands.be',
            'description': '2dehands België auto advertenties',
            'image_url': ''
        },
        # AutoTrack.nl
        {
            'external_id': 'search_autotrack_w123',
            'model': 'W123',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Nederland',
            'country': 'NL',
            'source': 'AutoTrack.nl',
            'source_url': 'https://www.autotrack.nl/aanbod/mercedes-benz?q=w123+diesel',
            'title': 'Zoek Mercedes W123 Diesel op AutoTrack.nl',
            'description': 'AutoTrack Nederland auto advertenties',
            'image_url': ''
        },
        {
            'external_id': 'search_autotrack_w124',
            'model': 'W124',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Nederland',
            'country': 'NL',
            'source': 'AutoTrack.nl',
            'source_url': 'https://www.autotrack.nl/aanbod/mercedes-benz?q=w124+diesel',
            'title': 'Zoek Mercedes W124 Diesel op AutoTrack.nl',
            'description': 'AutoTrack Nederland auto advertenties',
            'image_url': ''
        },
        # AutoWereld.nl
        {
            'external_id': 'search_autowereld_w123',
            'model': 'W123',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Nederland',
            'country': 'NL',
            'source': 'AutoWereld.nl',
            'source_url': 'https://www.autowereld.nl/autos/mercedes-benz/?q=w123+diesel',
            'title': 'Zoek Mercedes W123 Diesel op AutoWereld.nl',
            'description': 'AutoWereld Nederland auto advertenties',
            'image_url': ''
        },
        {
            'external_id': 'search_autowereld_w124',
            'model': 'W124',
            'year': None,
            'mileage': None,
            'price': None,
            'currency': 'EUR',
            'location': 'Nederland',
            'country': 'NL',
            'source': 'AutoWereld.nl',
            'source_url': 'https://www.autowereld.nl/autos/mercedes-benz/?q=w124+diesel',
            'title': 'Zoek Mercedes W124 Diesel op AutoWereld.nl',
            'description': 'AutoWereld Nederland auto advertenties',
            'image_url': ''
        },
    ]

    for link in links:
        db.add_advertisement(link)
        print(f"  + {link['source']}: {link['title'][:40]}")


def scrape_autotrack():
    """AutoTrack.nl - returns search links (site blocks scrapers)"""
    print(f"\n{'='*50}")
    print("AUTOTRACK.NL (search links only - site blocks scrapers)")
    print("="*50)
    # AutoTrack blocks scrapers, so we just return empty and add search links
    return []


def scrape_autowereld():
    """Scrape AutoWereld.nl for Mercedes W123/W124 Diesel (Selenium)"""
    print(f"\n{'='*50}")
    print("SCRAPING AUTOWERELD.NL (Selenium)")
    print("="*50)

    results = []

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium niet geinstalleerd, skip AutoWereld.nl")
        return results

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        chrome_service = get_chrome_service()
        driver = webdriver.Chrome(service=chrome_service, options=options) if chrome_service else webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)

        # First visit homepage to handle consent
        print("  Visiting homepage first for consent...")
        driver.get('https://www.autowereld.nl/')
        time.sleep(3)

        # Handle DPG Media consent if redirected
        if 'myprivacy' in driver.current_url or 'consent' in driver.current_url:
            print("  On consent page, accepting...")
            time.sleep(3)
            try:
                btns = driver.find_elements(By.TAG_NAME, 'button')
                for btn in btns:
                    txt = btn.text.lower()
                    if 'accepteer' in txt or 'akkoord' in txt or 'accept' in txt:
                        btn.click()
                        time.sleep(3)
                        break
            except:
                pass

        # AutoWereld zoek URLs - combinatie van zoeken en directe categorieën
        search_urls = [
            # Zoekresultaten
            'https://www.autowereld.nl/mercedes-benz/?q=w123',
            'https://www.autowereld.nl/mercedes-benz/?q=w124',
            'https://www.autowereld.nl/mercedes-benz/?q=w115',
            'https://www.autowereld.nl/mercedes-benz/?q=200d',
            'https://www.autowereld.nl/mercedes-benz/?q=240d',
            'https://www.autowereld.nl/mercedes-benz/?q=250d',
            'https://www.autowereld.nl/mercedes-benz/?q=300d',
            # Directe categorieën (voor combi's en andere varianten)
            'https://www.autowereld.nl/mercedes-benz/200-280-w123-combi/',
            'https://www.autowereld.nl/mercedes-benz/200-serie/',
            'https://www.autowereld.nl/mercedes-benz/300-serie/',
        ]

        for url in search_urls:
            print(f"\nFetching: {url[:55]}...")

            try:
                driver.get(url)
                time.sleep(4)

                # Handle DPG Media consent page redirect
                if 'myprivacy' in driver.current_url or 'consent' in driver.current_url:
                    try:
                        btns = driver.find_elements(By.TAG_NAME, 'button')
                        for btn in btns:
                            txt = btn.text.lower()
                            if 'accepteer' in txt or 'akkoord' in txt or 'accept' in txt:
                                btn.click()
                                time.sleep(3)
                                break
                    except:
                        pass

                # Accept cookies if present on main page
                try:
                    cookie_btn = driver.find_elements(By.CSS_SELECTOR, '[class*="accept"], [class*="agree"], button[id*="accept"]')
                    if cookie_btn:
                        cookie_btn[0].click()
                        time.sleep(2)
                except:
                    pass

                # Find car links - get all <a> tags and filter for /details.html
                all_links = driver.find_elements(By.TAG_NAME, 'a')

                # Filter for details.html links
                seen_urls = set()
                details_links = []
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/details.html' in href and href not in seen_urls:
                        seen_urls.add(href)
                        details_links.append((link, href))

                print(f"  Found {len(details_links)} details links")

                # Collect URLs to visit detail pages
                diesel_urls = []
                for link, ad_url in details_links[:30]:
                    url_lower = ad_url.lower()
                    # Check if diesel from URL
                    if any(d in url_lower for d in DIESEL_KEYWORDS):
                        # Quick classic check on URL
                        if any(kw in url_lower for kw in CLASSIC_KEYWORDS):
                            diesel_urls.append(ad_url)

                # Visit each detail page to get year, mileage, price
                for ad_url in diesel_urls:
                    try:
                        # Skip if already found
                        id_match = re.search(r'-(\d{6,})', ad_url)
                        external_id = id_match.group(1) if id_match else str(hash(ad_url))[:10]
                        if any(r['external_id'] == f'autowereld_{external_id}' for r in results):
                            continue

                        # Visit detail page
                        driver.get(ad_url)
                        time.sleep(3)  # Wait for page to fully load

                        # Handle consent redirect on detail page
                        if 'myprivacy' in driver.current_url or 'consent' in driver.current_url:
                            try:
                                btns = driver.find_elements(By.TAG_NAME, 'button')
                                for btn in btns:
                                    if 'accepteer' in btn.text.lower():
                                        btn.click()
                                        time.sleep(2)
                                        break
                            except:
                                pass

                        # Extract title
                        title = ''
                        try:
                            title_elem = driver.find_element(By.CSS_SELECTOR, 'h1')
                            title = title_elem.text.strip()
                        except:
                            url_parts = ad_url.split('/')
                            title = f"Mercedes-Benz {url_parts[-2]}"

                        if not is_classic_diesel(title, url=ad_url):
                            continue

                        # Scroll down to load all content
                        try:
                            driver.execute_script("window.scrollTo(0, 500);")
                            time.sleep(1)
                        except:
                            pass

                        # Extract data from page text
                        price = None
                        year = None
                        mileage = None
                        try:
                            page_text = driver.find_element(By.TAG_NAME, 'body').text

                            # Price: "Prijs € 24.500" or "€ 24.500"
                            price_match = re.search(r'(?:Prijs\s*)?€\s*([\d.]+)', page_text)
                            if price_match:
                                price_str = price_match.group(1).replace('.', '')
                                price = float(price_str) if price_str else None

                            # Year: "Bouwjaar 1983"
                            year_match = re.search(r'Bouwjaar\s*(\d{4})', page_text)
                            if year_match:
                                year = int(year_match.group(1))

                            # Mileage: "Kilometerstand 82.034 km"
                            km_match = re.search(r'Kilometerstand\s*([\d.]+)\s*km', page_text)
                            if km_match:
                                mileage = int(km_match.group(1).replace('.', ''))
                        except:
                            pass

                        # Model detection
                        url_lower = ad_url.lower()
                        model = 'W123/W124'
                        if any(x in url_lower for x in ['w115', '240-d', '240d']):
                            model = 'W115/W123'
                        elif any(x in url_lower for x in ['w123']):
                            model = 'W123'
                        elif any(x in url_lower for x in ['w124', '250d', '300d']):
                            model = 'W124'

                        ad = {
                            'external_id': f'autowereld_{external_id}',
                            'model': model,
                            'year': year,
                            'mileage': mileage,
                            'price': price,
                            'currency': 'EUR',
                            'location': 'Nederland',
                            'country': 'NL',
                            'source': 'AutoWereld.nl',
                            'source_url': ad_url,
                            'title': title,
                            'description': '',
                            'image_url': ''
                        }

                        results.append(ad)
                        yr = year if year else '?'
                        km = f'{mileage:,} km' if mileage else '? km'
                        pr = f'€{int(price):,}' if price else '?'
                        print(f"  + {title[:35]}... ({yr}, {km}, {pr})")

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"  Error: {e}")

        driver.quit()

    except Exception as e:
        print(f"  Selenium error: {e}")

    print(f"\nTotal from AutoWereld.nl: {len(results)}")
    return results


def main():
    print("="*60)
    print("EXTRA SOURCES SCRAPER")
    print("="*60)

    db = Database()
    all_results = []

    # Scrape AutoScout24 (DE, NL, BE, FR, AT)
    for country in ['de', 'nl', 'be', 'fr', 'at']:
        results = scrape_autoscout24_json(country)
        all_results.extend(results)
        time.sleep(2)

    # Scrape AutoTrack.nl
    results_autotrack = scrape_autotrack()
    all_results.extend(results_autotrack)

    # Scrape AutoWereld.nl
    results_autowereld = scrape_autowereld()
    all_results.extend(results_autowereld)

    # Scrape eBay.de
    results_ebay = scrape_ebay_motors()
    all_results.extend(results_ebay)

    # Scrape Gaspedaal.nl
    results_gaspedaal = scrape_gaspedaal()
    all_results.extend(results_gaspedaal)

    # Scrape 2dehands.be (requires Selenium)
    results_2dehands = scrape_2dehands()
    all_results.extend(results_2dehands)

    # Add search links
    add_search_links(db)

    # Save to database
    print("\n" + "="*60)
    print("SAVING TO DATABASE")
    print("="*60)

    added = 0
    for ad in all_results:
        if ad.get('source_url') and ad.get('external_id'):
            try:
                db.add_advertisement(ad)
                added += 1
            except:
                pass

    print(f"\nTotal scraped: {len(all_results)}")
    print(f"Added to database: {added}")

    # Statistics
    stats = db.get_statistics()
    print(f"\nDatabase now contains: {stats['total_active']} advertisements")
    print(f"By country: {stats['by_country']}")


if __name__ == '__main__':
    main()
