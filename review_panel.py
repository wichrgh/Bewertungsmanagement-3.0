from nicegui import ui
import events

EMOJIS_FACE = ['😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋','😎','😍','😘','🥰','🙂','🤗','🤩','🤔','👍','👎','👏','🙌','💪']
EMOJIS_OBJ = ['📦','🏷️','🚚','🚛','🛒','📁','📂','📅','📆','📊','📈','📉','🛠️','⚙️','💻','🖥️','📱','💰','💵','💳','🧰']
EMOJIS_SYM = ['⭐','🌟','✨','⚡','💥','🔥','💯','❌','⭕','🛑','🚫','⚠️','✅','✔️','❓','❗','📢','📣','💬','💭','❤️']

def injiziere_text_an_cursor(inputs, text_to_insert):
    """Injiziert Text/Emojis basierend auf dem clientseitigen Browser-Gedächtnis."""
    textarea = inputs['rev_text']
    js_text = text_to_insert.replace('\\', '\\\\').replace('\n', '\\n').replace("'", "\\'")
    
    ui.run_javascript(f'''
        const el = document.getElementById("{textarea.id}")?.querySelector("textarea");
        if (el) {{
            // Hole die exakte Position aus dem globalen Speicher
            const pos = window._rev_text_cursor !== undefined ? window._rev_text_cursor : el.value.length;
            const text = el.value;
            
            // Text punktgenau einschieben
            el.value = text.substring(0, pos) + '{js_text}' + text.substring(pos);
            
            // Position im Browser-Gedächtnis direkt weiterschieben (für Mehrfachklicks)
            const neuePos = pos + '{js_text}'.length;
            window._rev_text_cursor = neuePos;
            el.selectionStart = el.selectionEnd = neuePos;
            
            // NiceGUI-Hintergrund synchronisieren
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.focus();
        }}
    ''')

def aktualisiere_baustein_buttons(container, inputs):
    container.clear()
    raw_text = inputs['rev_bausteine_input'].value or ""
    teile = [t.strip() for t in raw_text.split(',') if t.strip()]
    with container:
        for bst in teile:
            ui.button(bst, on_click=lambda e, txt=bst: injiziere_text_an_cursor(inputs, f"\n\n**{txt}**\n"))\
                .props('dense flat text-color=slate-600').classes('bg-white border border-slate-200 text-[10px] px-1.5 py-0 rounded hover:bg-slate-100')

def baue_bewertungs_inhalt(inhalt_bewertung, inputs):
    """Baut die inneren Elemente des Amazon-Bewertungsmoduls auf."""
    with inhalt_bewertung:
        with ui.row().classes('w-full items-center gap-2 flex-nowrap'):
            ui.label('Bewertung:').classes('text-xs font-medium text-slate-500 w-24')
            inputs['rev_sterne'] = ui.rating(value=5).props('size=sm color=orange-400')
            ui.label('Titel:').classes('text-xs font-medium text-slate-500 w-10 text-right')
            inputs['rev_titel'] = ui.input(placeholder='Kurzes Fazit...').props('outlined dense').classes('flex-1 text-xs')
        
        with ui.row().classes('w-full items-center gap-2 mb-1'):
            ui.label('Bausteine-Edit:').classes('text-xs font-medium text-slate-500 w-24')
            inputs['rev_bausteine_input'] = ui.input(
                value="Verpackung & Versand, Optik/Haptik, Inbetriebnahme, Handhabung, Fazit"
            ).props('outlined dense placeholder="Mit Komma trennen..."').classes('flex-1 text-xs')

        baustein_container = ui.row().classes('w-full items-center gap-1.5 bg-slate-50 p-1.5 rounded-md border border-slate-100 flex-wrap')
        inputs['rev_bausteine_input'].on('value-change', lambda: aktualisiere_baustein_buttons(baustein_container, inputs))
        aktualisiere_baustein_buttons(baustein_container, inputs)

        with ui.row().classes('w-full items-start gap-2 flex-nowrap'):
            with ui.column().classes('w-24 items-start gap-1 shrink-0'):
                ui.label('Rezension:').classes('text-xs font-medium text-slate-500 pt-2')
                btn_emoji = ui.button(icon='sentiment_satisfied_alt').props('dense flat text-color=slate-500').classes('hover:bg-slate-100 rounded ml-1')
                with ui.menu().classes('w-80 border border-slate-200 shadow-xl rounded-md bg-white'):
                    with ui.tabs().classes('w-full dense text-slate-500') as emo_tabs:
                        tab_face = ui.tab('😀')
                        tab_obj = ui.tab('📦')
                        tab_sym = ui.tab('⭐')
                    with ui.tab_panels(emo_tabs, value=tab_face).classes('w-full p-2 h-44 overflow-y-auto bg-white'):
                        with ui.tab_panel(tab_face).classes('p-0'):
                            with ui.element('div').classes('grid grid-cols-6 gap-1 w-full'):
                                for emo in EMOJIS_FACE:
                                    ui.button(emo, on_click=lambda e, s=emo: injiziere_text_an_cursor(inputs, s)).props('dense flat').classes('text-base p-1 hover:bg-slate-100 min-w-0 w-full col-span-1')
                        with ui.tab_panel(tab_obj).classes('p-0'):
                            with ui.element('div').classes('grid grid-cols-6 gap-1 w-full'):
                                for emo in EMOJIS_OBJ:
                                    ui.button(emo, on_click=lambda e, s=emo: injiziere_text_an_cursor(inputs, s)).props('dense flat').classes('text-base p-1 hover:bg-slate-100 min-w-0 w-full col-span-1')
                        with ui.tab_panel(tab_sym).classes('p-0'):
                            with ui.element('div').classes('grid grid-cols-6 gap-1 w-full'):
                                for emo in EMOJIS_SYM:
                                    ui.button(emo, on_click=lambda e, s=emo: injiziere_text_an_cursor(inputs, s)).props('dense flat').classes('text-base p-1 hover:bg-slate-100 min-w-0 w-full col-span-1')

            inputs['rev_text'] = ui.textarea(placeholder='Schreiben Sie Ihren Testbericht...').props('outlined dense rows=5').classes('flex-1 text-xs')
            
            # UNZERSTÖRBAR-NATIV-BINDING: Injiziert die Event-Lauscher direkt auf dem echten HTML-Textknoten, sobald dieser im Browser erwacht!
            inputs['rev_text'].on('init', js_handler=f'''() => {{
                const ta = document.getElementById("{inputs["rev_text"].id}")?.querySelector("textarea");
                if (ta) {{
                    const updateCursor = () => {{ window._rev_text_cursor = ta.selectionStart; }};
                    ta.addEventListener("click", updateCursor);
                    ta.addEventListener("keyup", updateCursor);
                    ta.addEventListener("keydown", updateCursor);
                    ta.addEventListener("blur", updateCursor);
                }}
            }}''')

        with ui.row().classes('w-full justify-end mt-1 pt-1 border-t border-slate-100 shrink-0'):
            ui.button('Testbericht speichern', on_click=lambda: events.bewertung_speichern()).props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('rounded px-4 text-xs font-semibold shadow-sm')

# https://share.google/aimode/McyFNyHWv17XjF50v
