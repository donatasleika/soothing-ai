import uuid
from nicegui import ui
import secrets
from .route_schema import get_shared_state
from pymongo.mongo_client import MongoClient
from ..database.mongodb_db import Read, Update
from ..llm import api
from datetime import datetime
# import test_llm
import json
import httpx

import asyncio

# token = secrets.token_hex(16)
# client_name, patient_name, token = get_shared_state(token)
# print(client_name)



chat_bubbles = []



def register_submit_ui():
    ui.add_head_html("""
    <style>
    /* show dot when either the wrapper OR the inner q-btn has .recording */
    #recordButton.recording .rec-dot,
    #recordButton .q-btn.recording .rec-dot {
    display: inline-block;
    }

    #recordButton .rec-dot {
    display: none;
    width: 10px;
    height: 10px;
    background: #ff3b30;
    border-radius: 50%;
    margin-right: 6px;
    animation: recPulse 1s infinite;
    }

    @keyframes recPulse {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
    }
    </style>
    """)


    mic_js = r"""
    (async () => {
        if (typeof window.toggleRecording !== 'function') {
            let mediaRecorder = null;
            let chunks = [];
            let isRecording = false;
            let stream = null;

            function nodes(buttonId) {
                const root = document.getElementById(buttonId);
                const btn = root ? (root.querySelector('button.q-btn') || root.querySelector('button') || root) : null;
                return { root, btn };
            }

            function setRecording(buttonId, on) {
                const { root, btn } = nodes(buttonId);
                if (root) root.classList.toggle('recording', on);
                if (btn) btn.classList.toggle('recording', on);
            }

            function setBusy(buttonId, on) {
                const { btn } = nodes(buttonId);
                if (btn) btn.disabled = on;
            }

            function pickMimeType() {
                if (typeof MediaRecorder === 'undefined') return '';
                if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) return 'audio/webm;codecs=opus';
                if (MediaRecorder.isTypeSupported('audio/webm')) return 'audio/webm';
                if (MediaRecorder.isTypeSupported('audio/mp4')) return 'audio/mp4';
                return '';
            }

            window.toggleRecording = async function(buttonId) {
                if (!stream) stream = await navigator.mediaDevices.getUserMedia({ audio: true });

                if (!isRecording) {
                    chunks = [];
                    const mimeType = pickMimeType();
                    if (!mimeType) {
                        alert('No supported audio format on this device');
                        return;
                    }

                    mediaRecorder = new MediaRecorder(stream, { mimeType });
                    mediaRecorder.ondataavailable = (e) => {
                        if (e.data && e.data.size > 0) chunks.push(e.data);
                    };

                    mediaRecorder.onstop = async () => {
                        setRecording(buttonId, false);
                        setBusy(buttonId, true);
                        try {
                            const blob = new Blob(chunks, { type: mimeType });
                            const ext = mimeType.includes('webm') ? 'webm' : 'mp4';
                            const formData = new FormData();
                            formData.append('file', blob, `audio.${ext}`);
                            await fetch('/upload_user', { method: 'POST', body: formData });
                        } finally {
                            setBusy(buttonId, false);
                        }
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    setRecording(buttonId, true);
                } else {
                    isRecording = false;
                    setRecording(buttonId, false);
                    mediaRecorder.stop();
                }
            };
        }
    })();
    """



    @ui.page('/submit/{client_name}/{token}')
    def submit_entry(client_name, token):

        ui.timer(0.1, lambda: ui.run_javascript(mic_js), once=True)

        with ui.footer().classes('justify-center h-8').style('margin: 0; padding:0;'):
            ui.markdown('All inputs are secured and only shared with your healthcare professional').style('margin: 0; padding:0;')


        c_name, p_name, usable_token, patient_id = get_shared_state(token)

        # print(get_shared_state())

        print(f'Client Name: {c_name}, Patient Name: {p_name}, Token: {usable_token}')

        if not c_name or c_name != client_name:
            ui.notify('Invalid client name.', color='red')
            return
        
        
        ui.query('body').classes('bg-gradient-to-t from-blue-400 to-blue-100')
        

        with ui.row().classes('w-full h-screen items-center justify-center'):
            with ui.card().classes('max-w-3xl mx-auto mt-15 p-6 bg-white shadow-lg rounded-lg').style('border: 1px solid #e2e8f0; padding-bottom: 0;') \
                .props('rounded=lg shadow=md'):

                with ui.row().classes('items-center justify-between'):

                    # transcript_output = ui.label().style('margin-left: 17px')
                    input_box = (
                        ui.textarea(placeholder="Describe what's happening...")
                        .props('outlined auto-grow input-class=mic_textarea')  # applies to the native <textarea>
                        .props('id=mic_textbox')  # optional, keep if you want
                        .classes('w-full')
                        .style('padding: 0; margin:0;')
                    )

                    with ui.row().classes('w-full justify-between'):

                        mic = ui.button(icon='mic').props('flat').style('padding: 0; margin:0;')
                    
                        mic.on('click', lambda: ui.run_javascript('window.toggleRecording("recordButton")'))

                        ui.button('Send').props('flat').classes('justify-end')

                    # ui.on_event('speechText', lambda e: input_box.set_value(e.args))

                    async def handle_key(e):
                        if e.args['key'] == 'Enter' and not e.args.get('shiftKey', False):
                            message_text = input_box.value
                            ui.notify(f"Submitted")
                            print("Captured input:", p_name, input_box.value)
                            input_box.value = ''


                            # Local User Time (doesn't work yet)
                            local_time = await ui.run_javascript('''
                                (() => {
                                    const d = new Date();
                                    const pad = n => n.toString().padStart(2, '0');
                                    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} `
                                        + `${pad(d.getHours())}:${pad(d.getMinutes())}`;
                                })()
                            ''')


                            client_name = 'Joe Hudson'
                            client_data = {
                                'client_name': client_name,
                                'client_id': 1234, # Need to edit this. It's not important to have the client ID here (maybe)
                            }
                            # print(client_name)

                            async def poll_once():
                                async with httpx.AsyncClient() as client:
                                    try:
                                        resp = await client.get('http://localhost:8080/get_transcript')
                                        if resp.status_code == 200:
                                            result = resp.json()
                                            input_box.text = result.get('text', '')
                                            

                                    except Exception as e:
                                        print('Error fetching user transcript:', e)
                            
                            ui.timer(1.0, callback=lambda: asyncio.create_task(poll_once))

                            entries = (Read().find_entries(p_name)[0]["entries"])

                            # print(f'pewp: {len(entries)}')

        # The user's entry object creation
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

                            fallback_tags = {'sentiment': ['sample'], 'tone': ['sample', 'sample'], 'keywords': ['sample', 'sample']}
                            sentiments = ['positive', 'neutral', 'negative']

                            # Insert sample data as a fallback


                            async def fetch_llm_tagging(entry_data):

                                try:


                                    # Fetch LLM tagging
                                    counter = 0

                                    # asyncio.create_task(api.get_completions(entry_data, counter))
                                    result = await api.get_completions(entry_data, counter)

                                    return result

                                except Exception as e:
                                    print(e)

                                    upd = Update()
                                    await asyncio.to_thread(upd.insert_one_entry, client_data, entry_data, fallback_tags)


                            

                            result = await fetch_llm_tagging(entry_data)

                            print(f'LLM Tagging: {result}')
                            print(type(result))

                            llm_resulted_tags = result['choices'][0]['message']['content']

                            llm_resulted_tags_dict = json.loads(llm_resulted_tags)
                            # print(type(llm_resulted_tags_dict))
                            # print(llm_resulted_tags_dict)


                            async def parse_output(llm_resulted_tags_dict):
                                final_llm_output = {}

                                try:

                                    # Sense-checking keys (sentiment, tone, keywords) and values
                                    for key, value in llm_resulted_tags_dict.items():
                                        # print(type(key))
                                        # print(key)
                                        if key in fallback_tags.keys():
                                            # print(key)

                                    # Sentiment parsing
                                            if key == 'sentiment':
                                                # Sense-checking values 
                                                if isinstance(value, list):
                                                    for x in value:
                                                        llm_sentiment = [y for y in sentiments if x in y]
                                                        print(f'Outputted list of sentiments: {llm_sentiment}')
                                                        # tag_data[key] = llm_sentiment
                                                elif isinstance(value, str):
                                                        print(f'One value for sentiment: {value}')
                                                        final_llm_output[key] = value
                                    # Tone parsing
                                            elif key == 'tone':
                                                if isinstance(value, list):
                                                    for x in value:
                                                        llm_tone = [y for y in sentiments if x in y]
                                                        print(f'Outputted list of tones: {llm_tone}')

                                                        final_llm_output = key[llm_tone]

                                                elif isinstance(value, str):
                                                    if ',' in value:
                                                        tone_string_split = value.split(',')
                                                        print(f'Outputted, parsed tone list: {tone_string_split}')
                                                        final_llm_output[key] = tone_string_split                                                    
                                                    else:
                                                        final_llm_output[key] = value


                                                    print(value)
                                    # Keywords parsing
                                            elif key == 'keywords':
                                                print(key)
                                                print(type(key))
                                                if isinstance(value, list):
                                                    for x in value:
                                                        print(type(x))
                                                        llm_keywords = [y for y in sentiments if x in y]
                                                        print(llm_keywords)
                                                        print(f'Outputted list of keywords: {llm_keywords}')

                                                        final_llm_output[key] = llm_keywords

                                                elif isinstance (value, str):
                                                    if ',' in value:
                                                        keywords_string_split = value.split(',')
                                                        print(f'Outputted, parsed keyword list: {keywords_string_split}')

                                                        final_llm_output[key] = keywords_string_split
                                                    else:
                                                        final_llm_output[key] = keywords_string_split


                                                print(value)
                                            else:
                                                print('Value is: ' + value)
                                        else:
                                            print('Key type: ' + key)
                
                
                                    return final_llm_output                
                
                                except Exception as e:
                                    print(e)

                                    upd = Update()
                                    await asyncio.to_thread(upd.insert_one_entry, client_data, entry_data, fallback_tags)





                            # Update entry with LLM tags
                            final_output = await parse_output(llm_resulted_tags_dict)
                            print(f'Final Output: {final_output}')

                            Update().update_llm_tags(client_data, entry_data, final_output)


                            


                    input_box.on('keydown', handle_key)

                            # Poll the transcript
                async def poll_once():
                    async with httpx.AsyncClient() as client:
                            try:
                                response = await client.get('http://localhost:8080/get_user_transcript')
                                if response.status_code == 200:
                                    result = response.json()
                                    input_box.text = result.get('text', '')

                                    # print(response)

                                    # Gauti GPT atsakymą
                                    # g_response = await client.get('http://localhost:8080/get_response')
                                    # if g_response.status_code == 200:
                                    #     output_box.text = g_response.json().get('response', '')

                            except Exception as e:
                                print('Error fetching transcript:', e)

                ui.timer(1.0, callback=lambda: asyncio.create_task(poll_once()))


                with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; '):
                    pass
                    # toggle_recording = ui.button(icon='mic').props('flat id=recordButton')
                    # toggle_recording.on('click', lambda: ui.run_javascript('toggleRecording("recordButton")'))
                    #                     # input_box.on('keyup', handle_enter)


    # secret_key = secrets.token_hex(16)
    # ui.run(title='Soothing AI', port=8082)



all_tokens = []
new_url_usable = None



