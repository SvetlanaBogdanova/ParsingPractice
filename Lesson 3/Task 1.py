import requests
from bs4 import BeautifulSoup
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient


# Получим идентификатор вакансии из ссылки на вакансию:
def get_vacancy_id(vacancy_url):
    vacancy_url = vacancy_url.replace('https://hh.ru/vacancy/', '')
    return int(vacancy_url[:vacancy_url.index('?')])


client = MongoClient('localhost', 27017)

db = client['hh_vacancies']


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

url = 'https://hh.ru/search/vacancy'
searched_position = input('Введите искомую должность: ')
params = {'page': 0, 'text': searched_position, 'items_on_page': 20}

response_init = requests.get(url, params=params, headers=headers)

dom_init = BeautifulSoup(response_init.text, 'html.parser')

num_of_pages = int(dom_init.find_all('span', {'class': 'pager-item-not-in-short-range'})[3].find('span').getText())

for page_number in range(0, num_of_pages):
    params['page'] = page_number
    response = requests.get(url, params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_info = {}
        vacancy_link_info = vacancy.find('a', {'class': 'bloko-link'})
        name = vacancy_link_info.getText()
        vacancy_ref = vacancy_link_info['href']
        vacancy_id = get_vacancy_id(vacancy_ref)
        employer = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace('\xa0', ' ')

        salary_min = salary_max = salary_currency = None
        salary_tags = vacancy.find_all('span', {'class': 'bloko-header-section-3'})
        if len(salary_tags) > 1:
            salary = salary_tags[1].getText().replace('\u202f', '')
            salary_details = salary.split()
            if salary.startswith('до'):
                salary_max = int(salary_details[1])
                salary_currency = salary_details[2]
            elif salary.startswith('от'):
                salary_min = int(salary_details[1])
                salary_currency = salary_details[2]
            else:
                salary_min = int(salary_details[0])
                salary_max = int(salary_details[2])
                salary_currency = salary_details[3]

        vacancy_info['_id'] = vacancy_id
        vacancy_info['name'] = name
        vacancy_info['salary_min'] = salary_min
        vacancy_info['salary_max'] = salary_max
        vacancy_info['salary_currency'] = salary_currency
        vacancy_info['vacancy_ref'] = vacancy_ref
        vacancy_info['employer'] = employer

        try:
            db.vacancies.insert_one(vacancy_info)
        except DuplicateKeyError:
            pass

print(db.vacancies.count_documents({}))
