"""
Demo script to populate database with sample data for testing
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database import Database
from datetime import datetime
import random

def generate_demo_data():
    """Generate demo advertisements for testing"""

    db = Database()

    # Sample data based on the screenshot
    demo_ads = [
        {
            'external_id': 'demo_as24_1',
            'model': 'W123 300D',
            'year': 1979,
            'mileage': 131866,
            'price': 14990.00,
            'currency': 'EUR',
            'location': 'Neustadt',
            'country': 'DE',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.de/offers/mercedes-benz-200-beige-05e0e5e1-8cf3-49b1-b7e4-e5f7d7b7c7e8',
            'title': 'Mercedes-Benz W123 300D',
            'description': 'Klassischer Mercedes 300D in gutem Zustand',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_2',
            'model': 'W123 300D',
            'year': 1984,
            'mileage': 138000,
            'price': 12900.00,
            'currency': 'EUR',
            'location': 'Roetgen',
            'country': 'DE',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.de/offers/mercedes-benz-w123-300d-demo',
            'title': 'Mercedes-Benz W123 300D',
            'description': 'Schöner Oldtimer aus 1984',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_3',
            'model': 'W123 300TD',
            'year': 1984,
            'mileage': 177500,
            'price': 7900.00,
            'currency': 'EUR',
            'location': 'Villaviciosa',
            'country': 'ES',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.es/offers/mercedes-benz-w123-300td',
            'title': 'Mercedes-Benz W123 300TD Station',
            'description': 'Break T-modèle 300TD',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_4',
            'model': 'W123 300D',
            'year': 1979,
            'mileage': 54200,
            'price': 19000.00,
            'currency': 'EUR',
            'location': 'Berlin',
            'country': 'DE',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.de/offers/mercedes-benz-w123-300d-berlin',
            'title': 'Mercedes-Benz 300D - Wenig Kilometer',
            'description': 'Sehr gepflegter W123 mit nur 54.200 km',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_5',
            'model': 'W123 300D',
            'year': 1984,
            'mileage': 335000,
            'price': 11200.00,
            'currency': 'EUR',
            'location': 'Berlin',
            'country': 'DE',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.de/offers/mercedes-benz-w123-300d-hochlaufer',
            'title': 'Mercedes-Benz 300D Hochläufer',
            'description': 'Zuverlässiger Mercedes mit hoher Laufleistung',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_6',
            'model': 'W123 300D Turbo',
            'year': 1985,
            'mileage': 440085,
            'price': 16950.00,
            'currency': 'EUR',
            'location': 'Zelhem',
            'country': 'NL',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.nl/offers/mercedes-benz-w123-300d-turbo',
            'title': 'Mercedes-Benz 300D Turbo',
            'description': 'Originele Nederlandse W123 Turbo',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_7',
            'model': 'W123 300D',
            'year': 1984,
            'mileage': 342039,
            'price': 12950.00,
            'currency': 'EUR',
            'location': 'Bad Bentheim',
            'country': 'DE',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.de/offers/mercedes-benz-w123-300d-badbenheim',
            'title': 'Mercedes-Benz 300D',
            'description': 'Solider Mercedes Diesel',
            'image_url': ''
        },
        {
            'external_id': 'demo_markt_1',
            'model': 'W123 240D',
            'year': 1980,
            'mileage': 150000,
            'price': 5500.00,
            'currency': 'EUR',
            'location': 'Amsterdam',
            'country': 'NL',
            'source': 'Marktplaats',
            'source_url': 'https://www.marktplaats.nl/a/mercedes-w123-240d',
            'title': 'Mercedes W123 240D Oldtimer',
            'description': 'Klassieke Mercedes in goede staat',
            'image_url': ''
        },
        {
            'external_id': 'demo_as24_8',
            'model': 'W123 300D Turbo',
            'year': 1982,
            'mileage': 431939,
            'price': 17500.00,
            'currency': 'EUR',
            'location': 'Kauern',
            'country': 'DE',
            'source': 'AutoScout24',
            'source_url': 'https://www.autoscout24.de/offers/mercedes-benz-w123-300d-turbo-kauern',
            'title': 'Mercedes-Benz 300D Turbo',
            'description': 'Gut erhaltener Turbo Diesel',
            'image_url': ''
        },
        # W124 models
        {
            'external_id': 'demo_mobile_1',
            'model': 'W124 250D',
            'year': 1987,
            'mileage': 180000,
            'price': 6500.00,
            'currency': 'EUR',
            'location': 'München',
            'country': 'DE',
            'source': 'Mobile.de',
            'source_url': 'https://www.mobile.de/offers/mercedes-benz-w124-250d',
            'title': 'Mercedes-Benz 250D W124',
            'description': 'Klassischer W124 Diesel',
            'image_url': ''
        },
        {
            'external_id': 'demo_mobile_2',
            'model': 'W124 250TD',
            'year': 1994,
            'mileage': 430000,
            'price': 2690.00,
            'currency': 'EUR',
            'location': 'Waldkraiburg',
            'country': 'DE',
            'source': 'Mobile.de',
            'source_url': 'https://www.mobile.de/offers/mercedes-benz-w124-250td',
            'title': 'Mercedes-Benz 250TD T-Modell',
            'description': 'Zuverlässiger Kombi',
            'image_url': ''
        },
        {
            'external_id': 'demo_mobile_3',
            'model': 'W124 250D',
            'year': 1992,
            'mileage': 270000,
            'price': 7999.00,
            'currency': 'EUR',
            'location': 'Frankfurt',
            'country': 'DE',
            'source': 'Mobile.de',
            'source_url': 'https://www.mobile.de/offers/mercedes-benz-w124-250d-frankfurt',
            'title': 'Mercedes-Benz W124 250D',
            'description': 'Gepflegter W124',
            'image_url': ''
        },
        {
            'external_id': 'demo_mobile_4',
            'model': 'W124 300D',
            'year': 1987,
            'mileage': 95000,
            'price': 13995.00,
            'currency': 'EUR',
            'location': 'Herrenberg',
            'country': 'DE',
            'source': 'Mobile.de',
            'source_url': 'https://www.mobile.de/offers/mercedes-benz-w124-300d',
            'title': 'Mercedes-Benz 300D - Wenig KM',
            'description': 'Sehr gut erhaltener 300D',
            'image_url': ''
        },
        {
            'external_id': 'demo_mobile_5',
            'model': 'W124 300D Turbo',
            'year': 1991,
            'mileage': 213186,
            'price': 18990.00,
            'currency': 'EUR',
            'location': 'Lastrup',
            'country': 'DE',
            'source': 'Mobile.de',
            'source_url': 'https://www.mobile.de/offers/mercedes-benz-w124-300d-turbo',
            'title': 'Mercedes-Benz 300D Turbo',
            'description': 'Kraftvoller Turbo-Diesel',
            'image_url': ''
        },
    ]

    print("Populating database with demo data...")
    print(f"Adding {len(demo_ads)} advertisements...\n")

    for ad in demo_ads:
        success = db.add_advertisement(ad)
        if success:
            print(f"✓ Added: {ad['model']} ({ad['year']}) - {ad['location']} - €{ad['price']:.0f}")
        else:
            print(f"✗ Failed to add: {ad['model']}")

    # Log the scrape
    db.log_scrape(
        country='DEMO',
        source='Demo Data Generator',
        ads_found=len(demo_ads),
        ads_new=len(demo_ads),
        status='success'
    )

    print(f"\n✓ Demo data populated successfully!")
    print(f"Total ads in database: {len(db.get_active_advertisements())}")


if __name__ == '__main__':
    generate_demo_data()
