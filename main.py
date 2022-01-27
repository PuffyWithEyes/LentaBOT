import threading
import requests
from bs4 import BeautifulSoup
import json
import time
import fake_useragent
from selenium import webdriver
import csv


main_dict = []


url = 'https://lenta.com/catalog/'
useragent = fake_useragent.UserAgent().random
headers = {
    'User-Agent': useragent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

r = requests.get(url=url, headers=headers)

soup = BeautifulSoup(r.text, 'lxml')
cards = soup.find_all('a', class_='group-card')

categories_dicts = {}
for card in cards:
    card_title = card.find('div', class_='group-card__title').text.strip()
    card_url = f'https://lenta.com{card.get("href")}'

    card_id = card_url.split('/')[-2]

    categories_dicts[card_id] = {
        'category_name': card_title,
        'category_href': card_url
    }

with open('data/categories.json', 'w', encoding='utf-8') as file:
    json.dump(categories_dicts, file, indent=4, ensure_ascii=False)


def check_new_categories():
    with open('data/categories.json', encoding='utf-8') as file_0:
        card_dict = json.load(file_0)

    url_0 = 'https://lenta.com/catalog/'
    headers_0 = {
        'User-Agent': useragent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    r_0 = requests.get(url=url_0, headers=headers_0)

    soup_0 = BeautifulSoup(r_0.text, 'lxml')
    cards_0 = soup_0.find_all('a', class_='group-card')

    fresh_categories = {}
    for card_0 in cards_0:
        card_url_0 = f'https://lenta.com{card_0.get("href")}'
        card_id_0 = card_url_0.split('/')[-2]

        if card_id_0 in card_dict:
            continue
        else:
            card_title_0 = card_0.find('div', class_='group-card__title').text.strip()

            categories_dicts[card_id_0] = {
                'category_name': card_title_0,
                'category_href': card_url_0
            }

            fresh_categories[card_id_0] = {
                'category_name': card_title_0,
                'category_href': card_url_0
            }

        with open('data/categories.json', 'w', encoding='utf-8') as file_0:
            json.dump(categories_dicts, file_0, indent=4, ensure_ascii=False)

        return fresh_categories


def get_data_with_selenium():
    global driver
    numeral = 0
    count = 0
    products_dicts = {}
    product_dict = []
    with open('data/number_parser.txt', 'a', encoding='utf-8') as file_count:
        file_count.write('0 ')

    with open('data/number_parser.txt', encoding='utf-8') as file_count:
        counter = int(file_count.read().count('0'))

    for card_0 in cards:
        cards_url = f'https://lenta.com{card_0.get("href")}'
        card_id_0 = cards_url.split('/')[-2].replace('-', '_')
        options = webdriver.FirefoxOptions()
        options.set_preference('general.useragent.override',
                               useragent)
        try:
            driver = webdriver.Firefox(
                executable_path='D:\\Python Projects\\LentaBOT\\geckodriver.exe',
                options=options
            )
            driver.get(url=cards_url)
            time.sleep(5)

            with open(f'data/{numeral}. {card_id_0}.html', 'w', encoding='utf-8') as file_0:
                file_0.write(driver.page_source)

        except Exception as ex:
            print(ex)

        finally:
            driver.close()
            driver.quit()

        with open(f'data/{numeral}. {card_id_0}.html', encoding='utf-8') as file_0:
            src = file_0.read()

        s_soup = BeautifulSoup(src, 'lxml')
        try:
            product_dict.clear()
            pagination = int(s_soup.find('ul', class_='pagination').find_all('a')[-2].text)
            for page in range(1, pagination + 1):
                url_0 = f'{cards_url}?page={page}'
                response = requests.get(url=url_0, headers=headers)
                soup_0 = BeautifulSoup(response.text, 'lxml')
                products_items = soup_0.find_all('div', class_='sku-card-small-container')
                for product_item in products_items:

                    try:
                        product_name = product_item.find('div', class_='sku-card-small__title').text.strip()
                    except:
                        product_name = 'Продукт не нашёлся!'

                    try:
                        product_href = product_item.find('a', class_='sku-card-small sku-card-small--ecom')
                        card_url_0 = f'https://lenta.com{product_href.get("href")}'
                    except:
                        card_url_0 = 'Ссылка не нашлась!'

                    try:
                        product_sale = product_item.find('div',
                                                         class_='discount'
                                                                '-label-small discount-label-small--'
                                                                'sku-card sku-card-small__discount-label').text.strip()
                    except:
                        product_sale = 'Скидки нет!'

                    all_prices = product_item.find_all('div',
                                                       class_='sku-prices-block__item sku-prices-block__item--primary')

                    for price in all_prices:
                        currency = price.find('span', class_='sku-price__weight')
                        try:
                            price_rubles = price.find('span', class_='price-label__integer').text.strip()
                            secret_price = f'{price_rubles}'
                        except:
                            secret_price = 'Цена не найдена!'
                        if currency:
                            price_rubles = price.find('span', class_='price-label__integer').text.strip()
                            price_copes = price.find('small', class_='price-label__fraction').text.strip()
                            currency_0 = price.find('span', class_='sku-price__weight').text.strip()
                            all_price = f'{price_rubles},{price_copes}₽{currency_0}'
                        else:
                            price_rubles = price.find('span', class_='price-label__integer').text.strip()
                            price_copes = price.find('small', class_='price-label__fraction').text.strip()
                            all_price = f'{price_rubles},{price_copes}₽'

                        products_dicts[count] = {
                            'product_name': product_name,
                            'product_url': card_url_0,
                            'product_price': all_price,
                            'product_sale': product_sale,
                            'secret_price': secret_price
                        }

                        main_dict.append(
                            {
                                'product_name': product_name,
                                'product_url': card_url_0,
                                'product_price': all_price,
                                'product_sale': product_sale,
                                'secret_price': secret_price
                            }
                        )

                        product_dict.append(
                            {
                                'product_name': product_name,
                                'card_url': card_url,
                                'product_price': all_price,
                                'product_sale': product_sale,
                                'only_rubles': secret_price
                            }
                        )

                    time.sleep(1.5)

                    try:
                        with open(f"data/{counter}_all_products.json", encoding='utf-8') as file_reader:
                            json.load(file_reader)

                        with open(f"data/{counter}_all_products.json", 'a', encoding='utf-8') as file_append_json:
                            json.dump(products_dicts, file_append_json, indent=4, ensure_ascii=False)

                        for product in main_dict:
                            with open(f"data/{counter}_all_products.csv", 'a', newline='', encoding='utf-8') \
                                    as file_append_csv:
                                writer = csv.writer(file_append_csv)

                                writer.writerow(
                                    (
                                        product['product_name'],
                                        product['product_url'],
                                        product['product_price'],
                                        product['product_sale'],
                                        product['secret_price']
                                    )
                                )

                    except:
                        with open(f"data/{counter}_all_products.json", 'w', encoding='utf-8') as file_writer_json:
                            json.dump(products_dicts, file_writer_json, indent=4, ensure_ascii=False)

                        with open(f"data/{counter}_all_products.csv", 'w', newline='', encoding='utf-8')\
                                as file_writer_csv:
                            writer = csv.writer(file_writer_csv)

                            writer.writerow(
                                (
                                    'Наименование',
                                    'URL',
                                    'Цена по карте "Лента"',
                                    'Скидка в процентах',
                                    'Цена в рублях(без копеек)'
                                )
                            )

                        for product in main_dict:
                            with open(f"data/{counter}_all_products.csv", 'a', newline='', encoding='utf-8')\
                                    as file_append_csv:
                                writer = csv.writer(file_append_csv)

                                writer.writerow(
                                    (
                                        product['product_name'],
                                        product['product_url'],
                                        product['product_price'],
                                        product['product_sale'],
                                        product['secret_price']
                                    )
                                )

                    with open(f"data/{numeral}.csv", 'w', newline='', encoding='utf-8') as file_0:
                        writer = csv.writer(file_0)

                        writer.writerow(
                            (
                                'Наименование',
                                'URL',
                                'Цена по карте "Лента"',
                                'Скидка в процентах',
                                'Цена в рублях(без копеек)'
                            )
                        )

                    for product in product_dict:
                        with open(f"data/{numeral}.csv", 'a', newline='', encoding='utf-8') as file_0:
                            writer = csv.writer(file_0)

                            writer.writerow(
                                (
                                    product['product_name'],
                                    product['card_url'],
                                    product['product_price'],
                                    product['product_sale'],
                                    product['only_rubles']
                                )
                            )

                    count += 1

            with open(f"data/{numeral}.json", 'w', encoding='utf-8') as file_0:
                json.dump(product_dict, file_0, indent=4, ensure_ascii=False)

            product_dict.clear()

            numeral += 1
        except:
            product_dict.clear()
            for page in range(1, 2):
                url_0 = f'{cards_url}?page={page}'
                response = requests.get(url=url_0, headers=headers)
                soup_0 = BeautifulSoup(response.text, 'lxml')
                products_items = soup_0.find_all('div', class_='sku-card-small-container')
                for product_item in products_items:

                    try:
                        product_name = product_item.find('div', class_='sku-card-small__title').text.strip()
                    except:
                        product_name = 'Продукт не нашёлся!'

                    try:
                        product_href = product_item.find('a', class_='sku-card-small sku-card-small--ecom')
                        card_url_0 = f'https://lenta.com{product_href.get("href")}'
                    except:
                        card_url_0 = 'Ссылка не нашлась!'

                    try:
                        product_sale = product_item.find('div',
                                                         class_='discount'
                                                                '-label-small discount-label-small--'
                                                                'sku-card sku-card-small__discount-label').text.strip()
                    except:
                        product_sale = 'Скидки нет!'

                    all_prices = product_item.find_all('div',
                                                       class_='sku-prices-block__item sku-prices-block__item--primary')

                    for price in all_prices:
                        currency = price.find('span', class_='sku-price__weight')
                        try:
                            price_rubles = price.find('span', class_='price-label__integer').text.strip()
                            secret_price = f'{price_rubles}'
                        except:
                            secret_price = 'Цена не найдена!'
                        if currency:
                            price_rubles = price.find('span', class_='price-label__integer').text.strip()
                            price_copes = price.find('small', class_='price-label__fraction').text.strip()
                            currency_0 = price.find('span', class_='sku-price__weight').text.strip()
                            all_price = f'{price_rubles},{price_copes}₽{currency_0}'
                        else:
                            price_rubles = price.find('span', class_='price-label__integer').text.strip()
                            price_copes = price.find('small', class_='price-label__fraction').text.strip()
                            all_price = f'{price_rubles},{price_copes}₽'

                        products_dicts[count] = {
                            'product_name': product_name,
                            'product_url': card_url_0,
                            'product_price': all_price,
                            'product_sale': product_sale,
                            'secret_price': secret_price
                        }

                        main_dict.append(
                            {
                                'product_name': product_name,
                                'product_url': card_url_0,
                                'product_price': all_price,
                                'product_sale': product_sale,
                                'secret_price': secret_price
                            }
                        )

                        product_dict.append(
                            {
                                'product_name': product_name,
                                'card_url': card_url,
                                'product_price': all_price,
                                'product_sale': product_sale,
                                'only_rubles': secret_price
                            }
                        )

                    time.sleep(1.5)

                    try:
                        with open(f"data/{counter}_all_products.json", encoding='utf-8') as file_reader:
                            json.load(file_reader)

                        with open(f"data/{counter}_all_products.json", 'a', encoding='utf-8') as file_append_json:
                            json.dump(products_dicts, file_append_json, indent=4, ensure_ascii=False)

                        for product in main_dict:
                            with open(f"data/{counter}_all_products.csv", 'a', newline='', encoding='utf-8')\
                                    as file_append_csv:
                                writer = csv.writer(file_append_csv)

                                writer.writerow(
                                    (
                                        product['product_name'],
                                        product['product_url'],
                                        product['product_price'],
                                        product['product_sale'],
                                        product['secret_price']
                                    )
                                )

                    except:
                        with open(f"data/{counter}_all_products.json", 'w', encoding='utf-8') as file_writer_json:
                            json.dump(products_dicts, file_writer_json, indent=4, ensure_ascii=False)

                        with open(f"data/{counter}_all_products.csv", 'w', newline='', encoding='utf-8')\
                                as file_writer_csv:
                            writer = csv.writer(file_writer_csv)

                            writer.writerow(
                                (
                                    'Наименование',
                                    'URL',
                                    'Цена по карте "Лента"',
                                    'Скидка в процентах',
                                    'Цена в рублях(без копеек)'
                                )
                            )

                        for product in main_dict:
                            with open(f"data/{counter}_all_products.csv", 'a', newline='', encoding='utf-8')\
                                    as file_append_csv:
                                writer = csv.writer(file_append_csv)

                                writer.writerow(
                                    (
                                        product['product_name'],
                                        product['product_url'],
                                        product['product_price'],
                                        product['product_sale'],
                                        product['secret_price']
                                    )
                                )

                    with open(f"data/{numeral}.csv", 'w', newline='', encoding='utf-8') as file_0:
                        writer = csv.writer(file_0)

                        writer.writerow(
                            (
                                'Наименование',
                                'URL',
                                'Цена по карте "Лента"',
                                'Скидка в процентах',
                                'Цена в рублях(без копеек)'
                            )
                        )

                    for product in product_dict:
                        with open(f"data/{numeral}.csv", 'a', newline='', encoding='utf-8') as file_0:
                            writer = csv.writer(file_0)

                            writer.writerow(
                                (
                                    product['product_name'],
                                    product['card_url'],
                                    product['product_price'],
                                    product['product_sale'],
                                    product['only_rubles']
                                )
                            )

                    count += 1

            with open(f"data/{numeral}.json", 'w', encoding='utf-8') as file_0:
                json.dump(product_dict, file_0, indent=4, ensure_ascii=False)

            product_dict.clear()

            numeral += 1


def main():
    new_categories_thread = threading.Thread(target=check_new_categories)
    selenium_thread = threading.Thread(target=get_data_with_selenium)

    new_categories_thread.start()
    selenium_thread.start()

    new_categories_thread.join()
    selenium_thread.join()


if __name__ == '__main__':
    main()
