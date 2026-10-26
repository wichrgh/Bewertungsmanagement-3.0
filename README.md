import os
import sqlite3
from nicegui import ui
import database

def baue_medien_bereich(inhalt_medien, handler, galerie_panel, grossbild, uploader):
    """Baut den inneren Medien-Grid und die professionelle Vollbild-Lightbox auf."""
    
    # 1. Globale Vollbild-Lightbox 
    # FIX: .props('full-width full-height') zwingt Quasar, das Overlay auf 100% Bildschirmbreite aufzublasen!
    with ui.dialog().props('full-width full-height').classes('m-0 p-0') as lightbox:
        # Die Card füllt nun den gesamten echten Monitor aus
        with ui.card().classes('w-full h-full m-0 p-0 rounded-none bg-slate-950/95 justify-center items-center relative overflow-hidden select-none'):
            
            # Das Lightbox-Bild behält bedingungslos sein natürliches Seitenverhältnis bei (contain)
            lightbox_bild = ui.interactive_image().props('contain').classes('w-full h-full cursor-zoom-out')
            
            ui.label('Klicken zum Schließen').classes('absolute top-4 right-4 text-slate-400 text-xs font-medium bg-slate-900/80 px-3 py-1.5 rounded-md border border-slate-800 pointer-events-none')

    with inhalt_medien:
        # ZWEISPALTEN-GRID für die normale Dashboard-Ansicht
        with ui.grid(columns='140px 1fr').classes('w-full gap-3 items-start shrink-0'):
            with ui.column().classes('w-full gap-1 items-center'):
                uploader.classes('w-full text-xs').props('dense flat square')
                ui.button('Als Hauptbild', on_click=lambda: handler['setze_hauptbild']())\
                    .props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('w-full text-[11px] font-semibold shadow-sm')
                ui.button('Bild löschen', on_click=lambda: handler['bild_loeschen']())\
                    .props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('w-full text-[11px] font-semibold shadow-sm')
            
            with ui.column().classes('w-full gap-2 overflow-hidden'):
                galerie_panel.classes('w-full flex-nowrap overflow-x-scroll overflow-y-hidden p-1 bg-slate-50 border border-slate-200 rounded-md h-24 gap-2 items-center')
                galerie_panel.on('wheel', js_handler='(e) => { e.preventDefault(); e.currentTarget.scrollLeft += e.deltaY; }')
        
        # Der normale, kleine Vorschaubereich im Dashboard
        with ui.row().classes('w-full justify-center bg-slate-50 border border-slate-200 rounded-md p-1 mt-2 flex-1 relative select-none h-[48vh] overflow-hidden'):
            grossbild.classes('w-full h-full cursor-zoom-in bg-slate-50 grossansicht-ziel')
            
            def oeffne_lightbox():
                lightbox_bild.set_source(grossbild.source)
                lightbox.open()
            grossbild.on('click', oeffne_lightbox)

    # 2. DIE GEOMETRISCH SICHERE MAUS-LUPE (Im echten Vollbild-Käfig!)
    lightbox_bild.on('click', lightbox.close)
    
    lightbox_bild.on('mousemove', js_handler='''(mv) => {
        const target = mv.currentTarget;
        const img = target.querySelector('img');
        if (img) {
            const rect = target.getBoundingClientRect();
            const x = ((mv.clientX - rect.left) / rect.width) * 100;
            const y = ((mv.clientY - rect.top) / rect.height) * 100;
            
            img.style.objectFit = 'contain';
            img.style.transform = 'scale(2.2)'; // Proportionale Vergrößerung
            img.style.transformOrigin = `${x}% ${y}%`; // Verschiebt den Fokuspunkt butterweich
        }
    }''')
    
    lightbox_bild.on('mouseleave', js_handler='''(e) => {
        const img = e.currentTarget.querySelector('img');
        if (img) {
            img.style.transform = 'scale(1)';
            img.style.transformOrigin = 'center center';
        }
    }''')
