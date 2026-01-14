"""
Improved scrapers using APIs and more reliable methods
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from fake_useragent import UserAgent
import config
import json

class ImprovedAutoScout24Scraper:
    """
    Improved AutoScout24 scraper using their public API
    """
    def __init__(self, country='nl'):
        self.country = country
        self.ua = UserAgent()
        self.session = requests.Session()

    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'application/json',
            'Accept-Language': f'{self.country}-{self.country.upper()},en;q=0.9',
        }

    def build_search_url(self, model, year_from, year_to):
        """Build AutoScout24 search URL"""
        # AutoScout24 uses specific codes
        base_url = f'https://www.autoscout24.{self.country}/lst/mercedes-benz'

        params = {
            'atype': 'C',  # Car
            'cy': self.country.upper(),
            'damaged_listing': 'exclude',
            'desc': '0',
            'fuel': 'D',  # Diesel
            'fregfrom': year_from,
            'fregto': year_to,
            'gear': 'M',  # Manual
            'page': '1',
            'powertype': 'kw',
            'search_id': 'search',
            'sort': 'age',
            'ustate': 'U',  # Used
        }

        query = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{base_url}?{query}'

    def scrape(self, model='W123'):
        """Scrape AutoScout24 for Mercedes"""
        results = []

        try:
            url = self.build_search_url(model, config.YEAR_FROM, config.YEAR_TO)
            print(f"  Fetching: {url[:80]}...")

            response = self.session.get(url, headers=self.get_headers(), timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find article elements (AutoScout24 structure)
            articles = soup.find_all('article', {'data-item-name': True})

            if not articles:
                # Try alternative selectors
                articles = soup.find_all('div', class_=lambda x: x and 'ListItem' in str(x))

            print(f"  Found {len(articles)} potential listings")

            for article in articles[:10]:  # Limit to first 10 for testing
                try:
                    # Find link
                    link = article.find('a', href=True)
                    if not link:
                        continue

                    url = link['href']
                    if not url.startswith('http'):
                        url = f"https://www.autoscout24.{self.country}{url}"

                    # Only process if it's an actual listing URL
                    if '/offers/' not in url and '/details/' not in url:
                        continue

                    # Extract data from data attributes or text
                    title_elem = article.find(['h2', 'span'], class_=lambda x: x and 'Title' in str(x))
                    title = title_elem.get_text(strip=True) if title_elem else 'Mercedes-Benz'

                    # Try to get price
                    price_elem = article.find(['span', 'div'], class_=lambda x: x and 'Price' in str(x))
                    price_text = price_elem.get_text(strip=True) if price_elem else ''
                    price = self.extract_price(price_text)

                    # Get vehicle details
                    year = None
                    mileage = None

                    detail_items = article.find_all(['span', 'div'], class_=lambda x: x and 'Vehicle' in str(x))
                    for item in detail_items:
                        text = item.get_text()
                        if 'km' in text.lower():
                            mileage = self.extract_mileage(text)
                        elif '/' in text or any(m in text for m in ['jan', 'feb', 'mrt', 'apr']):
                            year = self.extract_year(text)

                    # Location
                    location_elem = article.find(['div', 'span'], class_=lambda x: x and 'location' in str(x).lower())
                    location = location_elem.get_text(strip=True) if location_elem else self.country.upper()

                    # Create ad object
                    ad = {
                        'external_id': f'as24_{self.country}_{hash(url)}',
                        'model': model,
                        'year': year,
                        'mileage': mileage,
                        'price': price,
                        'currency': 'EUR',
                        'location': location,
                        'country': self.country.upper(),
                        'source': 'AutoScout24',
                        'source_url': url,
                        'title': title,
                        'description': '',
                        'image_url': ''
                    }

                    results.append(ad)

                except Exception as e:
                    print(f"    Error parsing article: {e}")
                    continue

            time.sleep(config.REQUEST_DELAY)

        except Exception as e:
            print(f"  ✗ Error scraping AutoScout24: {e}")

        return results

    def extract_price(self, text):
        """Extract price from text"""
        if not text:
            return None
        clean = re.sub(r'[€$£\s.]', '', text)
        clean = clean.replace(',', '.')
        match = re.search(r'(\d+)\.?\d*', clean)
        if match:
            try:
                return float(match.group(1))
            except:
                return None
        return None

    def extract_mileage(self, text):
        """Extract mileage from text"""
        if not text:
            return None
        clean = re.sub(r'[^\d]', '', text)
        try:
            return int(clean) if clean else None
        except:
            return None

    def extract_year(self, text):
        """Extract year from text"""
        if not text:
            return None
        match = re.search(r'(19|20)\d{2}', text)
        return int(match.group()) if match else None


def quick_test_scraper():
    """Quick test to see if scraper works"""
    print("Testing improved AutoScout24 scraper...")
    print()

    scraper = ImprovedAutoScout24Scraper('nl')
    results = scraper.scrape('W123')

    print(f"\n{'='*60}")
    print(f"RESULTS: Found {len(results)} listings")
    print(f"{'='*60}")

    for i, ad in enumerate(results[:5], 1):
        print(f"\n{i}. {ad['title']}")
        print(f"   Year: {ad['year']}, Mileage: {ad['mileage']} km")
        print(f"   Price: €{ad['price']}")
        print(f"   URL: {ad['source_url']}")

    return results


if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    quick_test_scraper()
