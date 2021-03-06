from os import link
import requests
import csv
import re
import time
from bs4 import BeautifulSoup
import asyncio
import aiohttp

class PARSER(object): 

    def __init__(self, IN, OUT) -> None:
        super().__init__()
        self.HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'accept': '*/*'}
        self.IN = IN
        self.OUT = OUT
        self.categories = []
        self.categoriesWithPagination = []
        self.productsLinks = []  
        self.PRODUCTS = []
        self.firstLineCSV()
        # Получим список разделов из файла categories.txt и добавим его в метод LINKS
        # После выполнения в методе LINKS будет список разделов
        self.getLinksFromCategories()
        # Из списка ссылок в файле обьявим массив ссылок с пагинацией и запишем в файл categoriesWithPagination.txt
        # После выполнения появится файл со ссылками с учётом пагинации и метод класса LINKS
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(self.asynchronousGetPagination())
        with open('categoriesWithPagination.txt', 'w') as file:
            for i in self.categoriesWithPagination:
                file.write(i + '\n')
        file.close()
        self.categories.clear()
        # Получим ссылки на сстраницы товаров из метода LINKS
        # На выходе переопределим метод LINKS и занесём в него список ссылок
        # Также запишем ссылки в файл
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(self.asynchronousGetLinks())
        with open('productsLinks.txt', 'w') as file:
            for i in self.productsLinks:
                file.write(i + '\n')
        file.close()
        self.categoriesWithPagination.clear()
        
        self.productsLinksSeparated = [self.productsLinks[d:d+20] for d in range(0, len(self.productsLinks), 20)]
        self.productsLinks.clear()
        # Спарсим данные отдельных товаров из метода LINKS
        # # Положим данные в словарь PRODUCTS
        for i in self.productsLinksSeparated:
            self.PRODUCTS.clear()
            ioloop = asyncio.get_event_loop()
            ioloop.run_until_complete(self.asynchronousParseData(i))
            self.saveToCsv()
        
        

    def firstLineCSV(self):
        with open(self.OUT, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Код_товара', 'Название_позиции', 'Название_позиции_укр', 'Описание', 'Описание_укр', 'Цена', 'Валюта', 'Единица_измерения', 'Ссылка_изображения', 'Наличие', 'Идентификатор_товара', 'Категория', 'Полный путь'])
        file.close()

    def getHtml(self, url, params=None):
        r = requests.get(url, headers=self.HEADERS, params=params)
        return r

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
                    i['code'],
                    i['category'],
                    i['breadcrumbs']
                ])
            file.close()            

    def getLinksFromCategories(self):
        try:
            array = []
            f = open(self.IN, "r")
            for i in f:
                array.append(i.replace('\n', ''))
            f.close()
            self.categories = array
        except:
            print('Не удалось прочитать файл')

    async def parserDataAsync(self, url):
        session = aiohttp.ClientSession()
        async with session.get(url) as response:
            html = await response.text()
            
            product = {}
            soup = BeautifulSoup(html, 'html.parser')
            
            product['breadcrumbs'] = [i.get_text() for i in soup.select('.breadcrumbs > li')]
            del product['breadcrumbs'][-1]
            product['category'] = product['breadcrumbs'][-1]
            product['breadcrumbs'] = ', '.join(product['breadcrumbs'])
            product['name'] = soup.find('div', class_='box-card_right').find('h1').get_text(strip=True).replace(';',',')
            product['code'] = re.sub(r'Код*:', ':', soup.find('div', class_='box-card_code').get_text(strip=True)).split(':')[1].replace(';',',')
            product['price'] = soup.find('div', class_='box-card_hryvnia').get_text(strip=True).replace('$', '')
            product['pic_link'] = soup.find('div', class_='slider-big').find('img', class_='main__image').get('src')
            if soup.find('div', class_='text-description').get_text(strip=True).replace(';',',') == '':
                product['description'] = 'Описание отсутствует.'
            else:
                product['description'] = self.product_description = soup.find('div', class_='text-description').get_text(strip=True).replace(';',',')
            self.PRODUCTS.extend([product])
        await session.close()

    async def getProductsLinksAsync(self, url):
        session = aiohttp.ClientSession()
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            array = soup.find_all('div', class_='list-catalog_item')
            array = [item.find('a').get('href') for item in array]
            self.productsLinks.extend(array)
        await session.close()

    async def getPaginationAsync(self, url):
        session = aiohttp.ClientSession()
        async with session.get(url) as response:
            counter = 1
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            elements = len(soup.find_all('div', class_='list-catalog_item'))
            if response.status == 200 and elements > 0:
                self.categoriesWithPagination.extend([url])
                while response.status == 200 and elements > 0:
                    counter = counter + 1
                    async with session.get(url+'?page='+str(counter)) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        elements = len(soup.find_all('div', class_='list-catalog_item'))
                        if elements > 0:
                            self.categoriesWithPagination.extend([url+'?page='+str(counter)])
                else:
                    pass
            else:
                pass
        await session.close()

    async def asynchronousGetLinks(self):
        start = time.time()
        print("Получим список ссылок на товары")
        tasks = [asyncio.ensure_future(
            self.getProductsLinksAsync(i)) for i in self.categoriesWithPagination]
        await asyncio.wait(tasks)
        print("Process took: {:.2f} seconds".format(time.time() - start))
        
    async def asynchronousParseData(self, array):
        start = time.time()
        print("Парсим данные")
        tasks = [asyncio.ensure_future(
            self.parserDataAsync(i)) for i in array]
        await asyncio.wait(tasks)
        print("Process took: {:.2f} seconds".format(time.time() - start))

    async def asynchronousGetPagination(self):
        start = time.time()
        print("Получаем ссылки пагинации")
        tasks = [asyncio.ensure_future(
            self.getPaginationAsync(i)) for i in self.categories]
        await asyncio.wait(tasks)
        print("Process took: {:.2f} seconds".format(time.time() - start))