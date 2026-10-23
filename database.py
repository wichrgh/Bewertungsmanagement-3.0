from nicegui import ui
import sqlite3
import os

DB_PATH = 'projekte.db'
IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'images')

def initialize_database():
    """Erstellt das relationale Schema mitsamt Status- und Qualitäts-Flags."""
    with sqlite3.connect(DB_PATH) as conn:
        
        # 1. Haupttabelle Artikel (inkl. Status-Flag für Verluste/Diebstahl)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Artikel (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ArtikelNummer TEXT NOT NULL UNIQUE,
                Bezeichnung TEXT NOT NULL,
                Beschreibung TEXT,
                BestellNummer TEXT NOT NULL UNIQUE,
                BestellPreis REAL NOT NULL CHECK(BestellPreis >= 0),
                BestellDatum TEXT NOT NULL,
                LieferDatum TEXT,
                HauptBild TEXT,
                Status INTEGER DEFAULT 1 -- 0=Bestellt, 1=Geliefert, 2=Verlust/Gestohlen
            )
        ''')
        
        # Spalten-Sicherheits-Bypass für bestehende DBs
        try: conn.execute("ALTER TABLE Artikel ADD COLUMN Status INTEGER DEFAULT 1")
        except sqlite3.OperationalError: pass

        # 2. Bewertungstabelle (inkl. Qualitäts-Flag für qualifizierte Berichte)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Bewertungen (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ArtikelID INTEGER NOT NULL UNIQUE,
                Sterne INTEGER NOT NULL CHECK(Sterne BETWEEN 1 AND 5),
                Titel TEXT NOT NULL,
                Rezension TEXT NOT NULL,
                Qualifiziert INTEGER DEFAULT 0,
                FOREIGN KEY (ArtikelID) REFERENCES Artikel(ID) ON DELETE CASCADE
            )
        ''')
        try: conn.execute("ALTER TABLE Bewertungen ADD COLUMN Qualifiziert INTEGER DEFAULT 0")
        except sqlite3.OperationalError: pass

        # 3. Lieferanten
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Lieferanten (
                ID PRIMARY KEY AUTOINCREMENT,
                LieferantName TEXT UNIQUE
            )
        ''')

        # 4. RewardProfile
        conn.execute('''
            CREATE TABLE IF NOT EXISTS RewardProfile (
                ID PRIMARY KEY AUTOINCREMENT,
                LieferantenID INTEGER, 
                ProfilName TEXT, 
                Vorgaben TEXT, 
                Beschreibung TEXT, 
                FOREIGN KEY(LieferantenID) REFERENCES Lieferanten(ID) ON DELETE CASCADE, 
                UNIQUE(LieferantenID, ProfilName)
            )
        ''')

        # 5. TestProfile
        conn.execute('''
            CREATE TABLE IF NOT EXISTS TestProfile (
                ID PRIMARY KEY AUTOINCREMENT, 
                LieferantenID INTEGER, 
                RewardProfilID INTEGER, 
                StartDatum TEXT, 
                EndDatum TEXT, 
                Konditionen TEXT, 
                FOREIGN KEY(LieferantenID) REFERENCES Lieferanten(ID) ON DELETE CASCADE, 
                FOREIGN KEY(RewardProfilID) REFERENCES RewardProfile(ID) ON DELETE RESTRICT
            )
        ''')

def hole_kaufmaennische_kpis():
    """Berechnet die finanziellen Gegenwerte und Verlustquoten für Ottos Performance."""
    with sqlite3.connect(DB_PATH) as conn:
        # Ertragsstatistiken über geschriebene Berichte
        SQL_WERTE = """
            SELECT 
                COUNT(b.ID) as anzahl_berichte,
                SUM(CASE WHEN b.Qualifiziert = 1 THEN 1 ELSE 0 END) as qualifiziert,
                AVG(a.BestellPreis) as avg_wert,
                MIN(a.BestellPreis) as min_wert,
                MAX(a.BestellPreis) as max_wert,
                SUM(a.BestellPreis) as gesamt_wert
            FROM Bewertungen b
            JOIN Artikel a ON b.ArtikelID = a.ID
        """
        res_werte = conn.execute(SQL_WERTE).fetchone()
        
        # Verluststatistiken über gestohlene/verlorene Pakete
        SQL_VERLUST = """
            SELECT COUNT(ID), SUM(BestellPreis) FROM Artikel WHERE Status = 2
        """
        res_verlust = conn.execute(SQL_VERLUST).fetchone()
        
        return {
            'berichte': res_werte[0] or 0,
            'qualifiziert': res_werte[1] or 0,
            'avg_preis': round(res_werte[2] or 0.0, 2),
            'min_preis': round(res_werte[3] or 0.0, 2),
            'max_preis': round(res_werte[4] or 0.0, 2),
            'gesamt_preis': round(res_werte[5] or 0.0, 2),
            'verlust_anzahl': res_verlust[0] or 0,
            'verlust_summe': round(res_verlust[1] or 0.0, 2)
        }

def hole_artikel(suche=''):
    """Lädt die Artikel für das linke DataGrid chronologisch sortiert nach ISO-Bestelldatum."""
    with sqlite3.connect(DB_PATH) as conn:
        if suche:
            cursor = conn.execute(
                'SELECT ID, ArtikelNummer, Bezeichnung, HauptBild, BestellDatum, LieferDatum FROM Artikel '
                'WHERE ArtikelNummer LIKE ? OR Bezeichnung LIKE ? '
                'ORDER BY BestellDatum DESC',
                (f'%{suche}%', f'%{suche}%')
            )
        else:
            cursor = conn.execute(
                'SELECT ID, ArtikelNummer, Bezeichnung, HauptBild, BestellDatum, LieferDatum FROM Artikel '
                'ORDER BY BestellDatum DESC'
            )
            
        artikel_liste = []
        for row in cursor.fetchall():
            db_id = row[0]
            art_num = row[1]
            bezeichnung = row[2]
            db_bild_name = row[3]
            db_iso_bdat = row[4]  # Reines ISO-Datum (JJJJ-MM-TT)
            db_iso_ldat = row[5]  # Reines ISO-Datum (JJJJ-MM-TT)
            
            # Konvertierung für die DataGrid-Anzeige (Ohne Altdaten-Fallback)
            p_b = db_iso_bdat.split('-')
            de_bdat = f"{p_b[2]}.{p_b[1]}.{p_b[0]}"
            
            de_ldat = ""
            if db_iso_ldat:
                p_l = db_iso_ldat.split('-')
                de_ldat = f"{p_l[2]}.{p_l[1]}.{p_l[0]}"

            web_bild_pfad = ''
            if db_bild_name:
                physischer_pfad = os.path.join(IMAGES_FOLDER, db_bild_name)
                if os.path.exists(physischer_pfad):
                    web_bild_pfad = f"/images/{db_bild_name}?v={int(os.path.getmtime(physischer_pfad))}"
                    
            artikel_liste.append({
                'id': db_id,
                'num_anzeige': art_num,
                'name': bezeichnung,
                'thumb': web_bild_pfad,
                'bdat_anzeige': de_bdat,
                'ldat_anzeige': de_ldat
            })
            
    return artikel_liste

def bereinige_verwaiste_bilder():
    """Vergleicht alle physischen Bilder auf der SSD mit der Datenbank und löscht Verwaiste."""
    if not os.path.exists(IMAGES_FOLDER):
        return
        
    with sqlite3.connect(DB_PATH) as conn:
        # Holt die reinen Text-Strings der Artikelnummern aus den SQL-Tupeln
        existierende_artikel = {str(row[0]).strip() for row in conn.execute('SELECT ArtikelNummer FROM Artikel').fetchall()}
        
    anzahl_geloescht = 0
    for datei in os.listdir(IMAGES_FOLDER):
        if "_supplier_" in datei:
            teile = datei.split('_supplier_')
            art_num_aus_datei = str(teile[0]).strip()
            
            # Befindet sich das Bild auf der Platte, aber die ID NICHT in der Datenbank -> Löschen!
            if art_num_aus_datei not in existierende_artikel:
                voll_pfad = os.path.join(IMAGES_FOLDER, datei)
                try:
                    os.remove(voll_pfad)
                    anzahl_geloescht += 1
                except Exception as e:
                    print(f"Fehler beim automatischen Loeschen von verwaister Datei {datei}: {e}")
                    
    if anzahl_geloescht > 0:
        print(f"[Garbage Collector] {anzahl_geloescht} verwaiste Datei(en) erfolgreich gelöscht.")

def hole_alle_lieferanten():
    """Holt alle Lieferanten als ID-Namens-Dictionary für die ComboBox."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT ID, LieferantName FROM Lieferanten ORDER BY LieferantName ASC")
        return {row[0]: row[1] for row in cursor.fetchall()}

def hole_reward_profile_fuer_lieferant(lieferant_id):
    """Holt ausschließlich die Reward-Profile eines ganz bestimmten Lieferanten."""
    if not lieferant_id: return {}
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT ID, ProfilName FROM RewardProfile WHERE LieferantenID = ? ORDER BY ProfilName ASC", 
            (lieferant_id,)
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

def hole_reward_profil_details(profil_id):
    """Holt die Vorgaben und Beschreibung anhand der stabilen Profil-ID."""
    if not profil_id: return None
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT Vorgaben, Beschreibung FROM RewardProfile WHERE ID = ?", (profil_id,))
        res = cursor.fetchone()
        return dict(vorgaben=res[0], beschreibung=res[1]) if res else None

def hole_heute_aktives_testprofil():
    """Sucht in der Historie nach einem Testprofil, das am heutigen Tag gültig ist."""
    with sqlite3.connect(DB_PATH) as conn:
        # date('now') zieht das heutige ISO-Datum (JJJJ-MM-TT) für den perfekten mathematischen Vergleich
        SQL = """
            SELECT tp.LieferantenID, l.LieferantName, tp.RewardProfilID, rp.ProfilName
            FROM TestProfile tp
            JOIN Lieferanten l ON tp.LieferantenID = l.ID
            JOIN RewardProfile rp ON tp.RewardProfilID = rp.ID
            WHERE date('now') BETWEEN date(tp.StartDatum) AND date(tp.EndDatum)
            LIMIT 1
        """
        cursor = conn.execute(SQL)
        res = cursor.fetchone()

        # Gibt die IDs und Namen als sauberes Wörterbuch zurück, falls vorhanden
        return dict(l_id=res[0], l_name=res[1], r_id=res[2], r_name=res[3]) if res else None

def lieferant_speichern(name):
    """Fügt einen neuen Lieferanten hinzu."""
    if not name.strip(): return False
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO Lieferanten (LieferantName) VALUES (?)", (name.strip(),))
        return True
    except sqlite3.IntegrityError:
        return "Dublette"

def lieferant_loeschen(lieferant_id):
    """Löscht einen Lieferanten (Kaskadiert automatisch auf RewardProfile!)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM Lieferanten WHERE ID = ?", (lieferant_id,))
        return True
    except Exception:
        return False

def reward_profil_speichern(lieferanten_id, profil_name, vorgaben, beschreibung):
    """Speichert ein neues Reward-Profil für einen Lieferanten."""
    if not lieferanten_id or not profil_name.strip(): return False
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO RewardProfile (LieferantenID, ProfilName, Vorgaben, Beschreibung) VALUES (?, ?, ?, ?)",
                (lieferanten_id, profil_name.strip(), vorgaben.strip(), beschreibung.strip())
            )
        return True
    except sqlite3.IntegrityError:
        return "Dublette"

def test_profil_historie_speichern(lieferanten_id, reward_profil_id, start_de, ende_de, konditionen):
    """Speichert ein Testprofil mit automatischer ISO-Konvertierung der Laufzeiten."""
    try:
        # Datums-Konvertierung von UI (TT.MM.JJJJ) nach SQL-ISO (JJJJ-MM-TT)
        p_s = start_de.strip().split('.')
        p_e = ende_de.strip().split('.')
        
        if len(p_s) != 3 or len(p_e) != 3: return "Formatfehler"
        
        iso_start = f"{p_s[2]}-{p_s[1]}-{p_s[0]}"
        iso_ende = f"{p_e[2]}-{p_e[1]}-{p_e[0]}"
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO TestProfile (LieferantenID, RewardProfilID, StartDatum, EndDatum, Konditionen) VALUES (?, ?, ?, ?, ?)",
                (lieferanten_id, reward_profil_id, iso_start, iso_ende, konditionen.strip())
            )
        return True
    except Exception:
        return False

def hole_alle_testprofile_historie():
    """Holt die gesamte Historie der Testzeiträume für Ottos Nahtlosigkeits-Prüfung."""
    with sqlite3.connect(DB_PATH) as conn:
        SQL = """
            SELECT tp.ID, l.LieferantName, rp.ProfilName, tp.StartDatum, tp.EndDatum
            FROM TestProfile tp
            JOIN Lieferanten l ON tp.LieferantenID = l.ID
            JOIN RewardProfile rp ON tp.RewardProfilID = rp.ID
            ORDER BY tp.StartDatum DESC
        """
        cursor = conn.execute(SQL)
        # Rückgabe als UI-konformes deutsches Datumsformat
        liste = []
        for r in cursor.fetchall():
            p_s = r[3].split('-')
            p_e = r[4].split('-')
            liste.append({
                'id': r[0],
                'lieferant': r[1],
                'profil': r[2],
                'zeitraum': f"{p_s[2]}.{p_s[1]}.{p_s[0]} bis {p_e[2]}.{p_e[1]}.{p_e[0]}"
            })
        return liste

def testzeitraum_loeschen(zeitraum_id):
    """Löscht eine Periode aus der Historie."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM TestProfile WHERE ID = ?", (zeitraum_id,))
        return True
    except Exception:
        return False
