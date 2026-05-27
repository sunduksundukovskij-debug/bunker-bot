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
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Температура впала до -50°C. Рослинність вимерла, а поверхня стала радіоактивною пусткою на десятиліття.", "range": (20, 50), "needs": ["Лікар", "Інженер", "Аптечка", "🧥 Захисний костюм"]},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Невідомий мутований вірус перетворив 99% населення на агресивних монстрів. Міста заповнені ордами мерців, що реагують на звук та запах.", "range": (2, 7), "needs": ["Поліцейський", "Мисливець", "Ніж", "Рушниця"]},
    {"name": "🤖 Повстання роботів", "desc": "Штучний інтелект визнав людство загрозою для екосистеми планети. Автономні дрони та бойові мехи полюють на все біологічне.", "range": (5, 12), "needs": ["Програміст", "Електрик", "📡 Супутниковий телефон", "🔋 Потужна батарея"]},
    {"name": "🦖 Юрський реванш", "desc": "Експерименти з ДНК вийшли з-під контролю. Гігантські хижаки минулого повернулися і за лічені місяці зруйнували людську цивілізацію.", "range": (10, 15), "needs": ["Мисливець", "Хімік", "Ніж", "🔥 Вогнемет"]},
    {"name": "🌊 Всесвітній потоп", "desc": "Глобальне потепління миттєво розтопило льодовики. Більша частина суші пішла под воду, лишилися лише верхівки гір та плавучі міста.", "range": (15, 25), "needs": ["Пілот", "Кухар", "🍶 Запас води", "🗺 Карта поверхні"]},
    {"name": "👽 Інопланетне вторгнення", "desc": "Високотехнологічна раса заблокувала орбіту планети та почала масовану зачистку міст променями смерті для колонізації Землі.", "range": (8, 20), "needs": ["Програміст", "Лікар", "Рація", "📡 Супутинуковий телефон"]},
    {"name": "☣️ Біологічна загроза", "desc": "Військовий вірус вирвався з секретної лабораторії. Повітря стало отруйним, без герметизації бункера смерть настає за лічені хвилини.", "range": (3, 8), "needs": ["Хімік", "Лікар", "💊 Антидот", "🧥 Захисний костюм"]},
    {"name": "🔌 Глобальний блекаут", "desc": "Надпотужний сонячний спалах вивів з ладу всі електромережі та змінив фізику атмосфери — електрика більше не працює як фізичне явище.", "range": (15, 40), "needs": ["Інженер", "Електрик", "Ніж", "🔥 Вогнемет"]}
]

BUNKER_DATA = [
    {"name": "🥚 Інкубаторний", "desc": "Створений для відновлення популяції. Має величезні запаси генетичного матеріалу."},
    {"name": "📦 Звичайний", "desc": "Старе радянське сховище. Товсті стіни, надійні двері, техніка потребує ремонту."},
    {"name": "🌿 Гідропонний", "desc": "Містить автоматизовані ферми для вирощування свіжої їжі."},
    {"name": "🏨 Люкс-бункер", "desc": "Приватне сховище мільйонера з басейном і кінотеатром."},
    {"name": "🧬 Технологічний", "desc": "Автоматизована система з ШІ та фільтрацією повітря."},
    {"name": "🛠 Військовий", "desc": "Підземна фортеця з арсеналом. Максимальний рівень захисту."}
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
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "🛡 Імунітет від вигнання", "👁 Дізнатися секрет", "🧬 Змінити стать"]
BACKPACK_ITEMS = ["🔥 Вогнемет", "💊 Антидот", "🔋 Потужна батарея", "🗺 Карта поверхні", "🧥 Захисний костюм", "📡 Супутниковий телефон"]

