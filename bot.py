import random
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАЛАШТУВАННЯ ---
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
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Температура впала до -50°C. Рослинність вимерла, а поверхня стала пусткою.", "range": (20, 50), "needs": ["Лікар", "Інженер", "Аптечка", "🧥 Захисний костюм"]},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Невідомий мутований вірус перетворив 99% населення на агресивних монстрів. Міста заповнені ордами мерців.", "range": (2, 7), "needs": ["Поліцейський", "Мисливець", "Ніж", "Рушниця"]},
    {"name": "🤖 Повстання роботів", "desc": "Штучний інтелект визнав людство загрозою. Автономні дрони та бойові машини полюють на все біологічне.", "range": (5, 12), "needs": ["Програміст", "Електрик", "📡 Супутниковий телефон", "🔋 Потужна батарея"]},
    {"name": "🦖 Юрський реванш", "desc": "Експерименти з ДНК вийшли з-під контролю. Гігантські хижаки минулого повернулися і зруйнували людську цивілізацію.", "range": (10, 15), "needs": ["Мисливець", "Хімік", "Ніж", "🔥 Вогнемет"]},
    {"name": "🌊 Всесвітній потоп", "desc": "Глобальне потепління миттєво розтопило льодовики. Більша частина суші пішла під воду, лишилися лише верхівки гір.", "range": (15, 25), "needs": ["Пілот", "Кухар", "🍶 Запас води", "🗺 Карта поверхні"]},
    {"name": "👽 Інопланетне вторгнення", "desc": "Високотехнологічна раса заблокувала орбіту та почала масовану зачистку планети променями смерті.", "range": (8, 20), "needs": ["Програміст", "Лікар", "Рація", "📡 Супутниковий телефон"]},
    {"name": "☣️ Біологічна загроза", "desc": "Військовий вірус вирвався з лабораторії. Повітря стало отруйним, без герметизації смерть настає за лічені хвилини.", "range": (3, 8), "needs": ["Хімік", "Лікар", "💊 Антидот", "🧥 Захисний костюм"]},
    {"name": "🔌 Глобальний блекаут", "desc": "Потужний сонячний спалах вивів з ладу всі електромережі та змінив закони фізики — електрика більше не працює.", "range": (15, 40), "needs": ["Інженер", "Електрик", "Ніж", "🔥 Вогнемет"]}
]

BUNKER_DATA = [
    {"name": "🥚 Інкубаторний", "desc": "Створений для відновлення популяції. Має запаси генетичного матеріалу."},
    {"name": "📦 Звичайний", "desc": "Старе радянське сховище. Товсті стіни, але техніка постійно виходить з ладу."},
    {"name": "🌿 Гідропонний", "desc": "Містить автоматизовані ферми для вирощування свіжої їжі."},
    {"name": "🏨 Люкс-бункер", "desc": "Приватне сховище мільйонера з басейном і кінотеатром."},
    {"name": "🧬 Технологічний", "desc": "Автоматизована система з ШІ та найкращими фільтрами повітря."},
    {"name": "🛠 Військовий", "desc": "Підземна фортеця з арсеналом і максимальною бронею."}
]

BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Стан ідеальний"]
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Поліцейський", "Мисливець", "Пілот", "Хімік"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Безсоння", "Діабет", "Міцний імунітет"]
AGES = [f"{i} років" for i in range(18, 80)]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Лідер", "Меланхолік", "Цинік"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "📦 Консерви", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія", "Мізофобія", "Соціофобія", "Безстрашний(а)"]
SECRET_GOALS = ["🤫 Мета: Вижити за будь-яку ціну.", "🤫 Мета: Вижити разом із Лікарем."]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "🛡 Імунітет від вигнання", "👁 Дізнатися секрет", "🧬 Змінити стать"]

RANDOM_EVENTS = [
    {"text": "🎒 **ЗНАЙДЕНО РЮКЗАК!**\nХто перший напише слово `БУНКЕР` у чат, отримає предмет!", "type": "backpack"},
    {"text": "☢️ **ВИКИД РАДІАЦІЇ!**\nУсі здорові гравці отримують випадкову хворобу!", "type": "radiation"},
    {"text": "🩺 **МЕДИЧНЕ ДИВО!**\nОдин випадковий гравець стає повністю здоровим!", "type": "miracle_cure"}
]

BACKPACK_ITEMS = ["🔥 Вогнемет", "💊 Антидот", "🔋 Потужна батарея", "🗺 Карта поверхні", "🧥 Захисний костюм", "📡 Супутинуковий телефон"]

# --- РОЗРАХУНОК ВИЖИВАННЯ ---
def calculate_survival_chance(game_id):
    g = games[game_id]
    survivors = g["active_players"]
    if not survivors: return 0
    chance = 25 
    cat_data = next((c for c in CATASTROPHES_DATA if c["name"] == g["catastrophe"]), None)
    
    for p_id in survivors:
        c = player_cards[p_id]
        if cat_data:
            if c["prof"] in cat_data["needs"]: chance += 15
            if any(item in c["bag"] for item in cat_data["needs"]): chance += 10
        if "Здоровий" in c["health"] or "Ідеальне" in c["health"]: chance += 7
        else: chance -= 5
        if "Панікер" in c["psych"]: chance -= 5
    return min(max(chance, 5), 100)

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def find_game_id(user_id):
    for g_id, data in games.items():
        if user_id in data["players"]: return g_id
    return None

