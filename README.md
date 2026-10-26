import re
import os
import sqlite3
from datetime import datetime
from nicegui import ui
import database
import media

# Lokale Referenzen für dieses Modul
inputs = None
tabelle = None
suchfeld = None
galerie_panel = None
grossbild = None
uploader = None

def maske_leeren():
    """Versetzt die Maske sicher in den kaufmännischen Standardzustand."""
    if not inputs or 'num' not in inputs or inputs['num'] is None:
        return

    inputs['num'].set_value('')
    inputs['bez'].set_value('')
    inputs['besch'].set_value('')
    inputs['bnr'].set_value('')
    inputs['preis'].set_value('')
    inputs['bdat'].set_value(datetime.now().strftime('%d.%m.%Y'))
    inputs['ldat'].set_value('')
    tabelle.selected = []
    
    media.medien_status['aktiver_artikel'] = None
    media.medien_status['ausgewaehltes_bild'] = None
    
    if galerie_panel:
        galerie_panel.clear()
    if grossbild:
        grossbild.set_source('')

    if 'rev_sterne' in inputs and inputs['rev_sterne']:
        inputs['rev_sterne'].set_value(5)
        inputs['rev_titel'].set_value('')
        inputs['rev_text'].set_value('')

def artikel_hinzufuegen():
    """Fügt einen neuen Artikel im RAM und auf der SSD hinzu (mit entkoppeltem Datumszugriff)."""
    art_num = inputs['num'].value.strip()
    neue_bestell_nr = inputs['bnr'].value.strip()
    bezeichnung = inputs['bez'].value.strip()
    beschreibung = inputs['besch'].value.strip()
    
    # 0. BESTELLPREIS-KONVERTIERUNG
    raw_preis = str(inputs['preis'].value).replace(',', '.').strip()
    try: 
        bestell_preis = float(raw_preis) if raw_preis else 0.00
    except ValueError: 
        ui.notify('Ungültiger Preis eingegeben!', type='negative')
        return

    # 1. Pflichtfelder-Schutz
    if not art_num or not neue_bestell_nr or not bezeichnung:
        ui.notify('Artikelnummer, Bestellnummer und Bezeichnung sind Pflichtfelder!', type='warning')
        return

    # 2. Bestellnummer Format-Schutz (Regex)
    bestellnr_muster = r'^\d{3}-\d{7}-\d{7}$'
    if not re.match(bestellnr_muster, neue_bestell_nr):
        ui.notify('Fehler: Bestellnummer entspricht nicht dem Format ###-#######-#######', type='negative')
        return

    # 3. Bestellnummer Dubletten-Schutz
    with sqlite3.connect(database.DB_PATH) as conn:
        check = conn.execute('SELECT COUNT(*) FROM Artikel WHERE BestellNummer = ?', (neue_bestell_nr,)).fetchone()
        if check and check[0] > 0:
            ui.notify('Aktion abgebrochen: Diese Bestellnummer ist bereits im System vergeben!', type='negative')
            return

    # 4. Datums-Konvertierung nach ISO - RIGIDER KLARTEXT-BYPASS GEGEN INTERNE RAM-LISTEN!
    raw_bdat = str(inputs['bdat'].value).strip()
    # Falls hier noch Müllreste stehen, säubern wir sie radikal auf reine Ziffern
    zahlen_b = re.findall(r'\d+', raw_bdat)
    if len(zahlen_b) == 3:
        iso_bdat = f"{zahlen_b[2]}-{zahlen_b[1]}-{zahlen_b[0]}"
    else:
        iso_bdat = datetime.now().strftime('%Y-%m-%d')

    raw_ldat = str(inputs['ldat'].value).strip() if inputs['ldat'].value else ""
    iso_ldat = ""
    if raw_ldat:
        zahlen_l = re.findall(r'\d+', raw_ldat)
        if len(zahlen_l) == 3:
            iso_ldat = f"{zahlen_l[2]}-{zahlen_l[1]}-{zahlen_l[0]}"
        else:
            ui.notify('Lieferdatum-Format ist ungültig (erwartet: TT.MM.JJJJ)!', type='warning')
            return

    # 5. In die Datenbank schreiben
    try:
        with sqlite3.connect(database.DB_PATH) as conn:
            SQL = """INSERT INTO Artikel (ArtikelNummer, Bezeichnung, Beschreibung, BestellNummer, BestellPreis, BestellDatum, LieferDatum)
                     VALUES (?, ?, ?, ?, ?, ?, ?)"""
            conn.execute(SQL, (art_num, bezeichnung, beschreibung, neue_bestell_nr, bestell_preis, iso_bdat, iso_ldat))
            
        ui.notify('Artikel erfolgreich angelegt!', type='positive')
        tabelle.rows = database.hole_artikel()
        maske_leeren()
    except sqlite3.IntegrityError:
        ui.notify('Fehler: Artikelnummer existiert bereits!', type='negative')
    except Exception as e:
        ui.notify(f'Fehler beim Speichern: {e}', type='negative')