RANDOM_EVENTS = [
    {"text": "🎒 **ЗНАЙДЕНО РЮКЗАК!**\nХто перший напише слово `БУНКЕР` у чат, отримає предмет!", "type": "backpack"},
    {"text": "☢️ **ВИКИД РАДІАЦІЇ!**\nУсі здорові гравці отримують випадкову хворобу!", "type": "radiation"},
    {"text": "🩺 **МЕДИЧНЕ ДИВО!**\nОдин випадковий гравець стає повністю здоровим!", "type": "miracle_cure"}
]

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def calculate_survival_chance(game_id):
    g = games[game_id]
    survivors = g["active_players"]
    if not survivors: return 0
    
    chance = 30 
    if g["prob"] == "✅ Стан ідеальний": chance += 15
    else: chance -= 10

    cat_data = next((c for c in CATASTROPHES_DATA if c["name"] == g["catastrophe"]), None)
    genders_in_bunker = []
    
    for p_id in survivors:
        c = player_cards[p_id]
        genders_in_bunker.append(c["gender"])
        if cat_data:
            if c["prof"] in cat_data["needs"]: chance += 12
            for need in cat_data["needs"]:
                if need in c["bag"]: chance += 8
        if "Ідеальне" in c["health"] or "Здоровий" in c["health"] or "Міцний імунітет" in c["health"]: chance += 5
        elif "Вагітність" in c["health"]: chance += 10 
        else: chance -= 7
        age_val = int(c["age"].split()[0])
        if 20 <= age_val <= 40: chance += 7
        elif age_val > 65: chance -= 5
        if c["psych"] in ["Лідер", "Оптиміст", "Спокійний"]: chance += 5
        if c["psych"] == "Панікер" or "Соціофобія" in c["phobia"]: chance -= 5

    if g["bunker"] != "🥚 Інкубаторний":
        if "Чоловік" in genders_in_bunker and "Жінка" in genders_in_bunker: chance += 20
        else: chance -= 15

    return min(max(chance, 1), 100)

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
    builder.button(text="🧠 Психіка", callback_data=f"rev_psych_{game_id}")
    builder.button(text="😨 Фобія", callback_data=f"rev_phobia_{game_id}")
    builder.button(text="🎒 Багаж", callback_data=f"rev_bag_{game_id}")
    builder.button(text="✨ Здібність", callback_data=f"use_spec_{game_id}")
    builder.button(text="🗳 Голосування", callback_data=f"game_vote_{game_id}")
    builder.button(text="⚠️ Подія", callback_data=f"game_event_{game_id}")
    builder.adjust(3, 3, 2, 2)
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
    stay_time = random.randint(cat["range"][0], cat["range"][1])
    games[game_id] = {
        "catastrophe": cat["name"], "cat_desc": cat["desc"], "stay_time": stay_time,
        "bunker": bun["name"], "bunker_desc": bun["desc"],
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {}, "active_players": [], "immune_players": [], 
        "event_triggered": False, "waiting_for_word": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n\n🌍 {cat['name']}\n🔑 Код: `{game_id}`")
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ Введіть код гри:")
    await callback.answer()

@dp.message(GameStates.waiting_for_code, F.text.regexp(r'^\d{4}$'))
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games: return await message.answer("❌ Код не знайдено!")
    u_id = message.from_user.id
    games[game_id]["players"][u_id] = message.from_user.first_name
    if u_id not in games[game_id]["active_players"]: games[game_id]["active_players"].append(u_id)
    
    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "gender": random.choice(GENDERS), "bag": random.choice(BAGGAGE),
        "hobby": random.choice(HOBBIES), "phobia": random.choice(PHOBIAS),
        "spec": random.choice(SPECIAL_ABILITIES), "age": random.choice(AGES),
        "psych": random.choice(PSYCH), "spec_used": False,
        "revealed_stats": [] # Список характеристик, які гравець вже відкрив
    }
    
    g, c = games[game_id], player_cards[u_id]
    response = (f"🚨 **ГРА #{game_id}**\n\n🌍 **КАТАСТРОФА:** {g['catastrophe']}\n"
                f"📖 **ОПИС:** {g['cat_desc']}\n⏳ **ТЕРМІН:** {g['stay_time']} років\n\n"
                f"🛡 **БУНКЕР:** {g['bunker']}\nℹ️ {g['bunker_desc']}\n⚠️ Стан: {g['prob']}\n"
                f"------------------------------\n"
                f"💼 **ВАША КАРТКА:**\n"
                f"👤 Стать: {c['gender']}\n"
                f"⏳ Вік: {c['age']}\n"
                f"🛠 Професія: {c['prof']}\n"
                f"❤️ Здоров'я: {c['health']}\n"
                f"🧠 Психіка: {c['psych']}\n"
                f"😨 Фобія: {c['phobia']}\n"
                f"🎒 Багаж: {c['bag']}\n"
                f"✨ Здібність: {c['spec']}")
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# --- ПОДІЇ ТА ЗДІБНОСТІ ---
@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id]["event_triggered"]: return await callback.answer("❌ Вже було!")
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    
    for p_id in games[g_id]["players"]: 
        await bot.send_message(p_id, f"🔥 **ПОДІЯ:** {event['text']}")
    
    if event["type"] == "backpack": 
        games[g_id]["waiting_for_word"] = True
    
    elif event["type"] == "radiation":
        for p_id in games[g_id]["active_players"]:
            card = player_cards[p_id]
            # Якщо гравець здоровий (або має ідеальний стан)
            if any(word in card["health"] for word in ["Ідеальне", "Здоровий", "Міцний імунітет"]):
                old_h = card["health"]
                new_h = "Променева хвороба"
                card["health"] = new_h
                
                # Якщо здоров'я ВЖЕ було відкрито публічно
                if "health" in card["revealed_stats"]:
                    msg = f"☢️ **РАДІАЦІЯ!** У гравця {games[g_id]['players'][p_id]} стан здоров'я змінився: `{old_h}` ➔ `{new_h}`!"
                    for target in games[g_id]["players"]: await bot.send_message(target, msg)
                else:
                    # Якщо не було відкрито, просто повідомляємо гравця особисто
                    await bot.send_message(p_id, f"⚠️ Через радіацію ваше здоров'я погіршилось! Тепер у вас: `{new_h}`")
    
    await callback.answer()

