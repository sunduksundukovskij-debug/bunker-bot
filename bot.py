import random
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Твій актуальний токен
API_TOKEN = '8422077163:AAFzmEMuPnPKI2pau5G2oK6X1Vm4o6XC4ck'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}
player_cards = {} 

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ХАРАКТЕРИСТИК ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Астроном", "Уфолог", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота на одне око", "Безсоння", "Алергія", "Діабет", "Погана імунна система", "Безплодя", "1 нога", "Заражений(а)", "Міцний імунітет", "Витривалий(а)", "Швидка регенерація", "Чудовий зір", "Атлетична статура", "Відсутність хронічних хвороб"]
AGES = ["18 років", "22 роки", "25 років", "30 років", "33 роки", "35 років", "40 років", "45 років", "50 років", "55 років", "60 років", "90 років", "70 років", "85 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Набір хіміка", "Еліксир Молодості", "Гітара", "Інструменти", "Запальничка", "Компас", "📦 Консерви", "🥖 Сухпайок", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія", "Мізофобія", "Герпетофобія", "Соціофобія", "Немає", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "⏳ Помінятися віком", "📢 'Заткнути' гравця", "🛡 Імунітет від вигнання", "📝 Змінити професію", "👁 Дізнатися секрет", "🧨 Анулювати голос"]

CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп", "👽 Нашестя іншопланетян", "☀️ Сонячний спалах", "❄️ Льодовиковий період", "☣️ Глобальна пандемія", "🏜 Глобальна засуха"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🧪 Експериментальний", "🌿 Гідропонний", "🛠 Військовий", "🏨 Люкс-бункер", "🛸 Космічна станція"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Жодних проблем!", "✅ Стан ідеальний"]
SECRET_GOALS = ["🤫 Мета: Переконати всіх взяти найстаршого.", "🤫 Мета: Вижити разом із 'Лікарем'.", "🤫 Мета: Вигнати 'Поліцейського'.", "🤫 Мета: Вижити будь-якою ціною."]

RANDOM_EVENTS = [
    "⚠️ ПОДІЯ: Землетрус! Всі міняються багажем по колу!",
    "⚠️ ПОДІЯ: Витік газу! Ті, хто хворі, мовчать 1 хв.",
    "⚠️ ПОДІЯ: Сонячна буря! Всі гравці старше 40 років втрачають право голосу на раунд.",
    "⚠️ ПОДІЯ: Мутація! Випадковий гравець змінює свою Професію.",
    "⚠️ ПОДІЯ: Чутки про допомогу! Вигнання в цьому раунді скасовується.",
    "⚠️ ПОДІЯ: Обвал входу! Тепер у бункер зможе потрапити на одну людину менше."
]

def get_reveal_keyboard(game_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛠 Проф", callback_data=f"rev_prof_{game_id}")
    builder.button(text="❤️ Здор", callback_data=f"rev_health_{game_id}")
    builder.button(text="🎒 Багаж", callback_data=f"rev_bag_{game_id}")
    builder.button(text="🎸 Хобі", callback_data=f"rev_hobby_{game_id}")
    builder.button(text="😱 Фобія", callback_data=f"rev_phobia_{game_id}")
    builder.button(text="✨ Здібн", callback_data=f"rev_spec_{game_id}")
    builder.button(text="🗳 Голосування", callback_data=f"game_vote_{game_id}")
    builder.button(text="⚠️ Подія", callback_data=f"game_event_{game_id}")
    builder.adjust(3)
    return builder.as_markup()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    builder.adjust(1)
    await message.answer("🌋 **Бункер: Екстремальне Виживання**", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {},
        "event_triggered": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n\n🌍 {games[game_id]['catastrophe']}\n🛡 Бункер: {games[game_id]['bunker']}\n⚙️ Стан: {games[game_id]['prob']}\n🔑 Код: `{game_id}`", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ Введіть код гри:")
    await callback.answer()

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games:
        return await message.answer("❌ Код невірний!")
    
    user_id = message.from_user.id
    games[game_id]["players"][user_id] = message.from_user.first_name
    
    player_cards[user_id] = {
        "prof": random.choice(PROFESSIONS), "health": random.choice(HEALTH_STATUS),
        "bag": random.choice(BAGGAGE), "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS), "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES), "gender": random.choice(GENDERS),
        "psych": random.choice(PSYCH), "goal": random.choice(SECRET_GOALS)
    }
    
    g, c = games[game_id], player_cards[user_id]
    response = (
        f"🚨 **ГРА #{game_id}**\n\n🌍 **КАТАСТРОФА:** {g['catastrophe']}\n"
        f"🛡 **БУНКЕР:** {g['bunker']}\n⚠️ **СТАН:** {g['prob']}\n"
        f"------------------------------\n💼 **ВАША КАРТКА:**\n"
        f"👤 {c['gender']}, {c['age']} | 🧠 {c['psych']}\n"
        f"🛠 Професія: {c['prof']}\n❤️ Здоров'я: {c['health']}\n"
        f"🎒 Багаж: {c['bag']}\n🎸 Хобі: {c['hobby']}\n"
        f"😱 Фобія: {c['phobia']}\n✨ Здібність: {c['spec']}\n\n{c['goal']}\n"
        f"------------------------------"
    )
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("rev_"))
async def cb_reveal(callback: types.CallbackQuery):
    data = callback.data.split("_")
    attr_type, game_id = data[1], data[2]
    card = player_cards.get(callback.from_user.id)
    mapping = {"prof": ("🛠 Проф", card["prof"]), "health": ("❤️ Здоров'я", card["health"]), "bag": ("🎒 Багаж", card["bag"]), "hobby": ("🎸 Хобі", card["hobby"]), "phobia": ("😱 Фобію", card["phobia"]), "spec": ("✨ Здібн", card["spec"])}
    label, value = mapping[attr_type]
    msg = f"📢 **{callback.from_user.first_name}** розкриває {label}:\n➡️ `{value}`"
    for p_id in games[game_id]["players"]:
        try: await bot.send_message(p_id, msg, parse_mode="Markdown")
        except: pass
    await callback.answer()

