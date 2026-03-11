from nicegui import ui
import httpx
import asyncio
import os
from ..database.mongodb_db import Read
from ..llm.api import paste_scoped_entries


MODEL_URL = os.getenv('LLAMA_BASE')


client_data = {
    'client_name': 'Joe Hudson',
    'client_id': '1234'
}

client_name = 'Joe Hudson'

normalized_name = client_data['client_name'].lower().replace(' ', '-')
ROUTE_CLIENT = f'/{normalized_name}/writeup'

# ROUTE_PATIENT_PAGE = f'/{normalized_name}/writeup/{{patient_name}}'


def format_date_range(x):
    if not x:
        return None
    return f'{x["from"]} - {x["to"]}'

def parse_date_range(x):
    if not x or ' - ' not in x:
        return None
    start, end = x.split(' - ')
    return {'from': start, 'to': end}

def register_writeup_ui():
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
                            await fetch('/upload', { method: 'POST', body: formData });
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



    @ui.page(ROUTE_CLIENT)
    def create_window():
        ui.timer(0.1, lambda: ui.run_javascript(mic_js), once=True)

        with ui.header().style('padding: 0; padding-top: 0;'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').style('padding: 0; padding-top: 0;').classes('border-0')

        

        # Header
        with ui.card().classes('w-full justify-start').style('width: 100%; max-width: 100%; max-length: 100%; margin: 0 auto; padding: 20px; overflow-x: hidden;'):
            with ui.row().classes('w-full justify-start items-center').style('flex-wrap: nowrap; '):

                #  DATE Group
                with ui.row().classes('justify-between items-center orientation-horizontal border-2 rounded-lg w-56'):

                    date_input = ui.input(placeholder='Date Range').classes('justify-between items-center')

                    with ui.menu() as menu:
                        with ui.date().props('range').bind_value(
                            date_input,
                            forward=format_date_range,
                            backward=parse_date_range
                        ):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with date_input.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

                    print(date_input)

                ui.chip('Sentiment', selectable=True, icon='label', color='indigo-3').classes('justify-start')
                ui.chip('Tone', selectable=True, icon='label', color='green').classes('justify-start')
                ui.chip('Keywords', selectable=True, icon='label', color='orange').classes('justify-start')


        # Side Menu
        with ui.left_drawer().classes('border w-70') as left_drawer:
            ui.label('Side menu')


        # Summarize form
        with ui.card().classes('w-full justify-between items-center'):

        # Type-in box
            with ui.row().classes('w-full justify-center'):
                with ui.splitter().classes('w-full') as splitter:
                    with splitter.before:
                        with ui.card().classes('justify-center w-full border'):
                            # input_box = (
                            #     ui.textarea(placeholder='Session Prep').classes('w-full')
                            # )

                            input_box = ui.label().style('margin-left: 17px')
                            # typed_input = ui.label().classes('w-full h-32 p-2').props('clearable')
                            
                            pass

                    with splitter.after:
                        with ui.card().classes('justify-center w-full border'):
                            # output_box = (
                            #     ui.textarea().classes('w-full')
                            # )

                            output_box = ui.label('')
                            pass


                # Poll the transcript
                async def poll_once():
                    async with httpx.AsyncClient() as client:
                            try:
                                response = await client.get('http://localhost:8080/get_transcript')
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

                
                with ui.row().classes('w-full justify-between items-center'):
                    with ui.row().classes('w-full justify-start items-center'):
                        
    # Record Button
                        microphone = ui.button().classes('rounded-lg').props('id="recordButton"')
                        with microphone:
                            ui.html('<span class="rec-dot"></span>')
                            ui.icon('mic')

                        microphone.on('click', lambda: ui.run_javascript('window.toggleRecording("recordButton")'))
                        # .style('color: grey; background-color: grey; font-size: 100%; font-weight: 300; width:125px;')

                        async def generate_summary():
                            scoped_entries = []

                            raw = date_input.value
                            parsed = parse_date_range(raw)

                            print('raw:', raw)
                            print('parsed:', parsed)

                            entries = Read().find_entries(patient_name='Donatas Leika')[0]['entries']

                            if parsed:
                                start = parsed['from']
                                end = parsed['to']

                                for entry in entries:
                                    time_of_entry = entry['time_of_entry'][:10]
                                    print(time_of_entry)
                                    print(entry)


                                    if start <= time_of_entry <= end:
                                        scoped_entries.append('Entry: {} - {} \n'.format(entry['entry_id'], entry['description']))

                                        # print(entry['entry_id'], entry['description'])

                            else:
                                for entry in entries:
                                    scoped_entries.append('Entry: {} - {} \n'.format(entry['entry_id'], entry['description']))
                                    # print(entry['entry_id'], entry['description'])
                                


                            
                        
                            gen_response = await paste_scoped_entries(scoped_entries)
                            print(gen_response)

                            if gen_response:
                            
                                output_box.text = gen_response['choices'][0]['message']['content']

                                # if entry['time_of_entry'] > date_start:
                                    
                                
                        
                            # print(entry['entry_id'], entry['description'])


                        
                        ui.button('Generate Summary', on_click=generate_summary).classes('rounded-lg')


                        

                    # with ui.row().classes('w-full justify-end'):

                        ui.button('Save').classes('justify-end items-center rounded-lg')

        ui.button(icon='add').classes('w-full rounded-lg h-6 border').style('margin: 0; padding:0;').props('flat')

        # Footer
        with ui.footer(value=True).classes('h-8').style('margin: 0; padding:0;') as footer:
            pass
            # ui.label('Footer')

        # with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        #     ui.button(on_click=footer.toggle, icon='contact_support').props('fab')