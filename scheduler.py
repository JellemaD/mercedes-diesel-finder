import schedule
import time
from datetime import datetime
from scraper_manager import ScraperManager
import config

class DailyScheduler:
    def __init__(self):
        self.scraper_manager = ScraperManager()

    def run_daily_scrape(self):
        """Run the daily scraping job"""
        print(f"\n{'='*70}")
        print(f"DAILY SCRAPE STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        try:
            # Run the scraper
            self.scraper_manager.scrape_all()

            # Print statistics
            stats = self.scraper_manager.get_statistics()
            print(f"\nCurrent Statistics:")
            print(f"  Total active ads: {stats.get('total_active', 0)}")
            print(f"  By country:")
            for country, count in stats.get('by_country', {}).items():
                print(f"    {country}: {count}")
            print(f"  Last scrape: {stats.get('last_scrape', 'Never')}")

            print(f"\n{'='*70}")
            print(f"DAILY SCRAPE COMPLETED")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n{'='*70}")
            print(f"ERROR DURING DAILY SCRAPE: {e}")
            print(f"{'='*70}\n")

    def start(self):
        """Start the scheduler"""
        print(f"Scheduler started. Daily scraping scheduled at {config.UPDATE_TIME}")
        print(f"Next run: Today at {config.UPDATE_TIME}")
        print("Press Ctrl+C to stop\n")

        # Schedule the job
        schedule.every().day.at(config.UPDATE_TIME).do(self.run_daily_scrape)

        # Run immediately on start (optional - comment out if not needed)
        # print("Running initial scrape...")
        # self.run_daily_scrape()

        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")


if __name__ == '__main__':
    scheduler = DailyScheduler()
    scheduler.start()
