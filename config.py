# Configuration for Mercedes 190/200 Series Diesel Search

# Search parameters
MODELS = ['W123', 'W124', 'W201']  # W123 = 200-serie, W124 = 200-serie, W201 = 190-serie
FUEL_TYPES = ['Diesel']
YEAR_FROM = 1979
YEAR_TO = 1986

# Model variants to search for
MODEL_VARIANTS = {
    'W123': ['200D', '240D', '300D', '300TD', '300D Turbo'],
    'W124': ['200D', '250D', '250TD', '300D', '300TD', '300D Turbo', '250D Kombi'],
    'W201': ['190D', '190D 2.0', '190D 2.5']  # 190-serie diesel variants
}

# Countries and their marketplace URLs
MARKETPLACES = {
    'NL': {
        'name': 'Nederland',
        'sites': {
            'AutoScout24': 'https://www.autoscout24.nl',
            'Marktplaats': 'https://www.marktplaats.nl/l/auto-s'
        },
        'max_results': 50
    },
    'DE': {
        'name': 'Duitsland',
        'sites': {
            'AutoScout24': 'https://www.autoscout24.de',
            'Mobile.de': 'https://www.mobile.de',
            'Kleinanzeigen': 'https://www.kleinanzeigen.de/s-autos/c216'
        },
        'max_results': 50
    },
    'BE': {
        'name': 'België',
        'sites': {
            '2dehands': 'https://www.2dehands.be/l/auto-s',
            'AutoScout24': 'https://www.autoscout24.be'
        },
        'max_results': 100
    },
    'PL': {
        'name': 'Polen',
        'sites': {
            'Otomoto': 'https://www.otomoto.pl',
            'OLX': 'https://www.olx.pl/motoryzacja/samochody'
        },
        'max_results': 100
    },
    'CZ': {
        'name': 'Tsjechië',
        'sites': {
            'Sauto': 'https://www.sauto.cz'
        },
        'max_results': 100
    },
    'FR': {
        'name': 'Frankrijk',
        'sites': {
            'LeBonCoin': 'https://www.leboncoin.fr/voitures/offres'
        },
        'max_results': 100
    },
    'AT': {
        'name': 'Oostenrijk',
        'sites': {
            'Willhaben': 'https://www.willhaben.at/iad/gebrauchtwagen/auto'
        },
        'max_results': 100
    }
}

# Scraping configuration
UPDATE_TIME = "06:00"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # seconds between requests

# Database
DB_PATH = 'mercedes_diesel.db'

# Web server
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
DEBUG_MODE = False