@dp.callback_query(F.data.startswith("game_vote_"))
async def cb_vote(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    # Створюємо кнопки для вибору, кого вигнати
    builder = InlineKeyboardBuilder()
    for p_id, p_name in games[game_id]["players"].items():
        builder.button(text=f"Вигнати {p_name}", callback_data=f"kick_{p_id}_{game_id}")
    builder.adjust(1)
    
    for p_id in games[game_id]["players"]:
        try: await bot.send_message(p_id, "🗳 **ГОЛОСУВАННЯ!** Оберіть, хто на вашу думку має піти:", reply_markup=builder.as_markup())
        except: pass
    await callback.answer()

@dp.callback_query(F.data.startswith("kick_"))
async def cb_kick(callback: types.CallbackQuery):
    data = callback.data.split("_")
    kicked_id = int(data[1])
    game_id = data[2]
    
    k_name = games[game_id]["players"].get(kicked_id, "Невідомий")
    c = player_cards.get(kicked_id)
    
    # Формуємо повну характеристику для розкриття
    reveal_msg = (
        f"🚪 **ГРАВЦЯ {k_name} ВИГНАНО!**\n\n"
        f"📜 **Його справжня анкета:**\n"
        f"• Стать/Вік: {c['gender']}, {c['age']}\n"
        f"• Професія: {c['prof']}\n"
        f"• Здоров'я: {c['health']}\n"
        f"• Багаж: {c['bag']}\n"
        f"• Фобія: {c['phobia']}\n"
        f"• Психіка: {c['psych']}\n"
        f"• Мета: {c['goal']}"
    )
    
    for p_id in games[game_id]["players"]:
        try: await bot.send_message(p_id, reveal_msg)
        except: pass
    await callback.answer()

@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    game_id = callback.data.split("_")[2]
    if games[game_id]["event_triggered"]:
        return await callback.answer("❌ Івент вже використано!", show_alert=True)
    
    games[game_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    for p_id in games[game_id]["players"]:
        try: await bot.send_message(p_id, f"🔥 **РАНДОМНА ПОДІЯ!**\n\n{event}")
        except: pass
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
