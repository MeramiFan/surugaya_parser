# -*- coding: utf-8 -*-
from requests import session
from urllib.parse import quote, urlencode
from collections import namedtuple
from time import sleep
from bs4 import BeautifulSoup

Item = namedtuple('Item', 'title code category brand release_date price price_normal price_teika')
ItemDetail = namedtuple('ItemDetail', 'title code category release_date price_teika brand model_number')
ItemDS = namedtuple('ItemDS', 'title brand release_date model_number')

KaitoriItem = namedtuple('KaitoriItem', 'title code category price')
KaitoriItemDetail = namedtuple('KaitoriItemDetail',
                               'title jan code catogory release_date price list_price brand model_number picture explanation')

ENCODING = 'utf-8'


def _get(session: session(), url: str, params: dict, brand: str):
    _url = url + '?' + urlencode(params, safe='[,],=') + '&restrict[]=brand=' + quote(str(brand))
    _html = session.get(_url)
    _html.encoding = ENCODING
    return _html


class Search:
    url = "https://www.suruga-ya.jp/search"

    def __init__(self, session: session(), category: str = '', search_word: str = '', brand: str = '', inStock: str = 'On', adult_s: int = 1,
                 is_marketplace: int = 0, page: int = None):
        """
        検索一覧ページの内容を取得する
        :param session:
        :param category:
        :param search_word:
        :param inStock:
        :param adult_s:
        :param is_marketplace:
        :param page:
        """
        self.session = session
        self.category = category
        self.search_word = search_word
        self.brand = brand
        self.inStock = inStock
        self.adult_s = adult_s
        self.is_marketplace = is_marketplace
        self.page = page

        self.items = []

        # ページ指定ある場合
        if page:
            self.items = self._parse_search_page(page)

        # ページ指定なければ結果が取れなくなるまで全ページ
        else:
            page = 1
            while True:
                items = self._parse_search_page(page)

                if not items:
                    break

                self.items += items

                page += 1

                sleep(1)

    def _parse_search_page(self, page: int) -> list:
        """
        検索一覧ページの内容をパースする
        :param page:
        :return:
        """
        params = {'category': self.category, 'search_word': self.search_word, 'inStock': self.inStock, 'adult_s': self.adult_s,
                  'is_marketplace': self.is_marketplace, 'page': page}
        brand = self.brand

        html = _get(self.session, Search.url, params, brand)

        items = []

        soup = BeautifulSoup(html.text, 'html.parser')
        item_html_texts = soup.find_all('div', class_="item")

        for item in item_html_texts:
            item_soup = BeautifulSoup(str(item), 'html.parser')

            title = item_soup.find_all('p', class_='title')[0].text

            code = item_soup.find_all('a')[0]['href']
            code = code.split('/')[-1]

            category = item_soup.find_all('p', class_='condition')[0].text
            category = category.split('|')
            category = [cond.strip() for cond in category]
            category = ','.join(category)

            brand = item_soup.find_all('p', class_='brand')[0].text

            try:
                release_date = item_soup.find_all('p', class_='release_date')[0].text
                release_date = release_date.replace('発売日：', '')
            except IndexError:
                release_date = None

            try:
                price = item_soup.find_all('p', class_='price')[0].text
            except IndexError:
                price = None

            try:
                price_normal = item_soup.find_all('p', class_='price_normal')[0].text
                price_normal = price_normal.replace('中古通常価格', '')
                price_normal = price_normal.replace('税込', '')
                price_normal = price_normal.replace(chr(165), '')
                price_normal = price_normal.replace(',', '')
                price_normal = price_normal.strip()
            except IndexError:
                price_normal = None

            try:
                price_teika = item_soup.find_all('p', class_='price_teika')[0].text
                price_teika = price_teika.replace('中古：', '')
                price_teika = price_teika.replace('税込', '')
                price_teika = price_teika.replace('￥', '')
                price_teika = price_teika.replace(',', '')
                price_teika = price_teika.strip()
            except IndexError:
                price_teika = None

            items.append(Item(title, code, category, brand, release_date, price, price_normal, price_teika))

        return items


class SearchDetail:
    url = "https://www.suruga-ya.jp/product/detail/"

    def __init__(self, session: session(), code: str):
        """
        検索詳細ページの内容を取得する
        :param session:
        :param code:
        """
        self.session = session
        self.code = code

        self.item = self._parse_search_detail_page(self.code)

    def _parse_search_detail_page(self, code: str) -> ItemDetail:
        """
        検索詳細ページの内容をパースする
        :param code:
        :return:
        """
        params = {}
        brand = None

        html = _get(self.session, SearchDetail.url + code, params, brand)

        soup = BeautifulSoup(html.text, 'html.parser')

        title_block = soup.find('h1', class_='h1_title_product').text
        prep = title_block.split('　')
        category = prep[0]
        category = category.strip()
        title = prep[1].rsplit('/', 1)[0]
        title = title.strip()

        code = soup.find('td', id='proid').text
        code = code.replace('中古 ：', '').strip()

        table = soup.find('table', class_='table table-striped tbl_product_info')
        th_elements = table.find_all('th')
        td_elements = table.find_all('td')
        brand = None
        release_date = None
        price_teika = None
        model_number = None

        for item in th_elements:
            if (item.text.strip() == 'メーカー'):
                i = th_elements.index(item)
                brand = td_elements[i].text.strip()
            elif (item.text == '発売日'):
                i = th_elements.index(item)
                release_date = td_elements[i].text.strip()
            elif (item.text == '定価'):
                i = th_elements.index(item)
                price_teika = td_elements[i].text.strip()
            elif (item.text.strip() == '型番'):
                i = th_elements.index(item)
                model_number = td_elements[i].text.strip()

        return ItemDetail(title, code, category, release_date, price_teika, brand, model_number)


