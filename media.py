import os
import sqlite3
import time
from datetime import datetime
from nicegui import ui
import database

# Zentraler Zustandsspeicher im RAM (Rein passiv für Aktionen)
medien_status = {
    'aktiver_artikel': None,
    'ausgewaehltes_bild': None
}

def lade_bilder_galerie(galerie_panel, grossbild, erzwungene_art_id=None):
    """Liest die Bilder von der SSD und baut die Thumbnails auf.
    Nutzt reines Client-seitiges DOM-Targeting für absolute visuelle Stille links."""
    galerie_panel.clear()
    grossbild.set_source('')
    medien_status['ausgewaehltes_bild'] = None
    
    art_id = erzwungene_art_id if erzwungene_art_id else medien_status['aktiver_artikel']
    if not art_id: return
    if not os.path.exists(database.IMAGES_FOLDER): return
    
    # 1. Aktuelles Hauptbild aus der DB abfragen
    db_hauptbild = None
    with sqlite3.connect(database.DB_PATH) as conn:
        res = conn.execute('SELECT HauptBild FROM Artikel WHERE ArtikelNummer = ?', (art_id,)).fetchone()
        if res and res[0]:
            db_hauptbild = res[0]
    
    # 2. Alle Bilder des Artikels von der Festplatte einlesen
    dateien = [f for f in os.listdir(database.IMAGES_FOLDER) if f.startswith(f"{art_id}_supplier_")]
    if not dateien: return
        
    # 3. SORTIERUNG: Das in der DB hinterlegte Hauptbild landet bedingungslos an Index 0!
    dateien.sort(key=lambda x: 0 if (db_hauptbild and x == db_hauptbild) else 1)
    
    # Wir verpassen dem echten Bild-Tag im interaktiven Bild eine feste HTML-ID zum Ansteuern
    grossbild.classes('grossansicht-ziel')
    
    # 4. Kacheln zeichnen
    for datei in dateien:
        pfad = f"/images/{datei}?v={int(os.path.getmtime(os.path.join(database.IMAGES_FOLDER, datei)))}"
        ist_haupt = (db_hauptbild and datei == db_hauptbild)
        border_color = 'border-orange-500 border-2 shadow-md' if ist_haupt else 'border-slate-200'
        
        with galerie_panel:
            # KRUPP-STAHL-BYPASS: Ein Klick sucht direkt das native <img> Element im DOM
            # und tauscht dessen Quell-Attribut aus. 0% Serverlast, absolut 0% Zucken links!
            kachel = ui.card().classes(f'shrink-0 p-0 m-0 border rounded-md cursor-pointer hover:border-blue-500 overflow-hidden w-24 h-20 flex items-center justify-center bg-slate-100 {border_color}')
            
            kachel.on('click', js_handler=f'''(e) => {{
                const targetImg = document.querySelector('.grossansicht-ziel img');
                if (targetImg) {{
                    targetImg.src = "{pfad}";
                }}
                // Pfad im Browser merken, damit Hauptbild/Löschen-Buttons wissen, was gewählt ist
                window._aktives_galerie_bild = "{pfad}";
            }}''')
            
            with kachel:
                ui.image(pfad).classes('w-full h-full object-cover')
    
    # 5. Das vorderste Bild (Hauptbild) als Standard in die Großansicht laden
    if dateien:
        erstes_bild_url = f"/images/{dateien[0]}?v={int(os.path.getmtime(os.path.join(database.IMAGES_FOLDER, dateien[0])))}"
        grossbild.set_source(erstes_bild_url)
        medien_status['ausgewaehltes_bild'] = erstes_bild_url

