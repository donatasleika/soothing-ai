from nicegui import ui

def register_login_ui():
    @ui.page('/login')
    def login_user():

        ui.query('body').classes('bg-gradient-to-t from-blue-400 to-blue-100')

        with ui.card().classes('w-full h-screen items-center justify-center'):
            ui.label('Login Page')
            ui.input('Username').props('autofocus')
            ui.input('Password').props('type=password')
            ui.button('Login', on_click=lambda: ui.notify('Login clicked')).classes('primary')
            
            pass


