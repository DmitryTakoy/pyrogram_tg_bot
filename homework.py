from logging.handlers import RotatingFileHandler
from telegram import Bot
import requests
import os
from dotenv import load_dotenv
import time
import logging

# ПРОЛОГ
# Я в великом отчаянии и на грани
# Вложил много часов своих стараний, по-разному
# переписывал свой код, чтобы оно работало
# Но так и не смог написать работу, чтобы она
# 1 - cоответствала pytest
# 2 - работала
# либо одно, либо второе. В общем
# я заблудился в глубоком лесу и не могу выйти
# просьба изучить черновую работу и направить на путь праведный
# Так же приножу извинения за грязную и плохоработащую работу, попавшую к Вам
# С уважением
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='main.log',
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('my.log', maxBytes=50000000, backupCount=5)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
)
handler.setFormatter(formatter)
logger.addHandler(handler)


load_dotenv()
tg_token = os.getenv('TOKEN')
ya_token = os.getenv('YAPRAC')
id_tg = os.getenv('MYID')

PRACTICUM_TOKEN = ya_token
TELEGRAM_TOKEN = tg_token
TELEGRAM_CHAT_ID = id_tg

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
DCT_HWS = {}


def send_message(bot, message):
    """Отправляет сообщения."""
    bot = Bot(token=TELEGRAM_TOKEN)
    chat_id = TELEGRAM_CHAT_ID
    text = message
    try:
        bot.send_message(chat_id, text)
        logger.info('Message is sent')
    except Exception as error:
        logger.error(f'Error appeared while sending message. {error}')


def get_api_answer(current_timestamp):
    """Связывается с ресурсом."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}  # timestamp
    headers = HEADERS
    # if response.status_code != 200:
    #    logger.critical('Api unable - status not 200')
    # try:
    #    response = requests.get(ENDPOINT, headers=headers, params=params)
    #    hws = response.json()
    #    if type(hws) is dict and response.status_code == 200:
    #        logger.info('G_A_A made dict and S_C is 200')
    #    else:
    #        logger.error('Method didnt send dict')
    # except Exception:
    #    if response.status_code != 200:
    #        logger.error('Api unable - status not 200')
    #        raise ConnectionError
    #    else:
    #        logger.error('Didnt get response from API')
    # return hws
    response = requests.get(ENDPOINT, headers=headers, params=params)
    hws = response.json()
    # if type(hws) is not dict:
    #    raise TypeError
    # if not isinstance(hws, dict):
    #    raise TypeError
    if response.status_code != 200:
        raise ConnectionError
    return hws


def check_response(response):
    """Проверяет ответ на соотв-ие ожидаемому."""
    # response = get_api_answer()
    current_date = 'current_date'
    homeworks = 'homeworks'
    # try:
    #    if current_date and homeworks in response and type(response) is dict:
    #        homework = response[homeworks]
    #    #return homework
    #    else:
    #        logger.error(f'Data inst dict type')
    #        raise TypeError(f'No data')
    # except Exception:
    #    logger.error('Response isnt as expected')
    # return homework
    if current_date and homeworks not in response:
        raise TypeError
    elif type(response) is not dict:
        raise TypeError
    elif not isinstance(response, dict):
        raise TypeError
    elif not isinstance(response[homeworks], list):
        raise TypeError
    elif response is None:
        raise TypeError
    elif not len(response[homeworks]):
        raise TypeError
    return response.get('homeworks')


def parse_status(homework):
    """Парсит ответ АПИ."""
    if 'homework_name' and 'status' not in homework:
        raise KeyError('No homework name or status at homework dict!')
    else:
        homework_name = homework['homework_name']
        # check_response(homework_statuses)[0]['homework_name']
        homework_status = homework['status']
        # check_response(homework_statuses)[0]['status']
        # for objects in homework:
        #    homework_name = objects['homework_name']
        #    homework_status = objects['status']
        #    return homework_name, homework_status
    # если запись с кэша равна полученной записи, то пасс
    # еlse вызываем функцию отправки сбщ
    # можно добавлять в словарь, но тогда словарю пизда
        if homework_name not in DCT_HWS:
            DCT_HWS[homework_name] = homework_status
        # logger.error('New hw found, added to tracking')
            new_status = (f'Изменился статус проверки работы "{homework_name}"'
                          f'with status {HOMEWORK_STATUSES[homework_status]}')
            return new_status
        elif (homework_name in DCT_HWS
              and DCT_HWS[homework_name] == homework_status):
            logger.debug('Status of HW has not changed')
            new_status = ('nothing changed')
            return new_status
        elif (homework_name in DCT_HWS
              and DCT_HWS[homework_name] != homework_status):
            DCT_HWS[homework_name] = homework_status
            logger.error('HW status changed, added to dct')
            new_status = (f'Изменился статус проверки работы '
                          f'"{homework_name}". Новый статус:'
                          f' {HOMEWORK_STATUSES[homework_status]}')
            return new_status
        verdict = new_status
        return verdict


def check_tokens():
    """Проверяет доступность токенов."""
    if PRACTICUM_TOKEN and TELEGRAM_CHAT_ID and TELEGRAM_TOKEN is not None:
        return True
    else:
        logger.critical('No tokens inside')
        return False


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    bot = Bot(token=TELEGRAM_TOKEN)
    check_tokens()
    while True:
        try:
            response = get_api_answer(current_timestamp)
        except Exception:
            logger.error('Не удалось подключиться')
        try:
            homework = check_response(response)
        except Exception:
            logger.error('Не удалось получить список работ')
        try:
            first_homework = homework[0]
            message = parse_status(first_homework)
        except Exception:
            logger.error('Не удалось получить домашнюю работу')
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            first_homework = homework[0]
            message = parse_status(first_homework)
            sender = send_message(bot, message)
            # current_timestamp = ...
            logger.info('Сообщение отправлено')
            time.sleep(RETRY_TIME)
            return sender
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            sender = send_message(bot, message)
            time.sleep(RETRY_TIME)
            return sender
        # else:
        #    bot.stop()


if __name__ == '__main__':
    main()
