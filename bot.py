import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Твій токен
API_TOKEN = '8422077163:AAF0oF7nALNGo-N_Lk6WUKXwoRS8T0hb0C4'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

PROFESSIONS = ["Лікар-хірург", "Агроном", "Військовий інженер", "Фізик-ядерник", "Кухар", "Програміст", "Електрик", "Будівельник"]
HEALTH_STATUS = ["Ідеальне здоров'я, 25 років", "Хронічний астматик, 40 років", "Легка застуда, 19 років", "Здоровий, 35 років", "Абсолютно здоровий, 50 років"]
HOBBIES = ["Стрільба з лука", "Гра на гітарі", "Садівництво", "Виживання в лісі", "Бокс"]
BAGGAGE = ["Набір ножів", "Велика аптечка", "Насіння пшениці", "Два блоки цигарок", "Книга з виживання", "Рація", "Ліхтарик"]
CATASTROPHES = [
    "Ядерна зима. Поверхня непридатна для життя на 10 років.",
    "Зомбі-апокаліпсис. Потрібно перечекати 5 років.",
    "Всесвітній потоп. Суші майже не залишилося."
]

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎰 Мій персонаж", callback_data="generate_char")
    await message.answer(
        "🌋 **Гра «Бункер»** 🌋\n\nНатисни кнопку, щоб отримати свою секретну картку в особисті повідомлення.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "generate_char")
async def process_callback_generate(callback_query: types.CallbackQuery):
    prof = random.choice(PROFESSIONS)
    health = random.choice(HEALTH_STATUS)
    hobby = random.choice(HOBBIES)
    bag = random.choice(BAGGAGE)
    catastrophe = random.choice(CATASTROPHES)

    response = (
        f"🚨 **ВАША КАРТКА ГРАВЦЯ** 🚨\n\n"
        f"🌍 **Катастрофа:** {catastrophe}\n"
        f"-----------------------------------\n"
        f"💼 **Професія:** {prof}\n"
        f"❤️ **Здоров'я:** {health}\n"
        f"🎸 **Хобі:** {hobby}\n"
        f"🎒 **Багаж:** {bag}\n\n"
        f"⚠️ *Переконай інших, що ти маєш вижити!*"
    )
    try:
        await bot.send_message(callback_query.from_user.id, response, parse_mode="Markdown")
        await callback_query.answer("Картку надіслано!")
    except Exception:
        await callback_query.answer("❌ Спочатку напиши боту в приватні /start!", show_alert=True)

if __name__ == '__main__':
    import asyncio
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main())
