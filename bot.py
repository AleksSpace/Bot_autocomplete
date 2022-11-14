import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from time import sleep

import telebot
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.select import Select
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telebot import types
from validate_email import validate_email

from constants import (
    LOG_DEBUG_BOT_ERROE_MESSAGE,
    LOG_DEBUG_BOT_ERROR_OPEN_FILE,
    LOG_DEBUG_BOT_GET_MESSAGE,
    LOG_DEBUG_BOT_MESSAGE,
    PAUSE_DURATION_SECONDS,
    START_MESSAGE,
)
from database import User, adding_data_database

load_dotenv()

# Здесь задана глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
)

# А тут установлены настройки логгера для текущего файла
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("app.log", maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

try:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
except KeyError as error:
    logger.critical(f"Отсутствует обязательная переменная окружения: {error}!")
    quit()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

data_for_database = {}


@bot.message_handler(commands=["start"])
def start(message):
    """При нажатии кнопки /start активируется бот,
    отправляет стартовое сообщение и просит написать имя пользователя,
    потом ждёт пока пользователь напишет имя.
    """
    logger.info(f"{LOG_DEBUG_BOT_MESSAGE}'{message.text}'")
    try:
        bot.send_message(message.chat.id, START_MESSAGE)
    except TypeError as error:
        logger.error(f"{error}: {LOG_DEBUG_BOT_ERROE_MESSAGE}'{message.text}'")
    data_for_database["user_id"] = message.from_user.id
    send = bot.send_message(message.chat.id, "Напишите ваше имя")
    bot.register_next_step_handler(send, get_user_first_name)


@bot.message_handler(content_types=["text"])
def get_user_first_name(message):
    logger.info(f"{LOG_DEBUG_BOT_GET_MESSAGE}'{message.text}'")
    """Бот полуает имя пользователя, сохраняет его в словарь
    и просит написать фамилию. Потом ждет пока пользователь напишет фамилию
    """
    data_for_database["first_name"] = message.text
    send = bot.send_message(message.chat.id, "Напишите вашу фамилию")
    logger.info(f"{LOG_DEBUG_BOT_MESSAGE}'{message.text}'")
    try:
        bot.register_next_step_handler(send, get_user_last_name)
    except TypeError as error:
        logger.error(f"{error} {LOG_DEBUG_BOT_ERROE_MESSAGE}'{message.text}'")


@bot.message_handler(content_types=["text"])
def get_user_last_name(message):
    logger.info(f"{LOG_DEBUG_BOT_GET_MESSAGE}'{message.text}'")
    """Бот полуает фамилию пользователя, сохраняет его в словарь
    и просит написать email. Потом ждет пока пользователь напишет email
    """
    data_for_database["last_name"] = message.text
    send = bot.send_message(
        message.chat.id, "Напишите ваш email в формате example@example.ru"
    )
    try:
        bot.register_next_step_handler(send, get_user_email)
    except TypeError as error:
        logger.error(f"{error} {LOG_DEBUG_BOT_ERROE_MESSAGE}'{message.text}'")


@bot.message_handler(content_types=["text"])
def get_user_email(message):
    logger.info(f"{LOG_DEBUG_BOT_GET_MESSAGE}'{message.text}'")
    """Бот полуает email пользователя, сохраняет его в словарь
    и просит написать номер телефона.
    Потом ждет пока пользователь напишет номер телефона
    """
    validate_email(message.text)
    if validate_email(message.text):
        data_for_database["email"] = message.text
    else:
        bot.send_message(
            message.chat.id,
            "Возможно вы допустили ошибку " "в emeil, начните сначала",
        )
        quit()
    send = bot.send_message(message.chat.id, "Напишите ваш номер телефона")
    try:
        bot.register_next_step_handler(send, get_user_phone)
    except TypeError as error:
        logger.error(f"{error} {LOG_DEBUG_BOT_ERROE_MESSAGE}'{message.text}'")


@bot.message_handler(content_types=["text"])
def get_user_phone(message):
    logger.info(f"{LOG_DEBUG_BOT_GET_MESSAGE}'{message.text}'")
    """Бот полуает номер телефона пользователя, сохраняет его в словарь
    и просит написать дату рождения.
    Потом ждет пока пользователь напишет дату рождения
    """
    data_for_database["phone"] = message.text
    send = bot.send_message(
        message.chat.id, "Напишите вашу дату рождения в формате дд.мм.гггг"
    )
    try:
        bot.register_next_step_handler(send, get_user_date)
    except TypeError as error:
        logger.error(f"{error} {LOG_DEBUG_BOT_ERROE_MESSAGE}'{message.text}'")


@bot.message_handler(content_types=["text"])
def get_user_date(message):
    logger.info(f"{LOG_DEBUG_BOT_GET_MESSAGE}'{message.text}'")
    """Бот полуает дату рождения пользователя, сохраняет его в словарь
    и создаёт запись в БД.
    Потом ждет пока пользователь напишет "/Ok"
    """
    data_for_database["date"] = message.text

    adding_data_database(
        user_id=data_for_database["user_id"],
        first_name=data_for_database["first_name"],
        last_name=data_for_database["last_name"],
        email=data_for_database["email"],
        phone=data_for_database["phone"],
        date=data_for_database["date"],
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btnok = types.KeyboardButton("/Ок")
    markup.add(btnok)
    send = bot.send_message(
        message.chat.id, "Нажмите кнопку /Ок", reply_markup=markup
    )
    try:
        bot.register_next_step_handler(send, autocomplete)
    except TypeError as error:
        logger.error(f"{error} {LOG_DEBUG_BOT_ERROE_MESSAGE}'{message.text}'")


@bot.message_handler(commands=["Ок"])
def autocomplete(message):
    """Функция запускает заполнение формы на сайте,
    создаёт папку и сохраняет туда скриншот
    """
    engine = create_engine("sqlite:///autocomplete.db", echo=False)
    session = Session(engine)

    USER_ID = message.from_user.id

    try:
        URL_FORM = os.getenv("URL_FORM")
    except KeyError as error:
        logger.critical(
            f"Отсутствует обязательная переменная окружения: {error}!"
        )
        quit()
    try:
        FIRST_NAME = (
            session.query(User.first_name)
            .filter(User.user_id == USER_ID)
            .order_by(User.id.desc())
            .first()[0]
        )
    except IndexError as error:
        logger.critical(f"Не получилось достать данные из базы: {error}!")
        quit()
    try:
        LAST_NAME = (
            session.query(User.last_name)
            .filter(User.user_id == USER_ID)
            .order_by(User.id.desc())
            .first()[0]
        )
    except IndexError as error:
        logger.critical(f"Не получилось достать данные из базы: {error}!")
        quit()
    try:
        EMAIL = (
            session.query(User.email)
            .filter(User.user_id == USER_ID)
            .order_by(User.id.desc())
            .first()[0]
        )
    except IndexError as error:
        logger.critical(f"Не получилось достать данные из базы: {error}!")
        quit()
    try:
        PHONE = (
            session.query(User.phone)
            .filter(User.user_id == USER_ID)
            .order_by(User.id.desc())
            .first()[0]
        )
    except IndexError as error:
        logger.critical(f"Не получилось достать данные из базы: {error}!")
        quit()
    try:
        DATE_IN_BD = (
            session.query(User.date)
            .filter(User.user_id == USER_ID)
            .order_by(User.id.desc())
            .first()[0]
        )
    except IndexError as error:
        logger.critical(f"Не получилось достать данные из базы: {error}!")
        quit()
    DATE = str(DATE_IN_BD.day)
    MONTH = DATE_IN_BD.month
    YEAR = str(DATE_IN_BD.year)
    DATE_NOW = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M")
    USER_ID_STR = str(USER_ID)
    NAME_SCREEN = "./screenshot/" + DATE_NOW + USER_ID_STR + ".png"

    def filling_field(element, value):
        """функция принимает на вход элемен который обозначает поле для ввода
        и значение которое нужно ввести в это поле, и вводит данные
        имитируя клавиатуру
        """
        ActionChains(driver).send_keys_to_element(element, value).perform()

    logger.info("Создание папки для сохранения скриншотов")
    if not os.path.isdir("screenshot"):
        os.mkdir("screenshot")

    logger.info(
        "Проверка и установка (или обновление) драйвера"
        "для Chrome через DriverManager."
    )
    driver = webdriver.Remote(
        "http://selenium:4444/wd/hub",
        desired_capabilities=DesiredCapabilities.CHROME,
    )

    logger.info(f"Открытие страницы по адресу: {URL_FORM}")
    try:
        driver.get(URL_FORM)
    except Exception as error:
        logger.critical(
            f"{error}: Сайт временно недоступен, попробуйте позже!"
        )

    logger.info("Развёртывание окна на полный экран.")
    driver.maximize_window()
    # Здесь и далее паузы, чтобы рассмотреть происходящее.
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск поля для заполнения имени.")
    name_input = driver.find_element(By.NAME, "name")
    filling_field(name_input, FIRST_NAME)
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск поля для заполнения фамилии.")
    lastname_input = driver.find_element(By.NAME, "lastname")
    filling_field(lastname_input, LAST_NAME)
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск кнопки 'Далее'.")
    next_button = driver.find_element(By.TAG_NAME, "button")

    logger.info("Эмуляция щелчка мышью.")
    next_button.click()
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск поля Email")
    email = driver.find_element(By.NAME, "email")
    filling_field(email, EMAIL)
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск поля для ввода номера телефона")
    phone = driver.find_element(By.NAME, "phone")
    filling_field(phone, PHONE)
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск кнопки 'Далее'.")
    next_button_2 = driver.find_element(
        By.XPATH, '//div[@class="b24-form-btn-container"]//div[2]//button'
    )
    logger.info("Эмуляция щелчка мышью.")
    next_button_2.click()
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск поля для ввода даты")
    date = driver.find_element(By.XPATH, "//input")

    logger.info("Эмуляция клика мыши по полю ввода")
    date.click()
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск селектора выбора года в выпавшем календаре")
    select_year = driver.find_element(
        By.XPATH, '//div[@class="vdpPeriodControls"]//div[2]//select'
    )
    select_y = Select(select_year)
    select_y.select_by_value(YEAR)
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск селектора выбора месяца в выпавшем календаре")
    select_month = driver.find_element(
        By.XPATH, '//div[@class="vdpPeriodControls"]//div//select'
    )
    select_m = Select(select_month)
    select_m.select_by_value(str(MONTH - 1))
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск кнопки выбора нужного дня месяца")
    all_days = driver.find_elements(
        By.XPATH, '//table[@class="vdpTable"]//div'
    )
    for day_element in all_days:
        date = day_element.text
        if date == DATE:
            day_element.click()
            break

    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Поиск кнопки 'Далее'.")
    submit = driver.find_element(By.XPATH, '//button[@class="b24-form-btn"]')

    logger.info("Эмуляция щелчка мышью.")
    submit.click()
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Сохранение скриншота страницы с заданным именем.")
    driver.save_screenshot(NAME_SCREEN)
    sleep(PAUSE_DURATION_SECONDS)

    logger.info("Закрытие веб-драйвера.")
    driver.quit()

    logger.info("Открытие файла для отправки в бот")
    try:
        with open(NAME_SCREEN, "rb") as f:
            bot.send_photo(message.chat.id, f)
    except TypeError as error:
        logger.error(f"{error} {LOG_DEBUG_BOT_ERROR_OPEN_FILE}")


if __name__ == "__main__":
    bot.polling()
