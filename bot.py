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

# --- РОЗШИРЕНІ КАТАСТРОФИ З ДІАПАЗОНОМ ЧАСУ ---
CATASTROPHES_DATA = [
    {"name": "🌋 Ядерна зима", "desc": "Масований ядерний удар. Температура -50°C, небо затягнуте радіоактивним попелом.", "range": (20, 50)},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Вірус перетворив 95% людей на монстрів. Потрібно чекати, поки вони вимруть.", "range": (2, 7)},
    {"name": "🌊 Всесвітній потоп", "desc": "Рівень океану піднявся на 300 метрів. Суходолу майже не залишилося.", "range": (10, 20)},
    {"name": "👽 Нашестя іншопланетян", "desc": "Земля окупована. Бункер — останній сховок від ворожих сканерів.", "range": (5, 15)},
    {"name": "☀️ Сонячний спалах", "desc": "Атмосфера спалена енергією Сонця. Будь-яка електроніка згорає.", "range": (4, 10)},
    {"name": "❄️ Льодовиковий період", "desc": "Планета скута кригою. Життя можливе лише глибоко під землею.", "range": (50, 100)},
    {"name": "☣️ Пандемія", "desc": "Смертельний вірус у повітрі. Вихід назовні — миттєва смерть.", "range": (1, 3)}
]

# --- СПИСКИ (ВИПРАВЛЕНІ) ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Безсоння", "Алергія", "Діабет", "Міцний імунітет", "Витривалий(а)"]
AGES = [f"{i} років" for i in range(18, 80)]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "📦 Консерви", "🍶 Запас води", "🍶 Еліксир молодості (-10р)", "Лук та стріли", "Набір Юний Хімік", "Радіо", "Посібник з виживання"]
PHOBIAS = ["Клаустрофобія (боязнь замкнутого простору)", "Ахлуофобія (боязнь темряви)", "Мізофобія (боязнь бруду)", "Соціофобія (люди)", "Немає", "Гемофобія (боязнь крові)", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "❤️ Помінятися здоров'ям", "👁 Дізнатися секрет", "🛡 Імунітет від вигнання"]
BUNKER_TYPES = [
    "🥚 Інкубаторний (технологія вирощування людей, стать не важлива)",
    "📦 Звичайний (стандартний бетонний блок)",
    "🌿 Гідропонний (вирощування рослин без ґрунту)",
    "🏨 Люкс-бункер (басейн, комфорт, але мало ресурсів)",
    "🧬 Технологічний (лабораторії та системи фільтрації)",
    "🧪 Експериментальний (містить невідоме обладнання)",
    "🛠 Військовий (арсенал зброї та посилений вхід)"
]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Поломок не виявлено", "✅ Стан ідеальний"] 
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вигнати 'Поліцейського'.", "🤫 Мета: Вижити за будь-яку ціну.", "🤫 Мета: Вижити."]

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
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    cat = random.choice(CATASTROPHES_DATA)
    stay_time = random.randint(cat["range"][0], cat["range"][1]) # ГЕНЕРАЦІЯ РОКІВ
    
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
    
    msg = (f"🎮 **Гру #{game_id} створено!**\n\n"
           f"🌍 **Катастрофа:** {cat['name']}\n"
           f"📝 **Опис:** {cat['desc']}\n"
           f"⏳ **Час у бункері:** {stay_time} років\n"
           f"🛡 **Бункер:** {games[game_id]['bunker']}\n"
           f"⚠️ **Стан:** {games[game_id]['prob']}\n\n"
           f"🔑 Код для входу: `{game_id}`")
    
    await callback.message.answer(msg, parse_mode="Markdown")
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
    
    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "bag": random.choice(BAGGAGE), "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS),
        "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS),
        "spec_used": False
    }
    
    g = games[game_id]
    await state.clear()
    await message.answer(f"🚨 Ви у грі #{game_id}!\n🌍 Світ: {g['catastrophe']} ({g['stay_time']} років)", reply_markup=get_reveal_keyboard(game_id))

# --- ЛОГІКА ПОДІЙ (ЗЕМЛЕТРУС) ---
@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id]["event_triggered"]:
        return await callback.answer("❌ Вже було!", show_alert=True)
    
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"🔥 **ПОДІЯ!**\n{event['text']}")

    if event["type"] == "earthquake":
        rev_users = [u_id for u_id in games[g_id]["active_players"] if u_id in games[g_id]["revealed"]["bag"]]
        if len(rev_users) >= 2:
            bags = [player_cards[u_id]["bag"] for u_id in rev_users]
            random.shuffle(bags)
            summary = "🌍 **Результати землетрусу:**\n"
            for i, u_id in enumerate(rev_users):
                player_cards[u_id]["bag"] = bags[i]
                summary += f"🎒 {games[g_id]['players'][u_id]} отримав: {bags[i]}\n"
                await bot.send_message(u_id, f"⚠️ Твій новий багаж: {bags[i]}")
            for p_id in games[g_id]["players"]: await bot.send_message(p_id, summary)
    await callback.answer()

# --- ВІДКРИТТЯ ХАРАКТЕРИСТИК ---
@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    data = callback.data.split("_")
    attr, g_id, u_id = data[1], data[2], callback.from_user.id
    if attr in ["bag", "prof", "health"]: # Додаємо в список відкритих для подій/здібностей
        if u_id not in games[g_id]["revealed"][attr]:
            games[g_id]["revealed"][attr].append(u_id)
            
    card = player_cards[u_id]
    mapping = {"gen": ("Стать", card["gender"]), "age": ("Вік", card["age"]), "psy": ("Психіку", card["psych"]), "prof": ("Проф", card["prof"]), "health": ("Здоров'я", card["health"]), "bag": ("Багаж", card["bag"]), "hobby": ("Хобі", card["hobby"]), "phobia": ("Фобію", card["phobia"])}
    label, val = mapping[attr]
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"📢 {callback.from_user.first_name} відкриває {label}: `{val}`")
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
