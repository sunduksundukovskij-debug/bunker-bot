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

# База даних у пам'яті
games = {}
player_cards = {} # Зберігаємо картки гравців за їх ID

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ХАРАКТЕРИСТИК (ті самі) ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Астроном", "Уфолог", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота на одне око", "Безсоння", "Алергія", "Діабет", "Погана імунна система", "Безплодя", "1 нога", "Заражений(а)", "Міцний імунітет", "Витривалий(а)", "Швидка регенерація", "Чудовий зір", "Атлетична статура", "Відсутність хронічних хвороб"]
AGES = ["18 років", "22 роки", "25 років", "30 років", "33 роки", "35 років", "40 років", "45 років", "50 років", "55 років", "60 років", "90 років", "70 років", "85 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Набір (юний хімік)", "Еліксир Молодості", "Гітара", "Інструменти", "Запальничка", "Компас", "📦 Ящик консервів", "🥖 Сухпайок", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія", "Мізофобія", "Герпетофобія", "Соціофобія", "Немає", "Безстрашний(а)"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем", "⏳ Помінятися віком", "📢 'Заткнути' гравця", "🛡 Імунітет від вигнання", "📝 Змінити професію", "👁 Дізнатися секрет", "🧨 Анулювати голос"]
CATASTROPHES = ["🌋 Ядерна зима", "🧟 Зомбі-апокаліпсис", "🌊 Всесвітній потоп", "👽 Нашестя іншопланетян", "☀️ Сонячний спалах", "❄️ Льодовиковий період"]
BUNKER_TYPES = ["📦 Звичайний", "🧬 Технологічний", "🧪 Експериментальний", "🌿 Гідропонний", "🛠 Військовий", "🏨 Люкс-бункер"]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "✅ Жодних проблем!", "✅ Усе справно"]

# --- КНОПКИ ДЛЯ РОЗКРИТТЯ ---
def get_reveal_keyboard(game_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛠 Професія", callback_data=f"reveal_prof_{game_id}")
    builder.button(text="❤️ Здоров'я", callback_data=f"reveal_health_{game_id}")
    builder.button(text="🎒 Багаж", callback_data=f"reveal_bag_{game_id}")
    builder.button(text="🎸 Хобі", callback_data=f"reveal_hobby_{game_id}")
    builder.button(text="😱 Фобія", callback_data=f"reveal_phobia_{game_id}")
    builder.button(text="✨ Здібність", callback_data=f"reveal_spec_{game_id}")
    builder.adjust(2)
    return builder.as_markup()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    builder.adjust(1)
    await message.answer("🌋 **Бункер: Екстремальне Виживання** 🌋", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS),
        "players": {} # Словник {user_id: name}
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n\n🌍 {games[game_id]['catastrophe']}\n🔑 Код: `{game_id}`", parse_mode="Markdown")
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
    user_name = message.from_user.first_name
    
    # Реєструємо гравця в паті
    games[game_id]["players"][user_id] = user_name
    
    # Генеруємо картку, якщо її ще немає
    player_cards[user_id] = {
        "prof": random.choice(PROFESSIONS),
        "health": random.choice(HEALTH_STATUS),
        "bag": random.choice(BAGGAGE),
        "hobby": random.choice(HOBBIES),
        "phobia": random.choice(PHOBIAS),
        "spec": random.choice(SPECIAL_ABILITIES),
        "age": random.choice(AGES),
        "gender": random.choice(GENDERS)
    }
    
    card = player_cards[user_id]
    response = (
        f"🚨 **ВИ У ГРІ #{game_id}**\n\n"
        f"👤 Ви: {card['gender']}, {card['age']}\n"
        f"🛠 Професія: {card['prof']}\n"
        f"❤️ Здоров'я: {card['health']}\n"
        f"🎒 Багаж: {card['bag']}\n"
        f"🎸 Хобі: {card['hobby']}\n"
        f"😱 Фобія: {card['phobia']}\n"
        f"✨ Здібність: {card['spec']}\n\n"
        f"👇 **Оберіть, що розкрити всім гравцям:**"
    )
    
    await state.clear()
    await message.answer(response, reply_markup=get_reveal_keyboard(game_id), parse_mode="Markdown")

# --- ОБРОБНИК РОЗКРИТТЯ ХАРАКТЕРИСТИК ---
@dp.callback_query(F.data.startswith("reveal_"))
async def cb_reveal(callback: types.CallbackQuery):
    data = callback.data.split("_")
    attr_type = data[1] # prof, health, і т.д.
    game_id = data[2]
    
    if game_id not in games:
        return await callback.answer("Гра вже закінчилась", show_alert=True)
    
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name
    card = player_cards.get(user_id)
    
    # Співставлення ключів
    mapping = {
        "prof": ("🛠 Професію", card["prof"]),
        "health": ("❤️ Здоров'я", card["health"]),
        "bag": ("🎒 Багаж", card["bag"]),
        "hobby": ("🎸 Хобі", card["hobby"]),
        "phobia": ("😱 Фобію", card["phobia"]),
        "spec": ("✨ Здібність", card["spec"])
    }
    
    label, value = mapping[attr_type]
    reveal_text = f"📢 **Гравець {user_name}** розкриває свою {label}:\n➡️ `{value}`"
    
    # Надсилаємо всім гравцям у паті
    for p_id in games[game_id]["players"]:
        try:
            await bot.send_message(p_id, reveal_text, parse_mode="Markdown")
        except:
            pass # Якщо хтось заблокував бота
            
    await callback.answer(f"Ви розкрили {label}!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
