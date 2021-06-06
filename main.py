from myParser import PARSER


urls = [
    'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-61-12-pro-61-black',
    'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-61-12-pro-61-green',
    'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-61-12-pro-61-red',
    'https://kmt5.com.ua/jeystone-jack-series-case-iphone-12-pro-max-67-black'
]
FILEIN='sitemap.txt'
FILEOUT='products.csv'


parser = PARSER(FILEIN, FILEOUT)
