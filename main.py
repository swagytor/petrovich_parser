import pprint
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from services import get_page_info, get_items_ids, get_web_driver, get_item_data, upload_products_info
from multiprocessing import Pool

BASE_URL = 'https://petrovich.ru'


def main():
    start = time.time()
    items_count, max_pages = get_page_info()
    item_ids = get_items_ids(max_pages)

    #очищаем от дубликатов
    item_ids = list(set(item_ids))

    print(f'Кол-во ID: {len(item_ids)}')

    start_1 = time.time()

    with Pool(5) as p:
        result = p.map(get_item_data, item_ids)

    end_1 = time.time()
    print(f'Кол-во данных: {len(result)}')

    end = time.time()

    minutes = int(end - start) // 60
    seconds = int(end - start) % 60

    minutes_1 = int(end_1 - start_1) // 60
    seconds_1 = int(end_1 - start_1) % 60

    print(f'Время выполнения: {minutes} минут {seconds} секунд')
    print(f'Скорость выполнения: {round((end - start) / items_count, 2)} секунд на 1 элемент')

    print(f'Время выполнения парсинга: {minutes_1} минут {seconds_1} секунд')
    print(f'Скорость выполнения: {round((end_1 - start_1) / items_count, 2)} секунд на 1 элемент')

    start_2 = time.time()

    upload_products_info(result)

    end_2 = time.time()

    minutes_2 = int(end_2 - start_2) // 60
    seconds_2 = int(end_2 - start_2) % 60

    print(f'Время выполнения загрузки: {minutes_2} минут {seconds_2} секунд')


if __name__ == '__main__':
    main()
