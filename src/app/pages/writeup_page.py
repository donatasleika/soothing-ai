from nicegui import ui
import httpx
import asyncio
import os
from ..database.mongodb_db import Read, Update
from ..llm.api import paste_scoped_entries
from datetime import datetime
from urllib.parse import quote

MODEL_URL = os.getenv('LLAMA_BASE')


client_data = {
    'client_name': 'Joe Hudson',
    'client_id': '1234'
}

client_name = 'Joe Hudson'

normalized_name = client_data['client_name'].lower().replace(' ', '-')
ROUTE_CLIENT = f'/{normalized_name}/writeups'

selected_patient = {'name': None}
selected_button = {'button': None}
selected_writeup = {'id': None}
writeup_buttons = {}
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
                     
    .no-scrollbar {
        overflow-x: auto;
        overflow-y: hidden;
        scrollbar-width: none;      /* Firefox */
        -ms-overflow-style: none;   /* old Edge/IE */
    }
    .no-scrollbar::-webkit-scrollbar {
        width: 0 !important;
        height: 0 !important;
        background: transparent;
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
                            await fetch('/upload_pro', { method: 'POST', body: formData });
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


        # Header
        with ui.header().style('padding: 0; padding-top: 0;'):

        # with ui.header().classes('w-full justify-start').style('margin: 0; padding: 5;'):
            with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; margin: 0; padding: 0px;'):

                #  LEFT Group
                with ui.row().classes('w-full items-center gap-4').style('padding: 0px;'):

                    ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').classes('border-0').props('flat color=white')

                    # Front Page
                    ui.button(text='Home', on_click=lambda: ui.run_javascript(f"window.location.href='/{normalized_name}'")) \
                        .props('flat color=white') \
                        .tooltip('Home') \
                        .classes('orientation-vertical justify-start')


                    # View Entries Button
                    ui.button(text='Entries', on_click=lambda: ui.run_javascript(f"window.location.href='/{normalized_name}/entries'")) \
                        .props('flat color=white') \
                        .tooltip('View Entries') \
                        .style('color: white;') \
                        .classes('orientation-vertical justify-start')
                    
                    # Manage Programmes
                    # ui.button(text='Programmes', on_click='') \
                    #     .props('flat color=white') \
                    #     .tooltip('Manage Programmes') \
                    #     .classes('orientation-vertical justify-start')
                
                
                    # Writeup Page
                    ui.button(text='Writeups', on_click=lambda: ui.run_javascript(f"window.location.href='/{normalized_name}/writeups'")) \
                        .props('flat color=white') \
                        .tooltip('Writeups') \
                        .style('color: white;') \
                        .classes('orientation-vertical justify-start')
                

                # RIGHT Group
                with ui.row().classes('justify-end gap-4').style('flex-wrap: nowrap;'):

                    # Settings Button
                    ui.button(icon='settings', on_click='') \
                        .classes('justify-right') \
                        .props('flat color=white') \
                    
                    # Exit Button
                    ui.button(icon='power_settings_new', on_click=lambda: ui.run_javascript("window.location.href='/login'")) \
                        .tooltip('Logout') \
                        .props('flat color=white') \

        # Side Menu
        with ui.left_drawer().classes('w-20 h-full border').props('width=240').style('padding: 0; display: flex; gap: 0;') as left_drawer:
            
            with ui.row().classes('w-full flex-nowrap items-stretch'):
            # Sidebar

                with ui.element('aside').classes('w-full h-full').style('padding: 0; display: flex; flex-direction: column; gap: 0;'):
        
                    with ui.row().classes('justify-center'):

                        ui.label('').style('padding-top:20px')
                        # ui.input()

                    patients = Read().find_all_patients(client_data)

                    def set_active_writeup(patient_name, writeup_id):
                        selected_writeup['id'] = writeup_id

                        for wid, card in writeup_buttons.items():
                            if wid == writeup_id:
                                card.classes(add='bg-blue-200')
                                card.classes(remove='bg-blue-60')
                            else:
                                card.classes(add='bg-blue-100')
                                card.classes(remove='bg-blue-200')


                        result = Read().find_one_writeup(patient_name, writeup_id)

                        writeups = []
                        for doc in result:
                            writeups = doc.get('writeups', [])
                            break

                        if not writeups:
                            input_box.value = ''
                            return


                        input_box.value = writeups[0].get('commentary', '')
                        
                




                    def load_patient_writeups(patient_name):
                        selected_patient['name'] = patient_name
                        selected_writeup['id'] = None

                        writeup_strip.clear()
                        writeup_buttons.clear()
                        input_box.value = ''

                        result = Read().find_writeups(patient_name) or []
                        
                        if not result:
                            with writeup_strip:
                                ui.label('No writeups yet').classes('p-2 text-gray-500')
                                return
   
                        first_doc = result[0] or {}
                        all_writeups = first_doc.get('writeups', [])
                        
                        if not all_writeups:
                            with writeup_strip:
                                ui.label('No writeups yet').classes('text-gray-500 p-2')
                                return
                            
                        all_writeups = list(reversed(all_writeups))
                            
                            
                        with writeup_strip:
                            for index, writeup in enumerate(all_writeups):
                                writeup_id = writeup.get('id') or writeup.get('_id') or index
                                blurb = writeup.get('blurb', 'Untitled')
                                timestamp = writeup.get('time_created', 'None')

                                with ui.card().classes('min-w-[160px] p-2 cursor-pointer bg-blue-100') \
                                    .style('flex: 0 0 auto;') as card:

                                    ui.label(str(timestamp)).classes('text-xs text-gray-500')
                                    ui.label(str(blurb)).classes('text-sm font-medium truncate')


                                card.on('click', lambda _, p=patient_name, wid=writeup_id: set_active_writeup(p, wid))
                                writeup_buttons[writeup_id] = card

                    def select_patient(button, patient_name):

                        if selected_button['button']:
                            selected_button['button'].props('flat color=primary')
                            selected_button['button'].classes(remove='bg-blue-100 text-blue-900')

                        selected_patient['name'] = patient_name
                        selected_button['button'] = button

                        button.props('unelevated color=primary')
                        button.classes('bg-blue-100 text-blue-900')

                        load_patient_writeups(patient_name)


                    for patient in patients:
                        patient_name = patient['patient_name']
                        

                        btn = ui.button(patient_name).props('flat color=primary') \
                        .classes('w-full')
                        
                        
                        btn.on_click(lambda b=btn, p=patient_name: select_patient(b, p)) \

                        # .on_click(lambda p=patient_name, n=normalized_name: ui.run_javascript(
                        #     f"window.location.href='/{n}/writeup/{quote(p)}'"
                        # ))

                    def select_draft_writeup():
                        selected_writeup['id'] = 'draft'
                        input_box.value = ''

                        for wid, card in writeup_buttons.items():
                            if wid == 'draft':
                                card.classes(remove='bg-blue-100')
                                card.classes(add='bg-blue-200')
                            else:
                                card.classes(remove='bg-blue-200')
                                card.classes(add='bg-blue-100')

                    def render_draft_card():
                        with ui.card().classes('min-w-[160px] p-2 cursor-pointer bg-blue-200') \
                            .style('flex: 0 0 auto;') as draft_card:

                            ui.label('Draft').classes('text-xs text-gray-500')
                            ui.label('New writeup').classes('text-sm truncate')

                        draft_card.on('click', lambda _: select_draft_writeup())
                        writeup_buttons['draft'] = draft_card


                    async def new_writeup():
                        patient_name = selected_patient['name']
                        
                        if not patient_name:
                            writeup_strip.clear()
                            with writeup_strip:
                                ui.label('Select a patient first').classes('text-gray-500 p-2')
                            writeup_strip.update()
                            return
                        
                        selected_writeup['id'] = 'draft'
                        input_box.value = ''
                        
                        result = Read().find_writeups(patient_name)

                        # if not result:
                        #     return None
                        
                        first_doc = result[0] or {}
                        all_writeups = first_doc.get('writeups', [])


                        # new_id = len(all_writeups) + 1 if all_writeups else 1
                        # Create new writeup card at lookup

                        writeup_strip.clear()
                        writeup_buttons.clear()

                        with writeup_strip:
                            render_draft_card()

                            for index, writeup in enumerate(reversed(all_writeups)):
                                writeup_id = writeup.get('id') or writeup.get('_id') or index
                                blurb = writeup.get('blurb', 'Untitled')
                                timestamp = writeup.get('time_created', 'None')

                                with ui.card().classes('min-w-[160px] p-2 cursor-pointer bg-blue-100') \
                                    .style('flex: 0 0 auto;') as card:

                                    ui.label(str(timestamp)).classes('text-xs text-gray-500')
                                    ui.label(str(blurb)).classes('text-sm font-medium truncate')

                                card.on('click', lambda _, p=patient_name, wid=writeup_id: set_active_writeup(p, wid))
                                writeup_buttons[writeup_id] = card
                        
                        # draft_card.on('click', lambda _: select_draft_writeup())
                                
                        # writeup_buttons['draft'] = draft_card

                        # writeup_strip.update()

                        # selected_writeup['id'] = new_id

        # Writeup lookups
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-center gap-2 flex-nowrap'):

                ui.button(icon='add', on_click=new_writeup) \
                    .classes('shrink-0 min-w-[20px] h-[20px]') \
                    .props('dense')                

                # with ui.row().classes('w-full items-center gap-4').style('padding: 0px;'):
                with ui.element('div').classes('flex-1 min-w-0 overflow-x-auto no-scrollbar'):
                    with ui.row().classes('flex-nowrap border min-h-[70px]') as writeup_strip:


                            # Becomes active
                        pass

        # Parameter bar
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


        # Notebook form
        with ui.card().classes('w-full justify-between items-center'):

        # Type-in box
            with ui.row().classes('w-full gap-4 no-wrap'):
                # with ui.splitter().classes('w-full') as splitter:
                #     with splitter.before:
                        # with ui.card().classes('justify-center w-full border'):
                            
                with ui.editor(placeholder='Type something here').classes('w-1/2').style('min-height: 270px;') as input_box:
                
                # input_box = (
                #     ui.textarea(placeholder='Session Prep').classes('w-full')
                # )
                # input_box = ui.label('')
                # input_box = ui.label().style('margin-left: 17px; min-height: 250px')
                # typed_input = ui.label().classes('w-full h-32 p-2').props('clearable')
                
                    pass

        # with splitter.after:
                    with ui.card().classes(
                        # 'w-1/2 min-h-[270px] max-h-[420px] overflow-y-auto p-4 border rounded-xl shadow-sm bg-white'
                    ):                  
                        ui.label('Summarized Notes:')
  
                        output_box = (
                        ui.markdown('Summary Notes:').classes('w-full')
                        )
                # output_box = ui.label('').style('min-height: 250px')
                pass
            summary_extension_counter = {'count': 0}

            # Poll the transcript
            async def poll_once():
                async with httpx.AsyncClient() as client:
                        try:
                            response = await client.get('http://localhost:8080/get_pro_transcript')
                            if response.status_code == 200:
                                result = response.json()
                                text = result.get('text', '')

                                if not text:
                                    return
                                

                                # print(response)

                                # Gauti GPT atsakymą
                                # g_response = await client.get('http://localhost:8080/get_response')
                                # if g_response.status_code == 200:
                                #     output_box.text = g_response.json().get('response', '')

                        except Exception as e:
                            print('Error fetching transcript:', e)

            ui.timer(1.0, callback=lambda: asyncio.create_task(poll_once()))

            
            with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; margin: 0; padding: 0px;'):

            # LEFT GROUP
                with ui.row().classes('w-full items-center gap-4').style('padding: 0px;'):
                    
            # Record Button
                    button_id = f"recordButton-{summary_extension_counter['count']}"
                    microphone = ui.button().classes('rounded-lg').props(f'id="{button_id}"')
                    with microphone:
                        ui.html('<span class="rec-dot"></span>')
                        ui.icon('mic')

                    microphone.on('click', lambda bid=button_id: ui.run_javascript(f'window.toggleRecording("{bid}")'))
                    # .style('color: grey; background-color: grey; font-size: 100%; font-weight: 300; width:125px;')

                    async def generate_summary():
                        patient_name = selected_patient['name']

                        if not patient_name:
                            ui.notify('Select a patient first')
                            return

                        scoped_entries = []

                        raw = date_input.value
                        parsed = parse_date_range(raw)

                        print('raw:', raw)
                        print('parsed:', parsed)

                        result = Read().find_entries(patient_name)

                        if not result:
                            output_box.content = 'No entries found'
                            return
                        
                        entries = result[0].get('entries', [])

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
                                scoped_entries.append(
                                    'Entry: {} - {} \n'.format(
                                        entry.get('entry_id'), 
                                        entry.get('description')))
                                # print(entry['entry_id'], entry['description'])
                            


                        
                    
                        gen_response = await paste_scoped_entries(scoped_entries)
                        print(gen_response)

                        if gen_response:
                        
                            output_box.content = gen_response['choices'][0]['message']['content']

                            # if entry['time_of_entry'] > date_start:
                                
                            
                    
                        # print(entry['entry_id'], entry['description'])

                    ui.button('Enhance Summary', on_click=generate_summary).classes('rounded-lg')

                    def save_writeup():
                        patient_name = selected_patient['name']

                        if not patient_name:
                            with writeup_strip:
                                ui.label('Select a patient first')
                                return

                        commentary = input_box.value

                        if not commentary:
                            with writeup_strip:
                                ui.label('Nothing to save')
                            return
                        
                        result = Read().find_writeups(patient_name)
                        first_doc = result[0] if result else {}
                        all_writeups = first_doc.get('writeups', [])

                        print(commentary)

                        new_id = len(all_writeups) + 1 if all_writeups else 1

                        writeup_data = {
                            'id': new_id,
                            'time_created': datetime.now().ctime(),
                            'patient_name': patient_name,
                            'commentary': commentary,
                            'summary': output_box.content if hasattr(output_box, 'content') else ''
                        }

                        # tag_data = 'Placeholder'
                        
                        Update().insert_one_writeup(client_data, writeup_data)
                        
                        selected_writeup['id'] = new_id

                        load_patient_writeups(patient_name)
                        set_active_writeup(patient_name, new_id)

                        ui.notify('Writeup saved', type='positive')

                # with ui.row().classes('w-full justify-end'):
                with ui.row().classes('justify-end gap-4').style('flex-wrap: nowrap;'):

                    ui.button('Save', on_click=save_writeup).classes('justify-end items-center rounded-lg')



        async def extend_workflow(summary_extension_counter):
            summary_extension_counter['count'] += 1
                   # Notebook form
            with ui.card().classes('w-full justify-between items-center'):

            # Type-in box
                with ui.row().classes('w-full justify-center'):
                    with ui.splitter().classes('w-full') as splitter:
                        with splitter.before:
                            with ui.card().classes('justify-center w-full border'):
                                # input_box = (
                                #     ui.textarea(placeholder='Session Prep').classes('w-full')
                                # )

                                input_box = ui.label().style('margin-left: 17px; min-height: 250px')
                                # typed_input = ui.label().classes('w-full h-32 p-2').props('clearable')
                                
                                pass

                        with splitter.after:
                            with ui.card().classes('justify-center w-full border'):
                                # output_box = (
                                #     ui.textarea().classes('w-full')
                                # )

                                output_box = ui.label('').style('min-height: 250px')
                                pass


                    # Poll the transcript
                    async def poll_once():
                        async with httpx.AsyncClient() as client:
                                try:
                                    response = await client.get('http://localhost:8080/get_pro_transcript')
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

                    
                    with ui.row().classes('w-full justify-between items-center').style('flex-wrap: nowrap; margin: 0; padding: 0px;'):

                    # LEFT GROUP
                        with ui.row().classes('w-full items-center gap-4').style('padding: 0px;'):
                            
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

                            ui.button('Enhance Summary', on_click=generate_summary).classes('rounded-lg')


                            

                        # with ui.row().classes('w-full justify-end'):
                        with ui.row().classes('justify-end gap-4').style('flex-wrap: nowrap;'):

                            ui.button('Save').classes('justify-end items-center rounded-lg')


            ui.button(icon='add').classes('w-full rounded-lg h-6 border').style('margin: 0; padding:0;').props('flat')


        ui.button(icon='add', on_click=lambda: extend_workflow(summary_extension_counter)).classes('w-full rounded-lg h-6 border').style('margin: 0; padding:0;').props('flat')

        


        # Footer
        with ui.footer(value=True).classes('h-8').style('margin: 0; padding:0;') as footer:
            pass
