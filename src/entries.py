from nicegui import ui
from datetime import datetime
from . import mongodb_db

name = 'Donatas Leika'

client_data = {
    'client_name': 'Joe Hudson',
    'client_id': '1234'
}

selected_patient = {'name': None}
entries_container = ui.column().classes('justify-left').style('margin: 0; padding: 8px;') # Shared container for dynamic entry display


def normalize_entry(entry):
    """Recursively convert sets to lists to make entries JSON serializable."""
    if isinstance(entry, dict):
        return {k: normalize_entry(v) for k, v in entry.items()}
    elif isinstance(entry, list):
        return [normalize_entry(i) for i in entry]
    elif isinstance(entry, set):
        return list(entry)
    else:
        return entry
    
def mark_entry_read(patient_name: str, entry_id: int) -> bool:
    """Delegate to mongodb_db.read_receipts using only patient_name, client_data, entry_id."""
    return mongodb_db.read_receipts(
        client_data,
        {"patient_name": patient_name, "entry_id": entry_id},
    )


def render_entry_card(entry, index, patient_name):
    """Renders a single journal entry card."""
    show_more = True
    opened_once = True
    unread = not entry.get("read", False)
    close_dot = None

    def toggle():
        nonlocal show_more, opened_once, unread
        show_more = not show_more
        taggers.set_visibility(show_more)
        toggle_button.set_text('Show Less' if show_more else 'Show More')

        if show_more:
            opened_once = True
        else:
            # collapsed; if it was unread and has been opened, mark read and remove dot
            if not show_more and unread:   # collapsing now
                try:
                    mark_entry_read(patient_name, entry["entry_id"])
                    unread = False
                    entry["read"] = True
                    if close_dot:
                        close_dot.delete()
                except Exception as e:
                    print(f"Failed to mark read for entry_id={entry.get('entry_id')}: {e}")


    # Visualize the individual entries

    with entries_container:
        with ui.card().classes('w-72 mb-4 p-4'):
            with ui.row().classes('w-full justify-start items-center'):
                if unread:
                    close_dot = ui.element().style(
                        'position: absolute; top: -4px; right: -4px; width: 12px; height: 12px; '
                        'background-color: red; border-radius: 50%;'
                    )
                print(f'Entry: {entry}')
                ui.label(entry.get("time_of_entry", "Unknown"))
                ui.space()
                # ui.label(entry.get("patient_name", "N/A")).classes('text-sm').style('margin-right: 10px;')

            ui.label(entry.get("description", "No description")).classes('text-body-1')

            
            # more_text = ui.label(
            #     f'Tags: {", ".join(entry.get("tags", [{}]))}'
            # ).props('style="margin-top: 8px"').classes('text-sm')
            # more_text.set_visibility(False)
            ui.label()

            # more_text = entry.get("tags") or {}
            # parts = []

            # ui.label(more_text['sentiment']).style('width: 100%; margin: 0; border: none; box-shadow: none; padding-top: 5px;').classes('rounded-lg gap-0')

            # if more_text.get("sentiment"):
            #     parts.append(f"Sentiment: {ui.label(more_text['sentiment']).style('width: 100%; margin: 0; border: none; box-shadow: none; padding-top: 5px;').classes('rounded-lg gap-0')}")
            # if more_text.get("tone"):
            #     parts.append("Tone: " + ", ".join(more_text["tone"]))
            # if more_text.get("keywords"):
            #     parts.append("Keywords: " + ", ".join(more_text["keywords"]))
            # ui.label(" | ".join(parts) if parts else "No Tags") \

            taggers = ui.card().style('width: 100%; margin: 1; border: none; box-shadow: none; padding-top: 5px;').classes('rounded-lg gap-0')


            text = entry.get("tags")
            sentiment = text['sentiment'] if text else "No Tags"
            if not text:
                text = {'tone': [], 'keywords': []}
            else:
                tone = text.get('tone')
                keywords = text.get('keywords')

                with taggers:
                    with ui.row():
                        ui.label('Sentiment:').classes('text-s').style('line-height: 30px; text-align: center; white-space: nowrap; padding-right: 5px; padding-left: 5px;')
                        ui.label(sentiment).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')
                        
                    with ui.row():
                        ui.label('Tone:').classes('text-s').style('line-height: 30px; text-align: center; white-space: nowrap; padding-right: 5px; padding-left: 5px;')
                        for one in tone:
                            ui.label(one).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')

                    with ui.row():
                        ui.label('Keywords:').classes('text-s').style('line-height: 30px; text-align: center; white-space: nowrap; padding-right: 5px; padding-left: 5px;')
                        for word in keywords:
                            ui.label(word).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')


                # more_text = ui.label(str(entry.get("tags") if entry else "No Tags")) \
                #     .props('style="margin-top: 8px"').classes('text-sm')
                # more_text.set_visibility(True)
                taggers.set_visibility(True)

            with ui.row().classes('w-full justify-between items-center mt-4'):
                with ui.element('div').classes('w-6 h-6 rounded-full border border-black flex items-center justify-center').style('margin-left: 5px;'):
                    ui.label(str(index+1)).classes('text-sm p-0 m-0 text-bold')
                toggle_button = ui.button('Show Less', on_click=lambda: (toggle(), close_dot.delete())).props('flat color=primary').classes('text-sm justify-end')

