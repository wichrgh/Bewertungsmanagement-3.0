import os
from nicegui import app, ui
import database
import details

# 1. DATENBANK INITIALISIEREN
database.initialize_database()

# Lokalen Bilderordner über das app-Objekt für den Webbrowser freischalten
app.add_static_files('/images', database.IMAGES_FOLDER)

# 2. DIE CORE-ROUTING-ENGINE
@ui.page('/')
def main_page():
    """Baut das hochkompakte, perfekt austarierte kaufmännische Dashboard."""

    ui.add_head_html('''
        <style>
            .no-checkbox-table th:first-child, .no-checkbox-table td:first-child { display: none !important; }
            .custom-title { color: #334155 !important; font-weight: 700 !important; font-size: 0.875rem !important; }
            
            .q-table tbody tr {
                contain: layout paint; /* Zwingt den Browser, die Zeile isoliert zu rendern */
                will-change: transform;
            }
            .q-table td {
                white-space: nowrap; /* Verhindert Text-Zeilenumbrüche beim DOM-Refresh */
            }
            .q-notification {
                font-size: 1.25rem !important;   /* Deutlich größere Schrift (ca. 20px) */
                font-weight: bold !important;    /* Fetter Text für sofortige Lesbarkeit */
                padding: 20px 28px !important;   /* Viel mehr Innenabstand (Kasten wird wuchtiger) */
                border-radius: 12px !important;  /* Schicke, abgerundete Ecken */
                min-width: 500px !important;     /* Mindestbreite, damit es auf 4K nicht untergeht */
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important; /* Mächtiger Schatten */
            }
            .q-notification__icon {
                font-size: 2rem !important;      /* Doppelte Icon-Größe */
            }
        </style>
    ''')

    baue_kopfzeile()

    # CONTAINER: Perfekt ausgenutzte Höhe für FHD
    with ui.card().classes('w-full mx-1 my-1 p-2 shadow-md border border-slate-200 rounded-md bg-white h-[96vh] flex flex-col overflow-hidden'):
        
        # TITELLEISTE
        with ui.row().classes('w-full justify-between items-center border-b border-slate-200 pb-1 mb-1 shrink-0'):
            ui.label('Bewertungsmanagement 3.0').classes('text-xl font-bold text-slate-850 track-tight')

        # DYNAMISCHER GRID-SPLITTER
        with ui.splitter(value=30).classes('w-full flex-1 border border-slate-100 rounded-md p-0.5 bg-slate-50 overflow-hidden') as haupt_splitter:
            
            # ==================================================================
            # LINKES PANEL: ARTIKELLISTE (Horizontales Einklappen auf Klick!)
            # ==================================================================
            with haupt_splitter.before:
                with ui.column().classes('w-full h-full p-2 bg-white border border-slate-200 rounded-md flex flex-col overflow-hidden'):
                    
                    with ui.row().classes('w-full items-center gap-2 border-b border-slate-200 pb-1 mb-2 shrink-0 flex-nowrap cursor-pointer hover:bg-slate-50 p-0.5 rounded').on('click', lambda: setattr(haupt_splitter, 'value', 0)):
                        ui.icon('chevron_left', color='slate-500').classes('text-base shrink-0')
                        ui.icon('list_alt', color='slate-700').classes('text-base shrink-0')
                        ui.label('Artikel-Auswahl').classes('custom-title flex-1')
                        ui.tooltip('Artikelliste zur Seite ausblenden')
                    
                    suchfeld = ui.input(placeholder=' Artikel oder Nummer suchen...').props('outlined dense').classes('w-full mb-1 shrink-0')
                    
                    tabelle = ui.table(
                        columns = [
                            {'name': 'bdat_anzeige', 'label': 'Best.-Datum', 'field': 'bdat_anzeige', 'sortable': True, 'align': 'left', 'style': 'width: 15%'},
                            {'name': 'ldat_anzeige', 'label': 'Lieferdatum', 'field': 'ldat_anzeige', 'sortable': True, 'align': 'left', 'style': 'width: 15%'},
                            {'name': 'thumb', 'label': 'Bild', 'field': 'thumb', 'align': 'left', 'style': 'width: 60px'},
                            {'name': 'num_anzeige', 'label': 'Artikelnr.', 'field': 'num_anzeige', 'sortable': True, 'align': 'left', 'style': 'width: 20%'},
                            {'name': 'name', 'label': 'Bezeichnung', 'field': 'name', 'sortable': True, 'align': 'left', 'style': 'width: 45%'}
                        ],
                        rows=database.hole_artikel(),
                        selection='single',
                        row_key='id'
                    )

                    tabelle.props('''
                        hide-selected-banner 
                        dense 
                        flat 
                        wrap-cells=false 
                        sort-by="bdat_anzeige" 
                        binary-state-sort
                        :sort-method="(rows, sortBy, descending) => sortBy === 'bdat_anzeige' ? rows.sort((a, b) => { const pA = (a.bdat_anzeige || '').split('.'); const pB = (b.bdat_anzeige || '').split('.'); const dA = pA[2]+pA[1]+pA[0]; const dB = pB[2]+pB[1]+pB[0]; return descending ? dB.localeCompare(dA) : dA.localeCompare(dB); }) : rows"
                    ''')
                    
                    tabelle.classes('w-full flex-1 border border-slate-100 rounded-md cursor-pointer no-checkbox-table overflow-y-auto')

                    tabelle.add_slot('body-cell-thumb', '''
                        <q-td :props="props">
                            <q-img v-if="props.row.thumb" :src="props.row.thumb" style="width: 35px; height: 26px; border-radius: 3px;" class="border border-slate-200" />
                            <div v-else style="width: 35px; height: 26px;" class="bg-slate-100 rounded border border-dashed border-slate-300"></div>
                        </q-td>
                    ''')

            # ==================================================================
            # RECHTES PANEL: DELEGIERT AN DAS NEUE DETAILS-MODUL (Absolut bombensicher!)
            # ==================================================================
            inputs = {}
            details.baue_rechtes_panel(haupt_splitter, inputs, tabelle, suchfeld)

