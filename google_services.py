import os

from settings import drive


def download_file_from_google_drive(file_id, file_name):
    """Функция для загрузки файла из гугл облака"""
    file = drive.CreateFile({'id': file_id})

    file.GetContentFile(file_name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    return file


def upload_file_to_google_drive(file, file_name):
    """Функция для загрузки файла в гугл облако"""
    file.SetContentFile(file_name)

    file.Upload(param={'convert': True})

    if os.path.exists(file_name):
        os.remove(file_name)
