import logging
import asyncio #для асинхронных функций
import requests # для с вебом и апи\
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from weather import get_coord
from datetime import datetime

logging.basicConfig(level=logging.INFO) # логирование

bot = Bot(token="7728168775:AAErgIvs2OHRm8WTtnF3oAXnohqkBLlCUgE") # создание класса бота что бы потом с ним работать

storage = MemoryStorage() # активация памяти бота
dp = Dispatcher(storage=storage) # активация диспетчера

YANDEX_API_KEY = "57cb7358-081e-4a18-abed-158f09c21db1"


class Form(StatesGroup):
    adres = State()#Актив/Не актив



@dp.message(Command("start")) # обрабатывает команду /start
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Я бот для просмотра погоды. Отправь мне адрес любой точки мира на русском или англиском а я покажу тебе погоду там.")


@dp.message(Command("help")) # обрабатывает команду /help
async def send_help(message: types.Message):
    help_text = """
<b>📚 Справка по использованию Погодного бота</b>

Бот поможет вам узнать текущую погоду и прогноз в любой точке мира.

<b>🤖 Доступные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку
/weather - Узнать текущую погоду по адресу
/forecast - Получить прогноз погоды на 5 дней

<b>📝 Как пользоваться:</b>
1️⃣ <b>Прямой запрос</b> - просто отправьте боту название города, адрес или любую точку на карте (например, "Москва", "Красная площадь", "Эйфелева башня")

2️⃣ <b>Команда /weather</b> - отправьте эту команду, затем укажите адрес, и бот покажет вам текущую погоду в этом месте

3️⃣ <b>Команда /forecast</b> - отправьте эту команду, затем укажите адрес, и бот покажет вам прогноз погоды на ближайшие дни

<b>🌦 Информация о погоде включает:</b>
• Текущая температура и ощущаемая температура
• Состояние погоды (ясно, облачно, дождь и т.д.)
• Скорость и направление ветра
• Атмосферное давление
• Влажность воздуха
• УФ-индекс (если доступен)
• Прогноз на сегодня (днем и вечером)

<b>🔍 Примеры запросов:</b>
• Москва
• Нью-Йорк
• Красная площадь
• проспект Ленина, 1, Екатеринбург
• улица Пушкина, дом Колотушкина

<b>ℹ️ Обратите внимание:</b> бот использует API Яндекс.Погоды и может не найти некоторые адреса. В этом случае попробуйте указать более популярное место или ближайший крупный объект.
"""
    await message.reply(help_text, parse_mode="HTML")



@dp.message(Form.adres) # обрабатывает что отправленно сообщение боту и активена проверка на адрес
async def process_city(message: types.Message, state: FSMContext): # создаем асинхронную функцию
    await state.update_data(city=message.text) # заносим в память адрес
    await get_weather(message)
    await state.clear() # делаем адрес неактивным


async def get_yandex_weather(adres):
    try: # оброботчик исключений
        location = get_coord(adres) # возвращает координаты

        if not location:
            return None

        lat = location["lat"] # широта
        lon = location["lon"] #долгота

        url = f'https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}'
        headers = {
            'X-Yandex-Weather-Key': YANDEX_API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        return None


def get_wind_direction_text(wind_dir):
    directions = {
        "nw": "северо-западный",
        "n": "северный",
        "ne": "северо-восточный",
        "e": "восточный",
        "se": "юго-восточный",
        "s": "южный",
        "sw": "юго-западный",
        "w": "западный",
        "c": "штиль"
    }
    return directions.get(wind_dir, wind_dir)


def translate_condition(condition):
    conditions = {
        "clear": "ясно",
        "partly-cloudy": "малооблачно",
        "cloudy": "облачно с прояснениями",
        "overcast": "пасмурно",
        "drizzle": "морось",
        "rain": "дождь",
        "heavy-rain": "сильный дождь",
        "showers": "ливень",
        "wet-snow": "дождь со снегом",
        "light-snow": "небольшой снег",
        "snow": "снег",
        "snow-showers": "снегопад",
        "hail": "град",
        "thunderstorm": "гроза",
        "thunderstorm-with-rain": "дождь с грозой",
        "thunderstorm-with-hail": "гроза с градом"
    }
    return conditions.get(condition, condition)


@dp.message(F.text)
async def get_weather(message: types.Message):
    try:
        adres = message.text

        # Получаем данные о погоде
        weather_data = await get_yandex_weather(adres)

        if weather_data and 'fact' in weather_data:
            fact = weather_data['fact']
            print(fact)

            temp = fact['temp']
            feels_like = fact['feels_like']
            condition = translate_condition(fact['condition'])
            wind_speed = fact['wind_speed']
            wind_gust = fact['wind_gust']
            wind_dir = get_wind_direction_text(fact['wind_dir'])
            pressure = fact['pressure_mm']
            humidity = fact['humidity']

            # Данные о местоположении
            location_name = adres
            if 'info' in weather_data and 'tzinfo' in weather_data['info']:
                timezone = weather_data['info']['tzinfo']['name']
            else:
                timezone = "Неизвестный часовой пояс"

            # Дата и время наблюдения
            obs_time = datetime.fromtimestamp(fact['obs_time']).strftime('%d.%m.%Y %H:%M')

            # Формируем ответ
            response = (
                f"🌡️ <b>Погода в {location_name}</b> ({timezone})\n"
                f"📆 Данные от: {obs_time}\n\n"
                f"🌤️ <b>{condition.capitalize()}</b>\n"
                f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                f"💧 Влажность: {humidity}%\n"
                f"🌬️ Ветер: {wind_dir}, {wind_speed} м/с (порывы до {wind_gust} м/с)\n"
                f"🧭 Давление: {pressure} мм рт.ст.\n"
            )

            # Добавляем УФ-индекс если доступен
            if 'uv_index' in fact:
                response += f"☀️ УФ-индекс: {fact['uv_index']}\n"


            await message.answer(response, parse_mode="HTML")
        else:
            await message.reply(f"Не удалось получить информацию о погоде для адреса {adres}.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply(f"Произошла ошибка при получении данных о погоде: {e}")


# Функция для установки команд бота в меню Telegram
async def set_commands():
    commands = [
        types.BotCommand(command="start", description="Начать работу с ботом"),
        types.BotCommand(command="help", description="Помощь по использованию бота")
    ]
    await bot.set_my_commands(commands)




async def main():
    # Установка команд бота в меню Telegram
    await set_commands()
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    await dp.start_polling(bot)


asyncio.run(main())
