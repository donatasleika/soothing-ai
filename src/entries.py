from nicegui import ui
from datetime import datetime
from . import mongodb_db

name = 'Donatas Leika'

client_data = {
    'client_name': 'Joe Hudson',
    'client_id': '1234'
}

selected_patient = {'name': None}
entries_container = ui.column()  # Shared container for dynamic entry display


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


def render_entry_card(entry, index):
    """Renders a single journal entry card."""
    show_more = False

    def toggle():
        nonlocal show_more
        show_more = not show_more
        more_text.set_visibility(show_more)
        toggle_button.set_text('Show Less' if show_more else 'Show More')

    with entries_container:
        with ui.card().classes('w-full mb-4 p-4'):
            with ui.row().classes('w-full justify-start items-center'):
                ui.label(entry.get("time_of_entry", "Unknown"))
                ui.space()
                ui.label(entry.get("patient_name", "N/A")).classes('text-sm').style('margin-right: 10px;')

            ui.label(entry.get("description", "No description")).classes('text-body-1')

            more_text = ui.label(
                f'Tags: {", ".join(entry.get("tags", []))}'
            ).props('style="margin-top: 8px"').classes('text-sm')
            more_text.set_visibility(False)

            with ui.row().classes('w-full justify-between items-center').style('margin-top: 16px;'):
                with ui.element('div').classes('w-6 h-6 rounded-full border border-black flex items-center justify-center').style('margin-left: 5px;'):
                    ui.label(str(index)).classes('text-sm p-0 m-0 text-bold')
                toggle_button = ui.button('Show More', on_click=toggle).props('flat color=primary').classes('text-sm justify-end')

def register_entries_ui():
    @ui.page('/entries')
    def main():
        ui.add_body_html('''
        <style>
        * {
            margin: 1 !important;
            padding: 0 !important;
            box-sizing: border-box;
        }
        </style>
        ''')

        with ui.row().classes('w-full h-screen'):
            # Sidebar
            with ui.element('aside').classes('w-60 h-full bg-gray-100').style('padding: 0; margin-right: 5px; display: flex; flex-direction: column; gap: 0;'):
                with ui.row().classes('justify-center'):
                    ui.label('Patients').classes('text-lg font-bold mb-2')
                patients = mongodb_db.find_all_patients(client_data)

                for patient in patients:
                    patient_name = patient['patient_name']

                    def load_entries(patient_name=patient_name):
                        selected_patient['name'] = patient_name
                        entries = mongodb_db.find_entries(patient_name)
                        entries_container.clear()

                        for idx, entry in enumerate(entries):
                            entry = normalize_entry(entry)
                            render_entry_card(entry, idx)

                    ui.button(patient_name).props('flat color=primary') \
                        .on_click(load_entries).classes('w-full').style('margin: 0; padding: 8px;')

            # Main content area
            with ui.column().classes('flex-grow h-full p-6'):
                # ui.label('Entries').classes('text-2xl')
                with ui.row():
                    print('')
                global entries_container
                with ui.row().classes('w-full justify-between items-center').style('margin-bottom: 20px;'):
                    # ui.label(f"Selected Patient: {selected_patient['name'] or 'None'}").classes('text-lg')
                    entries_container = ui.column().classes('justify-left').style('margin: 0; padding: 8px;')
                    


    # ui.run(port=8081, title='Soothing AI - Entries', reload=True, favicon='', dark=False)
