"""
Mercedes W123 & W124 Diesel Finder
Main application entry point
"""

import argparse
import sys
from threading import Thread
from scheduler import DailyScheduler
from scraper_manager import ScraperManager
from web_app import app
import config


def run_scheduler():
    """Run the scheduler in a separate thread"""
    scheduler = DailyScheduler()
    scheduler.start()


def run_web_server():
    """Run the Flask web server"""
    print(f"\n{'='*70}")
    print("Starting Web Server...")
    print(f"Access the application at: http://localhost:{config.FLASK_PORT}")
    print(f"{'='*70}\n")

    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG_MODE, use_reloader=False)


def run_scraper_once():
    """Run the scraper once and exit"""
    print("Running scraper once...")
    manager = ScraperManager()
    manager.scrape_all()
    print("\nScraping completed!")


def main():
    parser = argparse.ArgumentParser(
        description='Mercedes W123 & W124 Diesel Finder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run both web server and scheduler
  python main.py --web-only         # Run only web server
  python main.py --scrape-only      # Run scraper once and exit
  python main.py --scheduler-only   # Run only scheduler (no web server)
        """
    )

    parser.add_argument(
        '--web-only',
        action='store_true',
        help='Run only the web server (no scheduler)'
    )

    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help='Run scraper once and exit'
    )

    parser.add_argument(
        '--scheduler-only',
        action='store_true',
        help='Run only the scheduler (no web server)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=config.FLASK_PORT,
        help=f'Port for web server (default: {config.FLASK_PORT})'
    )

    args = parser.parse_args()

    # Update config with port if specified
    if args.port:
        config.FLASK_PORT = args.port

    try:
        if args.scrape_only:
            # Just run scraper once
            run_scraper_once()

        elif args.web_only:
            # Just run web server
            run_web_server()

        elif args.scheduler_only:
            # Just run scheduler
            run_scheduler()

        else:
            # Run both web server and scheduler
            print(f"\n{'='*70}")
            print("Mercedes W123 & W124 Diesel Finder")
            print(f"{'='*70}")
            print("\nStarting application with:")
            print("  - Web Server (Flask)")
            print("  - Daily Scheduler (06:00)")
            print(f"\nWeb interface: http://localhost:{config.FLASK_PORT}")
            print("\nPress Ctrl+C to stop\n")

            # Start scheduler in separate thread
            scheduler_thread = Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()

            # Run web server in main thread
            run_web_server()

    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
