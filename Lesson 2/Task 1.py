import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

url = 'https://hh.ru/search/vacancy'
searched_position = input('Введите искомую должность: ')
params = {'page': 0, 'text': searched_position}

response_init = requests.get(url, params=params, headers=headers)

dom_init = BeautifulSoup(response_init.text, 'html.parser')

page_amount = int(dom_init.find_all('span', {'class': 'pager-item-not-in-short-range'})[3].find('span').getText())

vacancies_list = []
for page_number in range(0, page_amount):
    params['page'] = page_number
    response = requests.get(url, params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_info = {}
        salary_min = salary_max = salary_currency = None
        vacancy_link_info = vacancy.find('a', {'class': 'bloko-link'})
        name = vacancy_link_info.getText()
        vacancy_ref = vacancy_link_info['href']
        employer = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace('\xa0', ' ')
        try:
            salary = vacancy.find_all('span', {'class': 'bloko-header-section-3'})[1].getText().replace('\u202f', '')
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
        except:
            salary = None

        vacancy_info['name'] = name
        vacancy_info['salary_min'] = salary_min
        vacancy_info['salary_max'] = salary_max
        vacancy_info['salary_currency'] = salary_currency
        vacancy_info['vacancy_ref'] = vacancy_ref
        vacancy_info['employer'] = employer

        vacancies_list.append(vacancy_info)

pprint(vacancies_list)

with open("vacancies_result.json", "w", encoding='utf8') as file:
    json.dump(vacancies_list, file, ensure_ascii=False, indent=4)
