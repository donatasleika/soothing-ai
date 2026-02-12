from src.app.pages.test_ui import register_admin_ui
from src.app.pages.entries import register_entries_ui
from src.app.pages.patient_entry_url import register_submit_ui
from src.app.pages.login_page import register_login_ui
from nicegui import ui
import secrets
import src.app.pages.route_schema
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = secrets.token_hex(16)


print("NiceGUI app initialized")

MONGODB_URI = os.getenv("MONGO_CREDS")
print(MONGODB_URI)

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is required. See .env.example.")


register_login_ui()
register_admin_ui()
register_entries_ui()
register_submit_ui()

def get_base_url():
    return os.getenv("BASE_URL", "http://127.0.0.1:8082")


ui.run(
    storage_secret=secret_key,
    host='0.0.0.0', 
    port=8080, 
    title='Soothing AI', 
    favicon='', 
    dark=False,
    show=False,
    reload=False)

