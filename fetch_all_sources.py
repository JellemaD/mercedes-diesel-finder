"""
Fetch Mercedes W123/W124 Diesel from multiple sources:
- Marktplaats.nl
- AutoScout24 (NL, DE, BE)
- Kleinanzeigen.de
- Gaspedaal.nl
- Mobile.de
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from database import Database

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,de;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Keywords for filtering
CLASSIC_KEYWORDS = ['w123', 'w124', 'w115', 'w116', '200d', '240d', '250d', '300d', '300td',
                   '200 d', '240 d', '250 d', '300 d', '200-serie', '123', '124']
MODERN_KEYWORDS = ['glc', 'gle', 'gla', 'glb', 'gls', 'cls', 'cla', 'eqc', 'eqa', 'eqb',
                  'v-klasse', 'v klasse', 'b-klasse', 'b klasse', 'a-klasse', 'a klasse',
                  'c-klasse', 'c klasse', 'vito', 'sprinter', 'citan', 'marco polo',
                  '4matic', 'amg line', '7g-tronic', '9g-tronic', 'hybrid', 'plug-in',
                  '2020', '2021', '2022', '2023', '2024', '2025', '2026', 'g-klasse', 'g klasse']


def is_classic_mercedes(title, year=None):
    """Check if this is a classic W123/W124"""
    if not title:
        return False
    title_lower = title.lower()

    is_classic = any(kw in title_lower for kw in CLASSIC_KEYWORDS)
    is_modern = any(kw in title_lower for kw in MODERN_KEYWORDS)
    year_ok = year is None or (year and 1975 <= year <= 1997)

    return is_classic and not is_modern and year_ok


def extract_price(text):
    if not text:
        return None
    clean = re.sub(r'[€$£\s.]', '', str(text))
    clean = clean.replace(',', '.')
    match = re.search(r'\d+\.?\d*', clean)
    return float(match.group()) if match else None


def extract_year(text):
    if not text:
        return None
    match = re.search(r'(19[789]\d|199[0-7])', str(text))
    return int(match.group()) if match else None


def extract_mileage(text):
    if not text:
        return None
    match = re.search(r'(\d[\d.]*)\s*km', str(text).lower())
    if match:
        return int(match.group(1).replace('.', ''))
    return None


def scrape_kleinanzeigen():
    """Scrape Kleinanzeigen.de for Mercedes W123/W124"""
    print("\n" + "="*50)
    print("SCRAPING KLEINANZEIGEN.DE")
    print("="*50)

    results = []
    base_url = 'https://www.kleinanzeigen.de'

    # Search queries
    searches = [
        '/s-autos/mercedes-w123/k0c216',
        '/s-autos/mercedes-w124/k0c216',
        '/s-autos/mercedes-240d/k0c216',
        '/s-autos/mercedes-300d/k0c216',
    ]

    for search_path in searches:
        url = base_url + search_path
        print(f"\nSearching: {search_path}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                print(f"  Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find ad articles
            articles = soup.find_all('article', class_=re.compile(r'aditem'))
            print(f"  Found {len(articles)} listings")

            for article in articles[:15]:
                try:
                    # Find link
                    link = article.find('a', href=re.compile(r'/s-anzeige/'))
                    if not link:
                        continue

                    href = link.get('href', '')
                    ad_url = base_url + href if not href.startswith('http') else href

                    # Extract ID
                    id_match = re.search(r'/(\d+)(?:-|$)', href)
                    external_id = id_match.group(1) if id_match else href.split('/')[-1]

                    # Title
                    title_elem = article.find(['h2', 'a'], class_=re.compile(r'text-module-begin'))
                    if not title_elem:
                        title_elem = link
                    title = title_elem.get_text(strip=True)

                    # Check if classic
                    if not is_classic_mercedes(title):
                        continue

                    # Price
                    price_elem = article.find('p', class_=re.compile(r'aditem-main--middle--price'))
                    price = extract_price(price_elem.get_text() if price_elem else '')

                    # Details
                    details = article.get_text(' ', strip=True)
                    year = extract_year(details)
                    mileage = extract_mileage(details)

                    # Location
                    loc_elem = article.find('div', class_=re.compile(r'aditem-main--top--left'))
                    location = loc_elem.get_text(strip=True) if loc_elem else 'Deutschland'

                    # Image
                    img = article.find('img')
                    image_url = img.get('src', '') if img else ''

                    # Determine model
                    model = 'W123/W124'
                    if 'w123' in title.lower():
                        model = 'W123'
                    elif 'w124' in title.lower():
                        model = 'W124'

                    ad = {
                        'external_id': f'kleinanzeigen_{external_id}',
                        'model': model,
                        'year': year,
                        'mileage': mileage,
                        'price': price,
                        'currency': 'EUR',
                        'location': location,
                        'country': 'DE',
                        'source': 'Kleinanzeigen.de',
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

    print(f"\nTotal from Kleinanzeigen.de: {len(results)}")
    return results


def scrape_autoscout24_api():
    """Try to scrape AutoScout24 using their listing pages"""
    print("\n" + "="*50)
    print("SCRAPING AUTOSCOUT24")
    print("="*50)

    results = []

    countries = [
        ('nl', 'NL', 'Nederland'),
        ('de', 'DE', 'Deutschland'),
        ('be', 'BE', 'België'),
    ]

    for country_code, country, country_name in countries:
        print(f"\nAutoScout24.{country_code}...")

        # Different URL patterns
        urls = [
            f'https://www.autoscout24.{country_code}/lst/mercedes-benz/200-serie?fregfrom=1976&fregto=1996&fuel=D&sort=standard&desc=0&ustate=N%2CU&size=20&page=1&cy={country}&atype=C&',
            f'https://www.autoscout24.{country_code}/lst/mercedes-benz?fregfrom=1976&fregto=1996&fuel=D&sort=standard&desc=0',
        ]

        for url in urls:
            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # Try to find JSON data in page
                scripts = soup.find_all('script', {'type': 'application/json'})
                for script in scripts:
                    try:
                        if script.string and 'listings' in script.string.lower():
                            data = json.loads(script.string)
                            # Process JSON data if found
                    except:
                        pass

                # Find listing links
                links = soup.find_all('a', href=re.compile(r'/aanbod/|/angebot/|/offre/'))

                for link in links[:20]:
                    try:
                        href = link.get('href', '')
                        if not href:
                            continue

                        ad_url = href if href.startswith('http') else f'https://www.autoscout24.{country_code}{href}'

                        # Get parent for context
                        parent = link.find_parent(['article', 'div'])
                        if not parent:
                            continue

                        # Title
                        title = link.get_text(strip=True)
                        if len(title) < 5:
                            title_elem = parent.find(['h2', 'h3'])
                            title = title_elem.get_text(strip=True) if title_elem else ''

                        if not is_classic_mercedes(title):
                            continue

                        # Extract ID
                        id_match = re.search(r'/([a-f0-9-]{20,})', href)
                        external_id = id_match.group(1) if id_match else href.split('/')[-1].split('?')[0]

                        # Price
                        price_elem = parent.find(['span', 'p'], class_=re.compile(r'[Pp]rice'))
                        price = extract_price(price_elem.get_text() if price_elem else '')

                        # Year/mileage
                        text = parent.get_text(' ', strip=True)
                        year = extract_year(text)
                        mileage = extract_mileage(text)

                        # Model
                        model = 'W123/W124'
                        if 'w123' in title.lower():
                            model = 'W123'
                        elif 'w124' in title.lower():
                            model = 'W124'

                        ad = {
                            'external_id': f'as24_{country_code}_{external_id}',
                            'model': model,
                            'year': year,
                            'mileage': mileage,
                            'price': price,
                            'currency': 'EUR',
                            'location': country_name,
                            'country': country,
                            'source': 'AutoScout24',
                            'source_url': ad_url,
                            'title': title,
                            'description': '',
                            'image_url': ''
                        }

                        if not any(r['external_id'] == ad['external_id'] for r in results):
                            results.append(ad)
                            print(f"  + {title[:45]}...")

                    except:
                        continue

                time.sleep(1)
                break  # Only try first working URL

            except Exception as e:
                continue

    print(f"\nTotal from AutoScout24: {len(results)}")
    return results


def scrape_marktplaats():
    """Scrape Marktplaats.nl"""
    print("\n" + "="*50)
    print("SCRAPING MARKTPLAATS.NL")
    print("="*50)

    results = []
    base_url = 'https://www.marktplaats.nl'

    search_terms = ['w123+diesel', 'w124+diesel', 'mercedes+240d', 'mercedes+300d+oldtimer']

    for term in search_terms:
        url = f'{base_url}/l/auto-s/mercedes-benz/q/{term}/'
        print(f"\nSearching: {term}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('li', class_=re.compile(r'[Ll]isting'))
            if not listings:
                listings = soup.find_all('article')

            print(f"  Found {len(listings)} listings")

            for listing in listings[:15]:
                try:
                    link = listing.find('a', href=True)
                    if not link:
                        continue

                    href = link.get('href', '')
                    if '/v/' not in href and '/a/' not in href:
                        continue

                    ad_url = href if href.startswith('http') else base_url + href

                    # ID
                    id_match = re.search(r'/([am]\d+)', href)
                    external_id = id_match.group(1) if id_match else href.split('/')[-1]

                    # Title
                    title_elem = listing.find(['h3', 'h2'])
                    title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)

                    if not is_classic_mercedes(title):
                        continue

                    # Price
                    price_elem = listing.find(['span', 'p'], class_=re.compile(r'[Pp]rice'))
                    price = extract_price(price_elem.get_text() if price_elem else '')

                    # Details
                    text = listing.get_text(' ', strip=True)
                    year = extract_year(text)
                    mileage = extract_mileage(text)

                    # Location
                    loc_elem = listing.find(['span'], class_=re.compile(r'[Ll]ocation'))
                    location = loc_elem.get_text(strip=True) if loc_elem else 'Nederland'

                    # Model
                    model = 'W123/W124'
                    if 'w123' in title.lower():
                        model = 'W123'
                    elif 'w124' in title.lower():
                        model = 'W124'

                    ad = {
                        'external_id': f'mp_nl_{external_id}',
                        'model': model,
                        'year': year,
                        'mileage': mileage,
                        'price': price,
                        'currency': 'EUR',
                        'location': location,
                        'country': 'NL',
                        'source': 'Marktplaats',
                        'source_url': ad_url,
                        'title': title,
                        'description': '',
                        'image_url': ''
                    }

                    if not any(r['external_id'] == ad['external_id'] for r in results):
                        results.append(ad)
                        print(f"  + {title[:45]}...")

                except:
                    continue

            time.sleep(1)

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal from Marktplaats: {len(results)}")
    return results


def scrape_mobile_de():
    """Scrape Mobile.de"""
    print("\n" + "="*50)
    print("SCRAPING MOBILE.DE")
    print("="*50)

    results = []

    # Mobile.de has strong bot protection, but let's try
    urls = [
        'https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&fuels=DIESEL&isSearchRequest=true&makeModelVariant1.makeId=17200&maxFirstRegistrationDate=1996&minFirstRegistrationDate=1976&scopeId=C&sfmr=false',
    ]

    headers_de = HEADERS.copy()
    headers_de['Accept-Language'] = 'de-DE,de;q=0.9'

    for url in urls:
        print(f"\nTrying Mobile.de...")
        try:
            response = requests.get(url, headers=headers_de, timeout=30)
            print(f"  Status: {response.status_code}")

            if response.status_code == 403:
                print("  Bot protection active - skipping")
                continue

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for listings
                listings = soup.find_all('div', class_=re.compile(r'cBox-body'))
                print(f"  Found {len(listings)} potential listings")

                for listing in listings[:20]:
                    try:
                        link = listing.find('a', href=True)
                        if not link:
                            continue

                        href = link.get('href', '')
                        if 'fahrzeuge' not in href:
                            continue

                        title = link.get_text(strip=True)
                        if not is_classic_mercedes(title):
                            continue

                        ad_url = href if href.startswith('http') else 'https://www.mobile.de' + href

                        id_match = re.search(r'id=(\d+)', href)
                        external_id = id_match.group(1) if id_match else href.split('/')[-1]

                        text = listing.get_text(' ', strip=True)

                        ad = {
                            'external_id': f'mobile_de_{external_id}',
                            'model': 'W123/W124',
                            'year': extract_year(text),
                            'mileage': extract_mileage(text),
                            'price': extract_price(text),
                            'currency': 'EUR',
                            'location': 'Deutschland',
                            'country': 'DE',
                            'source': 'Mobile.de',
                            'source_url': ad_url,
                            'title': title,
                            'description': '',
                            'image_url': ''
                        }

                        if not any(r['external_id'] == ad['external_id'] for r in results):
                            results.append(ad)
                            print(f"  + {title[:45]}...")

                    except:
                        continue

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal from Mobile.de: {len(results)}")
    return results


def main():
    print("="*60)
    print("MERCEDES W123/W124 DIESEL - MULTI-SOURCE SCRAPER")
    print("="*60)

    db = Database()
    all_results = []

    # Scrape all sources
    results_kleinanzeigen = scrape_kleinanzeigen()
    all_results.extend(results_kleinanzeigen)

    results_autoscout = scrape_autoscout24_api()
    all_results.extend(results_autoscout)

    results_marktplaats = scrape_marktplaats()
    all_results.extend(results_marktplaats)

    results_mobile = scrape_mobile_de()
    all_results.extend(results_mobile)

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

    return all_results


if __name__ == '__main__':
    main()