class SearchDetailShort:
    url = "https://www.suruga-ya.jp/product/detail/"

    def __init__(self, session: session(), code: str):
        """
        検索詳細ページの内容を取得する
        :param session:
        :param code:
        """
        self.session = session
        self.code = code

        self.item = self._parse_search_detail_short_page(self.code)

    def _parse_search_detail_short_page(self, code: str) -> ItemDS:
        """
        検索詳細ページの内容をパースする
        :param code:
        :return:
        """
        params = {}
        brand = None

        html = _get(self.session, SearchDetailShort.url + code, params, brand)

        soup = BeautifulSoup(html.text, 'html.parser')

        title_block = soup.find('h1', class_='h1_title_product').text
        prep = title_block.split('　')
        category = prep[0]
        category = category.strip()
        title = prep[1].rsplit('/', 1)[0]
        title = title.strip()

        code = soup.find('td', id='proid').text
        code = code.replace('中古 ：', '').strip()

        table = soup.find('table', class_='table table-striped tbl_product_info')
        th_elements = table.find_all('th')
        td_elements = table.find_all('td')
        brand = None
        release_date = None
        model_number = None

        for item in th_elements:
            if (item.text.strip() == 'メーカー'):
                i = th_elements.index(item)
                brand = td_elements[i].text.strip()
            elif (item.text == '発売日'):
                i = th_elements.index(item)
                release_date = td_elements[i].text.strip()
            elif (item.text.strip() == '型番'):
                i = th_elements.index(item)
                model_number = td_elements[i].text.strip()

        return ItemDS(title, brand, release_date, model_number)


class KaitoriSearch:
    url = "https://www.suruga-ya.jp/search_buy"

    def __init__(self, session: session(), category: str = '', search_word: str = '', page: int = None):
        """
        買取検索一覧ページの内容を取得する
        :param session:
        :param category:
        :param search_word:
        :param page:
        """
        self.session = session
        self.category = category
        self.search_word = search_word

        self.items = []

        # ページ指定ある場合
        if page:
            self.items = self._parse_kaitori_search_page(page)

        # ページ指定なければ結果が取れなくなるまで全ページ
        else:
            page = 1
            while True:
                items = self._parse_kaitori_search_page(page)

                if not items:
                    break

                self.items += items

                page += 1

                sleep(1)

    def _parse_kaitori_search_page(self, page: int) -> list:
        """
        買取検索一覧ページの内容をパースする
        :param page:
        :return:
        """
        params = {'category': self.category, 'search_word': self.search_word, 'page': page, 'searchbox': 1}

        html = _get(self.session, KaitoriSearch.url, params)

        items = []

        soup = BeautifulSoup(html.text, 'html.parser')
        item_html_texts = soup.find_all('tr', class_="listap")

        for item in item_html_texts:
            item_soup = BeautifulSoup(str(item), 'html.parser')

            elements_a = item_soup.find_all('a')
            title = elements_a[0].text

            elements_input = item_soup.find_all('input')
            code = elements_input[1]['value']
            price = elements_input[2]['value']

            category = item_soup.find('div', class_='category').text
            category = category.strip()

            items.append(KaitoriItem(title, code, category, price))

        return items


class KaitoriSearchDetail:
    url = "https://www.suruga-ya.jp/kaitori_detail/"

    def __init__(self, session: session(), code: str):
        """
        買取検索詳細ページの内容を取得する
        :param session:
        :param code:
        """
        self.session = session
        self.code = code

        self.item = self._parse_kaitori_search_detail_page(self.code)

    def _parse_kaitori_search_detail_page(self, code: str) -> KaitoriItemDetail:
        """
        買取検索詳細ページの内容をパースする
        :param code:
        :return:
        """
        params = {}

        html = _get(self.session, KaitoriSearchDetail.url + code, params)

        soup = BeautifulSoup(html.text, 'html.parser')

        title = soup.find('div', id='title').text
        title = title.strip()

        price = soup.find('div', id='priceMain').text
        price = price.replace('買取価格', '')
        price = price.replace('円', '')
        price = price.replace(',', '')
        price = price.strip()

        catogory = soup.find('td', width='94%').text
        catogory = catogory.strip()

        elements_a = soup.find_all('a')
        brand = elements_a[5].text.strip()
        picture = elements_a[6].text.strip()

        elements_td = soup.find_all('td')
        jan = elements_td[7].text.strip()
        code = elements_td[9].text.strip()
        release_date = elements_td[11].text.strip()
        list_price = elements_td[13].text.strip()
        model_number = elements_td[17].text.strip()

        explanation = soup.find('div', id='explanation').text
        explanation = explanation.replace('備考', '')
        explanation = explanation.strip()

        return KaitoriItemDetail(title, jan, code, catogory, release_date, price, list_price, brand, model_number, picture,
                                 explanation)
