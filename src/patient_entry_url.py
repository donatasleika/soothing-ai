import uuid
from nicegui import ui
import secrets
from .route_schema import get_shared_state
from pymongo.mongo_client import MongoClient
from . import mongodb_db
from datetime import datetime
# import test_llm

import httpx
import asyncio

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




def register_submit_ui():
    @ui.page('/{client_name}/{token}')
    def submit_entry(client_name, token):

        # Inject JS script on page load
        ui.add_head_html('''
        <script>
        let isRecording = false;
        let recognition;
        let finalTranscript = '';

        if (!('webkitSpeechRecognition' in window)) {
            alert("Speech recognition not supported in this browser (try Chrome).");
        } else {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

        recognition.onresult = function(event) {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
            } else {
            interimTranscript += event.results[i][0].transcript;
            }
        }
        const el = document.querySelector('textarea.mic_textarea'); // native textarea
        if (!el) { console.warn('mic_textarea not found'); return; }
        el.value = finalTranscript + interimTranscript;
        el.dispatchEvent(new Event('input', { bubbles: true }));    // notify Quasar/NiceGUI
        };

        recognition.onend = function() {
        isRecording = false;
        const b = document.getElementById('recordButton');
        if (b) b.innerText = 'Start Microphone';
        };

        recognition.onerror = function(e) {
        console.error('speech error', e);
        };

        function toggleRecording(buttonId) {
            const button = document.getElementById(buttonId);
            if (!isRecording) {
                finalTranscript = '';
                recognition.start();
                isRecording = true;
                button.innerText = 'Stop Microphone';
            } else {
                recognition.stop();
            }
        }
        </script>
        ''')





        c_name, p_name, usable_token, patient_id = get_shared_state(token)

        print(f'Client Name: {c_name}, Patient Name: {p_name}, Token: {usable_token}')

        if not c_name or c_name != client_name:
            ui.notify('Invalid client name.', color='red')
            return
        
        
        ui.query('body').classes('bg-gradient-to-t from-blue-400 to-blue-100')

        # # Poll the transcript
        # async def update_label():
        #     async with httpx.AsyncClient() as client:
        #         while True:
        #             try:
        #                 # response = await client.get('http://localhost:8080/get_transcript')
        #                 # if response.status_code == 200:
        #                 #     result = response.json()
        #                     transcript_output.text = result.get('text', '')

        #                     # Gauti GPT atsakymą
        #                     g_response = await client.get('http://localhost:8080/get_response')
        #                     if g_response.status_code == 200:
        #                         input_box.text = g_response.json().get('response', '')

        #             except Exception as e:
        #                 print('Error fetching transcript:', e)
        #             await asyncio.sleep(1)

        # ui.timer(interval=1.0, callback=update_label)

        with ui.row().classes('w-full h-screen items-center justify-center'):
            with ui.card().classes('max-w-2xl mx-auto mt-10 p-6 bg-white shadow-lg rounded-lg').style('border: 1px solid #e2e8f0;') \
                .props('rounded=lg shadow=md'):

                with ui.row().classes('items-center justify-between'):

                    # transcript_output = ui.label().style('margin-left: 17px')
                    input_box = (
                        ui.textarea(placeholder="Describe what's happening...")
                        .props('outlined auto-grow input-class=mic_textarea')  # applies to the native <textarea>
                        .props('id=mic_textbox')  # optional, keep if you want
                        .classes('w-full')
                    )


                    # ui.on_event('speechText', lambda e: input_box.set_value(e.args))

                    async def handle_key(e):
                        if e.args['key'] == 'Enter' and not e.args.get('shiftKey', False):
                            message_text = input_box.value
                            ui.notify(f"Submitted")
                            print("Captured input:", input_box.value)
                            input_box.value = ''



                            local_time = await ui.run_javascript('''
                                (() => {
                                    const d = new Date();
                                    const pad = n => n.toString().padStart(2, '0');
                                    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} `
                                        + `${pad(d.getHours())}:${pad(d.getMinutes())}`;
                                })()
                            ''')


                            client_name = mongodb_db.client_data['client_name']

                            client_data = {
                                'client_name': client_name,
                                'client_id': 1234, # Need to edit this. It's not important to have the client ID here (maybe)
                            }
                            print(client_name)
                            
                            
                            # tags = test_llm.extract_content(message_text)
                            # print(tags)

                            entries = (mongodb_db.find_entries(p_name)[0]["entries"])
                            # for x in entries:
                            #     print(f'Entry: {x[0]}')

                            print(f'pewp: {len(entries)}')

                            new_entry_id = len(entries) + 1 if entries else 1

                            entry_data = {
                                 # Need to edit this. It's not important to have the client ID here (maybe)
                                'entry_id': int(new_entry_id),
                                'patient_id': patient_id,
                                # 'time_of_entry': str(datetime.now().strftime("%Y-%m-%d %H:%M")),
                                'time_of_entry': local_time,
                                'patient_name': p_name,
                                  # This should be dynamic based on the patient
                                'description': message_text,
                                'token': usable_token,
                                'read': False,
                            }

                            tag_data = {'sentiment': ['sample'], 'tone': ['sample', 'sample'], 'keywords': ['sample', 'sample']}


                            mongodb_db.insert_one_entry(client_data, entry_data, tag_data)


                            # total_entries = mongodb_db.check_num_entries(client_data, patient_data)

                            # entry_position = len(total_entries) + 1 if total_entries else 1

                            # print(patient_data)
                            # print(entry_position)
                            

                    input_box.on('keydown', handle_key)

                    

                with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; '):
                    pass
                    # toggle_recording = ui.button(icon='mic').props('flat id=recordButton')
                    # toggle_recording.on('click', lambda: ui.run_javascript('toggleRecording("recordButton")'))
                    #                     # input_box.on('keyup', handle_enter)


    # secret_key = secrets.token_hex(16)
    # ui.run(title='Soothing AI', port=8082)



all_tokens = []
new_url_usable = None



