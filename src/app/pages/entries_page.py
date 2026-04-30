from nicegui import ui
from datetime import datetime
from ..database.mongodb_db import Update, Read
import plotly.graph_objects as go


name = 'Donatas Leika'

client_data = {
    'client_name': 'Joe Hudson',
    'client_id': '1234'
}

selected_patient = {'name': None}
# entries_container = ui.column().classes('justify-left').style('margin: 0; padding: 8px;') # Shared container for dynamic entry display


async def ruler_plot(times, y, labels):

    time_series = go.Figure(
        go.Scatter(
            x=times, 
            y=y, 
            mode="markers", 
            marker=dict(size=10),
            hovertemplate="%{x}<br>%{text}<extra></extra>",
            text=labels
            )
        )
    # sizes = [6 + 2 * len(e.get("tags", [])) for e in entries]
    # time_series.update_traces(marker=dict(size=sizes))

    time_series.add_hline(y=0, line_width=1, line_color="black")


    time_series.update_layout(
        yaxis=dict(visible=False, range=[-0.5, 0.5]),
        xaxis=dict(
            showgrid=False,
            ticks="outside",
            ticklen=6,
            tickcolor="black",
            showline=True,
            linewidth=1,
            mirror=True,
        ),
        showlegend=False,
        height=120,
        width=750,
        margin=dict(l=20, r=20, t=10, b=20),
    )
    time_series.update_traces(
        marker=dict(size=8, opacity=0.85, line=dict(width=0)),
    )
    time_series.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    ui.plotly(time_series)._props['options']['config'] = {
    'displayModeBar': False,
    'displaylogo': False,
}

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
    return Update().update_read_receipts(
        client_data,
        {"patient_name": patient_name, "entry_id": entry_id},
    )

def render_entry_card(container, entry, index, patient_name):
    with container:
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
        with container:
            with ui.card().classes('w-72 mb-4 p-4'):
                with ui.row().classes('w-full justify-start items-center'):
                    if unread:
                        close_dot = ui.element().style(
                            'position: absolute; top: -4px; right: -4px; width: 12px; height: 12px; '
                            'background-color: red; border-radius: 50%;'
                        )
                    # print(f'Entry: {entry}')
                    ui.label(entry.get("time_of_entry", "Unknown"))
                    ui.space()
                    # ui.label(entry.get("patient_name", "N/A")).classes('text-sm').style('margin-right: 10px;')

                ui.label(entry.get("description", "No description")).classes('text-body-1')

                
                ui.label()

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
                            if isinstance(tone, list):
                                for one in tone:
                                    ui.label(one).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')
                            elif isinstance(tone, str):
                                    ui.label(tone).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')

                        with ui.row():
                            ui.label('Keywords:').classes('text-s').style('line-height: 30px; text-align: center; white-space: nowrap; padding-right: 5px; padding-left: 5px;')
                            if isinstance(keywords, list):
                                for word in keywords:
                                    ui.label(word).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')
                            elif isinstance(keywords, str):
                                    ui.label(keywords).classes('rounded-lg').style('height: 30px; background-color: #f0f0f0; padding: 1; box-shadow: none; display: flex; align-items: center;')


                    taggers.set_visibility(True)

                with ui.row().classes('w-full justify-between items-center mt-4'):
                    with ui.element('div').classes('w-6 h-6 rounded-full border border-black flex items-center justify-center').style('margin-left: 5px;'):
                        ui.label(str(index+1)).classes('text-sm p-0 m-0 text-bold')
                    toggle_button = ui.button('Show Less', on_click=lambda: (toggle(), close_dot.delete())).props('flat color=primary').classes('text-sm justify-end')




normalized_name = client_data['client_name'].lower().replace(' ', '-')




ROUTE_CLIENT = f'/{normalized_name}/entries'
ROUTE_PATIENT_PAGE = f'/{normalized_name}/entries/{{patient_name}}'



