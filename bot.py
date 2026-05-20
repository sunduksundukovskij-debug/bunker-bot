import random
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

# --- ПОВНІ СПИСКИ ХАРАКТЕРИСТИК ---
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
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🧪 Експериментальний", "🌿 Гідропонний", "🛠 Військовий", "🏨 Люкс-бункер"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "забруднена вода", "✅ Жодних проблем!", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вигнати 'Поліцейського'.", "🤫 Мета: Вижити будь-якою ціною."]
RANDOM_EVENTS = ["⚠️ Землетрус! Всі міняються багажем!", "⚠️ Витік газу! Ті, хто хворі, мовчать 1 хв.", "⚠️ Мутація! Випадковий гравець змінює Професію."]

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
    builder.button(text="⚠️ Подія",
