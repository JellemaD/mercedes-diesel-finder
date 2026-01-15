import requests
from bs4 import BeautifulSoup
import time
import re
from fake_useragent import UserAgent
import config

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.results = []

        # Set persistent cookies and better headers to avoid bot detection
        self.session.cookies.set('consent', 'true', domain='.marktplaats.nl')

    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    def extract_price(self, price_text):
        """Extract numeric price from text"""
        if not price_text:
            return None
        # Remove currency symbols and thousands separators
        price_clean = re.sub(r'[€$£\s.]', '', price_text)
        price_clean = price_clean.replace(',', '.')
        try:
            return float(re.search(r'\d+\.?\d*', price_clean).group())
        except:
            return None

    def extract_mileage(self, mileage_text):
        """Extract numeric mileage from text"""
        if not mileage_text:
            return None
        # Remove km and thousands separators
        mileage_clean = re.sub(r'[^\d]', '', mileage_text)
        try:
            mileage = int(mileage_clean)
            # SQLite INTEGER max is 2^63-1, but realistic mileage is < 1,000,000 km
            # Filter out unrealistic values (likely parsing errors)
            if mileage > 2000000:  # 2 million km is unrealistic
                return None
            return mileage
        except:
            return None

    def extract_year(self, year_text):
        """Extract year from text"""
        if not year_text:
            return None
        try:
            year_match = re.search(r'(19|20)\d{2}', year_text)
            if year_match:
                return int(year_match.group())
        except:
            pass
        return None


