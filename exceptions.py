class Error(Exception):
    """Родительский класс кастомных исключений."""

    pass


class MessageSendFailed(Error):
    """Не удалось отправить сообщение."""

    pass


class UnknownAPIAnswer(Error):
    """Неизвестный ответ API."""

    pass


class NoTokensFound(Error):
    """Нет токенов."""

    pass


class NoListOfHWs(Error):
    """Нет списка работ."""

    pass


class NoKeysInResponse(Error):
    """Нет ключей в ответе."""

    pass


class ListOfHWsNull(Error):
    """Список работ пустой."""

    pass


class StatusNotFound(Error):
    """Неизвестный статус работы."""

    pass
