#!/bin/bash
# Deployment Script voor PythonAnywhere
# Mercedes 190/200 Series Diesel Finder (1979-1986)

echo "========================================================================"
echo "  Mercedes Diesel Finder - PythonAnywhere Deployment"
echo "========================================================================"
echo ""

# Stap 1: Navigeer naar project directory
echo "📁 Stap 1: Navigeren naar project directory..."
cd ~/mercedes-diesel-finder || { echo "❌ Directory niet gevonden!"; exit 1; }
echo "✅ In directory: $(pwd)"
echo ""

# Stap 2: Backup huidige database
echo "💾 Stap 2: Database backup maken..."
BACKUP_NAME="mercedes_diesel.db.backup_$(date +%Y%m%d_%H%M%S)"
if [ -f "mercedes_diesel.db" ]; then
    cp mercedes_diesel.db "$BACKUP_NAME"
    echo "✅ Backup gemaakt: $BACKUP_NAME"
else
    echo "⚠️  Geen database gevonden - nieuwe database wordt aangemaakt"
fi
echo ""

# Stap 3: Toon huidige versie
echo "📊 Stap 3: Huidige versie..."
echo "Current branch: $(git branch --show-current)"
echo "Current commit: $(git log --oneline -1)"
echo ""

# Stap 4: Pull nieuwe code
echo "⬇️  Stap 4: Nieuwe code ophalen..."
git fetch --all --tags
git pull origin master
echo "✅ Code geüpdatet naar: $(git log --oneline -1)"
echo ""

# Stap 5: Verwijder __pycache__
echo "🧹 Stap 5: Cache opschonen..."
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
echo "✅ __pycache__ folders verwijderd"
echo ""

# Stap 6: Check configuratie
echo "⚙️  Stap 6: Configuratie check..."
python3 << 'PYEOF'
import config
print(f"  Models: {config.MODELS}")
print(f"  Jaar range: {config.YEAR_FROM} - {config.YEAR_TO}")
print(f"  Database: {config.DB_PATH}")
print(f"  Fuel types: {config.FUEL_TYPES}")
PYEOF
echo ""

# Stap 7: Check database
echo "🗄️  Stap 7: Database check..."
python3 << 'PYEOF'
from database import Database
db = Database()
stats = db.get_statistics()
print(f"  Total active ads: {stats['total_active']}")
print(f"  By country: {stats['by_country']}")
print(f"  Last update: {stats['last_scrape']}")
PYEOF
echo ""

echo "========================================================================"
echo "  ✅ Deployment succesvol!"
echo "========================================================================"
echo ""
echo "⚠️  BELANGRIJK: Vergeet niet de Web App te reloaden!"
echo ""
echo "Ga naar: PythonAnywhere Dashboard → Web tab → klik RELOAD button"
echo ""
echo "📋 Backups gemaakt:"
echo "  - Database: $BACKUP_NAME"
echo "  - Git tag: v1.0-pythonanywhere-backup (oude versie)"
echo ""
echo "🔄 Rollback (als nodig):"
echo "  git checkout v1.0-pythonanywhere-backup"
echo "  find . -type d -name '__pycache__' -exec rm -rf {} +"
echo ""
echo "========================================================================"
