"""
Test script to verify the system setup
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")

    try:
        import requests
        print("✓ requests")
    except ImportError:
        print("✗ requests - Run: pip install requests")
        return False

    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4")
    except ImportError:
        print("✗ beautifulsoup4 - Run: pip install beautifulsoup4")
        return False

    try:
        import flask
        print("✓ flask")
    except ImportError:
        print("✗ flask - Run: pip install flask")
        return False

    try:
        import schedule
        print("✓ schedule")
    except ImportError:
        print("✗ schedule - Run: pip install schedule")
        return False

    try:
        from fake_useragent import UserAgent
        print("✓ fake-useragent")
    except ImportError:
        print("✗ fake-useragent - Run: pip install fake-useragent")
        return False

    return True


def test_database():
    """Test database initialization"""
    print("\nTesting database...")

    try:
        from database import Database
        db = Database()
        print("✓ Database initialized")

        # Test adding a dummy ad
        test_ad = {
            'external_id': 'test_123',
            'model': 'W123 300D',
            'year': 1985,
            'mileage': 150000,
            'price': 12500.00,
            'currency': 'EUR',
            'location': 'Amsterdam',
            'country': 'NL',
            'source': 'Test',
            'source_url': 'https://example.com',
            'title': 'Test Mercedes',
            'description': 'Test description',
            'image_url': ''
        }

        db.add_advertisement(test_ad)
        print("✓ Database write test passed")

        # Test reading
        ads = db.get_active_advertisements(limit=1)
        if ads:
            print(f"✓ Database read test passed ({len(ads)} ads found)")
        else:
            print("✓ Database read test passed (no ads yet)")

        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")

    try:
        import config
        print(f"✓ Update time: {config.UPDATE_TIME}")
        print(f"✓ Year range: {config.YEAR_FROM} - {config.YEAR_TO}")
        print(f"✓ Countries configured: {len(config.MARKETPLACES)}")
        print(f"✓ Flask port: {config.FLASK_PORT}")
        return True

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_scrapers():
    """Test scraper initialization"""
    print("\nTesting scrapers...")

    try:
        from scrapers import AutoScout24Scraper, MobileDeScraper, MarktplaatsScraper
        print("✓ Scraper modules loaded")

        # Test scraper initialization
        scraper = AutoScout24Scraper('nl')
        print("✓ AutoScout24 scraper initialized")

        scraper = MobileDeScraper()
        print("✓ Mobile.de scraper initialized")

        scraper = MarktplaatsScraper()
        print("✓ Marktplaats scraper initialized")

        return True

    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        return False


def test_web_app():
    """Test web application"""
    print("\nTesting web application...")

    try:
        from web_app import app
        print("✓ Flask app loaded")

        # Test if routes are registered
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        print(f"✓ {len(routes)} routes registered")

        return True

    except Exception as e:
        print(f"✗ Web app test failed: {e}")
        return False


def test_templates():
    """Test if templates exist"""
    print("\nTesting templates and static files...")

    templates_exist = os.path.exists('templates/index.html')
    css_exists = os.path.exists('static/style.css')
    js_exists = os.path.exists('static/script.js')

    if templates_exist:
        print("✓ HTML template found")
    else:
        print("✗ HTML template missing")

    if css_exists:
        print("✓ CSS file found")
    else:
        print("✗ CSS file missing")

    if js_exists:
        print("✓ JavaScript file found")
    else:
        print("✗ JavaScript file missing")

    return templates_exist and css_exists and js_exists


def main():
    """Run all tests"""
    print("="*60)
    print("Mercedes W123/W124 Diesel Finder - System Test")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Scrapers", test_scrapers),
        ("Web Application", test_web_app),
        ("Templates & Static Files", test_templates),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nTo start the application, run:")
        print("  python main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Check file permissions")
        print("  - Verify all files are present")
        return 1

    print("="*60)


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
