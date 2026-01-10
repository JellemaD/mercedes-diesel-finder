from flask import Flask, render_template, jsonify, request
from database import Database
import config
from datetime import datetime, timedelta
import threading
import subprocess
import sys
import os

app = Flask(__name__)
db = Database()

# Scheduler status
scheduler_status = {
    'last_scrape': None,
    'next_scrape': None,
    'is_running': False,
    'last_result': None
}


def run_scrapers():
    """Run all scrapers to fetch new advertisements"""
    global scheduler_status

    if scheduler_status['is_running']:
        print("[Scheduler] Scrape already running, skipping...")
        return

    scheduler_status['is_running'] = True
    scheduler_status['last_scrape'] = datetime.now().isoformat()

    print(f"[Scheduler] Starting scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Run the scrapers
        scrapers = ['fetch_real_data.py', 'scrape_extra_sources.py']

        for scraper in scrapers:
            scraper_path = os.path.join(script_dir, scraper)
            if os.path.exists(scraper_path):
                print(f"[Scheduler] Running {scraper}...")
                result = subprocess.run(
                    [sys.executable, scraper_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per scraper
                )
                if result.returncode == 0:
                    print(f"[Scheduler] {scraper} completed successfully")
                else:
                    print(f"[Scheduler] {scraper} failed: {result.stderr[:200]}")

        scheduler_status['last_result'] = 'success'
        print(f"[Scheduler] Scrape completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        scheduler_status['last_result'] = f'error: {str(e)}'
        print(f"[Scheduler] Scrape failed: {e}")

    finally:
        scheduler_status['is_running'] = False


def should_scrape_on_startup():
    """Check if we should scrape on startup (last scrape > 24 hours ago)"""
    stats = db.get_statistics()
    last_scrape = stats.get('last_scrape')

    if not last_scrape:
        return True

    try:
        # Parse the last scrape time
        last_scrape_dt = datetime.fromisoformat(last_scrape.replace('Z', ''))
        hours_since = (datetime.now() - last_scrape_dt).total_seconds() / 3600

        print(f"[Scheduler] Last scrape was {hours_since:.1f} hours ago")
        return hours_since >= 24
    except:
        return True


def start_scheduler():
    """Start the background scheduler"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler(daemon=True)

    # Schedule daily scrape at 06:00
    scheduler.add_job(
        run_scrapers,
        CronTrigger(hour=6, minute=0),
        id='daily_scrape',
        name='Daily advertisement scrape',
        replace_existing=True
    )

    scheduler.start()

    # Calculate next run time
    next_run = scheduler.get_job('daily_scrape').next_run_time
    scheduler_status['next_scrape'] = next_run.isoformat() if next_run else None

    print(f"[Scheduler] Started. Next scrape scheduled for: {next_run}")

    # Check if we should scrape immediately
    if should_scrape_on_startup():
        print("[Scheduler] Last scrape was more than 24 hours ago, starting immediate scrape...")
        # Run in background thread to not block app startup
        thread = threading.Thread(target=run_scrapers, daemon=True)
        thread.start()

    return scheduler


@app.route('/')
def index():
    """Main page showing all listings"""
    return render_template('index.html')


@app.route('/api/listings')
def get_listings():
    """API endpoint to get listings with optional filtering"""
    country = request.args.get('country')
    limit = request.args.get('limit', 100, type=int)

    if country:
        listings = db.get_country_top_listings(country, limit)
    else:
        listings = db.get_top_listings(limit)

    return jsonify({
        'success': True,
        'count': len(listings),
        'listings': listings
    })


@app.route('/api/listings/top')
def get_top_listings():
    """Get top 100 listings overall"""
    listings = db.get_top_listings(100)
    return jsonify({
        'success': True,
        'count': len(listings),
        'listings': listings
    })


@app.route('/api/listings/nl')
def get_nl_listings():
    """Get top 50 listings from Netherlands"""
    listings = db.get_country_top_listings('NL', 50)
    return jsonify({
        'success': True,
        'country': 'Nederland',
        'count': len(listings),
        'listings': listings
    })


@app.route('/api/listings/de')
def get_de_listings():
    """Get top 50 listings from Germany"""
    listings = db.get_country_top_listings('DE', 50)
    return jsonify({
        'success': True,
        'country': 'Duitsland',
        'count': len(listings),
        'listings': listings
    })


@app.route('/api/statistics')
def get_statistics():
    """Get statistics about the database"""
    stats = db.get_statistics()
    return jsonify({
        'success': True,
        'statistics': stats
    })


@app.route('/api/scheduler')
def get_scheduler_status():
    """Get scheduler status"""
    return jsonify({
        'success': True,
        'scheduler': scheduler_status
    })


@app.route('/api/scrape/now', methods=['POST'])
def trigger_scrape():
    """Manually trigger a scrape"""
    if scheduler_status['is_running']:
        return jsonify({
            'success': False,
            'message': 'Scrape is already running'
        })

    # Run in background
    thread = threading.Thread(target=run_scrapers, daemon=True)
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Scrape started in background'
    })


@app.template_filter('format_price')
def format_price(price):
    """Format price with Euro symbol"""
    if price:
        return f"€{price:,.2f}".replace(',', '.')
    return "Prijs op aanvraag"


@app.template_filter('format_mileage')
def format_mileage(mileage):
    """Format mileage with km"""
    if mileage:
        return f"{mileage:,} km".replace(',', '.')
    return "Onbekend"


@app.template_filter('format_date')
def format_date(date_string):
    """Format date to readable format"""
    if date_string:
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%d-%m-%Y %H:%M')
        except:
            return date_string
    return "Onbekend"


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Starting Mercedes W123/W124 Diesel Finder")
    print("=" * 70)

    # Start the scheduler
    scheduler = start_scheduler()

    print(f"\nWeb server starting on http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("=" * 70 + "\n")

    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG_MODE)
