from nicegui import ui, app, events, storage
import secrets
import uuid
from . import mongodb_db
import json
import os
from types import SimpleNamespace
from .route_schema import set_shared_state, get_shared_state
patient_state_name = SimpleNamespace(patient_name=None)
# patient_name = 'Donatas Leika'
total_url_tokens = []
new_url_usable = []
client_name = 'Joe Hudson'
client_data = {
    'client_name': client_name,
    'client_id': '1234'
}

# Working patient_id
patient_cards = {}

def get_base_url():
    return os.getenv("BASE_URL", "http://127.0.0.1:8082")


def new_patient_id() -> str:
    current_patients = mongodb_db.find_all_patients(client_data=client_data)
    print(len(current_patients))


    return str(len(current_patients) + 1) if current_patients else '1'


# Check for tokens in the database
async def create_private_url(patient_name: str, patient_id: str) -> str:
    normalized = client_name.replace(' ', '-').lower()

    # token generator
    while True:
        token = str(uuid.uuid4())
        if not mongodb_db.check_url_tokens(token, client_data):
            set_shared_state(normalized, patient_name, token, patient_id)
            break

    base_url = get_base_url()

    return f'{base_url}/{normalized}/{token}'

def register_admin_ui():
    @ui.page('/')
    async def main(patient_name: str = patient_state_name.patient_name, total_entries: int = 0, client_name: str = client_name):

        # populate_patient_cards()

        new_patient_dialog = ui.dialog()
        url_dialog = ui.dialog()
        total_entries = mongodb_db.check_num_entries(client_data={'client_name': client_name, 'client_id': '1234'}, patient_data={'patient_name': patient_name, 'patient_id': '1'})

        # ui.label({client_data['client_name'][0]}).classes('text-h4 font-bold').style('margin-bottom: 20px;')
        
        with ui.card().classes('w-full justify-start').style('width: 100%; max-width: 100%; max-length: 100%; margin: 0 auto; padding: 20px; overflow-x: hidden;'):
            with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; '):

                #  LEFT Group
                with ui.row().classes('w-full items-center gap-4'):

                    # Add New Patient Button
                    ui.button(icon='add', on_click= lambda: new_patient_form()) \
                        .props('flat') \
                        .tooltip('Add New Patient') \
                        .classes('orientation-vertical')
                
                    async def submit(name_input) -> None:
                        new_patient_dialog.close()

                        patient_name = name_input.value
                        

                        patient_id = new_patient_id()
                        private_url = await create_private_url(patient_name, patient_id)


                        mongodb_db.insert_one_patient(
                            client_data=client_data,
                            patient_data={
                                'patient_name': patient_name,
                                'patient_id'  : patient_id,
                                'private_url_token': private_url.split('/')[-1],
                                'client_id'   : client_data['client_id'],
                            }
                        )


                        patient_state_name.patient_name = name_input.value

                        await new_patient(patient_name, total_entries, patient_id)

                        
                        url_dialog.close()
                        await url_dialog_form(patient_name, private_url, patient_id)



                    # New Patient Form
                    async def new_patient_form():
                        new_patient_dialog.clear()

                        with new_patient_dialog, ui.card():
                            with ui.column().classes('gap-4'):

                                # global name_input

                                name_input = ui.input(label='Patient Name')


                                    
                                with ui.row():
                                    ui.radio(options=['Default', 'CBT Programme', 'Custom Programme']) \
                                        .classes('w-full text-xs rounded-lg') \
                                        .style('width: 178px; font-size: 10px;')
                                    
                                ui.button('Submit', on_click= lambda: submit(name_input)) \
                                    .classes('text-white bg-blue-500 hover:bg-blue-600 w-full rounded-lg')

                        new_patient_dialog.open()

                    async def url_dialog_form(patient_name: str, private_url: str, patient_id: str):
                        url_dialog.clear()

                        with url_dialog, ui.card():
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label(f'{patient_name} URL').classes('text-lg font-bold')
                                ui.input(value=private_url).props('readonly').style('opacity: 0; height: 0; padding: 0; margin: 0; border:0;')

                                ui.button(icon='content_copy', on_click=lambda url=private_url: ui.run_javascript(
                                    f'navigator.clipboard.writeText("{url}")') or ui.notify('Copied!')
                                ).props('flat').classes('justify-start')

                            ui.label(private_url).classes('text-xs')

                        url_dialog.open()

                    # Manage Programmes Button
                    ui.button(icon='layers', on_click='') \
                        .props('flat') \
                        .tooltip('Manage Programmes') \
                        .classes('orientation-vertical justify-start')
                
                # RIGHT Group
                with ui.row().classes('justify-end gap-4').style('flex-wrap: nowrap;'):

                    # # Settings Button
                    # ui.button(icon='settings', on_click='') \
                    #     .props('flat') \
                    
                    # Exit Button
                    ui.button(icon='power_settings_new', on_click='') \
                        .props('flat') \

            # Patient Cards Section
        with ui.row().classes('w-full justify-between items-start').style('padding-top: 2px;'):
            # with ui.card().classes('bg-gray-100 p-6 w-full'):


                async def delete_patient(patient_card, new_patient_id):
                    patient_card.delete()
                    mongodb_db.delete_patient(new_patient_id)
                    

                patient_container = ui.row()
                # await new_patient()

                async def new_patient(patient_name: str, total_entries: int, patient_id: str):
                    patient_card = None

                    with patient_container:


                        with ui.element() as patient_card:
                            # Patient Card
                            with ui.card().classes('rounded-lg w-full').style('width: 367px;'):
                                with ui.row().classes('items-center gap-2').style('width: 100%;'):

                                    with ui.row().classes('justify-start gap-2'):
                                        # Patient Name
                                        ui.label(f'{patient_name}').classes('text-h6').style('margin-right: 1px;')
                                    
                                    with ui.row().classes('justify-end gap-2'):
                                        ui.label('|').classes('text-h5')

                                        # Entries
                                        with ui.element().style('position: relative; display: inline-block;'):
                                            with ui.card().classes('rounded-lg').style('width: 80px; height: 30px; background-color: white; border: 1px solid black; box-shadow: none; padding: 0; display: flex; align-items: center; justify-content: center;'):
                                                ui.link(f'{total_entries} Entries').classes('text-xs text-blue-500 underline').style('line-height: 30px; text-align: center; width: 100%;')
                                            
                                            ui.element().style('position: absolute; top: -3px; right: -3px; width: 10px; height: 10px; background-color: red; border-radius: 50%;')
                                        
                                        # Burger Menu
                                        # with ui.element('q-fab').props('icon=menu').classes('text-h7').style('color: black;'):
                                        with ui.dropdown_button().props('flat color=black').classes('text-h7 justify-end').style('color: black;'):
                                            with ui.column().classes('gap-0'):
                                                ui.button('Edit Programme').on_click(lambda: ui.notify('Edit Programme clicked!')).props('flat color=black').style('color: black; padding-top: 0px; padding-bottom: 0px; padding-left: 12px; padding-right: 12px; font-size: 9px;').classes('text-xs w-full')
                                                ui.button('Delete Patient').on_click(lambda c=patient_card, pid=patient_id: delete_patient(c, pid)).props('flat color=black').style('color: black; padding-top: 0px; padding-bottom: 0px; padding-left: 12px; padding-right: 12px; font-size: 9px; justify-content: flex-start; text-align: left;').classes('text-[9px] w-full q-pa-none')
                                            # ui.button(icon='menu').classes('text-h7').props('flat').style('foreground-color: black;')
                                        

                                ui.separator()

                                # Sentiment Thermometer
                                with ui.card().style('border-color: black; background-color: transparent; border-width: 0px; border-style: solid; padding: 0;').classes('rounded-lg w-full'):
                                    ui.echart({
                                        'title': {'text': ''},
                                        'tooltip': {
                                            'trigger': 'axis', 
                                            'axisPointer': {'type': 'shadow'},
                                        },
                                        # 'label': {
                                        #     'show': True,
                                        #     'position': 'inside',
                                        #     'color': 'white',
                                        #     'fontSize': 9,
                                        #     'formatter': '{c}%',  # Shows the value
                                        # },
                                        'grid': {'left': 0, 'right': 0, 'bottom': 0, 'top': 0},
                                        'xAxis': {
                                            'type': 'value',
                                            'splitLine': {'show': False},
                                            'axisLine': {'show': False},
                                            'axisTick': {'show': False},
                                            'axisLabel': {'show': False},
                                            },
                                        'yAxis': {
                                            'type': 'category',
                                            'data': [''],
                                            'axisLine': {'show': False},
                                            'axisTick': {'show': False},
                                            'axisLabel': {'show': False},
                                            },
                                        'series': [ 
                                            {'type': 'bar', 'stack': 'total', 'data': [30], 'name': 'Positive', 'barWidth': '100%', 'itemStyle': {'borderRadius': [10, 0, 0, 10]}},
                                            {'type': 'bar', 'stack': 'total', 'data': [50], 'name': 'Neutral', 'barWidth': '100%', 'itemStyle': {'borderRadius': 0}},
                                            {'type': 'bar', 'stack': 'total', 'data': [20], 'name': 'Negative', 'barWidth': 20, 'itemStyle': {'borderRadius': [0, 10, 10, 0]}}
                                        ],
                                        'barCategoryGap': '0%' 
                                    }).style('height: 18px; width: 100%; border-radius: 1px;')


                                # Interesting Keywords
                                with ui.column().style('width: 100%; margin: 0; border: none; box-shadow: none; padding-top: 5px;').classes('rounded-lg gap-0'):   
                                    with ui.row().style('padding: 0; margin: 0;').classes('gap-0'):

                                        for text in ['Stress', 'Sleep Issues']:

                                            with ui.card().classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 0; box-shadow: none; display: flex; align-items: center;'):
                                                ui.label(text).classes('text-xs').style('line-height: 30px; text-align: center; white-space: nowrap; padding-right: 5px; padding-left: 5px;')
                            
                                    with ui.row().style('padding: 0; margin: 0;').classes('gap-0'):

                                        for text in ['Gratefulness']:

                                            with ui.card().classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 0; box-shadow: none; display: flex; align-items: center;'):
                                                        ui.label(text).classes('text-xs').style('line-height: 30px; text-align: center; white-space: nowrap; padding-right: 5px; padding-left: 5px;')
                                        
                                # Interaction buttons
                                with ui.row().classes('w-full gap-2').style('padding-top: 5px; padding-bottom: 5px;'):
                                    
                                    # Write-Up Button
                                    ui.button('Write-Up') \
                                        .classes('text-white text-xs rounded-md hover:bg-blue-600') \
                                        .style('flex: 1; height: 32px; background-color: #4a90e2;')

                                    # Show Trends Button
                                    ui.button('Show Trends') \
                                        .classes('text-white text-xs rounded-md hover:bg-gray-300') \
                                        .style('flex: 1; height: 32px;')


        async def populate_patient_cards():
            current_patients = mongodb_db.find_all_patients(client_data=client_data)

            for patient in current_patients:
                patient_name = patient['patient_name']
                patient_id = patient.get('patient_id', str(patient['_id']))  # fallback if needed

                total_entries = mongodb_db.check_num_entries(
                    client_data=client_data,
                    patient_data={'patient_name': patient_name, 'patient_id': patient_id}
                )

                await new_patient(patient_name, total_entries, patient_id)
                



                        

            # with ui.column():
            #     ui.label('Another section of the UI')
            #     ui.input(label='Type something', placeholder='Enter text here')
                    
        await populate_patient_cards() 

    secret_key = secrets.token_hex(16)


    # if __name__ == '__main__':
    # ui.run(storage_secret=secret_key, port=8080, title='Soothing AI - Patient Management', favicon='https://example.com/favicon.ico', dark=False, reload=True)