def register_entries_ui():
    @ui.page(ROUTE_CLIENT)
    def main():


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
                    ui.button(text='Writeups', on_click=lambda: ui.run_javascript(f"window.location.href='/{normalized_name}/writeup'")) \
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
        


        with ui.left_drawer().classes('w-20 h-full border').props('width=240').style('padding: 0; display: flex; gap: 0;') as left_drawer:

                    with ui.row().classes('w-full flex-nowrap items-stretch'):
                    # Sidebar

                        with ui.element('aside').classes('w-full h-full').style('padding: 0; display: flex; flex-direction: column; gap: 0;'):
                
                            with ui.row().classes('justify-center'):

                                ui.label('')
                                patients = Read().find_all_patients(client_data)

                            for patient in patients:
                                patient_name = patient['patient_name']
                                print(patient_name)

        # with ui.row().classes('w-full h-screen flex-nowrap items-stretch'):

                                ui.button(patient_name).props('flat color=primary') \
                                    .on_click(lambda p=patient_name: populate_cards(p)) \
                                    .classes('w-full')
                                    # .on_click(lambda p=p: ui.link(f"/entries/{p['patient_name']}")) \
                             


                            # global entries_container


        with ui.row().classes('w-full items-center justify-between'):
            top = ui.column().classes('w-full items-center')
            # ui.separator()
            cards = ui.row().classes('justify-center').style('margin: 0; padding: 6px;')



            async def populate_cards(p_name):
                top.clear()
                cards.clear()


                patient_docs = Read().find_entries(p_name)


                for doc in patient_docs or []:
                    print(doc)
                    entries = doc.get("entries", {})
                    entries.sort(key=lambda x: x.get("time_of_entry", ""), reverse=True)


                    times = [e["time_of_entry"] for e in entries if "time_of_entry" in e]
                    labels = []

                    y = [0] * len(times)
                    # print(y)

                    with top:
                        await ruler_plot(times, y, labels)


                    with cards:
                        for idx, entry in enumerate(entries):
                            display_idx = len(entries) - idx -1
                            render_entry_card(cards, normalize_entry(entry), display_idx, p_name)




    # Footer
        with ui.footer(value=True).classes('justify-center h-8').style('margin: 0; padding:0;'):
            pass



            
ROUTE_GENERAL_PAGE = f'/{normalized_name}/entries'
ROUTE_PATIENT_PAGE = f'/{normalized_name}/entries/{{patient_name}}'


@ui.page(ROUTE_PATIENT_PAGE)
def patient_entries(patient_name: str):



    with ui.header().style('padding: 0; padding-top: 0;'):

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
                ui.button(text='Programmes', on_click='') \
                    .props('flat color=white') \
                    .tooltip('Manage Programmes') \
                    .classes('orientation-vertical justify-start')
            
            
                # Writeup Page
                ui.button(text='Writeups', on_click=lambda: ui.run_javascript(f"window.location.href='/{normalized_name}/writeup'")) \
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
    


    with ui.left_drawer().classes('w-20 h-full border').props('width=240').style('padding: 0; display: flex; gap: 0;') as left_drawer:

        with ui.row().classes('w-full flex-nowrap items-stretch'):
        # Sidebar

            with ui.element('aside').classes('w-full h-full').style('padding: 0; display: flex; flex-direction: column; gap: 0;'):
    
                with ui.row().classes('justify-center'):
            # ui.label('Patients').classes('text-lg font-bold mb-2')
                    ui.label('').style('padding-top:20px')



                # Display all present patients in sidebar
                patients = Read().find_all_patients(client_data)

                for p in patients:
                    p = p['patient_name']
                    ui.button(p).props('flat color=primary') \
                        .on_click(lambda: populate_cards(p)) \
                        .classes('w-full')


    with ui.row().classes('w-full items-center'):
        top = ui.column().classes('w-full items-center')

        cards = ui.row().classes('justify-center').style('margin: 0; padding: 6px;')

        async def populate_cards(p_name):


            patient_docs = Read().find_entries(p_name)
            print(patient_docs)


            for doc in patient_docs or []:
                entries = doc.get("entries", {})
                entries.sort(key=lambda x: x.get("time_of_entry", ""), reverse=True)


                times = [e["time_of_entry"] for e in entries if "time_of_entry" in e]
                labels = []

                y = [0] * len(times)
                # print(y)

                with top:
                    await ruler_plot(times, y, labels)

                with cards:
                    for idx, entry in enumerate(entries):
                        display_idx = len(entries) - idx -1
                        render_entry_card(cards, normalize_entry(entry), display_idx, p_name)


    # Footer
    with ui.footer(value=True).classes('justify-center h-8').style('margin: 0; padding:0;'):
        pagination = ui.pagination(1, 5, direction_links=True).props('flat color=white')
        
