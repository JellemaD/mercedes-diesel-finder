import config
from database import Database
from scrapers import get_scraper
import time
from datetime import datetime

class ScraperManager:
    def __init__(self):
        self.db = Database()

    def scrape_all(self):
        """Scrape all configured marketplaces"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scrape session...")

        all_ads = []
        active_ids = []

        for country_code, country_data in config.MARKETPLACES.items():
            print(f"\n{'='*60}")
            print(f"Scraping {country_data['name']} ({country_code})")
            print(f"{'='*60}")

            for site_name, site_url in country_data['sites'].items():
                print(f"\nScraping {site_name}...")

                try:
                    ads = self.scrape_site(site_name, country_code)
                    all_ads.extend(ads)

                    # Save ads to database
                    new_count = 0
                    for ad in ads:
                        if self.db.add_advertisement(ad):
                            new_count += 1
                            active_ids.append(ad['external_id'])

                    print(f"  Found: {len(ads)} ads")
                    print(f"  New: {new_count} ads")

                    # Log scrape
                    self.db.log_scrape(
                        country=country_code,
                        source=site_name,
                        ads_found=len(ads),
                        ads_new=new_count,
                        status='success'
                    )

                except Exception as e:
                    print(f"  Error scraping {site_name}: {e}")
                    self.db.log_scrape(
                        country=country_code,
                        source=site_name,
                        ads_found=0,
                        ads_new=0,
                        status=f'error: {str(e)}'
                    )

                # Delay between sites
                time.sleep(config.REQUEST_DELAY * 2)

        # Mark inactive ads
        if active_ids:
            # self.db.mark_inactive_ads(active_ids)  # DISABLED: keep old ads

        print(f"\n{'='*60}")
        print(f"Scrape session completed")
        print(f"Total ads found: {len(all_ads)}")
        print(f"{'='*60}\n")

        return all_ads

    def scrape_site(self, site_name, country_code):
        """Scrape a specific site for all models"""
        scraper = get_scraper(site_name, country_code.lower())

        if not scraper:
            print(f"  No scraper available for {site_name}")
            return []

        all_results = []

        # Scrape for each model
        for model in config.MODELS:
            try:
                print(f"  Searching for {model}...")
                results = scraper.scrape(model)

                # Filter by year
                filtered = [
                    ad for ad in results
                    if ad.get('year') and config.YEAR_FROM <= ad.get('year') <= config.YEAR_TO
                ]

                all_results.extend(filtered)
                print(f"    Found {len(filtered)} ads for {model}")

            except Exception as e:
                print(f"    Error scraping {model}: {e}")

        return all_results

    def scrape_country(self, country_code):
        """Scrape only a specific country"""
        country_data = config.MARKETPLACES.get(country_code.upper())

        if not country_data:
            print(f"Country {country_code} not configured")
            return []

        print(f"Scraping {country_data['name']}...")

        all_ads = []
        for site_name in country_data['sites'].keys():
            try:
                ads = self.scrape_site(site_name, country_code)
                all_ads.extend(ads)

                # Save to database
                for ad in ads:
                    self.db.add_advertisement(ad)

            except Exception as e:
                print(f"Error scraping {site_name}: {e}")

        return all_ads

    def get_statistics(self):
        """Get current statistics"""
        return self.db.get_statistics()


if __name__ == '__main__':
    # Test the scraper
    manager = ScraperManager()
    manager.scrape_all()
