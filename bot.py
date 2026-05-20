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

# --- КОНФІГУРАЦІЯ ---
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

# --- СПИСКИ ХАРАКТЕРИСТИК ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Астроном", "Уфолог", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота на одне око", "Безсоння", "Алергія", "Діабет", "Погана імунна система", "Безплодя", "1 нога", "Заражений(а)", "Міцний імунітет", "Витривалий(а)", "Швидка регенерація", "Чудовий зір", "Атлетична статура", "Відсутність хронічних хвороб"]
AGES = ["18 років", "22 роки", "25 років", "30 років", "33 роки", "40 років", "45 років", "50 років", "55 років", "60 років", "70 років", "85 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Набір (юний хімік)", "Еліксир Молодості(-10р)", "Гітара", "Інструменти", "Запальничка", "Компас", "📦 Ящик консервів", "🥖 Сухпайок", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія (темрява)", "Мізофобія (бруд)", "Герпетофобія (плазуни)", "Соціофобія", "Немає", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "⏳ Помінятися віком", "📢 'Заткнути' гравця на 1 хв", "🛡 Імунітет від вигнання", "📝 Змінити професію", "👁 Дізнатися секрет іншого", "🧨 Анулювати голос"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп", "👽 Нашестя іншопланетян", "🤖 Повстання ШІ", "🦠 Смертельний грибок"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🧪 Експериментальний", "🌿 Гідропонний", "🛠 Військовий", "🏨 Люкс-бункер", "🛸 Космічна станція"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "забагато мишей", "старе радіо", "грибок на стінах"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вигнати 'Поліцейського'.", "🤫 Мета: Вижити будь-якою ціною.", "🤫 Мета: Не допустити зброю в бункер."]

# --- ОБРОБНИКИ ---

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    builder.adjust(1)
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": []
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n\n🌍 {games[game_id]['catastrophe']}\n🔑 Код: `{game_id}`", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ Введіть код гри:")
    await callback.answer()

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games:
        return await message.answer("❌ Код невірний!")
    
    await state.clear()
    g = games[game_id]
    
    # ФОРМУЄМО ПОВНУ КАРТКУ ТУТ
    full_card = (
        f"🚨 **ВИ У ГРІ #{game_id}**\n\n"
        f"🌍 **Катастрофа:** {g['catastrophe']}\n"
        f"🛡 **Бункер:** {g['bunker']} ({g['prob']})\n\n"
        f"👤 {random.choice(GENDERS)}, {random.choice(AGES)}\n"
        f"🛠 **Професія:** {random.choice(PROFESSIONS)}\n"
        f"❤️ **Здоров'я:** {random.choice(HEALTH_STATUS)}\n"
        f"🧠 **Псих. стан:** {random.choice(PSYCH)}\n"
        f"🎸 **Хобі:** {random.choice(HOBBIES)}\n"
        f"🎒 **Багаж:** {random.choice(BAGGAGE)}\n"
        f"😱 **Фобія:** {random.choice(PHOBIAS)}\n"
        f"✨ **Здібність:** {random.choice(SPECIAL_ABILITIES)}\n\n"
        f"🎯 **{random.choice(SECRET_GOALS)}**"
    )
    
    await message.answer(full_card, parse_mode="Markdown")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
