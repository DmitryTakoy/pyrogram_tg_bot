from telegram import Bot
import requests
import os
from dotenv import load_dotenv
import time
import logging
from exceptions import ListOfHWsNull, MessageSendFailed, StatusNotFound
from exceptions import NoKeysInResponse, NoListOfHWs
from exceptions import UnknownAPIAnswer
import sys

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
    return hws


def check_response(response):
    """Проверяет ответ на соотв-ие ожидаемому."""
    # response = get_api_answer()
    current_date = 'current_date'
    homeworks = 'homeworks'
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
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise StatusNotFound('Неизвестный статус работы.')
    new_status = (f'Изменился статус проверки работы '
                  f'"{homework_name}". Новый статус:'
                  f' {HOMEWORK_STATUSES[homework_status]}')
    verdict = new_status
    return verdict


def check_tokens():
    """Проверяет доступность токенов."""
    tokens_able = all([PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN])
    return tokens_able


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    if not check_tokens():
        logger.critical
        sys.exit()
    bot = Bot(token=TELEGRAM_TOKEN)
    prev_report = ''
    new_report = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            first_homework = homework[0]
            new_report = parse_status(first_homework)
            if prev_report != new_report:
                prev_report = new_report
                send_message(bot, new_report)
        except Exception as error:
            new_report = f'Сбой в работе программы: {error}'
            if prev_report != new_report:
                send_message(bot, new_report)
                prev_report = new_report
            logger.error(new_report)
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
