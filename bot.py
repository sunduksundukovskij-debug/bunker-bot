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

RANDOM_EVENTS = [
    {"text": "⚠️ Землетрус! Гравці з відкритим багажем міняються ним!", "type": "earthquake"},
    {"text": "⚠️ Витік газу! Ті, хто хворі, мовчать наступний раунд.", "type": "gas_leak"},
    {"text": "⚠️ Викид радіації! Всі здорові гравці отримують випадкову хворобу.", "type": "radiation"}
]

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def find_game_id(user_id):
    for g_id, data in games.items():
        if user_id in data["players"]: return g_id
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

# --- ОСНОВНА ЛОГІКА ---
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
        "immune_players": [], "event_triggered": False, "votes": {}
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

# --- ЧАТ ---
@dp.message(F.text & ~F.text.startswith('/'))
async def game_chat(message: types.Message):
    game_id = find_game_id(message.from_user.id)
    if game_id:
        for p_id in games[game_id]["players"]:
            if p_id != message.from_user.id:
                await bot.send_message(p_id, f"💬 **{message.from_user.first_name}**: {message.text}")

# --- ФУНКЦІЇ ВІДКРИТТЯ (rev_) ---
@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    data = callback.data.split("_")
    attr, g_id, u_id = data[1], data[2], callback.from_user.id
    if attr in games[g_id]["revealed"] and u_id not in games[g_id]["revealed"][attr]:
        games[g_id]["revealed"][attr].append(u_id)
    card = player_cards[u_id]
    mapping = {"gen": ("Стать", card["gender"]), "age": ("Вік", card["age"]), "psy": ("Психіку", card["psych"]), "prof": ("Проф", card["prof"]), "health": ("Здоров'я", card["health"]), "bag": ("Багаж", card["bag"]), "hobby": ("Хобі", card["hobby"]), "phobia": ("Фобію", card["phobia"])}
    label, val = mapping[attr]
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"📢 {callback.from_user.first_name} відкриває {label}: `{val}`")
    await callback.answer()

# --- ПОДІЇ (ЗЕМЛЕТРУС ТА ІНШІ) ---
@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id]["event_triggered"]: return await callback.answer("❌ Вже було!", show_alert=True)
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🔥 **ПОДІЯ!**\n{event['text']}")
    if event["type"] == "earthquake":
        rev_users = [u for u in games[g_id]["active_players"] if u in games[g_id]["revealed"]["bag"]]
        if len(rev_users) >= 2:
            bags = [player_cards[u]["bag"] for u in rev_users]
            random.shuffle(bags)
            res = "🌍 **Наслідки:**\n"
            for i, u in enumerate(rev_users):
                player_cards[u]["bag"] = bags[i]
                res += f"🎒 {games[g_id]['players'][u]} -> {bags[i]}\n"
            for p_id in games[g_id]["players"]: await bot.send_message(p_id, res)
    await callback.answer()

# --- ЗДІБНОСТІ ТА ГОЛОСУВАННЯ ---
@dp.callback_query(F.data.startswith("use_spec_"))
async def cb_spec(callback: types.CallbackQuery):
    u_id, g_id = callback.from_user.id, callback.data.split("_")[2]
    if player_cards[u_id]["spec_used"]: return await callback.answer("❌ Ви вже використали здібність!", show_alert=True)
    player_cards[u_id]["spec_used"] = True
    if "Імунітет" in player_cards[u_id]["spec"]: games[g_id]["immune_players"].append(u_id)
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"✨ {callback.from_user.first_name} активував: {player_cards[u_id]['spec']}")
    await callback.answer()

@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote_menu(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    builder = InlineKeyboardBuilder()
    for p_id in games[g_id]["active_players"]:
        builder.button(text=games[g_id]["players"][p_id], callback_data=f"kick_{g_id}_{p_id}")
    builder.adjust(2)
    await callback.message.answer("🗳 Оберіть, кого вигнати:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    _, g_id, target_id = callback.data.split("_")
    target_id = int(target_id)
    if target_id in games[g_id]["immune_players"]:
        return await callback.message.answer(f"🛡 {games[g_id]['players'][target_id]} має імунітет!")
    if target_id in games[g_id]["active_players"]:
        games[g_id]["active_players"].remove(target_id)
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, f"🚪 Гравця **{games[g_id]['players'][target_id]}** вигнано з бункера!")
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
