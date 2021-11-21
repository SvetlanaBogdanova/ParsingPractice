from pymongo import MongoClient
from pprint import pprint


def get_desired_salary():
    while True:
        try:
            return int(input("Введите желаемую зарплату: "))
        except ValueError:
            print('Неверный формат данных! Введите целое число')


def get_desired_currency():
    desired_currency_dict = {1: 'EUR', 2: 'KZT', 3: 'USD', 4: 'бел.', 5: 'грн.', 6: 'руб.', 7: 'сум'}
    while True:
        try:
            currency_index = int(input("Введите номер валюты для поиска "
                                       "(1 - EUR, 2 - KZT, 3 - USD, 4 - бел., 5 - грн., 6 - руб., 7 - сум: "))
            return desired_currency_dict[currency_index]
        except KeyError:
            print('Введите целое число от 1 до 7')
        except ValueError:
            print('Неверный формат данных! Введите целое число от 1 до 7')


client = MongoClient('localhost', 27017)

db = client['hh_vacancies']

desired_salary = get_desired_salary()

# Выведем список валют, которые встречаются в вакансиях.
# print(db.vacancies.distinct('salary_currency'))
# Проверим, что вакансии с валютой None соответсвуют тем, где не указан уровень зп.
# for doc in db.vacancies.find({'salary_currency': None,
#                               '$or': [
#                                   {'salary_min': {'$ne': None}},
#                                   {'salary_max': {'$ne': None}}
#                               ]}):
#     pprint(doc)

desired_currency = get_desired_currency()

search_query = {'salary_currency': desired_currency,
                '$or': [
                    {'salary_min': {'$gte': desired_salary}},
                    {'salary_max': {'$gte': desired_salary}}
                ]}
for doc in db.vacancies.find(search_query):
    pprint(doc)
