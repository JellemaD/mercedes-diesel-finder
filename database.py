import sqlite3
from datetime import datetime
import config

class Database:
    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advertisements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE,
                model TEXT NOT NULL,
                year INTEGER,
                mileage INTEGER,
                price REAL,
                currency TEXT DEFAULT 'EUR',
                location TEXT,
                country TEXT,
                source TEXT,
                source_url TEXT,
                title TEXT,
                description TEXT,
                image_url TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                country TEXT,
                source TEXT,
                ads_found INTEGER,
                ads_new INTEGER,
                status TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_advertisement(self, ad_data):
        """Add or update an advertisement"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO advertisements
                (external_id, model, year, mileage, price, currency, location,
                 country, source, source_url, title, description, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET
                    price = excluded.price,
                    mileage = excluded.mileage,
                    date_updated = CURRENT_TIMESTAMP,
                    is_active = 1
            ''', (
                ad_data.get('external_id'),
                ad_data.get('model'),
                ad_data.get('year'),
                ad_data.get('mileage'),
                ad_data.get('price'),
                ad_data.get('currency', 'EUR'),
                ad_data.get('location'),
                ad_data.get('country'),
                ad_data.get('source'),
                ad_data.get('source_url'),
                ad_data.get('title'),
                ad_data.get('description'),
                ad_data.get('image_url')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding advertisement: {e}")
            return False
        finally:
            conn.close()

    def get_active_advertisements(self, country=None, limit=None):
        """Get active advertisements, optionally filtered by country"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT * FROM advertisements
            WHERE is_active = 1
        '''
        params = []

        if country:
            query += ' AND country = ?'
            params.append(country)

        query += ' ORDER BY date_updated DESC'

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_top_listings(self, limit=500):
        """Get top listings sorted by date and relevance"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Only show 190/200 series diesels from 1979-1986
        # Price > 500 to filter out parts/junk
        # Sort by year DESC (newest first)
        cursor.execute('''
            SELECT * FROM advertisements
            WHERE is_active = 1
            AND external_id NOT LIKE 'search_%'
            AND (year IS NULL OR (year >= 1979 AND year <= 1986))
            AND (price IS NULL OR price > 500)
            ORDER BY year DESC, date_updated DESC
            LIMIT ?
        ''', (limit,))

        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_country_top_listings(self, country, limit=100):
        """Get top listings for a specific country"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Only show 190/200 series diesels from 1979-1986
        # Price > 500 to filter out parts/junk
        # Sort by year DESC (newest first)
        cursor.execute('''
            SELECT * FROM advertisements
            WHERE is_active = 1
            AND external_id NOT LIKE 'search_%'
            AND country = ?
            AND (year IS NULL OR (year >= 1979 AND year <= 1986))
            AND (price IS NULL OR price > 500)
            ORDER BY year DESC, date_updated DESC
            LIMIT ?
        ''', (country, limit))

        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def mark_inactive_ads(self, active_ids):
        """Mark ads as inactive if they're not in the active_ids list"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if active_ids:
            placeholders = ','.join('?' * len(active_ids))
            cursor.execute(f'''
                UPDATE advertisements
                SET is_active = 0
                WHERE external_id NOT IN ({placeholders})
            ''', active_ids)

        conn.commit()
        conn.close()

    def log_scrape(self, country, source, ads_found, ads_new, status='success'):
        """Log a scraping session"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO scrape_history
            (country, source, ads_found, ads_new, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (country, source, ads_found, ads_new, status))

        conn.commit()
        conn.close()

    def get_statistics(self):
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total active ads (190/200 series 1979-1986, price > 500, excluding search links)
        cursor.execute("""
            SELECT COUNT(*) FROM advertisements
            WHERE is_active = 1 AND external_id NOT LIKE 'search_%'
            AND (year IS NULL OR (year >= 1979 AND year <= 1986))
            AND (price IS NULL OR price > 500)
        """)
        stats['total_active'] = cursor.fetchone()[0]

        # Ads by country (190/200 series 1979-1986, price > 500)
        cursor.execute('''
            SELECT country, COUNT(*) as count
            FROM advertisements
            WHERE is_active = 1 AND external_id NOT LIKE 'search_%'
            AND (year IS NULL OR (year >= 1979 AND year <= 1986))
            AND (price IS NULL OR price > 500)
            GROUP BY country
        ''')
        stats['by_country'] = dict(cursor.fetchall())

        # Last update time (from advertisements table)
        cursor.execute('SELECT MAX(date_updated) FROM advertisements WHERE is_active = 1')
        last_update = cursor.fetchone()[0]
        stats['last_scrape'] = last_update

        conn.close()
        return stats
