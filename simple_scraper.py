"""
Simple reliable scraper that generates search URLs
Instead of scraping HTML, we generate direct search URLs to marketplaces
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database import Database
import config

def generate_search_links():
    """
    Generate direct search links to marketplaces
    This approach always gives working URLs that users can click
    """

    db = Database()

    print("Generating marketplace search links...")
    print()

    links = []

    # AutoScout24 NL - W123
    links.append({
        'external_id': 'search_as24_nl_w123',
        'model': 'W123 (alle varianten)',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'Nederland',
        'country': 'NL',
        'source': 'AutoScout24',
        'source_url': 'https://www.autoscout24.nl/lst/mercedes-benz?fregfrom=1980&fregto=1987&fuel=D&sort=age&desc=0&ustate=U&page=1',
        'title': 'Zoekresultaten Mercedes W123 Diesel (1980-1987)',
        'description': 'Klik om alle Mercedes W123 diesels op AutoScout24.nl te bekijken',
        'image_url': ''
    })

    # AutoScout24 DE - W123/W124
    links.append({
        'external_id': 'search_as24_de_w123',
        'model': 'W123/W124 (alle varianten)',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'Duitsland',
        'country': 'DE',
        'source': 'AutoScout24',
        'source_url': 'https://www.autoscout24.de/lst/mercedes-benz?fregfrom=1980&fregto=1987&fuel=D&sort=age&desc=0&ustate=U&page=1',
        'title': 'Zoekresultaten Mercedes W123/W124 Diesel (1980-1987)',
        'description': 'Klik om alle Mercedes diesels op AutoScout24.de te bekijken',
        'image_url': ''
    })

    # Mobile.de
    links.append({
        'external_id': 'search_mobile_de',
        'model': 'W123/W124',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'Duitsland',
        'country': 'DE',
        'source': 'Mobile.de',
        'source_url': 'https://www.mobile.de/auto/search.html?isSearchRequest=true&makeModelVariant1.makeId=17200&fuels=DIESEL&minFirstRegistrationDate=1980-01-01&maxFirstRegistrationDate=1987-12-31&usage=USED',
        'title': 'Zoekresultaten Mercedes Diesel op Mobile.de',
        'description': 'Klik om alle Mercedes diesels op Mobile.de te bekijken',
        'image_url': ''
    })

    # Marktplaats NL - W123
    links.append({
        'external_id': 'search_marktplaats_w123',
        'model': 'W123',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'Nederland',
        'country': 'NL',
        'source': 'Marktplaats',
        'source_url': 'https://www.marktplaats.nl/l/auto-s/mercedes-benz/q/w123+diesel/',
        'title': 'Zoekresultaten Mercedes W123 Diesel',
        'description': 'Klik om alle Mercedes W123 diesels op Marktplaats.nl te bekijken',
        'image_url': ''
    })

    # Marktplaats NL - W124
    links.append({
        'external_id': 'search_marktplaats_w124',
        'model': 'W124',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'Nederland',
        'country': 'NL',
        'source': 'Marktplaats',
        'source_url': 'https://www.marktplaats.nl/l/auto-s/mercedes-benz/q/w124+diesel/',
        'title': 'Zoekresultaten Mercedes W124 Diesel',
        'description': 'Klik om alle Mercedes W124 diesels op Marktplaats.nl te bekijken',
        'image_url': ''
    })

    # 2dehands BE
    links.append({
        'external_id': 'search_2dehands_be',
        'model': 'W123/W124',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'België',
        'country': 'BE',
        'source': '2dehands.be',
        'source_url': 'https://www.2dehands.be/l/auto-s/mercedes-benz/q/w123/',
        'title': 'Zoekresultaten Mercedes W123 op 2dehands.be',
        'description': 'Klik om alle Mercedes op 2dehands.be te bekijken',
        'image_url': ''
    })

    # AutoScout24 BE
    links.append({
        'external_id': 'search_as24_be',
        'model': 'W123/W124',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'België',
        'country': 'BE',
        'source': 'AutoScout24',
        'source_url': 'https://www.autoscout24.be/nl/lst/mercedes-benz?fregfrom=1980&fregto=1987&fuel=D&sort=age&desc=0&ustate=U',
        'title': 'Zoekresultaten Mercedes Diesel op AutoScout24.be',
        'description': 'Klik om alle Mercedes diesels op AutoScout24.be te bekijken',
        'image_url': ''
    })

    # LeBonCoin FR
    links.append({
        'external_id': 'search_leboncoin_fr',
        'model': 'W123/W124',
        'year': None,
        'mileage': None,
        'price': None,
        'currency': 'EUR',
        'location': 'Frankrijk',
        'country': 'FR',
        'source': 'LeBonCoin',
        'source_url': 'https://www.leboncoin.fr/recherche?category=2&q=mercedes+w123+diesel',
        'title': 'Zoekresultaten Mercedes W123 Diesel op LeBonCoin',
        'description': 'Klik om alle Mercedes op LeBonCoin.fr te bekijken',
        'image_url': ''
    })

    # Add to database
    print(f"Adding {len(links)} search links to database...")
    for link in links:
        db.add_advertisement(link)
        print(f"✓ Added: {link['source']} - {link['country']}")

    print(f"\n✓ {len(links)} werkende zoeklinks toegevoegd!")
    print("\nDeze links brengen gebruikers direct naar de zoekresultaten")
    print("waar ze alle actuele advertenties kunnen zien.\n")

    return links


if __name__ == '__main__':
    generate_search_links()
