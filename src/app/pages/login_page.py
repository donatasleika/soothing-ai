from nicegui import ui

# from firebase import db

def register_login_ui():
    @ui.page('/login')
    def login_user():

        user_logged_in = False
        

        ui.query('body').classes('bg-gradient-to-t from-blue-400 to-blue-100')

        with ui.card().classes('w-full h-screen items-center justify-center'):
            ui.label('Login Page')
            username = ui.input('Username').props('autofocus')
            password = ui.input('Password').props('type=password')
            ui.button('Log in', on_click=lambda: ui.notify('Login clicked')).classes('primary')
            
            if username + password:
                user_logged_in = True


            


