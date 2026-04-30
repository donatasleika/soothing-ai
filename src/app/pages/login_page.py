from nicegui import ui

# from firebase import db

def register_login_ui():
    @ui.page('/login')
    def login_user():

        user_logged_in = False
        
        ui.query('body').classes('bg-gradient-to-t from-blue-400 to-blue-100')


        with ui.row().classes('w-full h-screen items-center justify-center'):
            with ui.card().classes('max-w-3xl mx-auto mt-15 p-6 bg-white shadow-lg rounded-lg') \
                .style('border: 1px solid #e2e8f0;') \
                .props('rounded=lg shadow=md'):

            
             
                username = ui.input('Username').props('autofocus')
                password = ui.input('Password').props('type=password')
                # with ui.row().classes('w-full justify-between items-center').style('padding-bottom: 10px;'):
                #     # ui.button('Register', on_click=lambda: ui.notify('Login clicked')).classes('primary')
                    
                #     ui.button('Log in', on_click=lambda: ui.notify('Login clicked')) \
                #     .classes('primary') \
                #     .props('flat')

                    
                # if username + password:
                #     user_logged_in = True


            


