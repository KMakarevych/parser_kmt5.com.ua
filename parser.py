import requests
import csv
import re
from bs4 import BeautifulSoup

class PARSER(object):
    urls = [
        'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-61-12-pro-61-black',
        'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-61-12-pro-61-green',
        'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-61-12-pro-61-red',
        'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-pro-max-67-black'
    ]
    SOUP = object
    HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'accept': '*/*'}
    LINKS=[]
    product_category = ''
    product_name = ''
    product_code = ''
    product_properties = ''
    product_price_usd = ''
    product_pictures = ''
    product_description = ''

    def __init__(self, FILE_IN, FILE_OUT) -> None:
        super().__init__()
        self.FILE_IN = FILE_IN
        self.FILE_OUT = FILE_OUT
        self.firstLineCSV()
        # self.get_section_array()
        self.parce_products_links()
        self.save_to_CSV()

    def get_sections_array(self):
        f = open(self.FILE_IN, "r")
        for i in f:
            self.LINKS.append(i.replace('\n', ''))
        f.close()

    def firstLineCSV(self):
        with open(self.FILE_OUT, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Раздел', 'Название', 'Цена', 'Ссылка на изображение', 'Код товара', 'Подробное описание'])
        file.close()

    def get_html(self, url, params=None):
        r = requests.get(url, headers=self.HEADERS, params=params)
        return r

    def parce_products_links(self):
        for link in self.urls:
            html = self.get_html(link)
            if html.status_code == 200:
                self.SOUP = BeautifulSoup(html.text, 'html.parser')

                breadcrumbs = self.SOUP.select('.breadcrumbs > li')                
                self.product_category = breadcrumbs[-2].get_text()
                self.product_name = self.SOUP.find('div', class_='box-card_right').find('h1').get_text(strip=True)
                product_code = self.SOUP.find('div', class_='box-card_code').get_text(strip=True)
                self.product_code = re.sub(r'Код*:', ':', product_code).split(':')[1]
                self.product_properties = self.SOUP.find('ul', class_='list-description') # не доделано
                self.product_price_usd = self.SOUP.find('div', class_='box-card_hryvnia').get_text(strip=True).replace('$','')
                self.product_pictures = self.SOUP.find('div', class_='slider-big').find('img', class_='main__image').get('src') # не доделано
                self.product_description = self.SOUP.find('div', class_='text-description').get_text(strip=True)

                self.SOUP = object
                self.save_to_CSV()
                

    def save_to_CSV(self):
        with open(self.FILE_OUT, 'a+', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([
                self.product_category,
                self.product_name,
                self.product_price_usd,
                self.product_pictures,
                self.product_code,
                self.product_description
            ])
        file.close()
