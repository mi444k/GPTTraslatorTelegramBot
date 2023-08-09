import os
from dotenv import load_dotenv
from distutils.util import strtobool

load_dotenv()

DEBUG = bool(strtobool(os.getenv('DEBUG')))
SHOW_ERROR_INFO = bool(strtobool(os.getenv('SHOW_ERROR_INFO')))
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAPI_KEY = os.getenv('OPENAPI_KEY')