def artikel_aktualisieren():
    """Aktualisiert einen bestehenden Artikel anhand der künstlichen ID (mit entkoppeltem Datumszugriff)."""
    db_id = inputs.get('aktive_db_id')
    if not db_id:
        ui.notify('Bitte wählen Sie zuerst einen Artikel aus der linken Liste!', type='warning')
        return

    art_num = inputs['num'].value.strip()
    neue_bestell_nr = inputs['bnr'].value.strip()
    bezeichnung = inputs['bez'].value.strip()
    beschreibung = inputs['besch'].value.strip()
    
    # 0. BESTELLPREIS-KONVERTIERUNG
    raw_preis = str(inputs['preis'].value).replace(',', '.').strip()
    try: 
        bestell_preis = float(raw_preis) if raw_preis else 0.00
    except ValueError: 
        ui.notify('Ungültiger Preis eingegeben!', type='negative')
        return

    # 1. Pflichtfelder-Schutz
    if not art_num or not neue_bestell_nr or not bezeichnung:
        ui.notify('Artikelnummer, Bestellnummer und Bezeichnung sind Pflichtfelder!', type='warning')
        return

    # 2. Bestellnummer Format-Schutz (Regex)
    bestellnr_muster = r'^\d{3}-\d{7}-\d{7}$'
    if not re.match(bestellnr_muster, neue_bestell_nr):
        ui.notify('Fehler: Bestellnummer entspricht nicht dem Format ###-#######-#######', type='negative')
        return

    # 3. Bestellnummer Dubletten-Schutz
    with sqlite3.connect(database.DB_PATH) as conn:
        check = conn.execute('SELECT COUNT(*) FROM Artikel WHERE BestellNummer = ? AND ID != ?', (neue_bestell_nr, db_id)).fetchone()
        if check and check[0] > 0:
            ui.notify('Aktion abgebrochen: Diese Bestellnummer ist bereits vergeben!', type='negative')
            return

    # 4. Datums-Konvertierung nach ISO - RIGIDER KLARTEXT-BYPASS GEGEN INTERNE RAM-LISTEN!
    raw_bdat = str(inputs['bdat'].value).strip()
    zahlen_b = re.findall(r'\d+', raw_bdat)
    if len(zahlen_b) == 3:
        iso_bdat = f"{zahlen_b[2]}-{zahlen_b[1]}-{zahlen_b[0]}"
    else:
        iso_bdat = datetime.now().strftime('%Y-%m-%d')

    raw_ldat = str(inputs['ldat'].value).strip() if inputs['ldat'].value else ""
    iso_ldat = ""
    if raw_ldat:
        zahlen_l = re.findall(r'\d+', raw_ldat)
        if len(zahlen_l) == 3:
            iso_ldat = f"{zahlen_l[2]}-{zahlen_l[1]}-{zahlen_l[0]}"
        else:
            ui.notify('Lieferdatum-Format ist ungültig (erwartet: TT.MM.JJJJ)!', type='warning')
            return

    # 5. Datenbank-Update ausführen
    try:
        with sqlite3.connect(database.DB_PATH) as conn:
            res = conn.execute('SELECT ArtikelNummer FROM Artikel WHERE ID = ?', (db_id,)).fetchone()
            alte_art_num = res[0] if res else ""

            SQL = """UPDATE Artikel 
                     SET ArtikelNummer = ?, Bezeichnung = ?, Beschreibung = ?, BestellNummer = ?, 
                         BestellPreis = ?, BestellDatum = ?, LieferDatum = ?
                     WHERE ID = ?"""
            conn.execute(SQL, (art_num, bezeichnung, beschreibung, neue_bestell_nr, bestell_preis, iso_bdat, iso_ldat, db_id))
            
            if alte_art_num and alte_art_num != art_num and os.path.exists(database.IMAGES_FOLDER):
                for datei in os.listdir(database.IMAGES_FOLDER):
                    if datei.startswith(f"{alte_art_num}_"):
                        alter_pfad = os.path.join(database.IMAGES_FOLDER, datei)
                        neuer_dateiname = datei.replace(f"{alte_art_num}_", f"{art_num}_")
                        os.rename(alter_pfad, os.path.join(database.IMAGES_FOLDER, neuer_dateiname))

        ui.notify('Artikel erfolgreich aktualisiert!', type='positive')
        
        import media
        media.medien_status['aktiver_artikel'] = art_num
        tabelle.rows = database.hole_artikel()
    except sqlite3.IntegrityError:
        ui.notify('Fehler: Diese Artikelnummer existiert bereits im System!', type='negative')
    except Exception as e:
        ui.notify(f'Fehler beim Aktualisieren: {e}', type='negative')

