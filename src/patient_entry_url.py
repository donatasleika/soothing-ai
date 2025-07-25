import uuid
from nicegui import ui
import secrets
from route_schema import get_shared_state
from pymongo.mongo_client import MongoClient
import mongodb_db

# token = secrets.token_hex(16)
# client_name, patient_name, token = get_shared_state(token)
# print(client_name)



chat_bubbles = []

# async def make_draggable_card(message: str):

#     with ui.card().classes('p-4 shadow-md rounded-lg bg-white text-black') \
#                 .style('position: absolute; top: 100px; left: 100px; cursor: grab; z-index: 999;') as bubble:
#         ui.label(message)


#     # if e.args.get('shiftKey'):
#     #     return

#     # message = input_box.value.strip()
#     # if message:
#     #     # Show message as a draggable card
#     #     with ui.card().classes('p-4 shadow-md rounded-lg bg-white text-black') \
#     #                 .style('position: absolute; top: 100px; left: 100px; cursor: grab; z-index: 999;') as bubble:
#     #         ui.label(message)

#     js = f"""
#     const el = document.querySelector("#{bubble.id}");
#     let offsetX = 0, offsetY = 0, isDragging = false;

#     el.addEventListener('mousedown', function(e) {{
#         isDragging = true;
#         offsetX = e.clientX - el.offsetLeft;
#         offsetY = e.clientY - el.offsetTop;
#         el.style.cursor = 'grabbing';
#     }});

#     document.addEventListener('mousemove', function(e) {{
#         if (isDragging) {{
#             el.style.left = (e.clientX - offsetX) + 'px';
#             el.style.top = (e.clientY - offsetY) + 'px';
#         }}
#     }});

#     document.addEventListener('mouseup', function() {{
#         isDragging = false;
#         el.style.cursor = 'grab';
#     }});
#     """
#     await ui.run_javascript(js)


@ui.page('/{client_name}/{token}')
def submit_entry(client_name, token):
    c_name, p_name, usable_token = get_shared_state(token)

    print(f'Client Name: {c_name}, Patient Name: {p_name}, Token: {usable_token}')

    if not c_name or c_name != client_name:
        ui.notify('Invalid client name.', color='red')
        return
    
    
    ui.query('body').classes('bg-gradient-to-t from-blue-400 to-blue-100')


    
    with ui.row().classes('w-full h-screen items-center justify-center'):
        with ui.card().classes('max-w-2xl mx-auto mt-10 p-6 bg-white shadow-lg rounded-lg').style('border: 1px solid #e2e8f0;') \
            .props('rounded=lg shadow=md'):

            with ui.row().classes('items-center justify-between'):

                input_box = ui.textarea(placeholder='Describe what`s happening...') \
                    .props('outlined auto-grow') \
                    .classes('w-full') \
                    .style('bottom: 0; left: 0; right: 0; padding: 12px; background: white; z-index: 50; y-index:50;')

                async def handle_key(e):
                    if e.args['key'] == 'Enter' and not e.args.get('shiftKey', False):
                        message_text = input_box.value
                        ui.notify(f"Submitted")
                        print("Captured input:", input_box.value)
                        input_box.value = ''
                        
                        client_name = mongodb_db.client_data['client_name']

                        client_data = {
                            'client_name': client_name,
                            'client_id': 1234, # Need to edit this. It's not important to have the client ID here (maybe)
                        }
                        print(client_name)

                        patient_data = {
                            'client_id': "1234", # Need to edit this. It's not important to have the client ID here (maybe)
                            'patient_name': p_name,
                            'patient_id': "1",  # This should be dynamic based on the patient
                            'message': message_text,
                            'token': usable_token,
                        }



                        total_entries = mongodb_db.check_num_entries(client_data, patient_data)

                        entry_position = len(total_entries) + 1 if total_entries else 1

                        print(patient_data)
                        print(entry_position)
                        

                input_box.on('keydown', handle_key)

                

            with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; '):
            
                ui.button(icon='mic').props('flat').classes('ml-auto')


                # input_box.on('keyup', handle_enter)


# secret_key = secrets.token_hex(16)
ui.run(title='Soothing AI', port=8082)



all_tokens = []
new_url_usable = None



