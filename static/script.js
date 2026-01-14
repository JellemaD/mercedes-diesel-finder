// Global variables
let allListings = [];
let currentFilter = 'all';
let currentSort = { column: null, direction: 'asc' };

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

// Detect car type from title/description
function detectCarType(listing) {
    const text = ((listing.title || '') + ' ' + (listing.description || '') + ' ' + (listing.model || '')).toLowerCase();

    // Station wagon / Combi
    if (/combi|estate|t-model|t-modell|break|touring|stationwagen|station|wagon|s123|s124|200t|250t|300t|200 t|250 t|300 t|t\s*diesel|td\b/.test(text)) {
        return 'Station';
    }
    // Cabrio / Convertible
    if (/cabrio|cabriolet|convertible|roadster/.test(text)) {
        return 'Cabrio';
    }
    // Coupe
    if (/coup[eé]|coupe/.test(text)) {
        return 'Coupé';
    }
    // Limousine / Sedan (default for W123/W124)
    if (/limousine|sedan|saloon|limo/.test(text)) {
        return 'Sedan';
    }
    // Default
    return 'Sedan';
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setCurrentDate();
    loadStatistics();
    loadListings('all');
    setupFilterButtons();
    setupSortableHeaders();
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
    if (currentFilter === 'hot') {
        allSectionTitle.textContent = '🔥 Hot: Stationwagen + Automaat + Trekhaak';
    } else if (currentFilter === '5-6cyl') {
        allSectionTitle.textContent = '⚙️ 5/6 Cilinder Diesels (1985-1987)';
    } else if (currentFilter === 'all') {
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

    // Sort by date_added (newest first) by default
    allListings = [...listings].sort((a, b) => {
        const dateA = a.date_added ? new Date(a.date_added).getTime() : 0;
        const dateB = b.date_added ? new Date(b.date_added).getTime() : 0;
        return dateB - dateA; // Descending (newest first)
    });

    // Set initial sort state
    currentSort = { column: 'date_added', direction: 'desc' };

    // Always use all-section for displaying listings
    document.getElementById('all-section').classList.remove('hidden');
    renderTable('all-tbody', allListings);

    // Update sort indicators
    updateSortIndicators();
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

    // Type
    const typeCell = document.createElement('td');
    const carType = detectCarType(listing);
    const typeBadge = document.createElement('span');
    typeBadge.className = `type-badge ${carType.toLowerCase()}`;
    typeBadge.textContent = carType;
    typeCell.appendChild(typeBadge);
    tr.appendChild(typeCell);

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

    // Date Added
    const dateCell = document.createElement('td');
    if (listing.date_added) {
        try {
            const date = new Date(listing.date_added);
            const dateStr = date.toLocaleDateString('nl-NL', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
            dateCell.textContent = dateStr;
            dateCell.className = 'date-cell';
        } catch (e) {
            dateCell.textContent = '-';
        }
    } else {
        dateCell.textContent = '-';
    }
    tr.appendChild(dateCell);

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
            <td colspan="9" class="empty-state">
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
            <td colspan="9" class="empty-state">
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

            // Check if Hot filter
            const filterType = this.getAttribute('data-filter');
            if (filterType === 'hot') {
                currentFilter = 'hot';
                loadHotListings();
                return;
            }

            // Check if 5/6 Cylinder filter
            if (filterType === '5-6cyl') {
                currentFilter = '5-6cyl';
                load56CylinderListings();
                return;
            }

            // Get country
            const country = this.getAttribute('data-country');
            currentFilter = country;

            // Load listings
            loadListings(country);
        });
    });
}

// Load Hot listings (stationwagen + automaat + trekhaak)
async function loadHotListings() {
    showLoading(true);

    try {
        // Load all listings first
        const response = await fetch('/api/listings/top?limit=500');
        const data = await response.json();

        if (data.success) {
            // Filter for Hot criteria
            const hotListings = data.listings.filter(listing => {
                const text = ((listing.title || '') + ' ' + (listing.description || '') + ' ' + (listing.model || '')).toLowerCase();

                // Check for station wagon (stationwagen/combi/estate/T-model/break/touring)
                const isStationWagon = /combi|estate|t-model|t-modell|break|touring|stationwagen|station|wagon|s123|s124|200t|250t|300t|200 t|250 t|300 t/.test(text);

                // Check for automatic transmission
                const isAutomatic = /automaat|automatic|automatik|automatisch|auto\s*matic/.test(text);

                // Check for tow bar
                const hasTowBar = /trekhaak|anhängerkupplung|ahk|towbar|tow bar|attelage/.test(text);

                return isStationWagon && isAutomatic && hasTowBar;
            });

            allListings = hotListings;

            // Update section title
            const allSectionTitle = document.querySelector('#all-section h2');
            allSectionTitle.textContent = '🔥 Hot: Stationwagen + Automaat + Trekhaak';

            displayListings(hotListings);
        }
    } catch (error) {
        console.error('Error loading hot listings:', error);
        showError('Er is een fout opgetreden bij het laden van de Hot advertenties.');
    } finally {
        showLoading(false);
    }
}

