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

# --- СПИСКИ ДАНИХ ---
CATASTROPHES_DATA = [
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Холод -50°C.", "range": (20, 50)},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Світ кишить зараженими. Чекаємо на їх розклад.", "range": (2, 7)},
    {"name": "🌊 Всесвітній потоп", "desc": "Танення льодовиків. Землі майже не залишилось.", "range": (10, 20)},
    {"name": "👽 Нашестя іншопланетян", "desc": "Окупація Землі. Ми в останньому сховку.", "range": (5, 15)},
    {"name": "☀️ Сонячний спалах", "desc": "Атмосфера пошкоджена. Радіація випалює поверхню.", "range": (4, 10)},
    {"name": "❄️ Льодовиковий період", "desc": "Світ замерз. Виживання можливе лише в бункерах.", "range": (50, 100)},
    {"name": "☣️ Пандемія", "desc": "Повітря отруєне вірусом. Вихід без захисту — смерть.", "range": (1, 3)}
]

BUNKER_TYPES = [
    "🥚 Інкубаторний (технологія вирощування людей, стать не важлива)",
    "📦 Звичайний (бетонний блок з базовими запасами)",
    "🌿 Гідропонний (вирощування рослин без ґрунту)",
    "🏨 Люкс-бункер (комфорт, але мало ресурсів)",
    "🧬 Технологічний (лабораторії та системи фільтрації)",
    "🧪 Експериментальний (невідоме обладнання)",
    "🛠 Військовий (арсенал зброї та посилений вхід)"
]

BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Поломок не виявлено", "✅ Стан ідеальний"]

PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Безсоння", "Алергія", "Діабет", "Міцний імунітет"]
AGES = [f"{i} років" for i in range(18, 80)]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "📦 Консерви", "🍶 Запас води", "🍶 Еліксир молодості", "Лук та стріли", "Радіо", "Посібник з виживання"]
PHOBIAS = ["Клаустрофобія (замкнутий простір)", "Ахлуофобія (темрява)", "Мізофобія (бруд)", "Соціофобія (люди)", "Безстрашний(а)"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вижити за будь-яку ціну.", "🤫 Мета: Вижити."]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "❤️ Помінятися здоров'ям", "👁 Дізнатися секрет", "🛡 Імунітет від вигнання"]

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
    cat = random.choice(CATASTROPHES_DATA)
    stay_time = random.randint(cat["range"][0], cat["range"][1])
    
    games[game_id] = {
        "catastrophe": cat["name"],
        "cat_desc": cat["desc"],
        "stay_time": stay_time,
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {},
        "active_players": [],
        "revealed": {"bag": [], "prof": [], "health": []},
        "immune_players": [],
        "event_triggered": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n\n🌍 {cat['name']}\n⏳ Час: {stay_time} років\n🔑 Код: `{game_id}`", parse_mode="Markdown")
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
    
    u_id = message.from_user.id
    games[game_id]["players"][u_id] = message.from_user.first_name
    if u_id not in games[game_id]["active_players"]:
        games[game_id]["active_players"].append(u_id)
    
    # Генерація картки гравця
    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "bag": random.choice(BAGGAGE), "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS),
        "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS),
        "spec_used": False
    }
    
    g = games[game_id]
    c = player_cards[u_id]
    
    # ПОВНЕ ПОВІДОМЛЕННЯ З УСІМА ДАНИМИ ПРИ ВХОДІ
    response = (
        f"🚨 **ВИ У ГРІ #{game_id}**\n\n"
        f"🌍 **СВІТ:** {g['catastrophe']}\n"
        f"📝 **Опис:** {g['cat_desc']}\n"
        f"⏳ **Термін:** {g['stay_time']} років\n\n"
        f"🛡 **БУНКЕР:** {g['bunker']}\n"
        f"⚠️ **СТАН:** {g['prob']}\n"
        f"------------------------------\n"
        f"💼 **ВАША КАРТКА (СЕКРЕТНО):**\n"
        f"👤 Стать: {c['gender']} | ⏳ Вік: {c['age']}\n"
        f"🧠 Психіка: {c['psych']}\n"
        f"🛠 Професія: {c['prof']}\n"
        f"❤️ Здоров'я: {c['health']}\n"
        f"🎒 Багаж: {c['bag']}\n"
        f"🎸 Хобі: {c['hobby']}\n"
        f"😱 Фобія: {c['phobia']}\n"
        f"✨ Здібність: {c['spec']}\n\n"
        f"{c['goal']}"
    )
    
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# (Тут мають бути функції rev_, use_spec_, kick_, game_vote_ та cb_event)
# Додайте їх зі свого попереднього коду для повної роботи.

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
