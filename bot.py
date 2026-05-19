import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = '8422077163:AAF0oF7nALNGo-N_Lk6WUKXwoRS8T0hb0C4'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сховище для ігор (у пам'яті сервера)
games = {}

PROFESSIONS = ["Лікар-хірург", "Агроном", "Військовий інженер", "Фізик-ядерник", "Кухар", "Програміст", "Електрик", "Будівельник", "Вчитель", "Поліцейський"]
HEALTH_STATUS = ["Ідеальне здоров'я, 25 років", "Хронічний астматик, 40 років", "Легка застуда, 19 років", "Здоровий, 35 років", "Абсолютно здоровий, 50 років", "Травма ноги, 30 років"]
HOBBIES = ["Стрільба з лука", "Гра на гітарі", "Садівництво", "Виживання в лісі", "Бокс", "Малювання", "Риболовля"]
BAGGAGE = ["Набір ножів", "Велика аптечка", "Насіння пшениці", "Два блоки цигарок", "Книга з виживання", "Рація", "Ліхтарик", "Каністра води 5л"]
CATASTROPHES = [
    "Ядерна зима. Поверхня непридатна для життя на 10 років.",
    "Зомбі-апокаліпсис. Потрібно перечекати 5 років.",
    "Всесвітній потоп. Суші майже не залишилося.",
    "Нашестя іншопланетян. Людство в підпіллі."
]

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "🌋 **Гра «Бункер: Паті Мод»** 🌋\n\n"
        "Команди:\n"
        "1️⃣ /create — створити нову гру (отримаєш код)\n"
        "2️⃣ /join КодГри — приєднатися до друзів\n\n"
        "Приклад: `/join 1234`",
        parse_mode="Markdown"
    )

@dp.message(Command("create"))
async def create_game(message: types.Message):
    game_id = str(random.randint(1000, 9999))
    catastrophe = random.choice(CATASTROPHES)
    games[game_id] = {"catastrophe": catastrophe, "players": []}
    
    await message.answer(
        f"🎮 **Гру створено!**\n\n"
        f"🌍 Катастрофа: {catastrophe}\n"
        f"🔑 Код для друзів: `{game_id}`\n\n"
        f"Друзі мають написати: `/join {game_id}`",
        parse_mode="Markdown"
    )

@dp.message(Command("join"))
async def join_game(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Вкажи код! Наприклад: `/join 1234`基礎")
    
    game_id = args[1]
    if game_id not in games:
        return await message.answer("❌ Гра з таким кодом не знайдена.")
    
    catastrophe = games[game_id]["catastrophe"]
    prof = random.choice(PROFESSIONS)
    health = random.choice(HEALTH_STATUS)
    hobby = random.choice(HOBBIES)
    bag = random.choice(BAGGAGE)

    response = (
        f"🚨 **ТИ ПРИЄДНАВСЯ ДО ГРИ #{game_id}** 🚨\n\n"
        f"🌍 **Спільна катастрофа:**\n{catastrophe}\n"
        f"-----------------------------------\n"
        f"💼 **Твій персонаж:**\n"
        f"• Професія: {prof}\n"
        f"• Здоров'я: {health}\n"
        f"• Хобі: {hobby}\n"
        f"• Багаж: {bag}\n\n"
        f"⚠️ *Тепер обговорюйте в чаті, хто залишиться в бункері!*"
    )
    
    await message.answer(response, parse_mode="Markdown")

if __name__ == '__main__':
    import asyncio
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main())
