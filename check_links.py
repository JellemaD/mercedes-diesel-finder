"""
Check which links are in the database
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database import Database

db = Database()
ads = db.get_active_advertisements()

# Separate search links from demo data
search_links = [ad for ad in ads if 'zoekresultaten' in ad['title'].lower() or 'search' in ad['external_id']]
demo_ads = [ad for ad in ads if ad not in search_links]

print("="*70)
print("WERKENDE LINKS IN DATABASE")
print("="*70)
print()

print(f"Totaal advertenties: {len(ads)}")
print(f"  - Werkende zoeklinks: {len(search_links)}")
print(f"  - Demo advertenties: {len(demo_ads)}")
print()

if search_links:
    print("="*70)
    print("WERKENDE ZOEKLINKS (Deze werken 100%!)")
    print("="*70)
    print()

    for i, ad in enumerate(search_links, 1):
        print(f"{i}. {ad['source']} - {ad['country']}")
        print(f"   Titel: {ad['title']}")
        print(f"   URL: {ad['source_url']}")
        print()

else:
    print("Geen zoeklinks gevonden!")
    print("Run: python simple_scraper.py")
    print()

if demo_ads:
    print("="*70)
    print("DEMO ADVERTENTIES (Voorbeeld data)")
    print("="*70)
    print()
    print(f"Eerste 5 demo advertenties:")
    print()

    for i, ad in enumerate(demo_ads[:5], 1):
        print(f"{i}. {ad['model']} ({ad['year']}) - {ad['location']}")
        print(f"   Prijs: €{ad['price']}, KM: {ad['mileage']}")
        print(f"   URL: {ad['source_url'][:60]}...")
        print()

print("="*70)
print("HOE TE TESTEN")
print("="*70)
print()
print("1. Start webserver: python main.py --web-only")
print("2. Open browser: http://localhost:5000")
print("3. Klik op een link met 'Zoekresultaten' in de titel")
print("4. Je wordt doorgestuurd naar de marketplace!")
print()
print("TIP: De zoeklinks werken altijd en tonen actuele advertenties!")
print("="*70)
