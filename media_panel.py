import os
import sqlite3
from nicegui import ui
import database

def baue_medien_bereich(inhalt_medien, handler, galerie_panel, grossbild, uploader):
    """Baut den inneren Medien-Grid und die Bild-Lupe sauber im kompakten Zweispaltensystem auf."""
    
    # Wir nutzen das bereits geöffnete 'inhalt_medien'-Element als direkten Layout-Käfig
    with inhalt_medien:
        # ZWEISPALTEN-GRID: Links 140px feste Steuerleiste, rechts der gesamte Rest elastisch (1fr)
        with ui.grid(columns='140px 1fr').classes('w-full gap-3 items-start shrink-0'):
            
            # LINKES BEDIENFELD: Alle Knöpfe und der Uploader perfekt untereinander geschichtet
            with ui.column().classes('w-full gap-1 items-center'):
                # PROFI-PROPS: dense flat macht den Kasten extrem kompakt und flach!
                uploader.classes('w-full text-xs').props('dense flat square')
                
                ui.button('Als Hauptbild', on_click=lambda: handler['setze_hauptbild']())\
                    .props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('w-full text-[11px] font-semibold shadow-sm')
                
                ui.button('Bild löschen', on_click=lambda: handler['bild_loeschen']())\
                    .props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('w-full text-[11px] font-semibold shadow-sm')
            
            # RECHTES BEDIENFELD: Die horizontale Bildergalerie fließt nahtlos daneben ein
            with ui.column().classes('w-full gap-2 overflow-hidden'):
                galerie_panel.classes('w-full flex-nowrap overflow-x-scroll overflow-y-hidden p-1 bg-slate-50 border border-slate-200 rounded-md h-24 gap-2 items-center')
                galerie_panel.on('wheel', js_handler='(e) => { e.preventDefault(); e.currentTarget.scrollLeft += e.deltaY; }')
        
        # INTERAKTIVER SCHIEBE-ZOOM-KÄFIG (Sitzt majestätisch über die volle Breite darunter)
        with ui.row().classes('w-full justify-center bg-slate-50 border border-slate-200 rounded-md p-1 mt-2 flex-1 overflow-auto relative select-none h-[48vh]') as bild_kaefig:
            grossbild.classes('w-full h-full cursor-zoom-in bg-slate-50 transition-all duration-200 grossansicht-ziel')
            
            grossbild.on('click', js_handler=f'''(e) => {{
                const img = e.currentTarget.querySelector('img');
                if (!img) return;
                const isZoomed = e.currentTarget.classList.toggle('zoomed-state');
                e.currentTarget.classList.toggle('cursor-zoom-in', !isZoomed);
                e.currentTarget.classList.toggle('cursor-zoom-out', isZoomed);
                img.style.objectFit = isZoomed ? 'none' : 'contain';
                img.style.transform = isZoomed ? 'scale(1.8)' : 'scale(1)';
                e.currentTarget.onmousemove = isZoomed ? (mv) => {{
                    const r = e.currentTarget.getBoundingClientRect();
                    img.style.transformOrigin = `${{((mv.clientX - r.left)/r.width)*100}}% ${{((mv.clientY - r.top)/r.height)*100}}%`;
                }} : null;
            }}''')
