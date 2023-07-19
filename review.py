import datetime as dt
import logging
import os
import re
import sqlite3
import time
from typing import Any, Union

import requests
import telegram
from bs4 import BeautifulSoup as Bs
from dotenv import load_dotenv

t = dt.datetime.now()


load_dotenv()


class MessageSendingError(Exception):
    """Ошибка отправки сообщения."""

    pass


class GlobalsError(Exception):
    """Ошибка, если есть пустые глобальные переменные."""

    pass


FAILURE_TO_SEND_MESSAGE = '{error}, {message}'
GLOBAL_VARIABLE_IS_MISSING = 'Отсутствует глобальная переменная'
GLOBAL_VARIABLE_IS_EMPTY = 'Пустая глобальная переменная'

# os.getenv('TELEGRAM_TOKEN')
TELEGRAM_TOKEN = '12345:AAHXXXXX'
# os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_CHAT_ID = -123456
# os.getenv('ENDPOINT')
ENDPOINT = 'https://localhost'

RETRY_TIME_SECONDS = 20


def send_message(bot: Any, message: Union[dt.datetime, int, str]) -> None:
    """Отправляет сообщение пользователю в Телеграм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        raise MessageSendingError(FAILURE_TO_SEND_MESSAGE.format(
            error=error,
            message=message,
        ))
    logging.info(f'Message "{message}" is sent')


def parse_status(
    current_timestamp: dt.datetime
) -> Union[dt.datetime, int, str]:
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = t.strftime('%m/%d/%Y')
    html_text = requests.get(ENDPOINT)
    soup = Bs(html_text.text, 'lxml')
    reviews = soup.find_all(
        'li', class_='ugc-list__item js-ugc-list-item'
    )

    ans = ''
    personal_info = ''
    for review in reviews:
        review_date = review.select('cat-brand-ugc-date > a')[0].text.strip()
        company_name = review.select('cat-brand-name > a')[1].text.strip()
        if 'Сегодня' in review_date:
            review_format_date = review_date.replace('Сегодня в', timestamp)
            review_url = (
                review.find(
                    'a', class_='link name t-text t-text--bold'
                ).get('href')
            )

            review_author = (
                review.select('cat-brand-name > a')[0].text.strip()
            )

            review_rating = review.find(
                'li', class_='review-estimation__item--checked'
            ).text.strip()

            review_text = ''
            comments = review.select('.t-text > .t-rich-text__p')
            for comment in comments:
                review_text += ' ' + comment.text.strip()

            review_text = re.sub(
                r'^.*?Показать целиком ', '', review_text
            ).strip().replace('  ', ' ')

            personal_info = (
                'Источник: ' + review_url + '\n' +
                'Автор: ' + review_author + '\n' +
                review_format_date + '\n' +
                'Рейтинг: ' + review_rating + '\n' +
                'Рейтинг: ' + review_text + '\n'
            )

            ans += personal_info + '\n\n'

            add_to_db(
                review_author,
                review_url,
                review_format_date,
                review_rating,
                review_text,
            )
        else:
            ans = "На сегодня у 'YourSite' нет отзывов."
    return ans


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    for key in (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ENDPOINT):
        if key is None:
            logging.error(GLOBAL_VARIABLE_IS_MISSING)
            return False
        if not key:
            logging.error(GLOBAL_VARIABLE_IS_EMPTY)
            return False
    return True


def add_to_db(
    review_author: str,
    review_url: str,
    review_format_date: dt.datetime,
    review_rating: int,
    review_text: str,
) -> None:
    '''Создание БД SQLite и добавление данных.'''
    db = sqlite3.connect('parser.db')
    c = db.cursor()
    c = db.execute('''CREATE TABLE IF NOT EXISTS users (
        author TEXT,
        url TEXT,
        date DATETIME,
        rating INTEGER,
        text TEXT
    )''')
    db.commit()

    c.execute(f"SELECT text FROM users WHERE text = '{review_text}'")

    if c.fetchone() is None:
        c.execute(
            'INSERT INTO users VALUES (?, ?, ?, ?, ?)',
            (
                review_author,
                review_url,
                review_format_date,
                review_rating,
                review_text
            )
        )
        db.commit()


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        raise GlobalsError('Ошибка глобальной переменной. Смотрите логи.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            message = parse_status(current_timestamp)
            send_message(bot, message)
        except IndexError:
            message = 'Статус работы не изменился'
            send_message(bot, message)
            logging.info(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME_SECONDS)


if __name__ == '__main__':
    main()