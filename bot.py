import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Твій токен
API_TOKEN = '8422077163:AAF0oF7nALNGo-N_Lk6WUKXwoRS8T0hb0C4'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сховище для ігор
games = {}

# Стан для очікування коду
class GameStates(StatesGroup):
    waiting_for_code = State()

PROFESSIONS = ["Лікар-хірург", "Агроном", "Військовий інженер", "Фізик-ядерник", "Кухар", "Програміст", "Електрик", "Будівельник", "Вчитель", "Поліцейський", "Психолог", "Мисливець"]
HEALTH_STATUS = ["Ідеальне здоров'я, 25 років", "Хронічний астматик, 40 років", "Легка застуда, 19 років", "Здоровий, 35 років", "Абсолютно здоровий, 50 років", "Травма ноги, 30 років", "Вагітність (2 місяць)", "Сліпота на одне око"]
HOBBIES = ["Стрільба з лука", "Гра на гітарі", "Садівництво", "Виживання в лісі", "Бокс", "Малювання", "Риболовля", "Паркур"]
BAGGAGE = ["Набір ножів", "Велика аптечка", "Насіння пшениці", "Два блоки цигарок", "Книга з виживання", "Рація", "Ліхтарик", "Каністра води 5л", "Протигаз", "Мисливська рушниця"]
CATASTROPHES = [
    "🌋 Ядерна зима. Поверхня непридатна для життя на 10 років.",
    "🧟 Зомбі-апокаліпсис. Потрібно перечекати 5 років.",
    "🌊 Всесвітній потоп. Суші майже не залишилося.",
    "👽 Нашестя іншопланетян. Людство в підпіллі.",
    "☀️ Гіперсонячний спалах. Життя можливе лише глибоко під землею."
]

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear() 
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    builder.adjust(1)

    await message.answer(
        "🌋 **Вітаємо у грі «Бункер»!** 🌋\n\n"
        "Створюйте лобі для друзів або приєднуйтесь до гри за кодом.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    catastrophe = random.choice(CATASTROPHES)
    games[game_id] = {"catastrophe": catastrophe}
    
    await callback.message.answer(
        f"🎮 **Гру створено!**\n\n"
        f"🌍 **Катастрофа:** {catastrophe}\n"
        f"🔑 **Код для друзів:** `{game_id}`\n\n"
        f"Надішліть цей код друзям, щоб вони могли приєднатися!",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ **Введіть 4 цифри коду**, щоб отримати карту персонажа:")
    await callback.answer()

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    # Перевіряємо, чи ввів користувач цифри
    game_id = message.text.strip()
    
    if game_id not in games:
        await message.answer("❌ **Помилка!** Гра з таким кодом не знайдена.\nСпробуйте ще раз або натисніть /start")
        return

    await state.clear()
    catastrophe = games[game_id]["catastrophe"]
    
    response = (
        f"🚨 **ВИ У ГРІ #{game_id}** 🚨\n\n"
        f"🌍 **Спільна катастрофа:**\n{catastrophe}\n"
        f"-----------------------------------\n"
        f"💼 **Ваша картка:**\n"
        f"• 🛠 **Професія:** {random.choice(PROFESSIONS)}\n"
        f"• ❤️ **Здоров'я:** {random.choice(HEALTH_STATUS)}\n"
        f"• 🎸 **Хобі:** {random.choice(HOBBIES)}\n"
        f"