# 3. Test- und Reward-Profile
badge_labels = {}

# Globale RAM-Zustände für das aktuell im Dashboard aktive Profil-Gedächtnis
aktiver_lieferant_id = None
aktives_reward_profil_id = None

# Hilfsvariablen, um die Text-Labels live im Header zu aktualisieren
header_labels = {}

def de_datum_format(iso_str):
    """Macht aus dem DB-Format JJJJ-MM-TT wieder ein lesbares TT.MM.JJJJ für das Auge."""
    if not iso_str or '-' not in iso_str: return iso_str if iso_str else ""
    p = iso_str.split('-')
    return f"{p[2]}.{p[1]}.{p[0]}"

def lade_reward_profil_details_in_dialog(profil_id, container_details):
    """Holt bei Auswahl in der ComboBox die Vorgaben aus der DB und zeichnet sie in voller Pracht."""
    container_details.clear()
    if not profil_id:
        return
        
    details = database.hole_reward_profil_details(profil_id)
    if details:
        with container_details:
            with ui.column().classes('w-full gap-1 mt-1 text-xs'):
                with ui.row().classes('gap-1'):
                    ui.label('Zielvereinbarung:').classes('font-medium text-slate-500 w-28')
                    ui.label(details['vorgaben']).classes('text-slate-700 italic')
                with ui.row().classes('gap-1 mt-1'):
                    ui.label('Beschreibung:').classes('font-medium text-slate-500 w-28')
                    ui.label(details['beschreibung']).classes('text-slate-600 leading-relaxed')

def update_profil_auswahl_kaskade(lieferant_id, select_reward, container_details):
    """Triggert die Kaskade: Lädt die Profile neu, sobald der Lieferant gewechselt wird."""
    container_details.clear()
    # 1. Neue, gefilterte Optionen aus der Datenbank holen
    neue_optionen = database.hole_reward_profile_fuer_lieferant(lieferant_id)
    
    # 2. ComboBox im Browser live updaten und nullen
    select_reward.set_options(neue_optionen)
    select_reward.set_value(None)