normalized_name = client_data['client_name'].lower().replace(' ', '-')
ROUTE_CLIENT = f'/{normalized_name}/entries'


def register_entries_ui():
    @ui.page(ROUTE_CLIENT)
    def main():
            ui.add_body_html('''
            <style>
            * {
                margin: 1 !important;
                padding: 1 !important;
                box-sizing: border-box;
            }
            </style>
            ''')

        # with ui.row().classes('w-full h-screen flex-nowrap items-stretch'):
            # Sidebar
            # with ui.element('aside').classes('w-60 h-full bg-gray-100').style('padding: 0; margin-right: 5px; display: flex; flex-direction: column; gap: 0;'):
            with ui.left_drawer(top_corner=True, bottom_corner=True).classes('w-60 h-full bg-gray-100').style('padding: 0; margin-right: 5px; display: flex; flex-direction: column; gap: 0;'):
                with ui.row().classes('justify-center'):
                    # ui.label('Patients').classes('text-lg font-bold mb-2')
                    ui.label('')
                patients = mongodb_db.find_all_patients(client_data)

                for patient in patients:
                    patient_name = patient['patient_name']

                    def load_entries(patient_name=patient_name):
                        selected_patient['name'] = patient_name
                        patient_docs = mongodb_db.find_entries(patient_name)
                        entries_container.clear()
                        print(f'Entry 1: {patient_docs}')

                        for doc in patient_docs:
                            print(f'Loaded doc: {doc}')
                            entries = doc.get("entries", [])
                            entries.sort(key=lambda x: x.get("time_of_entry", ""), reverse=True) 

                            for idx, entry in enumerate(entries):
                                display_idx = len(entries) - idx -1
                                render_entry_card(normalize_entry(entry), display_idx, patient_name)

                    ui.button(patient_name).props('flat color=primary') \
                        .on_click(load_entries).classes('w-full').style('margin: 0; padding: 8px;')
                    
                    # for p in patients:
                    #     ui.button(p['patient_name']).props('flat color=primary') \
                    #         .on_click(lambda p=p: ui.open(f"/entries/{p['patient_name']}")) \
                    #         .classes('w-full')
    
            with ui.column().classes('flex-1 min-w-0 h-full p-6 overflow-auto'):
                # with ui.card().classes('w-full'):
                    # ui.label('Entries').classes('text-2xl')
                    with ui.row():
                        print('')
                    global entries_container
                    # with ui.row().classes('w-full justify-between items-center').style('margin-bottom: 20px;'):
                        # ui.label(f"Selected Patient: {selected_patient['name'] or 'None'}").classes('text-lg')
                    entries_container = ui.row().classes('justify-left').style('margin: 0; padding: 8px;')
                    
ROUTE_PATIENT_PAGE = f'/{normalized_name}/entries/{selected_patient["name"]}'

@ui.page(ROUTE_PATIENT_PAGE)
def patient_entries(patient_name: str):
    selected_patient['name'] = patient_name
    patient_docs = mongodb_db.find_entries(patient_name)
    entries_container.clear()

    for doc in patient_docs:
        entries = doc.get("entries", [])
        entries.sort(key=lambda x: x.get("time_of_entry", ""), reverse=True) 

        for idx, entry in enumerate(entries):
            display_idx = len(entries) - idx -1
            render_entry_card(normalize_entry(entry), display_idx, patient_name)

        # ui.run(port=8081, title='Soothing AI - Entries', reload=True, favicon='', dark=False)

    # ui.run(port=8081, title='Soothing AI - Entries', reload=True, favicon='', dark=False)
