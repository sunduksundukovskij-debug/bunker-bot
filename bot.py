import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = '8422077163:AAHsR-dTCHTg8NVrMffi6juW_L9H-Y64bIk'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- ВЕЛИКІ СПИСКИ ХАРАКТЕРИСТИК ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Астроном"]
HEALTH = ["Ідеальне, 25 років", "Астма, 45 років", "Травма ноги, 30 років", "Вагітність, 22 роки", "Здоровий, 55 років", "Сліпота на око, 40 років", "Безсоння, 28 років", "Алергія, 33 роки", "Діабет, 50 років"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Гітара", "Інструменти", "Запальничка", "Компас"]

SPECIAL_ABILITIES = [
    "🔄 Помінятися багажем з будь-ким.",
    "⏳ Помінятися віком/здоров'ям.",
    "📢 'Заткнути' одного гравця на 1 хвилину.",
    "🛡 Імунітет від вигнання в цьому раунді.",
    "📝 Змінити свою професію на нову випадкову.",
    "👁 Дізнатися секретну мету іншого гравця.",
    "🧨 Анулювати результати голосування (1 раз)."
]

# --- РОЗШИРЕНІ КАТАСТРОФИ ---
CATASTROPHES = [
    "🌋 Ядерна зима (10 років). Радіація всюди.",
    "🧟 Зомбі-апокаліпсис (5 років). Вірус укусу.",
    "🌊 Всесвітній потоп. Суші майже немає.",
    "👽 Нашестя іншопланетян. Людство в підпіллі.",
    "☀️ Гіперсонячний спалах. Атмосфера спалена.",
    "❄️ Льодовиковий період. Температура -60°C.",
    "🤖 Повстання ШІ. Роботи полюють на людей.",
    "🦠 Смертельний грибок. Спори в повітрі.",
    "🦖 Повернення динозаврів (генетичний збій).",
    "🌑 Місяць зійшов з орбіти. Припливи нищать міста.",
    "💨 Кисневий голод. Рослини масово вимерли.",
    "🌋 Виверження супервулкана. Попіл закрив сонце."
]

# --- ТИПИ БУНКЕРІВ ---
BUNKER_TYPES = [
    "📦 Звичайний бункер (стандартні запаси).",
    "🧬 Технологічний з ІНКУБАТОРАМИ (стать не важлива).",
    "🧪 Експериментальний (багато ліків, мало їжі).",
    "🌿 Гідропонний (можна вирощувати їжу всередині).",
    "📚 Науковий (бібліотека знань, мало інструментів).",
    "🛠 Військовий (багато зброї, але тісно)."
]

BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "забагато мишей", "старе радіо", "грибок на стінах"]

# --- РОЗШИРЕНІ СЕКРЕТНІ ЗАВДАННЯ ---
SECRET_GOALS = [
    "🤫 Мета: Переконати всіх взяти найстаршого гравця.",
    "🤫 Мета: Вижити разом із 'Лікарем'.",
    "🤫 Мета: Вижити разом із 'Військовоим' чи 'Поліцейським''.",
    "🤫 Мета: Вигнати будь-якого 'Військового' чи 'Поліцейського'.",
    "🤫 Мета: Вижити будь-якою ціною (навіть брехнею).",
    "🤫 Мета: Взяти в бункер людину з найгіршим здоров'ям.",
    "🤫 Мета: Зробити так, щоб у бункері було 2 жінки.",
    "🤫 Мета: Зробити так, щоб у бункері було 2 чоловіка.",
    "🤫 Мета: Не допустити в бункер людину з багажем 'Зброя'.",
    "🤫 Мета: Помінятися здібностями або багажем до кінця гри.",
    "🤫 Мета: Зробити так, щоб у бункері не було жодного Програміста чи Хіміка."
]

RANDOM_EVENTS = [
    "⚠️ ПОДІЯ: Землетрус! Всі міняються багажем по колу!",
    "⚠️ ПОДІЯ: Радіоперехват! Катастрофа триватиме вдвічі довше.",
    "⚠️ ПОДІЯ: Витік газу! Ті, хто хворі, мовчать 1 хв.",
    "⚠️ ПОДІЯ: Сканер виявив мутацію! Кожен має відкрити своє справжнє здоров'я."
]

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Створити гру", callback_data="make_room")
    builder.button(text="🔑 Приєднатися", callback_data="join_room")
    builder.adjust(1)
    await message.answer("🌋 **Бункер: Екстремальне Виживання** 🌋\n\nНові катастрофи та секретні цілі додано!", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "make_room")
async def cb_create(callback: types.CallbackQuery):
    game_id = str(random.randint(1000, 9999))
    games[game_id] = {
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKER_TYPES),
        "prob": random.choice(BUNKER_PROBLEMS)
    }
    await callback.message.answer(
        f"🎮 **Гру створено!**\n\n🌍 **Катастрофа:** {games[game_id]['catastrophe']}\n"
        f"🛡 **Тип бункера:** {games[game_id]['bunker']}\n"
        f"❌ **Проблема:** {games[game_id]['prob']}\n\n"
        f"🔑 **Код:** `{game_id}`\n\n*Для випадкової події:* `/event`",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "join_room")
async def cb_join(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.waiting_for_code)
    await callback.message.answer("⌨️ Введіть код гри:")
    await callback.answer()

@dp.message(Command("event"))
async def trigger_event(message: types.Message):
    await message.answer(random.choice(RANDOM_EVENTS))

@dp.message(GameStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    game_id = message.text.strip()
    if game_id not in games:
        await message.answer("❌ Код невірний!")
        return
    await state.clear()
    
    response = (
        f"🚨 **ВИ У ГРІ #{game_id}**\n\n"
        f"💼 **Ваша картка:**\n"
        f"• 🛠 Професія: {random.choice(PROFESSIONS)}\n"
        f"• ❤️ Здоров'я/Вік: {random.choice(HEALTH)}\n"
        f"• 🧠 Псих. стан: {random.choice(PSYCH)}\n"
        f"• 🎸 Хобі: {random.choice(HOBBIES)}\n"
        f"• 🎒 Багаж: {random.choice(BAGGAGE)}\n"
        f"✨ Здібність: {random.choice(SPECIAL_ABILITIES)}\n\n"
        f"🎯 **{random.choice(SECRET_GOALS)}**\n\n"
        f"📣 Час переконувати інших!"
    )
    await message.answer(response, parse_mode="Markdown")

if __name__ == '__main__':
    import asyncio
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main())