def get_reveal_keyboard(game_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Стать", callback_data=f"rev_gen_{game_id}")
    builder.button(text="⏳ Вік", callback_data=f"rev_age_{game_id}")
    builder.button(text="🛠 Проф", callback_data=f"rev_prof_{game_id}")
    builder.button(text="❤️ Здор", callback_data=f"rev_health_{game_id}")
    builder.button(text="🎒 Багаж", callback_data=f"rev_bag_{game_id}")
    builder.button(text="🎸 Хобі", callback_data=f"rev_hobby_{game_id}")
    builder.button(text="✨ Здібність", callback_data=f"use_spec_{game_id}")
    builder.button(text="🗳 Голосування", callback_data=f"game_vote_{game_id}")
    builder.button(text="⚠️ Подія", callback_data=f"game_event_{game_id}")
    builder.adjust(3, 3, 3)
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
    bun = random.choice(BUNKER_DATA)
    games[game_id] = {
        "catastrophe": cat["name"], "cat_desc": cat["desc"],
        "bunker": bun["name"], "bunker_desc": bun["desc"],
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {}, "active_players": [], "immune_players": [], 
        "event_triggered": False, "waiting_for_word": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n🌍 {cat['name']}\n🔑 Код: `{game_id}`")
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
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "gender": random.choice(GENDERS), "bag": random.choice(BAGGAGE),
        "hobby": random.choice(HOBBIES), "phobia": random.choice(PHOBIAS),
        "spec": random.choice(SPECIAL_ABILITIES), "age": random.choice(AGES),
        "psych": random.choice(PSYCH), "spec_used": False
    }
    
    g, c = games[game_id], player_cards[u_id]
    response = (f"🚨 **ГРА #{game_id}**\n\n🌍 **КАТАСТРОФА:** {g['catastrophe']}\n"
                f"📖 **ОПИС:** {g['cat_desc']}\n\n"
                f"🛡 **БУНКЕР:** {g['bunker']}\nℹ️ {g['bunker_desc']}\n⚠️ Стан: {g['prob']}\n"
                f"------------------------------\n"
                f"💼 **ВАША КАРТКА:**\n👤 {c['gender']}, {c['age']}\n🛠 {c['prof']}\n❤️ {c['health']}\n"
                f"🧠 {c['psych']} | 😨 {c['phobia']}\n🎒 {c['bag']} | ✨ {c['spec']}")
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# --- ЧАТ ТА ПОДІЇ ---
@dp.message(F.text & ~F.text.startswith('/'))
async def game_chat(message: types.Message):
    u_id = message.from_user.id
    g_id = find_game_id(u_id)
    if not g_id: return
    if games[g_id].get("waiting_for_word") and message.text.strip().upper() == "БУНКЕР":
        games[g_id]["waiting_for_word"] = False
        item = random.choice(BACKPACK_ITEMS)
        player_cards[u_id]["bag"] += f", {item}"
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, f"🏆 {games[g_id]['players'][u_id]} забрав з рюкзака: `{item}`!")
        return
    for p_id in games[g_id]["players"]:
        if p_id != u_id: await bot.send_message(p_id, f"💬 **{games[g_id]['players'][u_id]}**: {message.text}")

@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id]["event_triggered"]: return await callback.answer("❌ Вже було!")
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🔥 **ПОДІЯ:** {event['text']}")
    if event["type"] == "backpack": games[g_id]["waiting_for_word"] = True
    elif event["type"] == "miracle_cure":
        t_id = random.choice(games[g_id]["active_players"])
        player_cards[t_id]["health"] = "Ідеальне"
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🩺 {games[g_id]['players'][t_id]} вилікуваний!")
    await callback.answer()

# --- ГОЛОСУВАННЯ ТА ФІНАЛ ---
@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    builder = InlineKeyboardBuilder()
    for p_id in games[g_id]["active_players"]:
        builder.button(text=games[g_id]["players"][p_id], callback_data=f"kick_{g_id}_{p_id}")
    await callback.message.answer("Кого вигнати?", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    _, g_id, t_id = callback.data.split("_")
    t_id = int(t_id)
    if t_id in games[g_id]["active_players"]:
        games[g_id]["active_players"].remove(t_id)
        c = player_cards[t_id]
        msg = f"🚪 **{games[g_id]['players'][t_id]} вигнаний!** Його карта:\n🛠 {c['prof']} | ❤️ {c['health']}"
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, msg)
        
        # ПЕРЕВІРКА КІНЦЯ ГРИ
        if len(games[g_id]["active_players"]) <= 2:
            chance = calculate_survival_chance(g_id)
            final = f"🏁 **ГРА ЗАВЕРШЕНА!**\n\nУ бункері залишилися:\n"
            for p_id in games[g_id]["active_players"]:
                final += f"👤 {games[g_id]['players'][p_id]} ({player_cards[p_id]['prof']})\n"
            final += f"\n📈 Шанс на виживання: **{chance}%**"
            for p_id in games[g_id]["players"]: await bot.send_message(p_id, final)
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
