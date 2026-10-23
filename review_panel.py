import os
from datetime import datetime
from nicegui import ui
import database
import events
import media
import media_panel
import review_panel

def baue_rechtes_panel(haupt_splitter, inputs, tabelle, suchfeld):
    """Baut das rechte Bedienfeld mit Stammdaten, Medien und lädt das Bewertungsmodul."""
    
    with haupt_splitter.after:
        with ui.column().classes('w-full h-full p-1 overflow-y-auto spacing-2'):
            
            # WIEDERAUFKLAPP-BALKEN
            with ui.row().classes('w-full shrink-0 mb-1'):
                ui.button('Artikel-Auswahl einblenden', icon='chevron_right', 
                          on_click=lambda: haupt_splitter.set_value(30))\
                          .props('dense flat text-color=blue-600').classes('bg-blue-50 w-full text-xs font-semibold py-1 rounded').bind_visibility_from(haupt_splitter, 'value', backward=lambda v: v == 0)

            # ------------------------------------------------------------------
            # BORDER 1: STAMMDATEN (UNZERSTÖRBARER CONTAINER-FIX)
            # ------------------------------------------------------------------
            with ui.column().classes('w-full p-3 bg-white border border-slate-200 rounded-md shadow-sm shrink-0') as box_stammdaten:
                header_stammdaten = ui.row().classes('w-full items-center gap-2 border-b border-slate-200 pb-1 mb-2 cursor-pointer hover:bg-slate-50 p-0.5 rounded')
                with header_stammdaten:
                    ui.icon('assignment', color='slate-700').classes('text-base shrink-0')
                    ui.label('Artikel-Stammdaten').classes('custom-title flex-1')

                with ui.column().classes('w-full spacing-1 font-normal') as inhalt_stammdaten:
                    with ui.row().classes('w-full items-center gap-2 mb-1 flex-nowrap'):
                        ui.label('Bestell-Nr:').classes('w-18 text-xs font-medium text-slate-500 shrink-0')
                        inputs['bnr'] = ui.input(placeholder='000-0000000-0000000').props('outlined dense').classes('w-44 text-xs')
                        
                        # --- 1. BESTELLDATUM IM EIGENEN KÄFIG ---
                        ui.label('Bestellt:').classes('w-14 text-xs font-medium text-slate-500 text-right shrink-0')
                        with ui.element('div').classes('relative inline-block'):
                            bdat_input = ui.input(value=datetime.now().strftime('%d.%m.%Y')).props('outlined dense').classes('w-36 text-xs')
                            inputs['bdat'] = bdat_input
                            with bdat_input.add_slot('append'):
                                ui.icon('edit_calendar').classes('cursor-pointer').on('click', lambda: m_bdat.open())
                            with ui.menu().props('no-parent-event') as m_bdat:
                                ui.date(mask='DD.MM.YYYY', on_change=lambda e, t=bdat_input, m=m_bdat: [t.set_value(e.value), m.close()])
                        
                        # --- 2. LIEFERDATUM IM EIGENEN KÄFIG ---
                        ui.label('Geliefert:').classes('w-16 text-xs font-medium text-slate-500 text-right shrink-0')
                        with ui.element('div').classes('relative inline-block'):
                            ldat_input = ui.input(placeholder='TT.MM.JJJJ').props('outlined dense').classes('w-36 text-xs')
                            inputs['ldat'] = ldat_input
                            with ldat_input.add_slot('append'):
                                ui.icon('edit_calendar').classes('cursor-pointer').on('click', lambda: m_ldat.open())
                            with ui.menu().props('no-parent-event') as m_ldat:
                                ui.date(mask='DD.MM.YYYY', on_change=lambda e, t=ldat_input, m=m_ldat: [t.set_value(e.value), m.close()])
                                                                                                        
                    with ui.row().classes('w-full items-center gap-2 mb-1'):
                        ui.label('Art.-Nr:').classes('w-18 text-xs font-medium text-slate-500')
                        inputs['num'] = ui.input(placeholder='Z.B. AB12345678').props('outlined dense maxlength="10"').classes('w-36 text-xs uppercase')
                        ui.label('Preis (€):').classes('w-14 text-xs font-medium text-slate-500 text-right')
                        inputs['preis'] = ui.input(placeholder='0,00').props('outlined Budget dense').classes('w-24 text-xs')

                    with ui.row().classes('w-full items-center gap-2 mb-1'):
                        ui.label('Bezeichn.:').classes('w-18 text-xs font-medium text-slate-500')
                        inputs['bez'] = ui.input().props('outlined dense').classes('flex-1 text-xs')

                    with ui.row().classes('w-full items-center gap-2 mb-1'):
                        ui.label('Beschreib.:').classes('w-18 text-xs font-medium text-slate-500')
                        inputs['besch'] = ui.textarea().props('outlined dense rows=4').classes('flex-1 text-xs')

                    with ui.row().classes('w-full justify-between mt-2 pt-1 border-t border-slate-100 shrink-0'):
                        inputs['btn_leeren'] = ui.button('Neuen Artikel anlegen').props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('rounded px-3 text-xs font-semibold shadow-sm')
                        with ui.row().classes('gap-1'):
                            inputs['btn_loeschen'] = ui.button('Artikel löschen').props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('rounded px-3 text-xs font-semibold shadow-sm')
                            inputs['btn_aktualisieren'] = ui.button('Artikel aktualisieren').props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('rounded px-3 text-xs font-semibold shadow-sm')
                            inputs['btn_hinzufuegen'] = ui.button('Artikel hinzufügen').props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('rounded px-3 text-xs font-semibold shadow-sm')

            # ------------------------------------------------------------------
            # BORDER 2: PRODUKT-MEDIEN & GALERIE
            # ------------------------------------------------------------------
            with ui.column().classes('w-full p-3 bg-white border border-slate-200 rounded-md shadow-sm mt-1') as box_medien:
                header_medien = ui.row().classes('w-full items-center gap-2 border-b border-slate-200 pb-1 mb-2 cursor-pointer hover:bg-slate-50 p-0.5 rounded')
                with header_medien:
                    ui.icon('collections', color='slate-700').classes('text-base shrink-0')
                    ui.label('Produkt-Medien & Galerie').classes('custom-title flex-1')

                with ui.column().classes('w-full font-normal') as inhalt_medien:
                    uploader = ui.upload(label='Bilder droppen', auto_upload=True).props('hide-upload-btn dense flat square')
                    galerie_panel = ui.row()
                    grossbild = ui.interactive_image().props('contain')
                    
                    uploader.on_upload(lambda e: media.bild_hinzufuegen(e, uploader, galerie_panel, grossbild, tabelle, inputs['num']))
                    
                    handler_dict = {
                        'setze_hauptbild': lambda: media.setze_hauptbild(galerie_panel, grossbild, tabelle),
                        'bild_loeschen': lambda: media.bild_loeschen(galerie_panel, grossbild, tabelle)
                    }
                    
                    media_panel.baue_medien_bereich(inhalt_medien, handler_dict, galerie_panel, grossbild, uploader)

                    inputs['btn_main'] = ui.element('div')  
                    inputs['btn_del_bild'] = ui.element('div')

            # ------------------------------------------------------------------
            # BORDER 3: ARTIKEL-BEWERTUNG
            # ------------------------------------------------------------------
            with ui.column().classes('w-full p-3 bg-white border border-slate-200 rounded-md shadow-sm mt-1') as box_bewertung:
                header_bewertung = ui.row().classes('w-full items-center gap-2 border-b border-slate-200 pb-1 mb-2 cursor-pointer hover:bg-slate-50 p-0.5 rounded')
                with header_bewertung:
                    ui.icon('rate_review', color='slate-700').classes('text-base shrink-0')
                    ui.label('Produkt-Bewertung & Rezension').classes('custom-title flex-1')

                with ui.column().classes('w-full font-normal gap-2') as inhalt_bewertung:
                    review_panel.baue_bewertungs_inhalt(inhalt_bewertung, inputs)

            # ==================================================================
            # 3. NATIVE EVENTS BINDEN
            # ==================================================================
            events.get_event_handlers(inputs, tabelle, suchfeld, galerie_panel, grossbild, uploader, haupt_splitter)

            header_stammdaten.on('click', lambda: setattr(inhalt_stammdaten, 'visible', not inhalt_stammdaten.visible))
            header_medien.on('click', lambda: setattr(inhalt_medien, 'visible', not inhalt_medien.visible))
            header_bewertung.on('click', lambda: setattr(inhalt_bewertung, 'visible', not inhalt_bewertung.visible))
