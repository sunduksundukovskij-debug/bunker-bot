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

# --- СПИСКИ (скорочено для коду) ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота", "Діабет"]
AGES = ["18 років", "25 років", "33 роки", "40 років", "55 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Лідер"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Бокс", "Малювання"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "📦 Консерви", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Мізофобія", "Соціофобія", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "👁 Дізнатися секрет"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🛠 Військовий"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вижити будьякою ціною."]
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
        "active_players": [],
        "revealed_bags": [], # Список тих, хто ВІДКРИВ багаж
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
    await state.clear()
    await message.answer(f"🚨 Ви у грі #{game_id}!", reply_markup=get_reveal_keyboard(game_id))

# --- ЗДІБНОСТІ З ПЕРЕВІРКОЮ ---

@dp.callback_query(F.data.startswith("use_spec_"))
async def cb_use_spec(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    user_id = callback.from_user.id
    card = player_cards[user_id]

    if card["spec_used"]:
        return await callback.answer("❌ Здібність вже використана!", show_alert=True)

    builder = InlineKeyboardBuilder()
    targets_found = False

    if "багажем" in card["spec"]:
        # Шукаємо гравців, які ВЖЕ ВІДКРИЛИ багаж
        for p_id in games[game_id]["active_players"]:
            if p_id != user_id and p_id in games[game_id]["revealed_bags"]:
                name = games[game_id]["players"][p_id]
                builder.button(text=f"Вкрасти багаж у {name}", callback_data=f"do_swap_{p_id}_{game_id}")
                targets_found = True
        
        if not targets_found:
            return await callback.answer("❌ Ніхто ще не відкрив свій багаж! Ви не знаєте, що красти.", show_alert=True)

    elif "секрет" in card["spec"]:
        # Секрет можна дізнатися у будь-кого живого
        for p_id in games[game_id]["active_players"]:
            if p_id != user_id:
                name = games[game_id]["players"][p_id]
                builder.button(text=f"Секрет {name}", callback_data=f"do_secret_{p_id}_{game_id}")
                targets_found = True

    builder.adjust(1)
    await callback.message.answer("🎯 Оберіть ціль:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    data = callback.data.split("_")
    attr_type, game_id = data[1], data[2]
    user_id = callback.from_user.id
    card = player_cards.get(user_id)
    
    # Якщо гравець відкриває БАГАЖ — записуємо це в пам'ять гри
    if attr_type == "bag":
        if user_id not in games[game_id]["revealed_bags"]:
            games[game_id]["revealed_bags"].append(user_id)

    mapping = {"gen": ("Стать", card["gender"]), "age": ("Вік", card["age"]), "psy": ("Психіку", card["psych"]), "prof": ("Проф", card["prof"]), "health": ("Здоров'я", card["health"]), "bag": ("Багаж", card["bag"]), "hobby": ("Хобі", card["hobby"]), "phobia": ("Фобію", card["phobia"])}
    label, value = mapping[attr_type]
    
    for p_id in games[game_id]["players"]:
        await bot.send_message(p_id, f"📢 {callback.from_user.first_name} розкриває {label}: `{value}`")
    await callback.answer()

@dp.callback_query(F.data.startswith("do_swap_"))
async def cb_do_swap(callback: types.CallbackQuery):
    _, _, target_id, game_id = callback.data.split("_")
    target_id, user_id = int(target_id), callback.from_user.id
    
    # Сама дія обміну
    player_cards[user_id]["bag"], player_cards[target_id]["bag"] = player_cards[target_id]["bag"], player_cards[user_id]["bag"]
    player_cards[user_id]["spec_used"] = True

    msg = f"🔄 **КРАДІЖКА!** {callback.from_user.first_name} помінявся багажем з {games[game_id]['players'][target_id]}!"
    for p_id in games[game_id]["players"]: await bot.send_message(p_id, msg)
    await callback.answer()

# --- ФІНАЛ ТА ІВЕНТИ ТАКІ Ж ЯК У ПОПЕРЕДНЬОМУ ПОВІДОМЛЕННІ ---
@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    builder = InlineKeyboardBuilder()
    for p_id in games[game_id]["active_players"]:
        name = games[game_id]["players"][p_id]
        builder.button(text=f"Вигнати {name}", callback_data=f"kick_{p_id}_{game_id}")
    builder.adjust(1)
    for p_id in games[game_id]["active_players"]:
        await bot.send_message(p_id, "🗳 Голосування:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    k_id, g_id = int(callback.data.split("_")[1]), callback.data.split("_")[2]
    if k_id in games[g_id]["active_players"]: games[g_id]["active_players"].remove(k_id)
    msg = f"🚪 {games[g_id]['players'][k_id]} вигнано! (Проф: {player_cards[k_id]['prof']})"
    for p_id in games[g_id]["players"]: await bot.send_message(p_id, msg)
    if len(games[g_id]["active_players"]) <= 2:
        names = [games[g_id]["players"][p] for p in games[g_id]["active_players"]]
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, f"🏆 **ФІНАЛ!** Залишилися: {', '.join(names)}. Шанс на виживання: {random.randint(40,90)}%")
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
