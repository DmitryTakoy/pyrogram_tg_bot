from telegram import Bot
import requests
import os
from dotenv import load_dotenv
import time
import logging
from exceptions import ListOfHWsNull, MessageSendFailed, StatusNotFound
from exceptions import NoKeysInResponse, NoListOfHWs
from exceptions import NoTokensFound, UnknownAPIAnswer
import sys

# ПРОЛОГ
# Спасибо Вам !!!

# handler = RotatingFileHandler('my.log', maxBytes=50000000, backupCount=5)
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#    '%(asctime)s - %(levelname)s - %(message)s',
# )
# handler.setFormatter(formatter)
# logger.addHandler(handler)


load_dotenv()
tg_token = os.getenv('TOKEN')
ya_token = os.getenv('YAPRAC')
id_tg = os.getenv('MYID')

PRACTICUM_TOKEN = ya_token
TELEGRAM_TOKEN = tg_token
TELEGRAM_CHAT_ID = id_tg
TOKENS = [ya_token, tg_token, id_tg]

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
        logger.info('Sending message')
        bot.send_message(chat_id, text)
        logger.info('Message is sent')
    except Exception:
        raise MessageSendFailed


def get_api_answer(current_timestamp):
    """Связывается с ресурсом."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}  # timestamp
    headers = HEADERS
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
        if response.status_code != 200:
            raise UnknownAPIAnswer('Неизвестный ответ АPI')
        hws = response.json()
    except Exception:
        raise ConnectionError('Не удалось подключиться')
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
    # response = requests.get(ENDPOINT, headers=headers, params=params)
    # hws = response.json()
    # if type(hws) is not dict:
    #    raise TypeError
    # if not isinstance(hws, dict):
    #    raise TypeError
    # if response.status_code != 200:
    #    raise ConnectionError
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
    if not isinstance(response, dict):
        raise TypeError
    elif current_date and homeworks not in response:
        raise NoKeysInResponse('Нет ключей в словаре')
    elif not isinstance(response[homeworks], list):
        raise NoListOfHWs('Не удалось получить список работ')
    elif not len(response[homeworks]):
        raise ListOfHWsNull('Список домашних работ пуст')
    return response.get('homeworks')


def parse_status(homework):
    """Парсит ответ АПИ."""
    if ('homework_name' not in homework
            or 'status' not in homework):
        raise KeyError('No homework name or status at homework dict!')
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
    # if homework_name not in DCT_HWS:
    #    DCT_HWS[homework_name] = homework_status
    #    # logger.error('New hw found, added to tracking')
    #    new_status = (f'Изменился статус проверки работы "{homework_name}"'
    #                  f'with status {HOMEWORK_STATUSES[homework_status]}')
    #    return new_status
    # elif (homework_name in DCT_HWS
    #      and DCT_HWS[homework_name] == homework_status):
    #    logger.debug('Status of HW has not changed')
    #    new_status = ('nothing changed')
    #    return new_status
    # elif (homework_name in DCT_HWS
    #      and DCT_HWS[homework_name] != homework_status):
    #    DCT_HWS[homework_name] = homework_status
    #    logger.error('HW status changed, added to dct')
    #    new_status = (f'Изменился статус проверки работы '
    #                  f'"{homework_name}". Новый статус:'
    #                  f' {HOMEWORK_STATUSES[homework_status]}')
    #    return new_status
    # verdict = new_status
    # return verdict
    if homework_status not in HOMEWORK_STATUSES:
        raise StatusNotFound('Неизвестный статус работы.')
    new_status = (f'Изменился статус проверки работы '
                  f'"{homework_name}". Новый статус:'
                  f' {HOMEWORK_STATUSES[homework_status]}')
    verdict = new_status
    return verdict


def check_tokens():
    """Проверяет доступность токенов."""
    try:
        if PRACTICUM_TOKEN and TELEGRAM_CHAT_ID and TELEGRAM_TOKEN is not None:
            return True
        else:
            return False
    except Exception:
        raise NoTokensFound('No tokens inside')
    # Встроенную функцию all() использовать нельзя, так как не проходит pytest,
    # код возвращает True на тесте, когда pytest ожидает False
    # toks = all(TOKENS)
    # return toks
    # for element in tokens:
    #    if not element:
    #        return True
    # return False


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    # try:
    #    check_tokens()
    # except NoTokensFound:
    if not check_tokens():
        logger.critical
        sys.exit()
    bot = Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.error
            homework = check_response(response)
            logger.error
            first_homework = homework[0]
            message = parse_status(first_homework)
            logger.error
            # response = get_api_answer(current_timestamp)
            # homework = check_response(response)
            # first_homework = homework[0]
            # message = parse_status(first_homework)
            sender = send_message(bot, message)
            # current_timestamp = ...
            logger.info('Сообщение отправлено')
            return sender
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error
            sender = send_message(bot, message)
            return sender
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    # main()
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename='main.log')
    logger = logging.getLogger(__name__)
    main()