def artikel_loeschen():
    """Löscht den Artikel aus SQLite und alle zugehörigen Bilder von der SSD."""
    art_num = inputs['num'].value.strip()
    if not art_num:
        ui.notify('Bitte wählen Sie zuerst einen Artikel aus!', type='warning')
        return

    try:
        if os.path.exists(database.IMAGES_FOLDER):
            for datei in os.listdir(database.IMAGES_FOLDER):
                if datei.startswith(f"{art_num}_supplier_"):
                    try:
                        os.remove(os.path.join(database.IMAGES_FOLDER, datei))
                    except:
                        pass

        with sqlite3.connect(database.DB_PATH) as conn:
            conn.execute("DELETE FROM Artikel WHERE ArtikelNummer = ?", (art_num,))
            
        ui.notify('Artikel und Bilder gelöscht!', type='positive')
        tabelle.rows = database.hole_artikel()
        maske_leeren()
    except Exception as e:
        ui.notify(f'Fehler beim Löschen: {e}', type='negative')

def lade_bewertung(art_db_id):
    """Lädt die Amazon-Rezension passiv aus der DB in die Maske."""
    with sqlite3.connect(database.DB_PATH) as conn:
        res = conn.execute('SELECT Sterne, Titel, Rezension FROM Bewertungen WHERE ArtikelID = ?', (art_db_id,)).fetchone()
    
    if res:
        inputs['rev_sterne'].set_value(res[0])
        inputs['rev_titel'].set_value(res[1])
        inputs['rev_text'].set_value(res[2])
    else:
        # Falls noch keine Bewertung existiert, Maske jungfräulich nullen
        inputs['rev_sterne'].set_value(5)
        inputs['rev_titel'].set_value('')
        inputs['rev_text'].set_value('')

def bewertung_speichern():
    """Schreibt oder aktualisiert die Rezension stramm in der Datenbank (Upsert)."""
    db_id = inputs.get('aktive_db_id')
    if not db_id:
        ui.notify('Bitte wählen Sie zuerst links einen Artikel aus!', type='warning')
        return

    sterne = int(inputs['rev_sterne'].value)
    titel = inputs['rev_titel'].value.strip()
    text = inputs['rev_text'].value.strip()

    if not titel or not text:
        ui.notify('Bitte befüllen Sie Titel und Rezensionstext!', type='warning')
        return

    try:
        with sqlite3.connect(database.DB_PATH) as conn:
            # Kaufmännischer SQL-Upsert (Insert oder bei Konflikt direkt Update)
            conn.execute('''
                INSERT INTO Bewertungen (ArtikelID, Sterne, Titel, Rezension)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(ArtikelID) DO UPDATE SET
                    Sterne=excluded.Sterne,
                    Titel=excluded.Titel,
                    Rezension=excluded.Rezension
            ''', (db_id, sterne, titel, text))
            
        ui.notify('Testbericht erfolgreich in der Datenbank verankert!', type='positive')
    except Exception as e:
        ui.notify(f'Fehler beim Speichern der Bewertung: {e}', type='negative')

