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

# --- ПОВНІ СПИСКИ ДАНИХ ---
CATASTROPHES_DATA = [
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Температура -50°C. Рослини гинуть, виживання лише в герметичних бункерах.", "range": (20, 50)},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Невідомий вірус перетворив 99% населення на монстрів. Потрібно перечекати розклад тіл мертвих.", "range": (2, 7)},
    {"name": "🌊 Всесвітній потоп", "desc": "Рівень океану піднявся на сотні метрів. Суходолу майже не залишилося.", "range": (10, 20)},
    {"name": "👽 Нашестя іншопланетян", "desc": "Земля окупована. Бункер захищений від теплових сканерів загарбників.", "range": (5, 15)},
    {"name": "☀️ Сонячний спалах", "desc": "Радіація випалила озоновий шар. Вихід на поверхню смертельний.", "range": (4, 10)},
    {"name": "❄️ Льодовиковий період", "desc": "Планета вкрилася кригою. Поверхня непридатна для життя на десятиліття.", "range": (50, 100)},
    {"name": "☣️ Пандемія", "desc": "Штучний вірус у повітрі. Будь-який контакт із зовнішнім світом — фатальний.", "range": (1, 3)}
]

BUNKER_TYPES = ["🥚 Інкубаторний", "📦 Звичайний", "🌿 Гідропонний", "🏨 Люкс-бункер", "🧬 Технологічний", "🧪 Експериментальний", "🛠 Військовий"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Стан ідеальний"]
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Журналіст", "Вірусолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Безсоння", "Алергія", "Діабет", "Міцний імунітет"]
AGES = [f"{i} років" for i in range(18, 80)]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "📦 Консерви", "🍶 Запас води", "Радіо"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія", "Мізофобія", "Соціофобія", "Безстрашний(а)"]
SECRET_GOALS = ["🤫 Мета: Вижити за будь-яку ціну.", "🤫 Мета: Переконати всіх взяти наймолодшого.", "🤫 Мета: Вижити разом із Лікарем."]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "📝 Помінятися професією", "🛡 Імунітет від вигнання", "👁 Дізнатися секрет"]

RANDOM_EVENTS = [
    {"text": "⚠️ Землетрус! Гравці з відкритим багажем міняються ним!", "type": "earthquake"},
    {"text": "⚠️ Викид радіації! Фільтри не витримали. Усі здорові гравці отримують випадкову хворобу!", "type": "radiation"}
]

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
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS), 
        "bag": random.choice(BAGGAGE), "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS), 
        "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS),
        "spec_used": False
    }
    g, c = games[game_id], player_cards[u_id]
    response = (f"🚨 **ВИ У ГРІ #{game_id}**\n\n🌍 **КАТАСТРОФА:** {g['catastrophe']}\n📖 **Опис:** {g['cat_desc']}\n⏳ **Термін:** {g['stay_time']} років\n"
                f"🛡 **БУНКЕР:** {g['bunker']}\n⚠️ **СТАН:** {g['prob']}\n------------------------------\n"
                f"💼 **ВАША КАРТКА:**\n👤 Стать: {c['gender']}\n⏳ Вік: {c['age']}\n🧠 Психіка: {c['psych']}\n🛠 Проф: {c['prof']}\n"
                f"❤️ Здор: {c['health']}\n🎒 Багаж: {c['bag']}\n🎸 Хобі: {c['hobby']}\n😱 Фобія: {c['phobia']}\n✨ Здібність: {c['spec']}")
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

@dp.message(F.text & ~F.text.startswith('/'))
async def game_chat(message: types.Message):
    u_id = message.from_user.id
    g_id = find_game_id(u_id)
    if g_id:
        sender_name = games[g_id]["players"][u_id]
        status = "" if u_id in games[g_id]["active_players"] else " (Глядач) 👻"
        for p_id in games[g_id]["players"]:
            if p_id != u_id:
                await bot.send_message(p_id, f"💬 **{sender_name}{status}**: {message.text}")
        await message.reply(f"📤 *Надіслано іншим гравцям{status}*", parse_mode="Markdown")

@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    u_id = callback.from_user.id
    g_id = callback.data.split("_")[2]
    
    # ПЕРЕВІРКА: чи гравець ще в грі
    if u_id not in games[g_id]["active_players"]:
        return await callback.answer("❌ Ви вигнані і не можете відкривати характеристики!", show_alert=True)

    data = callback.data.split("_")
    attr = data[1]
    card = player_cards[u_id]
    mapping = {"gen": ("Стать", card["gender"]), "age": ("Вік", card["age"]), "psy": ("Психіку", card["psych"]), "prof": ("Проф", card["prof"]), "health": ("Здоров'я", card["health"]), "bag": ("Багаж", card["bag"]), "hobby": ("Хобі", card["hobby"]), "phobia": ("Фобію", card["phobia"])}
    label, val = mapping[attr]
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"📢 {callback.from_user.first_name} відкриває {label}: `{val}`")
    await callback.answer()

@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id]["event_triggered"]: return await callback.answer("❌ Вже було!", show_alert=True)
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    for p_id in games[g_id]["players"]: await bot.send_message(p_id, f"🔥 **ПОДІЯ!**\n{event['text']}")
    if event["type"] == "radiation":
        summary = "☢️ **Наслідки опромінення:**\n"
        for u_id in games[g_id]["active_players"]:
            if player_cards[u_id]["health"] in ["Ідеальне", "Здоровий(а)"]:
                new_disease = random.choice(["Астма", "Травма ноги", "Сліпота", "Безсоння"])
                player_cards[u_id]["health"] = new_disease
                summary += f"☣️ {games[g_id]['players'][u_id]} -> **{new_disease}**\n"
        for p_id in games[g_id]["players"]: await bot.send_message(p_id, summary)
    await callback.answer()

@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote_menu(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if callback.from_user.id not in games[g_id]["active_players"]:
        return await callback.answer("❌ Глядачі не голосують!", show_alert=True)
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
    
    if target_id in games[g_id]["active_players"]:
        games[g_id]["active_players"].remove(target_id)
        c = player_cards[target_id]
        
        # ПОВНЕ РОЗКРИТТЯ КАРТКИ
        reveal_msg = (f"🚪 Гравця **{games[g_id]['players'][target_id]}** вигнано!\n"
                      f"💀 **Його справжня картка була:**\n"
                      f"👤 Стать: {c['gender']}\n"
                      f"⏳ Вік: {c['age']}\n"
                      f"🧠 Психіка: {c['psych']}\n"
                      f"🛠 Проф: {c['prof']}\n"
                      f"❤️ Здоров'я: {c['health']}\n"
                      f"🎒 Багаж: {c['bag']}\n"
                      f"🎸 Хобі: {c['hobby']}\n"
                      f"😱 Фобія: {c['phobia']}\n"
                      f"✨ Здібність: {c['spec']}")
        
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, reveal_msg)
        
        await bot.send_message(target_id, "👻 Ви вибули, але можете продовжувати стежити за чатом та грою.")
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