class AutoScout24Scraper(BaseScraper):
    def __init__(self, country='nl'):
        super().__init__()
        self.country = country
        self.base_url = f'https://www.autoscout24.{country}'

    def build_search_url(self, model, year_from, year_to):
        """Build search URL for AutoScout24"""
        # AutoScout24 search parameters
        params = {
            'make': 'Mercedes-Benz',
            'fregfrom': year_from,
            'fregto': year_to,
            'fuel': 'D',  # Diesel
            'sort': 'age',
            'desc': 1
        }

        # Add model-specific parameters
        if 'W123' in model:
            params['model'] = '200-serie'
        elif 'W124' in model:
            params['model'] = '200-serie'
        elif 'W201' in model:
            params['model'] = '190-serie'

        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{self.base_url}/lst?{query_string}'

    def scrape(self, model):
        """Scrape AutoScout24 for specific model"""
        url = self.build_search_url(model, config.YEAR_FROM, config.YEAR_TO)

        try:
            response = self.session.get(url, headers=self.get_headers(), timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all car listings
            listings = soup.find_all('article', class_=lambda x: x and 'ListItem' in x)

            for listing in listings:
                try:
                    ad_data = self.parse_listing(listing, model)
                    if ad_data:
                        self.results.append(ad_data)
                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue

            time.sleep(config.REQUEST_DELAY)

        except Exception as e:
            print(f"Error scraping AutoScout24 {self.country}: {e}")

        return self.results

    def parse_listing(self, listing, model):
        """Parse individual AutoScout24 listing"""
        try:
            # Extract link
            link_elem = listing.find('a', href=True)
            if not link_elem:
                return None

            url = link_elem['href']
            if not url.startswith('http'):
                url = self.base_url + url

            # Extract ID from URL
            external_id = re.search(r'/([a-zA-Z0-9-]+)$', url)
            external_id = external_id.group(1) if external_id else url

            # Extract title
            title_elem = listing.find('h2') or listing.find('span', class_=lambda x: x and 'Title' in x)
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Extract price
            price_elem = listing.find('span', class_=lambda x: x and 'Price' in x)
            price = self.extract_price(price_elem.get_text() if price_elem else '')

            # Extract year and mileage
            details = listing.find_all('span', class_=lambda x: x and 'VehicleDetailTable' in x)
            year = None
            mileage = None

            for detail in details:
                text = detail.get_text()
                if '/' in text or any(month in text.lower() for month in ['januari', 'februari', 'maart']):
                    year = self.extract_year(text)
                elif 'km' in text.lower():
                    mileage = self.extract_mileage(text)

            # Extract location
            location_elem = listing.find('span', class_=lambda x: x and 'Location' in x)
            location = location_elem.get_text(strip=True) if location_elem else ''

            # Extract image
            img_elem = listing.find('img')
            image_url = img_elem.get('src', '') if img_elem else ''

            return {
                'external_id': f'as24_{self.country}_{external_id}',
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
                'image_url': image_url
            }

        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None


class MobileDeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.mobile.de'
        self.country = 'DE'

    def build_search_url(self, model, year_from, year_to):
        """Build search URL for Mobile.de"""
        params = {
            'makeModelVariant1.makeId': '17200',  # Mercedes-Benz
            'cn': 'DE',
            'fuels': 'DIESEL',
            'yearFrom': year_from,
            'yearTo': year_to,
            'sortOption.sortBy': 'creationTime',
            'sortOption.sortOrder': 'DESCENDING'
        }

        # Add model-specific parameters
        if 'W201' in model:
            params['makeModelVariant1.modelId'] = '3'  # 190-serie
        else:
            params['makeModelVariant1.modelId'] = '4'  # 200-serie (W123/W124)

        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{self.base_url}/nl-NL/listing/search?{query_string}'

    def scrape(self, model):
        """Scrape Mobile.de for specific model"""
        url = self.build_search_url(model, config.YEAR_FROM, config.YEAR_TO)

        try:
            response = self.session.get(url, headers=self.get_headers(), timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all car listings
            listings = soup.find_all('div', class_=lambda x: x and 'cBox-body' in str(x))

            for listing in listings:
                try:
                    ad_data = self.parse_listing(listing, model)
                    if ad_data:
                        self.results.append(ad_data)
                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue

            time.sleep(config.REQUEST_DELAY)

        except Exception as e:
            print(f"Error scraping Mobile.de: {e}")

        return self.results

    def parse_listing(self, listing, model):
        """Parse individual Mobile.de listing"""
        try:
            # Extract link
            link_elem = listing.find('a', class_=lambda x: x and 'link--muted' in str(x))
            if not link_elem or not link_elem.get('href'):
                return None

            url = link_elem['href']
            if not url.startswith('http'):
                url = self.base_url + url

            # Extract ID
            external_id = re.search(r'id=(\d+)', url)
            external_id = external_id.group(1) if external_id else url

            # Extract title
            title_elem = listing.find('span', class_=lambda x: x and 'h3' in str(x))
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Extract price
            price_elem = listing.find('span', class_=lambda x: x and 'price' in str(x).lower())
            price = self.extract_price(price_elem.get_text() if price_elem else '')

            # Extract details
            year = None
            mileage = None

            detail_elems = listing.find_all('div', class_=lambda x: x and 'vehicle-data' in str(x))
            for elem in detail_elems:
                text = elem.get_text()
                if 'km' in text.lower():
                    mileage = self.extract_mileage(text)
                elif re.search(r'(19|20)\d{2}', text):
                    year = self.extract_year(text)

            # Extract location
            location_elem = listing.find('span', class_=lambda x: x and 'seller' in str(x).lower())
            location = location_elem.get_text(strip=True) if location_elem else ''

            # Extract image
            img_elem = listing.find('img', class_=lambda x: x and 'img-fluid' in str(x))
            image_url = img_elem.get('src', '') if img_elem else ''

            return {
                'external_id': f'mobile_de_{external_id}',
                'model': model,
                'year': year,
                'mileage': mileage,
                'price': price,
                'currency': 'EUR',
                'location': location,
                'country': 'DE',
                'source': 'Mobile.de',
                'source_url': url,
                'title': title,
                'description': '',
                'image_url': image_url
            }

        except Exception as e:
            print(f"Error parsing Mobile.de listing: {e}")
            return None


class MarktplaatsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.marktplaats.nl'
        self.country = 'NL'

    def build_search_url(self, search_term, offset=0):
        """Build search URL for Marktplaats with pagination support"""
        base = f'{self.base_url}/l/auto-s/q/{search_term.replace(" ", "+")}'
        if offset > 0:
            base += f'?offset={offset}'
        return base

    def scrape(self, model):
        """Scrape Marktplaats for specific model and all its variants"""
        # Get all variants for this model from config
        variants = config.MODEL_VARIANTS.get(model, [])

        # Build list of search terms
        # Use broader terms and year-based searches to catch more ads
        search_terms = [
            f'Mercedes {model} diesel',  # Original search
            f'Mercedes {model}',         # Without 'diesel' keyword
        ]

        # Add searches for each specific variant (200D, 240D, 300D, etc.)
        for variant in variants:
            # Clean variant name (remove "Turbo", "Kombi" suffixes for search)
            variant_clean = variant.replace(' Turbo', '').replace(' Kombi', '')
            search_terms.append(f'Mercedes {variant_clean}')

            # Also add space variant (e.g., "300 D" instead of "300D")
            if variant_clean[-1].isalpha() and variant_clean[-2].isdigit():
                spaced = variant_clean[:-1] + ' ' + variant_clean[-1]
                search_terms.append(f'Mercedes {spaced}')

        # Add year-based searches for years in config range (1979-1986)
        if model == 'W123':
            search_terms.extend(['Mercedes 1979 diesel', 'Mercedes 1980 diesel', 'Mercedes 1985 diesel'])
        elif model == 'W124':
            search_terms.extend(['Mercedes 1985 diesel', 'Mercedes 1986 diesel'])
        elif model == 'W201':  # 190-serie
            search_terms.extend(['Mercedes 190 diesel', 'Mercedes 1984 diesel', 'Mercedes 1985 diesel', 'Mercedes 1986 diesel'])

        print(f"Marktplaats: Searching for {model} with {len(search_terms)} search terms")

        # Track unique external_ids to avoid duplicates
        seen_ids = set()

        for search_term in search_terms:
            url = self.build_search_url(search_term, offset=0)
            print(f"  - Searching: {search_term}")

            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all listings using updated Marktplaats structure
                # Marktplaats uses hz-Listing-container now (as of 2026)
                listings = soup.find_all('div', class_=lambda x: x and 'hz-Listing-container' in str(x))

                # Fallback: if no listings found, try finding by ad links directly
                if not listings:
                    listings = soup.find_all('a', href=lambda x: x and '/v/auto-s/mercedes-benz/' in str(x))

                print(f"    Found {len(listings)} listings")

                for listing in listings:
                    try:
                        ad_data = self.parse_listing(listing, model)
                        if ad_data and ad_data['external_id'] not in seen_ids:
                            seen_ids.add(ad_data['external_id'])
                            self.results.append(ad_data)
                    except Exception as e:
                        print(f"Error parsing listing: {e}")
                        continue

                time.sleep(config.REQUEST_DELAY)

            except Exception as e:
                print(f"Error scraping Marktplaats for '{search_term}': {e}")
                continue

        print(f"Marktplaats: Total unique results for {model}: {len(self.results)}")
        return self.results

    def parse_listing(self, listing, model):
        """Parse individual Marktplaats listing (updated for 2026 HTML structure)"""
        try:
            # Check if listing is the container or the link itself
            if listing.name == 'a':
                link_elem = listing
            else:
                # Extract link from container
                link_elem = listing.find('a', href=True, class_=lambda x: x and 'hz-Listing-coverLink' in str(x))
                if not link_elem:
                    link_elem = listing.find('a', href=True)

            if not link_elem:
                return None

            url = link_elem['href']
            if not url.startswith('http'):
                url = self.base_url + url

            # Extract ID from URL (format: /v/auto-s/mercedes-benz/m1234567890-title)
            external_id = re.search(r'/(m\d+)', url)
            external_id = external_id.group(1) if external_id else url.split('/')[-1]

            # Extract title - try multiple selectors for new structure
            title_elem = (
                listing.find('h3', class_=lambda x: x and 'hz-Listing-title' in str(x)) or
                listing.find('span', class_=lambda x: x and 'title' in str(x).lower()) or
                listing.find('h3') or
                link_elem
            )
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Extract price - updated for hz-Listing structure
            price_elem = (
                listing.find('div', class_=lambda x: x and 'hz-Listing-price-extended-details' in str(x)) or
                listing.find('p', class_=lambda x: x and 'hz-Listing-price' in str(x)) or
                listing.find('span', class_=lambda x: x and 'price' in str(x).lower())
            )
            price = self.extract_price(price_elem.get_text() if price_elem else '')

            # Extract description - updated for hz-Listing structure
            desc_elem = (
                listing.find('p', class_=lambda x: x and 'hz-Listing-description' in str(x)) or
                listing.find('div', class_=lambda x: x and 'description' in str(x).lower())
            )
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Try to extract year and mileage from description or title
            combined_text = f"{title} {description}"
            year = self.extract_year(combined_text)
            mileage = self.extract_mileage(combined_text)

            # Extract location - updated for hz-Listing structure
            location_elem = (
                listing.find('span', class_=lambda x: x and 'hz-Listing-location' in str(x)) or
                listing.find('span', class_=lambda x: x and 'location' in str(x).lower())
            )
            location = location_elem.get_text(strip=True) if location_elem else ''

            # Extract image
            img_elem = listing.find('img')
            image_url = img_elem.get('src', '') if img_elem else ''

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
                'description': description,
                'image_url': image_url
            }

        except Exception as e:
            print(f"Error parsing Marktplaats listing: {e}")
            return None


def get_scraper(site_name, country='nl'):
    """Factory function to get appropriate scraper"""
    scrapers = {
        'AutoScout24': lambda c: AutoScout24Scraper(country=c),
        'Mobile.de': lambda c: MobileDeScraper(),
        'Marktplaats': lambda c: MarktplaatsScraper(),
        'Kleinanzeigen': lambda c: AutoScout24Scraper(country='de'),  # Similar to AutoScout24
    }

    scraper_func = scrapers.get(site_name)
    if scraper_func:
        return scraper_func(country)
    return None
