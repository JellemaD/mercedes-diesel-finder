#!/usr/bin/env python3
"""
Unified Mercedes Diesel Scraper
Combines:
- Marktplaats scraper (scrapers.py) with W201 support
- Extra sources (scrape_extra_sources.py) for AutoScout24, eBay, etc.

This ensures ALL sources are scraped in one run.
"""

import sys
from datetime import datetime
from database import Database
import config

def main():
    print("="*80)
    print("  UNIFIED MERCEDES DIESEL SCRAPER")
    print("  190/200 Series Diesel (1979-1986)")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Models: {config.MODELS}")
    print(f"Year range: {config.YEAR_FROM}-{config.YEAR_TO}")
    print()

    db = Database()
    all_results = []

    # ========================================================================
    # PART 1: Marktplaats Scraper (with W123, W124, W201 support)
    # ========================================================================
    print("\n" + "="*80)
    print("PART 1: MARKTPLAATS SCRAPER (W123, W124, W201)")
    print("="*80)

    try:
        from scrapers import MarktplaatsScraper

        scraper = MarktplaatsScraper()

        for model in config.MODELS:
            print(f"\n{'='*60}")
            print(f"Scraping Marktplaats for {model}")
            print(f"{'='*60}")

            try:
                results = scraper.scrape(model)

                # Filter by year range
                filtered = [
                    ad for ad in results
                    if ad.get('year') is None or (config.YEAR_FROM <= ad.get('year') <= config.YEAR_TO)
                ]

                print(f"Total found: {len(results)}")
                print(f"After year filter ({config.YEAR_FROM}-{config.YEAR_TO}): {len(filtered)}")

                all_results.extend(filtered)

                # Reset for next model
                scraper.results = []

            except Exception as e:
                print(f"Error scraping {model}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\nMarktplaats total: {len(all_results)} ads")

    except Exception as e:
        print(f"Error loading Marktplaats scraper: {e}")
        import traceback
        traceback.print_exc()

    # ========================================================================
    # PART 2: Extra Sources (AutoScout24, eBay, AutoWereld, etc.)
    # ========================================================================
    print("\n" + "="*80)
    print("PART 2: EXTRA SOURCES (AutoScout24, eBay, AutoWereld, etc.)")
    print("="*80)

    try:
        # Import functions from scrape_extra_sources
        from scrape_extra_sources import (
            scrape_autoscout24_json,
            scrape_ebay_motors,
            scrape_gaspedaal,
            scrape_2dehands,
            scrape_autotrack,
            scrape_autowereld
        )

        # AutoScout24 (Germany)
        print("\n--- AutoScout24.de ---")
        try:
            results = scrape_autoscout24_json(country='de')
            all_results.extend(results)
            print(f"Added {len(results)} ads from AutoScout24.de")
        except Exception as e:
            print(f"Error: {e}")

        # eBay Motors
        print("\n--- eBay Motors ---")
        try:
            results = scrape_ebay_motors()
            all_results.extend(results)
            print(f"Added {len(results)} ads from eBay Motors")
        except Exception as e:
            print(f"Error: {e}")

        # Gaspedaal.nl
        print("\n--- Gaspedaal.nl ---")
        try:
            results = scrape_gaspedaal()
            all_results.extend(results)
            print(f"Added {len(results)} ads from Gaspedaal.nl")
        except Exception as e:
            print(f"Error: {e}")

        # 2dehands.be (Selenium)
        print("\n--- 2dehands.be ---")
        try:
            results = scrape_2dehands()
            all_results.extend(results)
            print(f"Added {len(results)} ads from 2dehands.be")
        except Exception as e:
            print(f"Error: {e}")

        # AutoTrack.nl
        print("\n--- AutoTrack.nl ---")
        try:
            results = scrape_autotrack()
            all_results.extend(results)
            print(f"Added {len(results)} ads from AutoTrack.nl")
        except Exception as e:
            print(f"Error: {e}")

        # AutoWereld.nl
        print("\n--- AutoWereld.nl ---")
        try:
            results = scrape_autowereld()
            all_results.extend(results)
            print(f"Added {len(results)} ads from AutoWereld.nl")
        except Exception as e:
            print(f"Error: {e}")

    except ImportError as e:
        print(f"Could not import extra sources: {e}")
        print("Continuing with Marktplaats results only...")
    except Exception as e:
        print(f"Error with extra sources: {e}")
        import traceback
        traceback.print_exc()

    # ========================================================================
    # PART 3: Save to Database
    # ========================================================================
    print("\n" + "="*80)
    print("SAVING TO DATABASE")
    print("="*80)

    saved_count = 0
    error_count = 0

    for ad in all_results:
        try:
            if db.add_advertisement(ad):
                saved_count += 1
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Only show first 5 errors
                print(f"Error saving ad: {e}")

    print(f"\nTotal ads scraped: {len(all_results)}")
    print(f"Successfully saved: {saved_count}")
    print(f"Errors: {error_count}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    stats = db.get_statistics()

    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    print(f"Total active ads (1979-1986): {stats['total_active']}")
    print(f"By country: {stats['by_country']}")
    print(f"Last update: {stats['last_scrape']}")
    print()
    print("="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # NOTE: We do NOT call mark_inactive_ads() to preserve old listings
    # This allows us to accumulate ads over time without losing old ones

if __name__ == '__main__':
    main()
