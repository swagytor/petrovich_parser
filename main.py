import pprint
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from services import get_page_info, get_items_ids, get_web_driver, get_item_data, upload_products_info, \
    get_list_of_category_ids, get_category_info
from multiprocessing import Pool

BASE_URL = 'https://petrovich.ru'

def main(category_ids):
    start = time.time()

    with Pool(4) as p1:
        category_items = p1.map(get_category_info, category_ids)

    for category in category_items:
        category_title = category['category_title']
        items_ids = category['item_ids']
        # category_title = category['category_title']
        # print(f'Категория: {category_title}', {category['category_id']})
        with Pool(6) as p2:
            result = p2.map(get_item_data, items_ids)

        print(f'Кол-во данных: {len(result)}')

        # pprint.pprint(result)

        upload_products_info(category_title, result)

        with open('used_categories.txt', 'a') as file:
            file.write(category['category_id'] + '\n')

    end = time.time()

    minutes = int(end - start) // 60
    seconds = int(end - start) % 60

    print(f'Время выполнения: {minutes} минут {seconds} секунд')


if __name__ == '__main__':
    category_ids = get_list_of_category_ids()

    while category_ids:
        main(category_ids)
        category_ids = get_list_of_category_ids()
