import random
import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    print("КРИТИЧНА ПОМИЛКА: BOT_TOKEN не знайдено в налаштуваннях Render!")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
games = {}

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- ТУТ ТВОЇ СПИСКИ (PROFESSIONS, CATASTROPHES і т.д.) ---
# ... залиш їх як були ...

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

async def main():
    print("Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Сталася помилка: {e}")
