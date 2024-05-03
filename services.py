import pprint
import time
from math import ceil
from multiprocessing.pool import Pool

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Side, Border, Alignment, Font
from selenium import webdriver
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By

import settings
from google_services import download_file_from_google_drive, upload_file_to_google_drive

ITEMS_PER_PAGE = 20
BASE_URL = 'https://petrovich.ru'
thins = Side(border_style="thin", color="000000")
bold = Side(border_style="medium", color="000000")
thin_border = Border(left=thins, right=thins, top=thins, bottom=thins)
bold_border = Border(left=bold, right=bold, top=bold, bottom=bold)
bold_font = Font(bold=True)
align = Alignment(horizontal='center', vertical='center')


# def check_proxies(proxy):
#     print(f'Пробуем {proxy}')
#     proxy = proxy.strip()
#     try:
#         res = requests.get('https://petrovich.ru/', proxies={'http': proxy,
#                                                              'https': proxy}, )
#
#         if res.status_code == 200:
#             print(proxy)
#     except:
#         pass

def get_web_driver():
    # PROXY = '122.118.196.240:8088'

    ua = UserAgent(platforms='pc', os=['windows', 'macos', 'linux'])
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--no-sandbox')
    # options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--proxy-server=93.157.248.108:88')
    # options.add_argument('--proxy-server=http://%s' % PROXY)

    driver = webdriver.Chrome(options)

    return driver


def get_page_info():
    driver = get_web_driver()
    driver.implicitly_wait(5)
    driver.get(url=f'{BASE_URL}/catalog/1590/')

    tries_count = 0

    # while True:
    #     if tries_count >= 10:
    #         return {}
    #     try:
    #         items_count_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="products-counter"]')
    #         break
    #     except (StaleElementReferenceException, NoSuchElementException):
    #         time.sleep(2)
    #         tries_count += 1

    try:
        items_count_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="products-counter"]')
    except StaleElementReferenceException:
        time.sleep(1)
        items_count_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="products-counter"]')

    # items_count_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="products-counter"]')
    items_count = int(items_count_elem.text.split(': ')[-1])

    page_count = ceil(items_count / ITEMS_PER_PAGE) + 1

    driver.close()

    return items_count, page_count


def get_items_ids(max_pages):
    result = []

    for page in range(max_pages):
        driver = get_web_driver()
        driver.get(f'{BASE_URL}/catalog/1590/?p={page}')

        time.sleep(1.5)

        bs = BeautifulSoup(driver.page_source, 'html.parser')

        items = bs.find_all('div', class_='fade-in-list')

        for ind, item in enumerate(items, 1):
            item_info = item.find('p', class_='swiper-no-swiping')
            result.append(item_info.text)

        driver.close()

    return result


def get_item_data(item_id):
    driver = get_web_driver()

    driver.get(f'{BASE_URL}/product/{item_id}/')

    time.sleep(0.5)

    tries_count = 0

    while True:
        if tries_count >= 10:
            return
        try:
            driver.find_element(By.CSS_SELECTOR, '[data-test="product-characteristics-tab"]').click()
            break
        except (StaleElementReferenceException, NoSuchElementException):
            time.sleep(2)
            tries_count += 1

    # try:
    #     driver.find_element(By.CSS_SELECTOR, '[data-test="product-characteristics-tab"]').click()
    # except (StaleElementReferenceException, NoSuchElementException):
    #     time.sleep(4)
    #     driver.find_element(By.CSS_SELECTOR, '[data-test="product-characteristics-tab"]').click()

    bs = BeautifulSoup(driver.page_source, 'html.parser')

    title = bs.find('h1', class_='title-lg')
    if title:
        title = title.text

    price = bs.find('p', attrs={'data-test': 'product-gold-price'})
    if price:
        price = price.text.split(r'\u')[0]

    item_data = {
        'ID': item_id,
        'Название': title,
        'Цена': price
    }

    product_tabs = bs.find_all('span', class_='product-title-text')

    properties_table = None

    for tab in product_tabs:
        if tab.text == 'Характеристики':
            properties_table = tab.parent.parent.find('ul', class_='product-properties-list listing-data')
            break

    if properties_table:
        for li in properties_table.find_all('li'):
            item_key = li.find('div', class_='title').text
            item_value = li.find('div', class_='value').text

            item_data[item_key] = item_value
    return item_data


