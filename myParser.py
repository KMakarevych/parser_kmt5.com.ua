from os import link
import requests
import csv
import re
from bs4 import BeautifulSoup

class PARSER(object):
    SOUP = object
    HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'accept': '*/*'}
    LINKS=[]
    product_category = ''
    product_name = ''
    product_code = ''
    # product_properties = ''
    product_price_usd = ''
    product_pictures = ''
    product_description = ''

    def __init__(self, IN, OUT) -> None:
        super().__init__()
        self.IN = IN
        self.OUT = OUT
        self.firstLineCSV()
        self.getLinksForParsing()
        self.parce_products_links()
        self.save_to_CSV()

    def getLinksArray(self):
        f = open(self.FILE_IN, "r")
        for i in f:
            self.LINKS.append(i.replace('\n', ''))
        f.close()

    def firstLineCSV(self):
        with open(self.OUT, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Раздел', 'Название', 'Цена', 'Ссылка на изображение', 'Код товара', 'Подробное описание'])
        file.close()

    def get_html(self, url, params=None):
        r = requests.get(url, headers=self.HEADERS, params=params)
        return r

    def parce_products_links(self):
        for link in self.LINKS:
            print(link)
            html = self.get_html(link)
            if html.status_code == 200:
                self.SOUP = BeautifulSoup(html.text, 'html.parser')

                breadcrumbs = self.SOUP.select('.breadcrumbs > li')                
                self.product_category = breadcrumbs[-2].get_text().replace(';',',').replace('$', '').replace('"','')
                self.product_name = self.SOUP.find('div', class_='box-card_right').find('h1').get_text(strip=True).replace(';',',').replace('$', '').replace('"','')
                product_code = self.SOUP.find('div', class_='box-card_code').get_text(strip=True)
                self.product_code = re.sub(r'Код*:', ':', product_code).split(':')[1].replace(';',',').replace('$', '').replace('"','')
                # self.product_properties = self.SOUP.find('ul', class_='list-description') # не доделано
                self.product_price_usd = self.SOUP.find('div', class_='box-card_hryvnia').get_text(strip=True).replace(';',',').replace('$', '').replace('"','')
                self.product_pictures = self.SOUP.find('div', class_='slider-big').find('img', class_='main__image').get('src').replace(';',',').replace('$', '').replace('"','') # не доделано
                product_description = self.SOUP.find('div', class_='text-description').get_text(strip=True).replace(';',',').replace('$', '').replace('"','')
                if product_description == '':
                    self.product_description = 'Описание отсутствует.'
                else:
                    self.product_description = self.SOUP.find('div', class_='text-description').get_text(strip=True).replace(';',',').replace('$', '').replace('"','')

                self.save_to_CSV()
                

    def save_to_CSV(self):
        with open(self.OUT, 'a+', newline='') as file:
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

    def getLinksForParsing(self):
        if isinstance(self.IN, list):
            self.LINKS.extend(self.IN)
        if isinstance(self.IN, str):
            try:
                f = open(self.IN, "r")
                for i in f:
                    self.LINKS.append(i.replace('\n', ''))
                f.close()
            except:
                print('Не удалось прочитать файл')
