from nicegui import ui
import events

EMOJIS_FACE = ['😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋','😎','😍','😘','🥰','🙂','🤗','🤩','🤔','👍','👎','👏','🙌','💪']
EMOJIS_OBJ = ['📦','🏷️','🚚','🚛','🛒','📁','📂','📅','📆','📊','📈','📉','🛠️','⚙️','💻','🖥️','📱','💰','💵','💳','🧰']
EMOJIS_SYM = ['⭐','🌟','✨','⚡','💥','🔥','💯','❌','⭕','🛑','🚫','⚠️','✅','✔️','❓','❗','📢','📣','💬','💭','❤️']

def aktualisiere_baustein_buttons(container, inputs):
    """Baut die Baustein-Buttons live ohne Zeilenumbrüche und ohne Markdown-Sternchen auf."""
    container.clear()
    raw_text = inputs['rev_bausteine_input'].value or ""
    teile = [t.strip() for t in raw_text.split(',') if t.strip()]
    with container:
        for bst in teile:
            # Kaufmännischer 1:1 Klartext-Bypass ohne Modifikatoren oder Umbrüche!
            js_safe_text = bst.replace('\\', '\\\\').replace("'", "\\'")
            
            btn = ui.button(bst).props('dense flat text-color=slate-600 no-caps')\
                .classes('bg-white border border-slate-200 text-[10px] px-1.5 py-0 rounded hover:bg-slate-100')
            
            btn.on('click', js_handler=f'''() => {{
                const ta = document.querySelector('.target-rezension textarea');
                if (ta) {{
                    const start = ta.selectionStart;
                    const end = ta.selectionEnd;
                    const text = ta.value;
                    ta.value = text.substring(0, start) + '{js_safe_text}' + text.substring(end);
                    ta.selectionStart = ta.selectionEnd = start + '{js_safe_text}'.length;
                    ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    ta.focus();
                }}
            }}''')

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
        
        # UNZERSTÖRBARER CLIENT-TAKT-BYPASS:
        # Wir klinken uns nativ in das 'keyup' des Browsers ein, damit der 1-Schritt-Verzug restlos verfliegt!
        inputs['rev_bausteine_input'].on('keyup', lambda: aktualisiere_baustein_buttons(baustein_container, inputs))
        
        # Initiales Zeichnen beim ersten Laden der Maske
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
                                    btn = ui.button(emo).props('dense flat').classes('text-base p-1 hover:bg-slate-100 min-w-0 w-full col-span-1')
                                    btn.on('click', js_handler=f'''() => {{
                                        const ta = document.querySelector('.target-rezension textarea');
                                        if (ta) {{
                                            const start = ta.selectionStart;
                                            const end = ta.selectionEnd;
                                            const text = ta.value;
                                            ta.value = text.substring(0, start) + '{emo}' + text.substring(end);
                                            ta.selectionStart = ta.selectionEnd = start + '{emo}'.length;
                                            ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                            ta.focus();
                                        }}
                                    }}''')
                        with ui.tab_panel(tab_obj).classes('p-0'):
                            with ui.element('div').classes('grid grid-cols-6 gap-1 w-full'):
                                for emo in EMOJIS_OBJ:
                                    btn = ui.button(emo).props('dense flat').classes('text-base p-1 hover:bg-slate-100 min-w-0 w-full col-span-1')
                                    btn.on('click', js_handler=f'''() => {{
                                        const ta = document.querySelector('.target-rezension textarea');
                                        if (ta) {{
                                            const start = ta.selectionStart;
                                            const end = ta.selectionEnd;
                                            const text = ta.value;
                                            ta.value = text.substring(0, start) + '{emo}' + text.substring(end);
                                            ta.selectionStart = ta.selectionEnd = start + '{emo}'.length;
                                            ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                            ta.focus();
                                        }}
                                    }}''')
                        with ui.tab_panel(tab_sym).classes('p-0'):
                            with ui.element('div').classes('grid grid-cols-6 gap-1 w-full'):
                                for emo in EMOJIS_SYM:
                                    btn = ui.button(emo).props('dense flat').classes('text-base p-1 hover:bg-slate-100 min-w-0 w-full col-span-1')
                                    btn.on('click', js_handler=f'''() => {{
                                        const ta = document.querySelector('.target-rezension textarea');
                                        if (ta) {{
                                            const start = ta.selectionStart;
                                            const end = ta.selectionEnd;
                                            const text = ta.value;
                                            ta.value = text.substring(0, start) + '{emo}' + text.substring(end);
                                            ta.selectionStart = ta.selectionEnd = start + '{emo}'.length;
                                            ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                            ta.focus();
                                        }}
                                    }}''')

            inputs['rev_text'] = ui.textarea(placeholder='Schreiben Sie Ihren Testbericht...')\
                .props('outlined dense rows=5').classes('flex-1 text-xs target-rezension')

        with ui.row().classes('w-full justify-end mt-1 pt-1 border-t border-slate-100 shrink-0'):
            ui.button('Testbericht speichern', on_click=lambda: events.bewertung_speichern()).props('dense unelevated').style('background-color: #475569 !important; color: white !important;').classes('rounded px-4 text-xs font-semibold shadow-sm')
