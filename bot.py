import random
import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- НАЛАШТУВАННЯ ---
# Токен береться з налаштувань Render (Environment)
API_TOKEN = os.getenv('BOT_TOKEN')

if not API_TOKEN:
    print("КРИТИЧНА ПОМИЛКА: Не знайдено BOT_TOKEN у змінних середовища!")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ДЛЯ ГЕНЕРАЦІЇ ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Військовий", "Пілот", "Хімік"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Здоровий(а)", "Міцний імунітет", "Витривалий(а)"]
AGES = ["22 роки", "30 років", "40 років", "50 років", "60 років", "80 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Лідер", "Оптиміст", "Параноїк"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Ящик консервів", "Запас води"]
CATASTROPHES = ["Ядерна зима", "Зомбі-апокаліпсис", "Всесвітній потоп", "Глобальна пандемія"]

# --- КЛАВІАТУРА ---
def get_game_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/status"), KeyboardButton(text="/vote")],
            [KeyboardButton(text="/list"), KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )

# --- КОМАНДИ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "players": {}
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n🌍 Катастрофа: {games[game_id]['catastrophe']}\nЗапрошуйте друзів: /join {game_id}")
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ Введіть код гри:")
    await callback.answer()

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games: return await message.answer("❌ Код невірний!")
    
    char = {
        "gender": random.choice(GENDERS), "prof": random.choice(PROFESSIONS),
        "health": random.choice(HEALTH_STATUS), "age": random.choice(AGES),
        "bag": random.choice(BAGGAGE)
    }
    games[game_id]["players"][message.from_user.first_name] = char
    
    await state.clear()
    await message.answer(
        f"🚨 **Ви в бункері!**\n\n👤 {char['gender']}, {char['age']}\n🛠 Професія: {char['prof']}\n❤️ Здоров'я: {char['health']}\n🎒 Багаж: {char['bag']}",
        reply_markup=get_game_keyboard()
    )

@dp.message(Command("list"))
async def show_players(message: types.Message):
    found = False
    for gid, g in games.items():
        if message.from_user.first_name in g["players"]:
            await message.answer(f"👥 Гравці в бункері #{gid}: {', '.join(g['players'].keys())}")
            found = True
    if not found: await message.answer("❌ Ви не в грі.")

@dp.message(Command("vote"))
async def start_vote(message: types.Message):
    for gid, g in games.items():
        if message.from_user.first_name in g["players"]:
            return await message.answer_poll(question="Кого виганяємо?", options=list(g["players"].keys()), is_anonymous=False)
    await message.answer("❌ Ви не в грі.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
