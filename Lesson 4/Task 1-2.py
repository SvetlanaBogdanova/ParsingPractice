from lxml import html
from pprint import pprint
import requests
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient


client = MongoClient('localhost', 27017)

db = client['mail_ru_news']

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

url = 'https://news.mail.ru'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

news_block = dom.xpath("//div[contains(@class, 'daynews__item')] | //ul[contains(@class, 'list_half')]/li[@class='list__item']")
for news in news_block:
    page_info = {}
    link = news.xpath(".//a/@href")[0]
    news_id = link.split('/')[-2]

    response_news = requests.get(link, headers=header)
    dom_news = html.fromstring(response_news.text)

    news_header = dom_news.xpath("//h1/text()")[0]
    news_time = dom_news.xpath("//span[@class='note']//@datetime")[0]
    news_source = dom_news.xpath("//span[@class='breadcrumbs__item'][2]//span[@class='link__text']/text()")[0]

    page_info['_id'] = news_id
    page_info['name'] = news_header
    page_info['link'] = link
    page_info['time'] = news_time
    page_info['source'] = news_source
    pprint(page_info)

    try:
        db.news.insert_one(page_info)
    except DuplicateKeyError:
        pass

print(db.news.count_documents({}))