async def bild_hinzufuegen(e, uploader, galerie_panel, grossbild, tabelle, num_input_element):
    """Speichert ein Bild und erzeugt bei Neuanlagen vollautomatisch den Artikel."""
    import events
    art_id = medien_status['aktiver_artikel']
    ist_neuanlage = False
    
    if not art_id and num_input_element and num_input_element.value:
        art_id = str(num_input_element.value).strip()
        ist_neuanlage = True

    if not art_id:
        ui.notify('Bitte tragen Sie zuerst eine Artikelnummer ein!', type='warning')
        uploader.reset()
        return

    if ist_neuanlage:
        inputs = events.inputs
        bezeichnung = inputs['bez'].value.strip()
        if not bezeichnung:
            ui.notify('Bitte tragen Sie eine Bezeichnung ein!', type='warning')
            uploader.reset()
            return
            
        try:
            beschreibung = inputs['besch'].value.strip()
            bestell_nr = inputs['bnr'].value.strip()
            raw_preis = str(inputs['preis'].value).replace(',', '.').strip()
            bestell_preis = float(raw_preis) if raw_preis else 0.00
            bestell_datum = inputs['bdat'].value.strip()
            liefer_datum = inputs['ldat'].value.strip()
            
            with sqlite3.connect(database.DB_PATH) as conn:
                SQL = """INSERT INTO Artikel (ArtikelNummer, Bezeichnung, Beschreibung, BestellNummer, 
                                             BestellPreis, BestellDatum, LieferDatum, HauptBild) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                conn.execute(SQL, (art_id, bezeichnung, beschreibung, bestell_nr, bestell_preis, bestell_datum, liefer_datum, None))
                
            if events.inputs and 'btn_hinzufuegen' in events.inputs and events.inputs['btn_hinzufuegen']:
                events.inputs['btn_hinzufuegen'].disable()
                events.inputs['btn_aktualisieren'].disable()

            medien_status['aktiver_artikel'] = art_id
            ui.notify('Neuer Artikel wurde automatisch in der Datenbank registriert!', type='info')
        except sqlite3.OperationalError:
            ui.notify('Diese Artikelnummer existiert bereits!', type='negative')
            uploader.reset()
            return
        except Exception as ex:
            ui.notify(f'Fehler beim Erzeugen: {ex}', type='negative')
            uploader.reset()
            return

    nano_time = time.time_ns()
    dateiname = f"{art_id}_supplier_{nano_time}.png"
    ziel_pfad = os.path.join(database.IMAGES_FOLDER, dateiname)
    
    try:
        bytes_daten = await e.file.read()
        with open(ziel_pfad, 'wb') as f:
            f.write(bytes_daten)
        uploader.reset()
            
        with sqlite3.connect(database.DB_PATH) as conn:
            res = conn.execute('SELECT HauptBild FROM Artikel WHERE ArtikelNummer = ?', (art_id,)).fetchone()
            if not res or res[0] is None or res[0] == '':
                conn.execute('UPDATE Artikel SET HauptBild = ? WHERE ArtikelNummer = ?', (dateiname, art_id))
                ui.notify('Erstes Bild als Hauptbild hinterlegt.', type='info')
                
        ui.notify(f'Datei gespeichert: {e.file.name}', type='positive')
    except Exception as ex:
        ui.notify(f'Fehler beim Speichern: {ex}', type='negative')
        uploader.reset()
        
    lade_bilder_galerie(galerie_panel, grossbild, erzwungene_art_id=art_id)
    tabelle.rows = database.hole_artikel()

def setze_hauptbild(galerie_panel, grossbild, tabelle):
    """Befördert das ausgewählte Bild zum Hauptbild."""
    async def hole_und_speichere():
        gewaehlt = await ui.run_javascript('window._aktives_galerie_bild || ""')
        if not gewaehlt:
            gewaehlt = medien_status['ausgewaehltes_bild']
            
        art_id = medien_status['aktiver_artikel']
        if not gewaehlt or not art_id:
            ui.notify('Wählen Sie zuerst ein Bild aus der Galerie aus!', type='warning')
            return
            
        datei_name = os.path.basename(gewaehlt).split('?')[0]
        with sqlite3.connect(database.DB_PATH) as conn:
            conn.execute('UPDATE Artikel SET HauptBild = ? WHERE ArtikelNummer = ?', (datei_name, art_id))
            
        ui.notify('Hauptbild in Datenbank aktualisiert!', type='positive')
        lade_bilder_galerie(galerie_panel, grossbild)
        tabelle.rows = database.hole_artikel()
        
    ui.timer(0.01, hole_und_speichere, once=True)

def bild_loeschen(galerie_panel, grossbild, tabelle):
    """Löscht das gewählte Bild von der SSD."""
    async def hole_und_loeschen():
        gewaehlt = await ui.run_javascript('window._aktives_galerie_bild || ""')
        if not gewaehlt:
            gewaehlt = medien_status['ausgewaehltes_bild']
            
        art_id = medien_status['aktiver_artikel']
        if not gewaehlt or not art_id:
            ui.notify('Wählen Sie zuerst ein Bild aus der Galerie aus!', type='warning')
            return
            
        datei_name = os.path.basename(gewaehlt).split('?')[0]
        voll_pfad = os.path.join(database.IMAGES_FOLDER, datei_name)
        
        war_hauptbild = False
        with sqlite3.connect(database.DB_PATH) as conn:
            res = conn.execute('SELECT HauptBild FROM Artikel WHERE ArtikelNummer = ?', (art_id,)).fetchone()
            if res and res[0] == datei_name:
                war_hauptbild = True
        
        if os.path.exists(voll_pfad):
            os.remove(voll_pfad)
            
        with sqlite3.connect(database.DB_PATH) as conn:
            if war_hauptbild:
                restliche = [f for f in os.listdir(database.IMAGES_FOLDER) if f.startswith(f"{art_id}_supplier_")]
                nachfolger = restliche[0] if restliche else None
                conn.execute('UPDATE Artikel SET HauptBild = ? WHERE ArtikelNummer = ?', (nachfolger, art_id))
                
        ui.notify('Bild erfolgreich gelöscht.', type='positive')
        lade_bilder_galerie(galerie_panel, grossbild)
        tabelle.rows = database.hole_artikel()

    ui.timer(0.01, hole_und_loeschen, once=True)
