# Deployment Guide - PythonAnywhere

## 📦 Huidige Versie Status

**Master Branch (Nieuw):**
- Models: W123, W124, W201 (190/200 serie)
- Jaar: 1979-1986
- Commit: 473ffb6

**Backup (Oud):**
- Tag: `v1.0-pythonanywhere-backup`
- Models: W123, W124
- Jaar: 1975-1996
- Commit: 4e3fddf

---

## 🚀 Deployment Naar PythonAnywhere

### Stap 1: Login op PythonAnywhere
```
https://www.pythonanywhere.com
```

### Stap 2: Open Bash Console
Ga naar: **Consoles** → **Start new bash console**

### Stap 3: Backup Huidige Database
```bash
cd ~/mercedes-diesel-finder
cp mercedes_diesel.db mercedes_diesel.db.backup_$(date +%Y%m%d)
```

### Stap 4: Pull Nieuwe Code
```bash
cd ~/mercedes-diesel-finder
git fetch --all --tags
git pull origin master
```

### Stap 5: Verwijder __pycache__
```bash
cd ~/mercedes-diesel-finder
find . -type d -name '__pycache__' -exec rm -rf {} +
```

### Stap 6: Reload Web App
Ga naar: **Web** tab → **Reload** button (groene knop rechtsboven)

### Stap 7: Run Initial Scrape (optioneel)
```bash
cd ~/mercedes-finder
python3 scraper_manager.py
```

---

## 🔄 Terug Rollen Naar Oude Versie

Als je terug wilt naar de oude versie (1975-1996, W123/W124 only):

### Via Tag:
```bash
cd ~/mercedes-diesel-finder
git checkout v1.0-pythonanywhere-backup
find . -type d -name '__pycache__' -exec rm -rf {} +
```

Dan **Reload Web App** in PythonAnywhere Web tab.

### Database Terugzetten:
```bash
cd ~/mercedes-diesel-finder
cp mercedes_diesel.db.backup_YYYYMMDD mercedes_diesel.db
```

---

## 🔍 Verificatie

### Check Versie:
```bash
cd ~/mercedes-diesel-finder
git log --oneline -1
python3 -c "import config; print(f'Year: {config.YEAR_FROM}-{config.YEAR_TO}, Models: {config.MODELS}')"
```

### Check Database Stats:
```bash
python3 -c "from database import Database; db = Database(); print(db.get_statistics())"
```

---

## 📋 Belangrijke Verschillen

| Aspect | Oude Versie | Nieuwe Versie |
|--------|-------------|---------------|
| Models | W123, W124 | W123, W124, **W201** |
| Jaren | 1975-1996 | **1979-1986** |
| Marktplaats | Oude HTML | **Nieuwe HTML** (hz-Listing) |
| Zoektermen | 1-2 per model | **14-16 per model** |
| W201 Support | ❌ | ✅ 190D, 190D 2.0, 190D 2.5 |
| Mileage Bug | Overflow errors | ✅ Gefixt |

---

## ⚠️ BELANGRIJK

1. **Maak altijd een database backup** voor je update!
2. **Verwijder __pycache__** na git checkout/pull
3. **Reload de web app** via PythonAnywhere dashboard
4. Test de site na deployment: check of advertenties laden

---

## 🆘 Troubleshooting

**Probleem:** Site toont oude data
**Oplossing:** Run scraper handmatig: `cd ~/mercedes-diesel-finder && python3 scraper_manager.py`

**Probleem:** Import errors
**Oplossing:** `find . -type d -name '__pycache__' -exec rm -rf {} +`

**Probleem:** Database errors
**Oplossing:** Restore backup: `cp mercedes_diesel.db.backup_YYYYMMDD mercedes_diesel.db`

---

## 📞 Quick Commands

**Update naar nieuwe versie:**
```bash
cd ~/mercedes-diesel-finder && git pull origin master && find . -type d -name '__pycache__' -exec rm -rf {} +
```

**Rollback naar oude versie:**
```bash
cd ~/mercedes-diesel-finder && git checkout v1.0-pythonanywhere-backup && find . -type d -name '__pycache__' -exec rm -rf {} +
```

**Terug naar master:**
```bash
cd ~/mercedes-diesel-finder && git checkout master && find . -type d -name '__pycache__' -exec rm -rf {} +
```
