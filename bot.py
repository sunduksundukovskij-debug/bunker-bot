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

# --- ТУТ ВСІ ВАШІ СПИСКИ (PROFESSIONS, CATASTROPHES_DATA і т.д.) ---
# (Залишаю їх за замовчуванням, як у попередньому варіанті)

CATASTROPHES_DATA = [
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Холод -50°C.", "range": (20, 50)},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Світ кишить зараженими. Чекаємо на їх розклад.", "range": (2, 7)},
    {"name": "🌊 Всесвітній потоп", "desc": "Танення льодовиків. Землі майже не залишилось.", "range": (10, 20)},
    {"name": "👽 Нашестя іншопланетян", "desc": "Окупація Землі. Ми в останньому сховку.", "range": (5, 15)},
    {"name": "☀️ Сонячний спалах", "desc": "Атмосфера пошкоджена. Радіація випалює поверхню.", "range": (4, 10)},
    {"name": "❄️ Льодовиковий період", "desc": "Світ замерз. Виживання можливе лише в бункерах.", "range": (50, 100)},
    {"name": "☣️ Пандемія", "desc": "Повітря отруєне вірусом. Вихід без захисту — смерть.", "range": (1, 3)}
]

BUNKER_TYPES = ["🥚 Інкубаторний (технологія вирощування людей)", "📦 Звичайний", "🌿 Гідропонний", "🏨 Люкс-бункер", "🧬 Технологічний", "🧪 Експериментальний", "🛠 Військовий"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "✅ Стан ідеальний"]
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)"]
AGES = [f"{i} років" for i in range(18, 80)]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "📦 Консерви"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія", "Безстрашний(а)"]
SECRET_GOALS = ["🤫 Мета: Вижити за будь-яку ціну."]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "🛡 Імунітет"]

# --- ДОПОМІЖНА ФУНКЦІЯ ДЛЯ ПОШУКУ ГРИ ГРАВЦЯ ---
def find_game_id(user_id):
    for g_id, data in games.items():
        if user_id in data["players"]:
            return g_id
    return None

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
        "catastrophe": cat["name"], "cat_desc": cat["desc"], "stay_time": stay_time,
        "bunker": random.choice(BUNKER_TYPES), "prob": random.choice(BUNKER_PROBLEMS),
        "players": {}, "active_players": [], "revealed": {"bag": [], "prof": [], "health": []},
        "immune_players": [], "event_triggered": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n\n🌍 {cat['name']}\n⏳ Час: {stay_time} років\n🔑 Код: `{game_id}`")
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
    if u_id not in games[game_id]["active_players"]: games[game_id]["active_players"].append(u_id)
    
    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS), "bag": random.choice(BAGGAGE),
        "hobby": random.choice(HOBBIES), "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS), "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS),
        "spec_used": False
    }
    g, c = games[game_id], player_cards[u_id]
    response = (f"🚨 **ВИ У ГРІ #{game_id}**\n\n🌍 **СВІТ:** {g['catastrophe']}\n⏳ **Термін:** {g['stay_time']} років\n"
                f"🛡 **БУНКЕР:** {g['bunker']}\n⚠️ **СТАН:** {g['prob']}\n------------------------------\n"
                f"💼 **ВАША КАРТКА:**\n👤 {c['gender']}, {c['age']}\n🛠 Проф: {c['prof']}\n❤️ Здор: {c['health']}\n"
                f"🎒 Багаж: {c['bag']}\n😱 Фобія: {c['phobia']}\n✨ Здібність: {c['spec']}\n\n{c['goal']}")
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# --- ЧАТ: ПЕРЕСИЛАННЯ ПОВІДОМЛЕНЬ МІЖ ГРАВЦЯМИ ---
@dp.message(F.text)
async def game_chat(message: types.Message):
    # Шукаємо, в якій грі цей гравець
    game_id = find_game_id(message.from_user.id)
    
    if game_id:
        # Пересилаємо повідомлення всім учасникам цієї гри
        sender_name = message.from_user.first_name
        text = message.text
        
        for player_id in games[game_id]["players"]:
            if player_id != message.from_user.id:  # Не надсилати самому собі
                try:
                    await bot.send_message(player_id, f"💬 **{sender_name}**: {text}", parse_mode="Markdown")
                except Exception:
                    pass # На випадок, якщо бот заблокований
    else:
        await message.answer("💡 Ви не в грі. Створіть гру або приєднайтеся.")

# --- ТУТ ФУНКЦІЇ rev_ ТА game_event_ (ЗЕМЛЕТРУС) ---
# ... (Додайте їх з попереднього коду)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
