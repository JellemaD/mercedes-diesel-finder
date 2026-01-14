"""
Test script to perform a real scrape with actual URLs
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from scraper_manager import ScraperManager
from database import Database

def test_real_scrape():
    """Perform a real scrape to get actual working URLs"""

    print("="*60)
    print("REAL SCRAPE TEST - Getting actual Mercedes listings")
    print("="*60)
    print()

    print("⚠️  This will take 5-10 minutes and scrape real websites")
    print("Continue? (y/n): ", end='')

    response = input().lower()
    if response != 'y':
        print("Cancelled.")
        return

    print("\nStarting real scrape...")
    print("This may take a while. Please be patient.\n")

    # Clear old demo data
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM advertisements WHERE source IN ('Test', 'Demo Data Generator')")
    conn.commit()
    conn.close()
    print("✓ Cleared demo data\n")

    # Run scraper
    manager = ScraperManager()

    # Test with just Netherlands first (faster)
    print("Testing with Netherlands only (AutoScout24 and Marktplaats)...")
    ads = manager.scrape_country('NL')

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"Found {len(ads)} advertisements")

    if ads:
        print("\nFirst 5 ads with real URLs:")
        for i, ad in enumerate(ads[:5], 1):
            print(f"\n{i}. {ad['model']} ({ad['year']})")
            print(f"   Price: €{ad['price']}")
            print(f"   Location: {ad['location']}")
            print(f"   URL: {ad['source_url']}")
    else:
        print("\n⚠️  No ads found. This could be due to:")
        print("   - Website structure changes")
        print("   - Rate limiting")
        print("   - Connection issues")
        print("\nTry running again or check scrapers.py")

    # Check database
    active_ads = db.get_active_advertisements()
    print(f"\nTotal active ads in database: {len(active_ads)}")

    print("\n✓ Test complete!")
    print("\nStart web server to view:")
    print("  python main.py --web-only")
    print("  http://localhost:5000")

if __name__ == '__main__':
    test_real_scrape()
