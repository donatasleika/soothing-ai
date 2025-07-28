from src.test_ui import register_admin_ui
from src.entries import register_entries_ui
from src.patient_entry_url import register_submit_ui
from nicegui import ui
import secrets
import src.route_schema

secret_key = secrets.token_hex(16)

def main():

    register_admin_ui()
    register_entries_ui()
    register_submit_ui()


    ui.run(
        storage_secret=secret_key,
        port=8081, 
        title='Soothing AI', 
        reload=True, 
        favicon='', 
        dark=False)