// Load 5/6 Cylinder listings (1985-1987)
async function load56CylinderListings() {
    showLoading(true);

    try {
        // Load all listings first
        const response = await fetch('/api/listings/top?limit=500');
        const data = await response.json();

        if (data.success) {
            // Filter for 5/6 cylinder criteria
            const filtered = data.listings.filter(listing => {
                const text = ((listing.title || '') + ' ' + (listing.description || '') + ' ' + (listing.model || '')).toLowerCase();
                const year = listing.year;

                // Check year range (1985-1987)
                if (!year || year < 1985 || year > 1987) {
                    return false;
                }

                // Check for 5 or 6 cylinder models
                // W123: 300D/300TD/300CD = 5 cylinder (OM617)
                // W124: 300D/300TD = 6 cylinder (OM603), 250D/250TD = 5 cylinder (OM602)
                const is56Cylinder = /300d|300td|300cd|300 d|300 td|300 cd|250d|250td|250 d|250 td|om617|om603|om602|5.*cylinder|6.*cylinder|5.*zylinder|6.*zylinder/.test(text);

                return is56Cylinder;
            });

            allListings = filtered;

            // Update section title
            const allSectionTitle = document.querySelector('#all-section h2');
            allSectionTitle.textContent = '⚙️ 5/6 Cilinder Diesels (1985-1987)';

            displayListings(filtered);
        }
    } catch (error) {
        console.error('Error loading 5/6 cylinder listings:', error);
        showError('Er is een fout opgetreden bij het laden van de 5/6 cilinder advertenties.');
    } finally {
        showLoading(false);
    }
}

// Auto-refresh every 5 minutes
setInterval(() => {
    loadStatistics();
    if (currentFilter === 'hot') {
        loadHotListings();
    } else if (currentFilter === '5-6cyl') {
        load56CylinderListings();
    } else {
        loadListings(currentFilter);
    }
}, 5 * 60 * 1000);

// Setup sortable headers
function setupSortableHeaders() {
    const headers = document.querySelectorAll('#all-table thead th');
    const columnMap = ['model', 'type', 'year', 'mileage', 'price', 'location', 'source', 'date_added', 'link'];

    headers.forEach((th, index) => {
        if (columnMap[index] === 'link') return; // Don't sort link column

        th.style.cursor = 'pointer';
        th.setAttribute('data-column', columnMap[index]);
        th.addEventListener('click', function() {
            const column = this.getAttribute('data-column');
            sortByColumn(column);
        });
    });
}

// Sort by column
function sortByColumn(column) {
    // Toggle direction if same column
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }

    // Sort the listings
    const sorted = [...allListings].sort((a, b) => {
        let valA, valB;

        switch (column) {
            case 'model':
                valA = (a.model || '').toLowerCase();
                valB = (b.model || '').toLowerCase();
                break;
            case 'type':
                valA = detectCarType(a).toLowerCase();
                valB = detectCarType(b).toLowerCase();
                break;
            case 'year':
                valA = a.year || 0;
                valB = b.year || 0;
                break;
            case 'date_added':
                valA = a.date_added ? new Date(a.date_added).getTime() : 0;
                valB = b.date_added ? new Date(b.date_added).getTime() : 0;
                break;
            case 'mileage':
                valA = a.mileage || 999999999;
                valB = b.mileage || 999999999;
                break;
            case 'price':
                valA = a.price || 999999999;
                valB = b.price || 999999999;
                break;
            case 'location':
                valA = (a.location || a.country || '').toLowerCase();
                valB = (b.location || b.country || '').toLowerCase();
                break;
            case 'source':
                valA = (a.source || '').toLowerCase();
                valB = (b.source || '').toLowerCase();
                break;
            default:
                return 0;
        }

        if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
        if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });

    // Update header indicators
    updateSortIndicators();

    // Re-render the table
    renderTable('all-tbody', sorted);
}

// Update sort indicators in headers
function updateSortIndicators() {
    const headers = document.querySelectorAll('#all-table thead th');

    headers.forEach(th => {
        const column = th.getAttribute('data-column');
        // Remove existing indicators
        th.textContent = th.textContent.replace(/ ▲| ▼/g, '');

        if (column === currentSort.column) {
            th.textContent += currentSort.direction === 'asc' ? ' ▲' : ' ▼';
        }
    });
}
