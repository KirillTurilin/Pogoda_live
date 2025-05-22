# Telegram Weather Bot

Телеграм бот для просмотра погоды на aiogram 3.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` в корне проекта со следующим содержимым:
   ```
   TELEGRAM_API_TOKEN=your_telegram_bot_token_here
   WEATHER_API_KEY=your_openweathermap_api_key_here
   ```
   Замените `your_telegram_bot_token_here` на ваш токен от Telegram Bot API (получить можно у [@BotFather](https://t.me/BotFather)).
   Замените `your_openweathermap_api_key_here` на ваш API ключ от [OpenWeatherMap](https://openweathermap.org/api).

## Запуск

```
python bot.py
```

## Использование

1. Отправьте боту команду `/start` или `/help`, чтобы получить приветственное сообщение
2. Отправьте название города или используйте команду `/weather`, чтобы получить информацию о погоде 