from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
driver.implicitly_wait(5)
driver.get('https://account.mail.ru/login/')

el = driver.find_element(By.NAME, 'username')
el.send_keys('study.ai_172@mail.ru', Keys.ENTER)

el = driver.find_element(By.NAME, 'password')
el.send_keys('NextPassword172#', Keys.ENTER)

# Выведем общее количество входящих сообщений:
number_of_letters = driver.find_element(By.XPATH, "//div[@class='nav-folders']//a[1]").get_attribute('title').split(', ')[1].split(' ')[0]
print(number_of_letters)

message_links = {}
while True:
    number_of_links = len(message_links)
    messages = driver.find_elements(By.XPATH, "//div[@class='dataset__items']/a")
    for message in messages:
        link = message.get_attribute('href')
        message_id = message.get_attribute('data-id')
        if message_id is not None:
            message_links[message_id] = link
    if len(message_links) == number_of_links:
        break

    actions = ActionChains(driver)
    actions.move_to_element(messages[-1])
    actions.perform()
    time.sleep(2)

print(len(message_links.keys()))

# Пройдем по собранным ссылкам и соберем детальную информацию по каждому письму:
client = MongoClient('localhost', 27017)

db = client['mail_ru_letters']

for link in message_links.items():
    letter_info = {}
    driver.get(link[1])
    letter_from = driver.find_element(By.XPATH, "//span[@class='letter-contact']").text
    letter_date = driver.find_element(By.XPATH, "//div[@class='letter__date']").text
    letter_subject = driver.find_element(By.XPATH, "//h2[@class='thread__subject']").text
    letter_content = driver.find_element(By.XPATH, "//div[@class='letter__body']").text

    letter_info['_id'] = link[0]
    letter_info['from'] = letter_from
    letter_info['date'] = letter_date
    letter_info['subject'] = letter_subject
    letter_info['content'] = letter_content

    try:
        db.letters.insert_one(letter_info)
    except DuplicateKeyError:
        pass

print(db.letters.count_documents({}))