def profil_im_header_aktivieren(dialog, inputs):
    """Speichert die Auswahl im RAM und aktualisiert den Header reaktiv."""
    global aktiver_lieferant_id, aktives_reward_profil_id
    
    aktiver_lieferant_id = inputs['select_lieferant'].value
    aktives_reward_profil_id = inputs['select_reward'].value
    
    lieferant_name = "Kein Lieferant"
    profil_name = "Kein Profil"
    
    if inputs['select_lieferant'].value:
        lieferant_name = inputs['select_lieferant'].options.get(aktiver_lieferant_id, "Kein Lieferant")
    if inputs['select_reward'].value:
        profil_name = inputs['select_reward'].options.get(aktives_reward_profil_id, "Kein Profil")
        
    # PROFI-FIX: .set_text() statt .set_value() angewendet!
    header_labels['txt_badge'].set_text(f"{lieferant_name} | {profil_name}")
    
    ui.notify('Testprofil erfolgreich scharfgeschaltet!', type='positive')
    dialog.close()

def baue_kopfzeile():
    """Rendert die obere Kopfzeile mitsamt dem automatischen Boot-Loader für aktive Profile."""
    global aktiver_lieferant_id, aktives_reward_profil_id
    
    # PROFI-BOOT-LOADER: Wir prüfen beim Laden der Seite, ob heute ein Profil aktiv ist!
    heute_profil = database.hole_heute_aktives_testprofil()
    
    initialer_text = "Kein Profil aktiv"
    if heute_profil:
        # IDs und Namen direkt aus der DB-Historie ins RAM einrasten lassen!
        aktiver_lieferant_id = heute_profil['l_id']
        aktives_reward_profil_id = heute_profil['r_id']
        initialer_text = f"{heute_profil['l_name']} | {heute_profil['r_name']}"

    with ui.row().classes('w-full items-center justify-between p-3 bg-slate-800 text-white shadow shrink-0'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('inventory').classes('text-xl text-blue-400')
            ui.label('Warenwirtschaft & Produkttest').classes('text-base font-bold tracking-wide')
            
        # DIE COMPAKTE INFO-BOX IM HEADER (Zeigt jetzt ab Sekunde 1 den echten DB-Status an!)
        with ui.row().classes('items-center gap-1.5 bg-slate-700 px-2.5 py-1 rounded-md border border-slate-600 text-xs cursor-pointer hover:bg-slate-600 transition-colors') as reward_badge:
            ui.icon('workspace_premium').classes('text-sm text-amber-400')
            
            # Befüllt das Label reaktiv mit dem ermittelten Start-Zustand
            header_labels['txt_badge'] = ui.label(initialer_text).classes('font-bold text-white')
            
            ui.icon('info').classes('text-[14px] text-slate-400 ml-0.5')
        
        reward_badge.on('click', zeige_status_details)

def _baue_tab_lieferanten(panel):
    """Rendert Lieferanten-Eingabe und deren Löschliste."""
    with panel:
        ui.label('Neuen Lieferanten verankern:').classes('font-bold text-slate-600')
        with ui.row().classes('w-full items-center gap-2 mb-2 flex-nowrap'):
            inp = ui.input(placeholder='Name...').props('outlined dense').classes('flex-1 text-xs')
            def save():
                if database.lieferant_speichern(inp.value) == "Dublette": ui.notify('Existiert bereits!', type='negative')
                elif inp.value: ui.notify('Erfolgreich!', type='positive'); inp.set_value(''); box.clear(); draw()
            ui.button('Anlegen', on_click=save).props('dense unelevated').classes('rounded px-3 text-xs bg-slate-600 text-white')
        box = ui.column().classes('w-full gap-1 max-h-36 overflow-y-auto')
        def draw():
            with box:
                for idx, name in database.hole_alle_lieferanten().items():
                    with ui.row().classes('w-full justify-between items-center bg-slate-50 p-1 rounded border text-xs flex-nowrap'):
                        ui.label(name)
                        ui.button(icon='delete', on_click=lambda e, i=idx: [database.lieferant_loeschen(i), ui.notify('Gelöscht'), box.clear(), draw()]).props('dense flat text-color=red-500')
        draw()

def _baue_tab_reward_profile(panel):
    """Rendert Reward-Eingabe und Lieferanten-Profile mit On-Demand-Refresh."""
    with panel:
        ui.label('Profile für Lieferanten definieren:').classes('font-bold text-slate-600')
        
        # Das Dropdown zieht sich die Optionen LIVE im Moment des Klicks (on-focus)
        sel_l = ui.select(options=database.hole_alle_lieferanten(), on_change=lambda e: [box.clear(), draw(e.value)]).props('outlined dense').classes('w-full text-xs')
        sel_l.on('focus', lambda: sel_l.set_options(database.hole_alle_lieferanten()))
        
        inp_n = ui.input(placeholder='Profil-Name (z.B. Premium)...').props('outlined dense').classes('w-full text-xs')
        inp_z = ui.input(placeholder='Zielvorgabe...').props('outlined dense').classes('w-full text-xs')
        inp_b = ui.textarea(placeholder='Beschreibung...').props('outlined dense rows=2').classes('w-full text-xs')
        
        def save():
            if database.reward_profil_speichern(sel_l.value, inp_n.value, inp_z.value, inp_b.value) == "Dublette": ui.notify('Profil existiert bereits!', type='negative')
            else: ui.notify('Erfolgreich!', type='positive'); inp_n.set_value(''); box.clear(); draw(sel_l.value)
        ui.button('Profil speichern', on_click=save).props('dense unelevated').classes('w-full bg-slate-600 text-white rounded text-xs mt-1')
        
        box = ui.column().classes('w-full gap-1 max-h-32 overflow-y-auto mt-2')
        def draw(lid):
            if not lid: return
            import sqlite3
            with box, sqlite3.connect(database.DB_PATH) as conn:
                for pid, pname in conn.execute("SELECT ID, ProfilName FROM RewardProfile WHERE LieferantenID=?", (lid,)).fetchall():
                    with ui.row().classes('w-full justify-between items-center bg-slate-50 p-1 rounded border text-xs flex-nowrap'):
                        ui.label(pname)
                        ui.button(icon='delete', on_click=lambda e, p=pid: [conn.execute("DELETE FROM RewardProfile WHERE ID=?", (p,)), ui.notify('Entfernt'), box.clear(), draw(lid)]).props('dense flat text-color=red-500')

def _baue_tab_testzeitraeume(panel, dialog):
    """Aktiviert Perioden inkl. Kalendericons, Kaskade und listet nahtlose Historie auf."""
    global aktiver_lieferant_id, aktives_reward_profil_id
    with panel:
        p_in = {}
        
        # Lieferantenauswahl mit Focus-Refresh und Live-Kaskade für das Reward-Feld
        p_in['select_lieferant'] = ui.select(options=database.hole_alle_lieferanten(), value=aktiver_lieferant_id).props('outlined dense').classes('w-full text-xs')
        p_in['select_lieferant'].on('focus', lambda: p_in['select_lieferant'].set_options(database.hole_alle_lieferanten()))
        
        p_in['select_reward'] = ui.select(options=database.hole_reward_profile_fuer_lieferant(aktiver_lieferant_id), value=aktives_reward_profil_id).props('outlined dense').classes('w-full text-xs')
        
        # Kaskaden-Bypass: Wenn der Lieferant wechselt, laden wir die Rewards dieses Lieferanten sofort nach
        p_in['select_lieferant'].on_value_change(lambda e: [
            p_in['select_reward'].set_options(database.hole_reward_profile_fuer_lieferant(e.value)),
            p_in['select_reward'].set_value(None),
            det.clear()
        ])
        p_in['select_reward'].on_value_change(lambda e: lade_reward_profil_details_in_dialog(e.value, det))

        # --- KALENDER-ICONS WIEDER HERGESTELLT & IN ISOLIERTE KÄFIGE GESPERRT ---
        with ui.row().classes('w-full items-center gap-2 flex-nowrap overflow-visible'):
            with ui.element('div').classes('relative inline-block w-1/2'):
                start_field = ui.input(placeholder='Von (TT.MM.JJJJ)').props('outlined dense').classes('w-full text-xs')
                p_in['start_input'] = start_field
                with start_field.add_slot('append'):
                    ui.icon('edit_calendar').classes('cursor-pointer').on('click', lambda: m_start.open())
                with ui.menu().props('no-parent-event') as m_start:
                    ui.date(mask='DD.MM.YYYY', on_change=lambda e, t=start_field, m=m_start: [t.set_value(e.value), m.close()])

            with ui.element('div').classes('relative inline-block w-1/2'):
                ende_field = ui.input(placeholder='Bis (TT.MM.JJJJ)').props('outlined dense').classes('w-full text-xs')
                p_in['ende_input'] = ende_field
                with ende_field.add_slot('append'):
                    ui.icon('edit_calendar').classes('cursor-pointer').on('click', lambda: menu_ende.open())
                with ui.menu().props('no-parent-event') as menu_ende:
                    ui.date(mask='DD.MM.YYYY', on_change=lambda e, t=ende_field, m=menu_ende: [t.set_value(e.value), m.close()])

        det = ui.column().classes('w-full gap-0.5 text-[11px]')
        if aktives_reward_profil_id: lade_reward_profil_details_in_dialog(aktives_reward_profil_id, det)
        
        def activate():
            if not p_in['select_lieferant'].value or not p_in['select_reward'].value or not p_in['start_input'].value or not p_in['ende_input'].value:
                ui.notify('Bitte befüllen Sie alle Felder!', type='warning')
                return
            database.test_profil_historie_speichern(p_in['select_lieferant'].value, p_in['select_reward'].value, p_in['start_input'].value, p_in['ende_input'].value, "")
            profil_im_header_aktivieren(dialog, p_in)
            
        ui.button('Perioden-Aktivierung', on_click=activate).props('dense unelevated').classes('w-full bg-slate-600 text-white rounded text-xs mt-1')
        ui.label('📋 Perioden-Historie (Nahtlosigkeits-Check):').classes('font-bold text-slate-500 mt-2 border-t pt-1 text-[11px]')
        
        hist_box = ui.column().classes('w-full gap-1 max-h-28 overflow-y-auto')
        def draw_hist():
            with hist_box:
                for item in database.hole_alle_testprofile_historie():
                    with ui.row().classes('w-full justify-between items-center bg-slate-50 p-1 rounded border text-[11px] flex-nowrap'):
                        ui.label(f"{item['lieferant']} ({item['profil']}): {item['zeitraum']}")
                        ui.button(icon='delete', on_click=lambda e, t=item['id']: [database.testzeitraum_loeschen(t), ui.notify('Entfernt'), hist_box.clear(), draw_hist()]).props('dense flat text-color=red-400')
        draw_hist()

def zeige_status_details():
    """Öffnet das kaskadierende Kontrollzentrum als schlanke Stammdatenpflege-Maske."""
    with ui.dialog() as dialog, ui.card().classes('p-3 min-w-[500px] max-w-[550px] border shadow-xl rounded-lg bg-white'):
        with ui.column().classes('w-full gap-2 text-xs'):
            with ui.row().classes('w-full items-center justify-between border-b pb-1 shrink-0'):
                ui.label('⚙️ Stammdaten- & Profilpflege').classes('text-xs font-bold text-slate-700')
                ui.button(icon='close', on_click=dialog.close).props('dense flat text-color=slate-400')
            with ui.tabs().classes('w-full dense text-slate-500 border-b') as pflege_tabs:
                t1 = ui.tab('1. Lieferanten', icon='business')
                t2 = ui.tab('2. Rewards', icon='workspace_premium')
                t3 = ui.tab('3. Historie', icon='date_range')
            with ui.tab_panels(pflege_tabs, value=t3).classes('w-full p-0 bg-white overflow-visible'):
                _baue_tab_lieferanten(ui.tab_panel(t1).classes('p-1 gap-2 flex flex-col'))
                _baue_tab_reward_profile(ui.tab_panel(t2).classes('p-1 gap-2 flex flex-col'))
                _baue_tab_testzeitraeume(ui.tab_panel(t3).classes('p-1 gap-2 flex flex-col overflow-visible'), dialog)
        dialog.open()

# 4. SERVER-START (Port 8090)
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Bewertungsmanagement 3.0', reload=False, port=8090, show=False)
