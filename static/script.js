// Global variables
let allListings = [];
let currentFilter = 'all';

// Country flags mapping
const countryFlags = {
    'NL': '🇳🇱',
    'DE': '🇩🇪',
    'BE': '🇧🇪',
    'FR': '🇫🇷',
    'PL': '🇵🇱',
    'CZ': '🇨🇿',
    'AT': '🇦🇹',
    'ES': '🇪🇸'
};

// Country names mapping
const countryNames = {
    'NL': 'Nederland',
    'DE': 'Duitsland',
    'BE': 'België',
    'FR': 'Frankrijk',
    'PL': 'Polen',
    'CZ': 'Tsjechië',
    'AT': 'Oostenrijk'
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setCurrentDate();
    loadStatistics();
    loadListings('all');
    setupFilterButtons();
});

// Set current date
function setCurrentDate() {
    const now = new Date();
    const dateString = now.toLocaleDateString('nl-NL', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    document.getElementById('current-date').textContent = dateString;
    document.getElementById('footer-date').textContent = now.toLocaleString('nl-NL');
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();

        if (data.success) {
            const stats = data.statistics;
            document.getElementById('total-ads').textContent = stats.total_active || 0;
            document.getElementById('nl-ads').textContent = stats.by_country?.NL || 0;
            document.getElementById('de-ads').textContent = stats.by_country?.DE || 0;

            if (stats.last_scrape) {
                const lastUpdate = new Date(stats.last_scrape + 'Z');
                document.getElementById('last-update').textContent = lastUpdate.toLocaleTimeString('nl-NL', {
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZone: 'Europe/Amsterdam'
                });
            }
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Load listings
async function loadListings(country = 'all') {
    showLoading(true);

    try {
        let url = '/api/listings/top';

        if (country !== 'all') {
            url = `/api/listings?country=${country}&limit=50`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            allListings = data.listings;
            displayListings(allListings);
        }
    } catch (error) {
        console.error('Error loading listings:', error);
        showError('Er is een fout opgetreden bij het laden van de advertenties.');
    } finally {
        showLoading(false);
    }
}

// Display listings
function displayListings(listings) {
    // Clear all tables
    document.getElementById('w123-tbody').innerHTML = '';
    document.getElementById('w124-tbody').innerHTML = '';
    document.getElementById('all-tbody').innerHTML = '';

    // Hide all sections
    document.getElementById('w123-section').classList.add('hidden');
    document.getElementById('w124-section').classList.add('hidden');
    document.getElementById('all-section').classList.add('hidden');

    // Update section title based on filter (before empty check)
    const allSectionTitle = document.querySelector('#all-section h2');
    if (currentFilter === 'all') {
        allSectionTitle.textContent = 'Mercedes W123/W124 Diesel (Alle landen)';
    } else {
        const flag = countryFlags[currentFilter] || '';
        const countryName = countryNames[currentFilter] || '';
        if (countryName) {
            allSectionTitle.textContent = `${flag} Mercedes W123/W124 Diesel (${countryName})`;
        } else {
            allSectionTitle.textContent = `${flag} Mercedes W123/W124 Diesel`;
        }
    }

    if (!listings || listings.length === 0) {
        showEmptyState();
        return;
    }

    // Always use all-section for displaying listings
    document.getElementById('all-section').classList.remove('hidden');
    renderTable('all-tbody', listings);
}

// Render table
function renderTable(tbodyId, listings) {
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = '';

    listings.forEach(listing => {
        const row = createTableRow(listing);
        tbody.appendChild(row);
    });
}

// Create table row
function createTableRow(listing) {
    const tr = document.createElement('tr');

    // Model
    const modelCell = document.createElement('td');
    const modelBadge = document.createElement('span');
    modelBadge.className = `model-badge ${listing.model && listing.model.includes('W123') ? 'w123' : 'w124'}`;
    modelBadge.textContent = listing.model || 'Onbekend';
    modelCell.appendChild(modelBadge);
    tr.appendChild(modelCell);

    // Year
    const yearCell = document.createElement('td');
    if (listing.year) {
        const yearBadge = document.createElement('span');
        yearBadge.className = 'year-badge';
        if (listing.year <= 1986) {
            yearBadge.classList.add('oldtimer');
        }
        yearBadge.textContent = listing.year;
        yearCell.appendChild(yearBadge);
    } else {
        yearCell.textContent = '-';
    }
    tr.appendChild(yearCell);

    // Mileage
    const mileageCell = document.createElement('td');
    if (listing.mileage) {
        const mileageSpan = document.createElement('span');
        mileageSpan.className = 'mileage';
        if (listing.mileage < 100000) {
            mileageSpan.classList.add('low');
        } else if (listing.mileage > 300000) {
            mileageSpan.classList.add('high');
        }
        mileageSpan.textContent = formatNumber(listing.mileage) + ' km';
        mileageCell.appendChild(mileageSpan);
    } else {
        mileageCell.textContent = 'Onbekend';
    }
    tr.appendChild(mileageCell);

    // Price
    const priceCell = document.createElement('td');
    if (listing.price) {
        const priceSpan = document.createElement('span');
        priceSpan.className = 'price';
        if (listing.price < 5000) {
            priceSpan.classList.add('low');
        } else if (listing.price > 15000) {
            priceSpan.classList.add('expensive');
        } else {
            priceSpan.classList.add('moderate');
        }
        priceSpan.textContent = '€' + formatNumber(listing.price);
        priceCell.appendChild(priceSpan);
    } else {
        priceCell.textContent = 'Op aanvraag';
    }
    tr.appendChild(priceCell);

    // Location
    const locationCell = document.createElement('td');
    const flag = countryFlags[listing.country] || '';
    locationCell.innerHTML = `${flag} ${listing.location || listing.country || 'Onbekend'}`;
    tr.appendChild(locationCell);

    // Source
    const sourceCell = document.createElement('td');
    sourceCell.textContent = listing.source || 'Onbekend';
    tr.appendChild(sourceCell);

    // Link
    const linkCell = document.createElement('td');
    const link = document.createElement('a');
    link.href = listing.source_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Bekijk →';
    linkCell.appendChild(link);
    tr.appendChild(linkCell);

    return tr;
}

// Format number with thousand separators
function formatNumber(num) {
    if (!num) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Show loading
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.add('show');
    } else {
        loading.classList.remove('show');
    }
}

// Show empty state
function showEmptyState() {
    const allSection = document.getElementById('all-section');
    allSection.classList.remove('hidden');

    const tbody = document.getElementById('all-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="empty-state">
                <h3>Geen advertenties gevonden</h3>
                <p>Er zijn momenteel geen advertenties beschikbaar voor de geselecteerde filters.</p>
            </td>
        </tr>
    `;
}

// Show error
function showError(message) {
    const allSection = document.getElementById('all-section');
    allSection.classList.remove('hidden');

    const tbody = document.getElementById('all-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="empty-state">
                <h3>Error</h3>
                <p>${message}</p>
            </td>
        </tr>
    `;
}

// Setup filter buttons
function setupFilterButtons() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Get country
            const country = this.getAttribute('data-country');
            currentFilter = country;

            // Load listings
            loadListings(country);
        });
    });
}

// Auto-refresh every 5 minutes
setInterval(() => {
    loadStatistics();
    loadListings(currentFilter);
}, 5 * 60 * 1000);
