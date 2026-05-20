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

# --- СПИСКИ ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Безсоння", "Алергія", "Діабет", "Міцний імунітет", "Витривалий(а)"]
AGES = ["18 років", "25 років", "33 роки", "40 років", "55 років", "70 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Лідер", "Цинік"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Бокс", "Малювання", "Риболовля"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "📦 Консерви", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Мізофобія", "Соціофобія", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "👁 Дізнатися секрет"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп", "👽 Нашестя іншопланетян"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🧪 Експериментальний", "🛠 Військовий"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вижити будь-якою ціною."]

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
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {},
        "active_players": [], # Список ID тих, хто ще в грі
        "event_triggered": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n🔑 Код: `{game_id}`", parse_mode="Markdown")
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
    
    user_id = message.from_user.id
    games[game_id]["players"][user_id] = message.from_user.first_name
    if user_id not in games[game_id]["active_players"]:
        games[game_id]["active_players"].append(user_id)
    
    player_cards[user_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "bag": random.choice(BAGGAGE), "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS),
        "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS),
        "spec_used": False
    }
    
    g, c = games[game_id], player_cards[user_id]
    response = (f"🚨 **ГРА #{game_id}**\n\n🌍 **КАТАСТРОФА:** {g['catastrophe']}\n🛡 **БУНКЕР:** {g['bunker']}\n⚠️ **СТАН:** {g['prob']}\n"
                f"------------------------------\n💼 **ВАША КАРТКА:**\n👤 {c['gender']}, {c['age']} | 🧠 {c['psych']}\n"
                f"🛠 Професія: {c['prof']}\n❤️ Здоров'я: {c['health']}\n🎒 Багаж: {c['bag']}\n✨ Здібність: {c['spec']}\n\n{c['goal']}")
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# --- ЛОГІКА ВИГНАННЯ ТА ФІНАЛУ ---

@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    builder = InlineKeyboardBuilder()
    for p_id in games[game_id]["active_players"]:
        name = games[game_id]["players"][p_id]
        builder.button(text=f"Вигнати {name}", callback_data=f"kick_{p_id}_{game_id}")
    builder.adjust(1)
    for p_id in games[game_id]["active_players"]:
        try: await bot.send_message(p_id, "🗳 **ГОЛОСУВАННЯ!** Оберіть кого вигнати:", reply_markup=builder.as_markup())
        except: pass
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    data = callback.data.split("_")
    kicked_id, game_id = int(data[1]), data[2]
    
    if kicked_id in games[game_id]["active_players"]:
        games[game_id]["active_players"].remove(kicked_id)
    
    k_name = games[game_id]["players"][kicked_id]
    c = player_cards[kicked_id]
    
    msg = f"🚪 **ГРАВЦЯ {k_name} ВИГНАНО!**\n📜 Анкета: {c['prof']}, {c['health']}, {c['bag']}\n{c['goal']}"
    for p_id in games[game_id]["players"]:
        try: await bot.send_message(p_id, msg)
        except: pass
    
    # ПЕРЕВІРКА НА ФІНАЛ (залишилось 2 людини)
    if len(games[game_id]["active_players"]) <= 2:
        await finish_game(game_id)
    
    await callback.answer()

async def finish_game(game_id):
    g = games[game_id]
    survivors = g["active_players"]
    
    # Розрахунок шансу (рандом + логіка)
    chance = random.randint(30, 95)
    if g["prob"] == "✅ Стан ідеальний": chance += 10
    
    names = [g["players"][p] for p in survivors]
    final_text = (
        f"🏁 **ГРА ЗАВЕРШЕНА!**\n\n"
        f"🏆 У бункері залишилися: **{', '.join(names)}**\n\n"
        f"📊 **АНАЛІЗ ВИЖИВАННЯ:**\n"
        f"З професіями {player_cards[survivors[0]]['prof']} та {player_cards[survivors[1]]['prof']} "
        f"шанс на відродження цивілізації в умовах '{g['catastrophe']}' становить **{min(chance, 100)}%**.\n\n"
        f"Бункер типу '{g['bunker']}' успішно герметизовано. Успіхів!"
    )
    
    for p_id in g["players"]:
        try: await bot.send_message(p_id, final_text, parse_mode="Markdown")
        except: pass

# --- ЗДІБНОСТІ ТА ІВЕНТИ (залишаються як були) ---
@dp.callback_query(F.data.startswith("use_spec_"))
async def cb_use_spec(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    user_id = callback.from_user.id
    card = player_cards[user_id]
    if card["spec_used"]: return await callback.answer("❌ Вже використано!", show_alert=True)
    builder = InlineKeyboardBuilder()
    for p_id in games[game_id]["active_players"]:
        if p_id != user_id:
            action = "swap" if "багажем" in card["spec"] else "secret"
            builder.button(text=games[game_id]["players"][p_id], callback_data=f"do_{action}_{p_id}_{game_id}")
    builder.adjust(1)
    await callback.message.answer("🎯 Оберіть ціль:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("do_swap_"))
async def cb_do_swap(callback: types.CallbackQuery):
    _, _, target_id, game_id = callback.data.split("_")
    target_id, user_id = int(target_id), callback.from_user.id
    player_cards[user_id]["bag"], player_cards[target_id]["bag"] = player_cards[target_id]["bag"], player_cards[user_id]["bag"]
    player_cards[user_id]["spec_used"] = True
    msg = f"🔄 {callback.from_user.first_name} та {games[game_id]['players'][target_id]} обмінялися багажем!"
    for p_id in games[game_id]["players"]: await bot.send_message(p_id, msg)
    await callback.answer()

@dp.callback_query(F.data.startswith("do_secret_"))
async def cb_do_secret(callback: types.CallbackQuery):
    _, _, target_id, game_id = callback.data.split("_")
    target_id, user_id = int(target_id), callback.from_user.id
    player_cards[user_id]["spec_used"] = True
    msg = f"👁 {callback.from_user.first_name} розкрив секрет {games[game_id]['players'][target_id]}: {player_cards[target_id]['goal']}"
    for p_id in games[game_id]["players"]: await bot.send_message(p_id, msg)
    await callback.answer()

@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    data = callback.data.split("_")
    attr_type, game_id = data[1], data[2]
    card = player_cards.get(callback.from_user.id)
    mapping = {"gen": ("Стать", card["gender"]), "age": ("Вік", card["age"]), "psy": ("Психіку", card["psych"]), "prof": ("Проф", card["prof"]), "health": ("Здоров'я", card["health"]), "bag": ("Багаж", card["bag"]), "hobby": ("Хобі", card["hobby"]), "phobia": ("Фобію", card["phobia"])}
    label, value = mapping[attr_type]
    for p_id in games[game_id]["players"]:
        await bot.send_message(p_id, f"📢 {callback.from_user.first_name} розкрив {label}: {value}")
    await callback.answer()

@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    if games[game_id]["event_triggered"]: return await callback.answer("❌ Використано!", show_alert=True)
    games[game_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    for p_id in games[game_id]["players"]: await bot.send_message(p_id, f"🔥 ПОДІЯ: {event}")
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
