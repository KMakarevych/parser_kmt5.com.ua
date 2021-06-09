from os import link
import requests
import csv
import re
from bs4 import BeautifulSoup

class PARSER(object): 

    def __init__(self, IN, OUT) -> None:
        super().__init__()
        self.HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'accept': '*/*'}
        self.IN = IN
        self.OUT = OUT   
        self.firstLineCSV()
        # Получим список разделов из файла categories.txt и добавим его в метод LINKS
        # После выполнения в методе LINKS будет список разделов
        self.getLinks()
        # Из списка ссылок в файле обьявим массив ссылок с пагинацией и запишем в файл categoriesWithPagination.txt
        # После выполнения появится файл со ссылками с учётом пагинации и метод класса LINKS
        self.getPagination()
        # Получим ссылки на сстраницы товаров из метода LINKS
        # На выходе переопределим метод LINKS и занесём в него список ссылок
        # Также запишем ссылки в файл
        self.getProducts()
        # Спарсим данные отдельных товаров из метода LINKS
        # Положим данные в словарь PRODUCTS
        self.parseProductsLinks()
        # Заполним файл products.csv данными
        self.saveToCsv()



    def firstLineCSV(self):
        with open(self.OUT, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Код_товара', 'Название_позиции', 'Название_позиции_укр', 'Описание', 'Описание_укр', 'Цена', 'Валюта', 'Единица_измерения', 'Ссылка_изображения', 'Наличие', 'Идентификатор_товара'])
        file.close()

    def getHtml(self, url, params=None):
        r = requests.get(url, headers=self.HEADERS, params=params)
        return r

    def parseProductsLinks(self):
        self.PRODUCTS = []
        for link in self.LINKS:
            print(link)
            product = {}
            html = self.getHtml(link)
            if html.status_code == 200:
                self.SOUP = BeautifulSoup(html.text, 'html.parser')
                breadcrumbs = self.SOUP.select('.breadcrumbs > li')   
                product_code = self.SOUP.find('div', class_='box-card_code').get_text(strip=True)
                product_description = self.SOUP.find('div', class_='text-description').get_text(strip=True).replace(';',',')
             
            
                product['category'] = breadcrumbs[-2].get_text().replace(';',',')
                product['name'] = self.SOUP.find('div', class_='box-card_right').find('h1').get_text(strip=True).replace(';',',')
                product['code'] = re.sub(r'Код*:', ':', product_code).split(':')[1].replace(';',',')
                product['price'] = self.SOUP.find('div', class_='box-card_hryvnia').get_text(strip=True).replace('$', '')
                product['pic_link'] = self.SOUP.find('div', class_='slider-big').find('img', class_='main__image').get('src')
                if product_description == '':
                    product['description'] = 'Описание отсутствует.'
                else:
                    product['description'] = self.product_description = self.SOUP.find('div', class_='text-description').get_text(strip=True).replace(';',',')
                
                self.PRODUCTS.extend([product])              

    def saveToCsv(self):
        for i in self.PRODUCTS:
            with open(self.OUT, 'a+', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow([
                    i['code'],
                    i['name'],
                    '',
                    i['description'],
                    '',
                    i['price'],
                    'USD',
                    'шт.',
                    i['pic_link'],
                    '\'+',
                    i['code']
                ])
            file.close()            

    def getLinks(self):
        try:
            array = []
            f = open(self.IN, "r")
            for i in f:
                array.append(i.replace('\n', ''))
            f.close()
            self.LINKS = array
        except:
            print('Не удалось прочитать файл')

    def getPagination(self):
        counter = 1
        array = []
        for link in self.LINKS:
            self.HTML = self.getHtml(link, 'page=' + str(counter))
            if self.HTML.status_code == 200:
                self.SOUP = BeautifulSoup(self.HTML.text, 'html.parser')
                array.append(link)
                while len(self.SOUP.find_all('div', class_='list-catalog_item')) > 0:
                    counter = counter + 1
                    self.HTML = self.getHtml(link, 'page=' + str(counter))
                    self.SOUP = BeautifulSoup(self.HTML.text, 'html.parser')
                    if len(self.SOUP.find_all('div', class_='list-catalog_item')) > 0:
                        array.append(link + '?page=' + str(counter))
                else:
                    pass
        self.LINKS = array
        with open('categoriesWithPagination.txt', 'w') as file:
            for i in self.LINKS:
                file.write(i + '\n')
        file.close()

    def getProducts(self):
        array = []
        links = []
        for i in self.LINKS:
            self.HTML = self.getHtml(i)
            self.SOUP = BeautifulSoup(self.HTML.text, 'html.parser')
            array = self.SOUP.find_all('div', class_='list-catalog_item')
            for item in array:
                links.extend([item.find('a').get('href')])
        self.LINKS = links
        with open('productsLinksTest.txt', 'w') as file:
            for i in self.LINKS:
                file.write(i + '\n')
        file.close()
