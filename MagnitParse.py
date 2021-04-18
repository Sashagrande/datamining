import requests
import bs4
from urllib.parse import urljoin
import pymongo
from dateutil.parser import parse
from datetime import datetime

MONTH_DICT = {
    'янв': '01',
    'фев': '02',
    'мар': '03',
    'апр': '04',
    'мая': '05',
    'июн': '06',
    'июл': '07',
    'авг': '08',
    'сен': '09',
    'окт': '10',
    'ноя': '11',
    'дек': '12'

}
class MagnitParse:

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        db = db_client['gb_datamining']
        self.collection = db['magnit']

    def _get_response(self, url):
        return requests.get(url)

    def _get_soup(self, url):
        return bs4.BeautifulSoup(self._get_response(url).text, 'lxml')

    def run(self):

        for product in self._parse(self.start_url):
            self._save(product)

    @property
    def _template(self):
        return {
            'product_name': lambda tag: tag.find('div', attrs={'class': 'card-sale__title'}).text,
            'url': lambda tag: urljoin(self.start_url, tag.attrs.get('href', '')),
            'promo_name': lambda a: a.find('div', attrs={'class': 'card-sale__name'}).text,
            'old_price': lambda a: float('.'.join(price for price in a.find('div',
            attrs={'class': 'label__price_old'}).text.split())),
            'new_price': lambda a: float('.'.join(price for price in a.find('div',
            attrs={'class': 'label__price_new'}).text.split())),
            'image_url': lambda a: urljoin(self.start_url, a.find('img').attrs.get('data-src')),
            'date_from': lambda a: self._get_date(a.find('div', attrs={'class': 'card-sale__date'}).text, 'from'),
            'date_to': lambda a: self._get_date(a.find('div', attrs={'class': 'card-sale__date'}).text, 'to')
        }


    def _get_date(self, date_str:str, *args):
        tmp = date_str.split('\n')[1:-1]
        if 'from' in args:
            tmp = tmp[0].split(' ')
            date = parse(str(datetime.now().year) + MONTH_DICT[tmp[2][:3]] + tmp[1]).strftime('%d-%m-%Y')
        else:
            tmp = tmp[1].split(' ')
            date = parse(str(datetime.now().year) + MONTH_DICT[tmp[2][:3]] + tmp[1]).strftime('%d-%m-%Y')
        return date



    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        product_tags = catalog_main.find_all('a', recursive=False)
        for product_tag in product_tags:
            product = {}
            for key, func in self._template.items():
                try:
                    product[key] = func(product_tag)
                except:
                    pass
            yield product

    def _save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    url = 'https://magnit.ru/promo/'
    db_client = pymongo.MongoClient('mongodb://localhost:27017')
    parser = MagnitParse(url, db_client)
    parser.run()