def get_event_handlers(p_inputs, p_tabelle, p_suchfeld, p_galerie_panel, p_grossbild, p_uploader, p_haupt_splitter=None):
    """Zentralisiert alle kaufmännischen Event-Handler und bindet die UI-Referenzen typsicher."""
    global inputs, tabelle, suchfeld, galerie_panel, grossbild, uploader
    inputs = p_inputs
    tabelle = p_tabelle
    suchfeld = p_suchfeld
    galerie_panel = p_galerie_panel
    grossbild = p_grossbild
    uploader = p_uploader

    def suche():
        tabelle.rows = database.hole_artikel(suchfeld.value)

    def row_click(e):
        art_id = None
        try:
            if isinstance(e.args, list) and len(e.args) > 0:
                for arg in e.args:
                    if isinstance(arg, dict):
                        if 'id' in arg: art_id = arg['id']; break
                        elif 'row' in arg and 'id' in arg['row']: art_id = arg['row']['id']; break
            elif isinstance(e.args, dict):
                art_id = e.args.get('id') or e.args.get('row', {}).get('id')
        except: pass

        if not art_id and e.args:
            art_id = str(e.args) if isinstance(e.args, list) else str(e.args)
        if not art_id or art_id == "None": return

        with sqlite3.connect(database.DB_PATH) as conn:
            cursor = conn.execute('SELECT * FROM Artikel WHERE ID = ?', (art_id,))
            row = cursor.fetchone()
            if row:
                # Exakte Fluchtung anhand des CREATE TABLE Schemas:
                inputs['aktive_db_id'] = row[0] # ID
                inputs['num'].set_value(row[1]) # ArtikelNummer
                inputs['bez'].set_value(row[2]) # Bezeichnung
                inputs['besch'].set_value(row[3] if row[3] else '') # Beschreibung (fängt None ab)
                inputs['bnr'].set_value(row[4]) # BestellNummer
                inputs['preis'].set_value(str(row[5]).replace('.', ',')) # BestellPreis
                
                # Datums-Rückübersetzung (row[6] = BestellDatum, row[7] = LieferDatum)
                p_b = row[6].split('-')
                inputs['bdat'].set_value(f"{p_b[2]}.{p_b[1]}.{p_b[0]}")
                
                de_ldat = ""
                if row[7]:
                    p_l = row[7].split('-')
                    de_ldat = f"{p_l[2]}.{p_l[1]}.{p_l[0]}"
                inputs['ldat'].set_value(de_ldat)
                
                import media
                media.medien_status['aktiver_artikel'] = row[1] # ArtikelNummer für Medien-Engine
                media.lade_bilder_galerie(galerie_panel, grossbild)
                lade_bewertung(art_id)
                
                if 'btn_hinzufuegen' in inputs and inputs['btn_hinzufuegen']: inputs['btn_hinzufuegen'].disable()
                if 'btn_aktualisieren' in inputs and inputs['btn_aktualisieren']: inputs['btn_aktualisieren'].disable()

    # === DYNAMISCHE TIPP-ÜBERWACHUNG ===
    def schalte_buttons_auf_geaendert():
        """Wird getriggert, sobald Otto ein Zeichen in den Stammdaten ändert."""
        if inputs and 'btn_hinzufuegen' in inputs and inputs['btn_hinzufuegen']:
            import media
            if media.medien_status['aktiver_artikel']:
                inputs['btn_hinzufuegen'].disable()
                if inputs['btn_aktualisieren']: inputs['btn_aktualisieren'].enable()
            else:
                inputs['btn_hinzufuegen'].enable()
                if inputs['btn_aktualisieren']: inputs['btn_aktualisieren'].disable()

    # Live-Überwachung an alle kritischen Eingabefelder anheften!
    for feld in ['num', 'bez', 'besch', 'bnr', 'preis', 'bdat', 'ldat']:
        if feld in inputs and inputs[feld]:
            inputs[feld].on_value_change(schalte_buttons_auf_geaendert)

    # UI-Klick-Aktionen absolut sicher im geladenen Scope binden
    inputs['btn_leeren'].on('click', lambda: [maske_leeren(), database.bereinige_verwaiste_bilder(), ui.notify('Maske geleert.', type='info')])
    inputs['btn_loeschen'].on('click', lambda: artikel_loeschen())
    inputs['btn_aktualisieren'].on('click', lambda: artikel_aktualisieren())
    inputs['btn_hinzufuegen'].on('click', lambda: artikel_hinzufuegen())
    
    # Medien-Aktionen binden (Das Uploader-Event läuft jetzt unzerstörbar inline!)
    inputs['btn_main'].on('click', lambda: media.setze_hauptbild(galerie_panel, grossbild, tabelle))
    inputs['btn_del_bild'].on('click', lambda: media.bild_loeschen(galerie_panel, grossbild, tabelle))
    
    suchfeld.on_value_change(lambda e: suche())
    tabelle.on('row-click', row_click)

    return {
        'suche': suche, 'row_click': row_click, 'leeren': maske_leeren,
        'loeschen': artikel_loeschen, 'aktualisieren': artikel_aktualisieren, 'hinzufuegen': artikel_hinzufuegen
    }
