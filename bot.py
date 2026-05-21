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

# --- СПИСКИ ДАНИХ (РОЗШИРЕНО КАТАСТРОФИ) ---
CATASTROPHES_DATA = [
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Температура -50°C. Рослини не ростуть.", "range": (20, 50)},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Невідомий вірус перетворив 99% населення на монстрів. Вулиці заповнені ордами.", "range": (2, 7)},
    {"name": "🤖 Повстання роботів", "desc": "ШІ вирішив, що люди — помилка. Автономні дрони полюють на все біологічне.", "range": (5, 12)},
    {"name": "🦖 Юрський реванш", "desc": "Динозаври повернулися. Гігантські хижаки панують на руїнах міст.", "range": (10, 15)},
    {"name": "🌊 Всесвітній потоп", "desc": "Льодовики розтанули. Весь світ — це безмежний океан із рідкісними островами.", "range": (15, 25)},
    {"name": "👽 Інопланетне вторгнення", "desc": "Прибульці захопили орбіту. Вони випалюють міста та викрадають людей.", "range": (8, 20)},
    {"name": "☄️ Падіння астероїда", "desc": "Гігантський удар спричинив цунамі та хмару пилу. Дихати на поверхні неможливо.", "range": (20, 35)},
    {"name": "☣️ Біологічна загроза", "desc": "Лабораторний вірус перетворює повітря на отруту. Без герметизації смерть миттєва.", "range": (3, 8)},
    {"name": "🧊 Новий Льодовиковий період", "desc": "Зупинка Гольфстріму заморозила планету. Світ вкритий кілометровим шаром льоду.", "range": (50, 100)},
    {"name": "👹 Вторгнення демонів", "desc": "Відкрився розлом у вимірювання темряви. На поверхні панує хаос і магія.", "range": (10, 13)},
    {"name": "🌫 Загадковий Туман", "desc": "Світ накрив густий туман, у якому живуть істоти, що реагують на звук.", "range": (5, 10)},
    {"name": "🔌 Глобальний блекаут", "desc": "Електрика більше не працює як фізичне явище. Технології відкинуті на століття назад.", "range": (15, 40)}
]

BUNKER_TYPES = ["🥚 Інкубаторний", "📦 Звичайний", "🌿 Гідропонний", "🏨 Люкс-бункер", "🧬 Технологічний", "🛠 Військовий"]
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
    {"text": "🎒 **ЗНАЙДЕНО РЮКЗАК!**\nХто перший напише слово `БУНКЕР` у чат, отримає додатковий предмет у багаж!", "type": "backpack"},
    {"text": "☢️ **ВИКИД РАДІАЦІЇ!**\nУсі здорові гравці отримують випадкову хворобу!", "type": "radiation"},
    {"text": "🩺 **МЕДИЧНЕ ДИВО!**\nОдин випадковий гравець стає повністю здоровим!", "type": "miracle_cure"},
    {"text": "🌪 **МАГНІТНА БУРЯ!**\nЕлектронні прилади дають збій.", "type": "storm"}
]

BACKPACK_ITEMS = ["🔥 Вогнемет", "💊 Антидот", "🔋 Потужна батарея", "🗺 Карта поверхні", "🧥 Захисний костюм", "📡 Супутниковий телефон"]

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
    stay_time = random.randint(cat["range"][0], cat["range"][1])
    games[game_id] = {
        "catastrophe": cat["name"], "cat_desc": cat["desc"], "stay_time": stay_time,
        "bunker": random.choice(BUNKER_TYPES), "prob": random.choice(BUNKER_PROBLEMS),
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

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games: return await message.answer("❌ Код невірний!")
    u_id = message.from_user.id
    games[game_id]["players"][u_id] = message.from_user.first_name
    if u_id not in games[game_id]["active_players"]: games[game_id]["active_players"].append(u_id)
    
    gender = random.choice(GENDERS)
    health = random.choice(HEALTH_STATUS)
    if gender == "Чоловік" and health == "Вагітність": health = "Здоровий(а)"

    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": health, "gender": gender,
        "bag": random.choice(BAGGAGE), "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "psych": random.choice(PSYCH), 
        "goal": random.choice(SECRET_GOALS), "spec_used": False
    }
    
    g, c = games[game_id], player_cards[u_id]
    response = (f"🚨 **ВИ У ГРІ #{game_id}**\n\n🌍 **КАТАСТРОФА:** {g['catastrophe']}\n📖 **ОПИС:** {g['cat_desc']}\n"
                f"🛡 **БУНКЕР:** {g['bunker']} ({g['prob']})\n------------------------------\n"
                f"💼 **ВАША КАРТКА:**\n👤 Стать: {c['gender']} | ⏳ Вік: {c['age']}\n🛠 Проф: {c['prof']}\n"
                f"❤️ Здор: {c['health']} | 🎒 Багаж: {c['bag']}\n✨ Здібність: {c['spec']}")
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# --- ЧАТ ТА ПОДІЯ РЮКЗАК ---
@dp.message(F.text & ~F.text.startswith('/'))
async def game_chat(message: types.Message):
    u_id = message.from_user.id
    g_id = find_game_id(u_id)
    if not g_id: return

    if games[g_id].get("waiting_for_word") and message.text.strip().upper() == "БУНКЕР":
        games[g_id]["waiting_for_word"] = False
        item = random.choice(BACKPACK_ITEMS)
        player_cards[u_id]["bag"] += f", {item}"
        sender_name = games[g_id]["players"][u_id]
        
        broadcast = f"🏆 **ГРАВЕЦЬ {sender_name} БУВ НАЙШВИДШИМ!**\nВін забирає з рюкзака: `{item}`.\nТепер його багаж: {player_cards[u_id]['bag']}"
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, broadcast)
        return

    status = "" if u_id in games[g_id]["active_players"] else " (Глядач) 👻"
    sender_name = games[g_id]["players"][u_id]
    for p_id in games[g_id]["players"]:
        if p_id != u_id:
            try: await bot.send_message(p_id, f"💬 **{sender_name}{status}**: {message.text}")
            except: pass
    await message.reply(f"📤 *Надіслано іншим*", parse_mode="Markdown")

