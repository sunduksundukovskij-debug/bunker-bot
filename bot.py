import random
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАЛАШТУВАННЯ ---
# Токен зчитується з налаштувань Environment на Render
API_TOKEN = os.getenv('BOT_TOKEN')

# Якщо токен не знайдено, бот не запуститься, щоб не було помилок Unauthorized
if not API_TOKEN:
    raise ValueError("ПОМИЛКА: Змінна середовища BOT_TOKEN не встановлена!")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Вчитель", "Поліцейський"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Здоровий", "Міцний імунітет"]
AGES = ["22 роки", "30 років", "40 років", "60 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Лідер", "Оптиміст"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Ящик консервів"]
CATASTROPHES = ["Ядерна зима", "Зомбі-апокаліпсис", "Всесвітній потоп", "Глобальна пандемія"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🛠 Військовий", "🏨 Люкс-бункер"]

# --- КОМАНДИ ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    builder.adjust(1)
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {"catastrophe": random.choice(CATASTROPHES), "bunker": random.choice(BUNKER_TYPES), "players": []}
    await callback.message.answer(f"🎮 Гру #{game_id} створено!\n🌍 {games[game_id]['catastrophe']}\n🔑 Код: `{game_id}`", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ Введіть код гри:")

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games: return await message.answer("❌ Невірний код!")
    
    await state.clear()
    p_name = message.from_user.first_name
    if p_name not in games[game_id]["players"]: games[game_id]["players"].append(p_name)
    
    g = games[game_id]
    response = (f"🚨 **ВИ У ГРІ #{game_id}**\n\n🌍 {g['catastrophe']}\n🛡 {g['bunker']}\n\n"
                f"👤 {random.choice(GENDERS)}, {random.choice(AGES)}\n🛠 Професія: {random.choice(PROFESSIONS)}\n"
                f"❤️ Здоров'я: {random.choice(HEALTH_STATUS)}\n🎒 Багаж: {random.choice(BAGGAGE)}")
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("vote"))
async def start_vote(message: types.Message):
    game_id = next(iter(games), None)
    if game_id and games[game_id]["players"]:
        await message.answer_poll(question="Кого виганяємо?", options=games[game_id]["players"], is_anonymous=False)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