# get_item_data(170014)

def upload_products_info(data):
    # data = [
    #     {'ID': '656216',
    #      'Название': 'Наличник 70х8х2150 мм финишпленка серый (1 шт.)',
    #      'Цена': '270 ₽',
    #      'Тип товара': 'Наличник',
    #      'Бренд': 'Verda ДПГ',
    #      'Страна-производитель': 'Россия',
    #      'Материал': 'МДФ',
    #      'Покрытие': 'Финишпленка',
    #      'Фактура': 'Гладкая',
    #      'Влагостойкость': 'Да',
    #      'Цвет производителя': 'Серый',
    #      'Длина, мм': '2150',
    #      'Форма': 'Плоская',
    #      'Конструкция наличника': 'Простая',
    #      'Коллекция': 'Verda',
    #      'Вес, кг': '0,8'},
    #     {'ID': '612180',
    #      'Название': 'Наличник гладкий 50х11х2200 мм сорт Экстра сращенный',
    #      'Цена': '198 ₽',
    #      'Артикул': '3802',
    #      'Тип товара': 'Наличник',
    #      'Сортность': 'Экстра',
    #      'Страна-производитель': 'Россия',
    #      'Толщина, мм': '11',
    #      'Материал': 'Массив хвойных пород',
    #      'Покрытие': 'Без покрытия',
    #      'Фактура': 'Гладкая',
    #      'Влагостойкость': 'Да',
    #      'Ширина, мм': '50',
    #      'Длина, мм': '2200',
    #      'Форма': 'Плоская',
    #      'Конструкция наличника': 'Простая',
    #      'Вес, кг': '0,61'},
    #     {'ID': '692289',
    #      'Название': 'Наличник Палитра/Сафари/Норд 70х8х2140 мм финишпленка белый '
    #                  'прямой (1 шт.)',
    #      'Цена': '260 ₽',
    #      'Тип товара': 'Наличник',
    #      'Бренд': 'СД',
    #      'Страна-производитель': 'Россия',
    #      'Материал': 'МДФ',
    #      'Покрытие': 'Финишпленка',
    #      'Фактура': 'Структурированная',
    #      'Влагостойкость': 'Да',
    #      'Цвет производителя': 'Белый',
    #      'Длина, мм': '2140',
    #      'Форма': 'Плоская',
    #      'Конструкция наличника': 'Простая',
    #      'Коллекция': 'Палитра',
    #      'Упаковка': 'Полиэтилен',
    #      'Вес, кг': '0,7'}
    # ]

    file = download_file_from_google_drive(settings.FILE_ID, settings.FILE_NAME)

    wb = load_workbook(settings.FILE_NAME)

    ws = wb.active

    headers = []

    for product in data:
        for key in product.keys():
            if key not in headers:
                headers.append(key)
        # headers = [col[0].value for col in [row for row in ws.iter_rows(min_row=1, max_row=1, max_col=30)] if col[0].value is not None]

    for col, value in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = value
        cell.alignment = align
        cell.border = bold_border
        cell.font = bold_font

    print(headers)

    for ind, product in enumerate(data, 2):
        for row in ws.iter_rows(min_row=ind, max_row=ind, max_col=len(headers)):
            for col in row:
                col.border = thin_border

        for key, value in product.items():
            column = headers.index(key) + 1
            cell = ws.cell(row=ind, column=column)
            cell.value = value

            # print(key, ws.cell(row=ind, column=column).value)

        # for key, value in product.items():
        #     for row in ws.iter_rows(min_row=1, max_row=1, max_col=30):
        #         for col in row:
        #             if not col.value:
        #                 col.value = key
        #                 break
        # print(row)
        # if key == col[0].value:
        #     col[0].value = value

    wb.save(settings.FILE_NAME)

    upload_file_to_google_drive(file, settings.FILE_NAME)

# with open('proxy_list.txt') as f:
#     proxies = f.readlines()
#
# print(proxies)
#
# with Pool(5) as p:
#     p.map(check_proxies, proxies)
# # check_proxies()