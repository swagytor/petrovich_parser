# Аутентификация в Гугл с помощью сервисного аккаунта
# https://docs.iterative.ai/PyDrive2/oauth/#authentication-with-a-service-account
import os
from pathlib import Path

import dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(BASE_DIR / '.env')

FILE_ID = os.environ.get('FILE_ID')
FILE_NAME = os.environ.get('FILE_NAME')

settings = {
    "client_config_backend": "service",
    "service_config": {
        "client_json_file_path": BASE_DIR / 'access_key.json',
    }
}
gauth = GoogleAuth(settings=settings)
gauth.ServiceAuth()
drive = GoogleDrive(gauth)
