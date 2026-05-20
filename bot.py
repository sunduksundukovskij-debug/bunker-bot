import random
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters iimport random
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = '8422077163:AAFzmEMuPnPKI2pau5G2oK6X1Vm4o6XC4ck'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}
player_cards = {} 

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ З ПОЯСНЕННЯМИ ---

# Фобії з розшифровкою
PHOBIAS = [
    "Клаустрофобія (боязнь замкнутого простору)",
    "Ахлуофобія (боязнь темряви)",
    "Мізофобія (боязнь бруду та мікробів)",
    "Герпетофобія (боязнь рептилій та змій)",
    "Соціофобія (боязнь спілкування та людей)",
    "Акрофобія (боязнь висоти)",
    "Ніктофобія (боязнь нічної пори та темряви)",
    "Аквафобія (боязнь води)",
    "Гемофобія (боязнь крові)",
    "Безстрашний(а) (немає виражених фобій)"
]

# Типи бункерів з описом призначення
BUNKER_TYPES = [
    "📦 Звичайний (стандартний бетонний блок з базовими запасами)",
    "🧬 Технологічний (має лабораторії та передові системи фільтрації)",
    "🧪 Експериментальний (містить невідоме обладнання, можливі аномалії)",
    "🛠 Військовий (має арсенал зброї та посилений броньований вхід)",
    "🌿 Гідропонний (спеціалізується на вирощуванні рослин без ґрунту)",
    "🏨 Люкс-бункер (комфортні умови, басейн, але обмежені корисні ресурси)"
]

# (Решта списків залишається для функціонування гри)
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Мисливець", "Пілот", "Хімік", "Архітектор"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Діабет", "Міцний імунітет"]
AGES = ["18 років", "25 років", "33 роки", "40 років", "55 років", "70 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Лідер"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Бокс", "Малювання"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "📦 Консерви", "🍶 Запас води"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "❤️ Помінятися здоров'ям", "👁 Дізнатися секрет", "🛡 Імунітет від вигнання"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп", "👽 Нашестя іншопланетян"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити будь-якою ціною."]

RANDOM_EVENTS = [
    {"text": "⚠️ Землетрус! Гравці з відкритим багажем міняються ним!", "type": "earthquake"},
    {"text": "⚠️ Витік газу! Всі гравці з поганим здоров'ям мовчать наступний раунд.", "type": "gas_leak"}
]

# --- ЛОГІКА КНОПОК ТА СТАРТУ ---

def get_reveal_keyboard(game_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Стать", callback_data=f"rev_gen_{game_id}")
    builder.button(text="⏳ Вік", callback_data=f"rev_age_{game_id}")
    builder.button(text="🧠 Психіка", callback_data=f"rev_psy_{game_id}")
    builder.button(text="🛠 Проф", callback_data=f"rev_prof_{game_id}")
    builder.button(text="❤️ Здор", callback_data=f"rev_health_{game_id}")
    builder.button(text="🎒 Багаж", callback_data=f"rev_bag_{game_id}")
    builder.button(text="🎸 Хобі", callback_data=f"rev_hobby_{game_id}")
    builder.button(text="😱 Фобія", callback_data=f"rev_phobia_{game_id}")
    builder.button(text="✨ Здібність", callback_data=f"use_spec_{game_id}")
    builder.button(text="🗳 Голосування", callback_data=f"game_vote_{game_id}")
    builder.button(text="⚠️ Подія", callback_data=f"game_event_{game_id}")
    builder.adjust(3, 3, 3, 2)
    return builder.as_markup()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {},
        "active_players": [],
        "revealed": {"bag": [], "prof": [], "health": []},
        "immune_players": [],
        "event_triggered": False
    }
    g = games[game_id]
    await callback.message.answer(
        f"🎮 **Гру #{game_id} створено!**\nmport Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = '8422077163:AAFzmEMuPnPKI2pau5G2oK6X1Vm4o6XC4ck'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}
player_cards = {} 

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Безсоння", "Алергія", "Діабет", "Міцний імунітет", "Витривалий(а)"]
AGES = ["18 років", "22 роки", "25 років", "30 років", "35 років", "40 років", "45 років", "50 років", "60 років", "75 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "📦 Консерви", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія", "Мізофобія", "Соціофобія", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "❤️ Помінятися здоров'ям", "👁 Дізнатися секрет", "🛡 Імунітет від вигнання"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп", "👽 Нашестя іншопланетян", "☀️ Сонячний спалах", "❄️ Льодовиковий період", "☣️ Пандемія"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🧪 Експериментальний", "🛠 Військовий"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вигнати 'Поліцейського'.", "🤫 Мета: Вижити будь-якою ціною."]

# Події тепер мають ключі для виклику функцій
RANDOM_EVENTS = [
    {"text": "⚠️ Землетрус! Гравці з відкритим багажем міняються ним!", "type": "earthquake"},
    {"text": "⚠️ Витік газу! Ті, хто хворі, мовчать наступний раунд.", "type": "gas_leak"},
    {"text": "⚠️ Викид радіації! Всі здорові гравці отримують випадкову хворобу.", "type": "radiation"}
]

def get_reveal_keyboard(game_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Стать", callback_data=f"rev_gen_{game_id}")
    builder.button(text="⏳ Вік", callback_data=f"rev_age_{game_id}")
    builder.button(text="🧠 Психіка", callback_data=f"rev_psy_{game_id}")
    builder.button(text="🛠 Проф", callback_data=f"rev_prof_{game_id}")
    builder.button(text="❤️ Здор", callback_data=f"rev_health_{game_id}")
    builder.button(text="🎒 Багаж", callback_data=f"rev_bag_{game_id}")
    builder.button(text="🎸 Хобі", callback_data=f"rev_hobby_{game_id}")
    builder.button(text="😱 Фобія", callback_data=f"rev_phobia_{game_id}")
    builder.button(text="✨ Здібність", callback_data=f"use_spec_{game_id}")
    builder.button(text="🗳 Голосування", callback_data=f"game_vote_{game_id}")
    builder.button(text="⚠️ Подія", callback_data=f"game_event_{game_id}")
    builder.adjust(3, 3, 3, 2)
    return builder.as_markup()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await
