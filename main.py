from src.test_ui import register_admin_ui
from src.entries import register_entries_ui
from src.patient_entry_url import register_submit_ui
from nicegui import ui
import secrets
import src.route_schema
import os

secret_key = secrets.token_hex(16)


print("NiceGUI app initialized")


register_admin_ui()
register_entries_ui()
register_submit_ui()


ui.run(
    storage_secret=secret_key,
    host='0.0.0.0', 
    port=8080, 
    title='Soothing AI', 
    favicon='', 
    dark=False)

