import os
import requests
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Функция для получения погоды
def get_weather(city: str, api_key: str) -> dict:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "ru"
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "clouds": data["clouds"]["all"],
            "description": data["weather"][0]["description"]
        }
    elif response.status_code == 404:
        return {"error": f"Город '{city}' не найден. Проверьте правильность написания."}
    else:
        return {"error": "Не удалось получить данные о погоде. Попробуйте позже."}

# Хендлер команды /start
@router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    await message.answer("Привет! Напишите название города на русском, чтобы узнать погоду.")

# Хендлер для обработки текстовых сообщений (городов)
@router.message()
async def weather_handler(message: Message):
    city = message.text.strip()
    weather = get_weather(city, WEATHER_API_KEY)
    if "error" in weather:
        await message.answer(weather["error"])
    else:
        await message.answer(
            f"Погода в {weather['city']}:\n"
            f"Температура: {weather['temp']}°C\n"
            f"Облачность: {weather['clouds']}%\n"
            f"Описание: {weather['description'].capitalize()}."
        )

# Запуск бота
async def main():
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")  
    finally:
        await bot.session.close()  # Закрытие сессии бота

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())