# --- ВИПАДКОВІ ПОДІЇ ---
@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id]["event_triggered"]: return await callback.answer("❌ Подія вже використана!", show_alert=True)
    
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"🔥 **АКТИВОВАНО ПОДІЮ!**\n{event['text']}")

    if event["type"] == "backpack":
        games[g_id]["waiting_for_word"] = True
    
    elif event["type"] == "radiation":
        summary = "☢️ **ОПРОМІНЕННЯ:**\n"
        for u_id in games[g_id]["active_players"]:
            if "Ідеальне" in player_cards[u_id]["health"] or "Здоровий" in player_cards[u_id]["health"]:
                new_h = random.choice(["Астма", "Травма ноги", "Сліпота", "Діабет"])
                player_cards[u_id]["health"] = new_h
                summary += f"☣️ {games[g_id]['players'][u_id]} -> `{new_h}`\n"
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, summary)

    elif event["type"] == "miracle_cure":
        if games[g_id]["active_players"]:
            target_id = random.choice(games[g_id]["active_players"])
            player_cards[target_id]["health"] = "Ідеальне (Повністю здоровий)"
            target_name = games[g_id]["players"][target_id]
            for p_id in games[g_id]["players"]:
                await bot.send_message(p_id, f"🩺 **ДИВО!** Гравець **{target_name}** був повністю вилікуваний! Тепер його здоров'я: `Ідеальне`.")

    await callback.answer()

# --- СПЕЦІАЛЬНІ ЗДІБНОСТІ ТА ІНШЕ ---
@dp.callback_query(F.data.startswith("use_spec_"))
async def cb_spec_start(callback: types.CallbackQuery):
    u_id, g_id = callback.from_user.id, callback.data.split("_")[2]
    if player_cards[u_id].get("spec_used"): return await callback.answer("❌ Використано!", show_alert=True)
    
    spec = player_cards[u_id]["spec"]
    if "🧬 Змінити стать" in spec:
        old = player_cards[u_id]["gender"]
        new = "Жінка" if old == "Чоловік" else "Чоловік"
        player_cards[u_id]["gender"] = new
        player_cards[u_id]["spec_used"] = True
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🧬 {callback.from_user.first_name} тепер {new}!")
        return await callback.answer()

    if "🛡 Імунітет" in spec:
        player_cards[u_id]["spec_used"] = True
        games[g_id]["immune_players"].append(u_id)
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🛡 {callback.from_user.first_name} має імунітет!")
        return await callback.answer()

    builder = InlineKeyboardBuilder()
    for p_id in games[g_id]["active_players"]:
        if p_id != u_id: builder.button(text=games[g_id]["players"][p_id], callback_data=f"target_{g_id}_{p_id}")
    builder.adjust(2)
    await callback.message.answer("Оберіть ціль:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("target_"))
async def cb_spec_target(callback: types.CallbackQuery):
    _, g_id, t_id = callback.data.split("_")
    u_id, t_id = callback.from_user.id, int(t_id)
    spec = player_cards[u_id]["spec"]
    player_cards[u_id]["spec_used"] = True
    u_n, t_n = games[g_id]["players"][u_id], games[g_id]["players"][t_id]

    if "🔄 Помінятися багажем" in spec:
        player_cards[u_id]["bag"], player_cards[t_id]["bag"] = player_cards[t_id]["bag"], player_cards[u_id]["bag"]
        msg = f"🔄 {u_n} та {t_n} обмінялися багажем!"
    elif "📝 Помінятися професією" in spec:
        player_cards[u_id]["prof"], player_cards[t_id]["prof"] = player_cards[t_id]["prof"], player_cards[u_id]["prof"]
        msg = f"📝 {u_n} та {t_n} обмінялися професіями!"
    elif "👁 Дізнатися секрет" in spec:
        c = player_cards[t_id]
        await bot.send_message(u_id, f"👁 Секрет {t_n}: {c['prof']}, {c['health']}, {c['bag']}")
        msg = f"👁 {u_n} дізнався секрет {t_n}!"

    for p_id in games[g_id]["players"]: await bot.send_message(p_id, msg)
    await callback.message.delete()
    await callback.answer()

@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    builder = InlineKeyboardBuilder()
    for p_id in games[g_id]["active_players"]:
        if p_id not in games[g_id]["immune_players"]:
            builder.button(text=games[g_id]["players"][p_id], callback_data=f"kick_{g_id}_{p_id}")
    await callback.message.answer("Голосування:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    _, g_id, t_id = callback.data.split("_")
    t_id = int(t_id)
    if t_id in games[g_id]["active_players"]:
        games[g_id]["active_players"].remove(t_id)
        c = player_cards[t_id]
        reveal = f"🚪 **{games[g_id]['players'][t_id]} вигнаний!** Карта:\n👤 {c['gender']}, {c['age']}\n🛠 {c['prof']}\n❤️ {c['health']}\n🎒 {c['bag']}"
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, reveal)
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
