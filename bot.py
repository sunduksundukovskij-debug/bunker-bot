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

# --- СПИСКИ ЗДІБНОСТЕЙ ---
SPECIAL_ABILITIES = [
    "🔄 Помінятися багажем", 
    "📝 Помінятися професією", 
    "❤️ Помінятися здоров'ям", 
    "👁 Дізнатися секрет",
    "🛡 Імунітет від вигнання"
]

# (Решта списків характеристик залишаються без змін)
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Мисливець", "Пілот", "Хімік"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Діабет", "Міцний імунітет"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "📦 Консерви", "🍶 Запас води"]
AGES = ["18 років", "25 років", "33 роки", "40 років", "55 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Лідер"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🛠 Військовий"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вижити будь-якою ціною."]
RANDOM_EVENTS = ["⚠️ ПОДІЯ: Землетрус!", "⚠️ ПОДІЯ: Витік газу!"]

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
        "immune_players": [],  # Ті, хто активував імунітет
        "event_triggered": False
    }
    await callback.message.answer(f"🎮 Гру #{game_id} створено!\nКод: `{game_id}`")
    await callback.answer()

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games: return await message.answer("❌ Невірний код!")
    u_id = message.from_user.id
    games[game_id]["players"][u_id] = message.from_user.first_name
    games[game_id]["active_players"].append(u_id)
    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "bag": random.choice(BAGGAGE), "hobby": "Риболовля", "phobia": "Немає",
        "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS),
        "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS),
        "spec_used": False
    }
    await state.clear()
    await message.answer(f"🚨 Ви у грі #{game_id}!", reply_markup=get_reveal_keyboard(game_id))

# --- ВИКОРИСТАННЯ ЗДІБНОСТЕЙ ---

@dp.callback_query(F.data.startswith("use_spec_"))
async def cb_use_spec(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    u_id = callback.from_user.id
    card = player_cards[u_id]

    if card["spec_used"]:
        return await callback.answer("❌ Ви вже використали свою здібність!", show_alert=True)

    # 🛡 ПЕРЕВІРКА НА ІМУНІТЕТ
    if "Імунітет" in card["spec"]:
        card["spec_used"] = True
        games[g_id]["immune_players"].append(u_id)
        msg = f"🛡 **ЗДІБНІСТЬ!** Гравець {callback.from_user.first_name} активував ІМУНІТЕТ! Тепер за нього не можна голосувати."
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, msg)
        return await callback.answer()

    # (Логіка для обміну та секретів)
    attr_map = {"багажем": "bag", "професією": "prof", "здоров'ям": "health"}
    target_attr = next((attr_map[k] for k in attr_map if k in card["spec"]), None)
    
    builder = InlineKeyboardBuilder()
    if target_attr:
        targets = [p
