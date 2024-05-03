# Аутентификация в Гугл с помощью сервисного аккаунта
# https://docs.iterative.ai/PyDrive2/oauth/#authentication-with-a-service-account
from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

BASE_DIR = Path(__file__).resolve().parent
FILE_ID = '1bQPZNm31Mg_DUItxST34MeebatkRPTcKr4uvz3xyKd8'
FILE_NAME = 'Петрович товары.xlsx'

settings = {
    "client_config_backend": "service",
    "service_config": {
        "client_json_file_path": BASE_DIR / 'access_key.json',
    }
}
gauth = GoogleAuth(settings=settings)
gauth.ServiceAuth()
drive = GoogleDrive(gauth)
