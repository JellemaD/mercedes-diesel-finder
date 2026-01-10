"""
Fetch real Mercedes W123/W124 Diesel advertisements from working marketplaces
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

# Headers to avoid bot detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}


def extract_price(price_text):
    """Extract numeric price from text"""
    if not price_text:
        return None
    price_clean = re.sub(r'[€$£\s.]', '', price_text)
    price_clean = price_clean.replace(',', '.')
    try:
        match = re.search(r'\d+\.?\d*', price_clean)
        if match:
            return float(match.group())
    except:
        pass
    return None


def extract_year(text):
    """Extract year from text, supporting multiple formats:
    - Plain year: 1986
    - Erstzulassung format: EZ 02/1986, Erstzulassung 02/1986
    - Date format: 02/1986, 1986-02
    - Bouwjaar: Bj. 1986
    """
    if not text:
        return None

    text = str(text)

    # Format: EZ 02/1986 or Erstzulassung 02/1986 or Bj. 1986
    ez_match = re.search(r'(?:EZ|Erstzulassung|Bj\.?|Baujahr|Bouwjaar)?\s*(\d{1,2})[/.-]?(19[789]\d|199[0-7])', text, re.IGNORECASE)
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
    """Extract mileage from text"""
    if not text:
        return None
    try:
        # Look for patterns like "150.000 km" or "150000 km"
        match = re.search(r'(\d[\d.]*)\s*km', text.lower())
        if match:
            mileage_str = match.group(1).replace('.', '')
            return int(mileage_str)
    except:
        pass
    return None


def scrape_autoscout24(country='nl'):
    """Scrape AutoScout24 for Mercedes W123/W124 Diesel using API"""

    print(f"\nScraping AutoScout24.{country}...")

    results = []

    # AutoScout24 API endpoint
    api_url = f'https://www.autoscout24.{country}/lst/api/search'

    # Different search queries for W123 and W124
    searches = [
        {'query': 'mercedes w123 diesel', 'model': 'W123'},
        {'query': 'mercedes w124 diesel', 'model': 'W124'},
        {'query': 'mercedes 200d', 'model': 'W123/W124'},
        {'query': 'mercedes 240d', 'model': 'W123'},
        {'query': 'mercedes 250d', 'model': 'W124'},
        {'query': 'mercedes 300d', 'model': 'W123/W124'},
    ]

    base_url = f'https://www.autoscout24.{country}'

    for search in searches:
        # Try direct search URL (max 1987 for oldtimer/road tax exemption)
        search_url = f'{base_url}/lst?fregfrom=1976&fregto=1987&fuel=D&sort=age&desc=0&query={search["query"].replace(" ", "+")}'

        try:
            session = requests.Session()
            response = session.get(search_url, headers=HEADERS, timeout=30)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links to car listings
            all_links = soup.find_all('a', href=re.compile(r'/aanbod/|/angebot/|/offre/|/offers/'))

            for link in all_links:
                url = link.get('href', '')
                if not url.startswith('http'):
                    url = base_url + url

                # Skip if already found
                if any(r['source_url'] == url for r in results):
                    continue

                # Extract data from link context
                parent = link.find_parent(['article', 'div', 'li'])
                if parent:
                    title_elem = parent.find(['h2', 'h3', 'span'], class_=re.compile(r'[Tt]itle'))
                    title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)

                    # Filter: only W123/W124 related
                    title_lower = title.lower()
                    is_classic = any(kw in title_lower for kw in ['w123', 'w124', '200d', '240d', '250d', '300d', '200 d', '240 d', '250 d', '300 d'])
                    is_modern = any(kw in title_lower for kw in ['glc', 'gle', 'gla', 'cls', 'cla', 'v-klasse', 'b-klasse', 'a-klasse', 'vito', 'sprinter', 'amg'])

                    if not is_classic or is_modern:
                        continue

                    price_elem = parent.find(['span', 'div'], class_=re.compile(r'[Pp]rice'))
                    price = extract_price(price_elem.get_text() if price_elem else '')

                    all_text = parent.get_text(' ', strip=True)
                    year = extract_year(all_text)
                    mileage = extract_mileage(all_text)

                    # Only include if year is in classic range
                    if year and (year < 1976 or year > 1996):
                        continue

                    id_match = re.search(r'/([a-f0-9-]{20,})', url)
                    external_id = id_match.group(1) if id_match else url.split('/')[-1].split('?')[0]

                    img = parent.find('img')
                    image_url = img.get('src', '') if img else ''

                    ad = {
                        'external_id': f'as24_{country}_{external_id}',
                        'model': search['model'],
                        'year': year,
                        'mileage': mileage,
                        'price': price,
                        'currency': 'EUR',
                        'location': country.upper(),
                        'country': country.upper(),
                        'source': 'AutoScout24',
                        'source_url': url,
                        'title': title,
                        'description': '',
                        'image_url': image_url
                    }

                    results.append(ad)
                    print(f"  Found: {title[:50]}...")

            time.sleep(1)

        except Exception as e:
            print(f"  Error for {search['query']}: {e}")
            continue

    print(f"Extracted {len(results)} advertisements from AutoScout24.{country}")
    return results


def parse_autoscout24_listing(listing, base_url, country):
    """Parse a single AutoScout24 listing"""

    # Find link
    link = listing.find('a', href=True)
    if not link:
        return None

    url = link.get('href', '')
    if not url.startswith('http'):
        url = base_url + url

    # Skip non-car links
    if '/offers/' not in url and '/angebote/' not in url and '/aanbiedingen/' not in url:
        return None

    # Extract ID from URL
    id_match = re.search(r'/([a-f0-9-]{20,})(?:\?|$)', url)
    external_id = id_match.group(1) if id_match else url.split('/')[-1].split('?')[0]

    # Find title
    title_elem = listing.find(['h2', 'h3', 'span'], class_=re.compile(r'[Tt]itle|[Nn]ame'))
    if not title_elem:
        title_elem = listing.find(['h2', 'h3'])
    title = title_elem.get_text(strip=True) if title_elem else ''

    # Find price
    price_elem = listing.find(['span', 'div', 'p'], class_=re.compile(r'[Pp]rice'))
    price = extract_price(price_elem.get_text() if price_elem else '')

    # Find details (year, mileage)
    all_text = listing.get_text(' ', strip=True)
    year = extract_year(all_text)
    mileage = extract_mileage(all_text)

    # Find image
    img = listing.find('img')
    image_url = ''
    if img:
        image_url = img.get('src', '') or img.get('data-src', '')

    # Determine model from title
    model = 'W123/W124'
    if 'w123' in title.lower() or '200d' in title.lower() or '240d' in title.lower():
        model = 'W123'
    elif 'w124' in title.lower() or '250d' in title.lower() or '300d' in title.lower():
        model = 'W124'

    return {
        'external_id': f'as24_{country}_{external_id}',
        'model': model,
        'year': year,
        'mileage': mileage,
        'price': price,
        'currency': 'EUR',
        'location': country.upper(),
        'country': country.upper(),
        'source': 'AutoScout24',
        'source_url': url,
        'title': title,
        'description': '',
        'image_url': image_url
    }


def is_classic_mercedes(title, year=None):
    """Check if advertisement is for a classic W123/W124 DIESEL (oldtimer <= 1987)"""
    title_lower = title.lower() if title else ''

    # Positive indicators for classic diesel cars
    classic_keywords = ['w123', 'w124', 'w115', 'w116', '200d', '240d', '250d', '300d',
                       '200 d', '240 d', '250 d', '300 d', 'youngtimer', 'young timer',
                       '200-serie', '123', '124', 'diesel sedan', 'diesel kombi']

    # Negative indicators for modern cars
    modern_keywords = ['glc', 'gle', 'gla', 'glb', 'gls', 'cls', 'cla', 'eqc', 'eqa', 'eqb',
                      'v-klasse', 'v klasse', 'b-klasse', 'b klasse', 'a-klasse', 'a klasse',
                      'c-klasse', 'c klasse', 'e-klasse', 'e klasse', 's-klasse', 's klasse',
                      'vito', 'sprinter', 'citan', 'marco polo', '4matic', 'amg pakket',
                      '7g-tronic', '7g-dct', '9g-tronic', 'hybrid', 'plug-in', 'eq',
                      '2020', '2021', '2022', '2023', '2024', '2025', '2026']

    # Benzine modellen uitsluiten (E = Einspritzung = benzine injectie)
    benzine_keywords = ['200e', '230e', '260e', '280e', '300e', '320e',
                        '200 e', '230 e', '260 e', '280 e', '300 e', '320 e',
                        'benzine', 'petrol', 'gasoline']

    is_classic = any(kw in title_lower for kw in classic_keywords)
    is_modern = any(kw in title_lower for kw in modern_keywords)
    is_benzine = any(kw in title_lower for kw in benzine_keywords)

    # Year check: only oldtimers (max 1987 for road tax exemption)
    year_ok = year is None or (year and year <= 1987)

    return is_classic and not is_modern and not is_benzine and year_ok


def scrape_marktplaats():
    """Scrape Marktplaats for Mercedes W123/W124 Diesel"""

    base_url = 'https://www.marktplaats.nl'
    results = []

    search_terms = ['w123+diesel', 'w124+diesel', 'mercedes+240d', 'mercedes+300d+1985', 'mercedes+diesel+oldtimer']

    for term in search_terms:
        search_url = f'{base_url}/l/auto-s/mercedes-benz/q/{term}/'

        print(f"\nScraping Marktplaats: {term}...")

        try:
            session = requests.Session()
            response = session.get(search_url, headers=HEADERS, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find listings
            listings = soup.find_all('li', class_=re.compile(r'[Ll]isting'))
            if not listings:
                listings = soup.find_all('article')
            if not listings:
                listings = soup.find_all('div', {'data-testid': re.compile(r'listing')})

            print(f"Found {len(listings)} potential listings for {term}")

            for listing in listings[:20]:  # Limit per search
                try:
                    ad = parse_marktplaats_listing(listing, base_url)
                    if ad and ad.get('source_url'):
                        # Filter: only classic Mercedes
                        if not is_classic_mercedes(ad.get('title', ''), ad.get('year')):
                            continue
                        # Avoid duplicates
                        if not any(r['external_id'] == ad['external_id'] for r in results):
                            results.append(ad)
                            print(f"  Found: {ad['title'][:50]}...")
                except:
                    continue

            time.sleep(1)  # Be polite

        except Exception as e:
            print(f"Error scraping Marktplaats ({term}): {e}")

    print(f"\nExtracted {len(results)} unique advertisements from Marktplaats")
    return results


def parse_marktplaats_listing(listing, base_url):
    """Parse a single Marktplaats listing"""

    # Find link
    link = listing.find('a', href=True)
    if not link:
        return None

    url = link.get('href', '')
    if not url.startswith('http'):
        url = base_url + url

    # Skip non-car links
    if '/a/' not in url and '/v/' not in url:
        return None

    # Extract ID from URL
    id_match = re.search(r'/([am]\d+)', url)
    external_id = id_match.group(1) if id_match else url.split('/')[-1].split('.')[0]

    # Find title
    title_elem = listing.find(['h3', 'h2', 'span'], class_=re.compile(r'[Tt]itle|[Nn]ame'))
    if not title_elem:
        title_elem = listing.find(['h3', 'h2'])
    title = title_elem.get_text(strip=True) if title_elem else ''

    # Find price
    price_elem = listing.find(['span', 'div'], class_=re.compile(r'[Pp]rice'))
    price = extract_price(price_elem.get_text() if price_elem else '')

    # Find details
    all_text = listing.get_text(' ', strip=True)
    year = extract_year(all_text)
    mileage = extract_mileage(all_text)

    # Find location
    loc_elem = listing.find(['span', 'div'], class_=re.compile(r'[Ll]ocation'))
    location = loc_elem.get_text(strip=True) if loc_elem else 'Nederland'

    # Find image
    img = listing.find('img')
    image_url = ''
    if img:
        image_url = img.get('src', '') or img.get('data-src', '')

    # Determine model
    model = 'W123/W124'
    if 'w123' in title.lower():
        model = 'W123'
    elif 'w124' in title.lower():
        model = 'W124'

    return {
        'external_id': f'mp_nl_{external_id}',
        'model': model,
        'year': year,
        'mileage': mileage,
        'price': price,
        'currency': 'EUR',
        'location': location,
        'country': 'NL',
        'source': 'Marktplaats',
        'source_url': url,
        'title': title,
        'description': '',
        'image_url': image_url
    }


def main():
    """Main function to fetch real data"""

    print("="*70)
    print("MERCEDES W123/W124 DIESEL - REAL DATA FETCHER")
    print("="*70)

    db = Database()
    all_results = []

    # Scrape AutoScout24 NL
    results_nl = scrape_autoscout24('nl')
    all_results.extend(results_nl)
    time.sleep(2)

    # Scrape AutoScout24 DE
    results_de = scrape_autoscout24('de')
    all_results.extend(results_de)
    time.sleep(2)

    # Scrape AutoScout24 BE
    results_be = scrape_autoscout24('be')
    all_results.extend(results_be)
    time.sleep(2)

    # Scrape Marktplaats
    results_mp = scrape_marktplaats()
    all_results.extend(results_mp)

    # Add results to database
    print("\n" + "="*70)
    print("SAVING TO DATABASE")
    print("="*70)

    added = 0
    for ad in all_results:
        if ad.get('source_url') and ad.get('external_id'):
            try:
                db.add_advertisement(ad)
                added += 1
                print(f"+ {ad['source']}: {ad['title'][:50]}...")
            except Exception as e:
                print(f"Error adding: {e}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total fetched: {len(all_results)}")
    print(f"Added to database: {added}")

    # Show statistics
    stats = db.get_statistics()
    print(f"\nDatabase now contains: {stats['total_active']} active advertisements")
    print(f"By country: {stats['by_country']}")

    return all_results


if __name__ == '__main__':
    main()