@dp.callback_query(F.data.startswith("use_spec_"))
async def cb_spec(callback: types.CallbackQuery):
    u_id, g_id = callback.from_user.id, callback.data.split("_")[2]
    if u_id not in games[g_id]["active_players"]:
        return await callback.answer("❌ Вигнані не можуть діяти!", show_alert=True)
    if player_cards[u_id]["spec_used"]: return await callback.answer("❌ Вже використано!")
    
    player_cards[u_id]["spec_used"] = True
    spec_name = player_cards[u_id]["spec"]
    
    if spec_name == "🧬 Змінити стать":
        old_gender = player_cards[u_id]["gender"]
        player_cards[u_id]["gender"] = "Жінка" if old_gender == "Чоловік" else "Чоловік"
        broadcast = f"✨ **{games[g_id]['players'][u_id]}** використав здібність `{spec_name}`!\n🔄 Стать змінена з `{old_gender}` на `{player_cards[u_id]['gender']}`!"
    else:
        broadcast = f"✨ **{games[g_id]['players'][u_id]}** активує здібність:\n🧬 `{spec_name}`"

    for p_id in games[g_id]["players"]: await bot.send_message(p_id, broadcast)
    await callback.answer()

# --- ЧАТ ТА РОЗКРИТТЯ ---
@dp.message(F.text & ~F.text.startswith('/'))
async def game_chat(message: types.Message):
    u_id = message.from_user.id
    g_id = find_game_id(u_id)
    if not g_id: return
    if games[g_id].get("waiting_for_word") and message.text.strip().upper() == "БУНКЕР":
        if u_id in games[g_id]["active_players"]:
            games[g_id]["waiting_for_word"] = False
            item = random.choice(BACKPACK_ITEMS)
            player_cards[u_id]["bag"] += f", {item}"
            for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🏆 {games[g_id]['players'][u_id]} забрав: `{item}`!")
            return
    sender_name = games[g_id]["players"].get(u_id, "Гравець")
    for p_id in games[g_id]["players"]:
        chat_label = "Ви" if p_id == u_id else sender_name
        chat_text = f"💬 **{chat_label}**: {message.text}"
        try: await bot.send_message(p_id, chat_text)
        except: pass

@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    data, u_id = callback.data.split("_"), callback.from_user.id
    mode, g_id = data[1], data[2]
    if u_id not in games[g_id]["active_players"]: return await callback.answer("❌ Вигнані не можуть розкривати дані!", show_alert=True)
    
    card = player_cards[u_id]
    # Додаємо в список розкритих, щоб події знали, чи показувати зміни всім
    if mode not in card["revealed_stats"]:
        card["revealed_stats"].append(mode)
        
    mapping = {"gen": ("Стать", card["gender"]), "age": ("Вік", card["age"]), "prof": ("Професія", card["prof"]), "health": ("Здоров'я", card["health"]), "bag": ("Багаж", card["bag"]), "psych": ("Психіка", card["psych"]), "phobia": ("Фобія", card["phobia"])}
    label, val = mapping[mode]
    broadcast = f"📢 **{games[g_id]['players'][u_id]}** розкриває:\n🔍 {label}: `{val}`"
    for p_id in games[g_id]["players"]: await bot.send_message(p_id, broadcast)
    await callback.answer()

@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote(callback: types.CallbackQuery):
    u_id, g_id = callback.from_user.id, callback.data.split("_")[2]
    if u_id not in games[g_id]["active_players"]: return await callback.answer("❌ Вигнані не голосують!", show_alert=True)
    builder = InlineKeyboardBuilder()
    for p_id in games[g_id]["active_players"]: builder.button(text=games[g_id]["players"][p_id], callback_data=f"kick_{g_id}_{p_id}")
    await callback.message.answer("Голосування:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    _, g_id, t_id = callback.data.split("_")
    t_id = int(t_id)
    if t_id in games[g_id]["active_players"]:
        games[g_id]["active_players"].remove(t_id)
        c = player_cards[t_id]
        reveal_msg = (f"🚪 **ГРАВЦЯ {games[g_id]['players'][t_id]} ВИГНАНО!**\n"
                      f"💀 **Його розкрита картка:**\n"
                      f"👤 Стать: {c['gender']}\n"
                      f"⏳ Вік: {c['age']}\n"
                      f"🛠 Професія: {c['prof']}\n"
                      f"❤️ Здоров'я: {c['health']}\n"
                      f"🧠 Психіка: {c['psych']}\n"
                      f"😨 Фобія: {c['phobia']}\n"
                      f"🎒 Багаж: {c['bag']}")
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, reveal_msg)
        if len(games[g_id]["active_players"]) <= 2:
            chance = calculate_survival_chance(g_id)
            final = f"🏁 **ГРА ЗАВЕРШЕНА!**\n📈 Шанс вижити: **{chance}%**"
            for p_id in games[g_id]["players"]: await bot.send_message(p_id, final)
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
