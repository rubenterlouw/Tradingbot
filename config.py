import os 
from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY_DEMO = os.getenv("BYBIT_API_KEY_DEMO")
BYBIT_API_SECRET_DEMO = os.getenv("BYBIT_API_SECRET_DEMO")

USE_DEMO = os.getenv("USE_DEMO") == "True"

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")



