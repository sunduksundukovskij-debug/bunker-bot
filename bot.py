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
active_bonuses = {} 

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ХАРАКТЕРИСТИК ---
PROFESSIONS = [
    "Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", 
    "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", 
    "Слюсар", "Журналіст", "Астроном", "Уфолог", "Вірусолог", "Радіолог", "Спелеолог"
]

HEALTH_STATUS = [
    "Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота на одне око", 
    "Безсоння", "Алергія", "Діабет", "Погана імунна система", "Безплодя", "1 нога", 
    "Заражений(а)", "Міцний імунітет", "Витривалий(а)", "Швидка регенерація", 
    "Чудовий зір", "Атлетична статура", "Відсутність хронічних хвороб"
]

AGES = ["18 років", "22 роки", "25 років", "30 років", "33 роки", "40 років", "45 років", "50 років", "55 років", "60 років", "90 років", "70 років", "85 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]

BAGGAGE = [
    "Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Набір (юний хімік)","Еліксир Молодості(-10р)", 
    "Гітара", "Інструменти", "Запальничка", "Компас", 
    "📦 Ящик консервів (їжа)", "🥖 Сухпайок на місяць (їжа)", "🍶 Запас чистої води (їжа)"
]

PHOBIAS = ["Клаустрофобія", "Ахлуофобія (темрява)", "Мізофобія (бруд)", "Герпетофобія (плазуни)", "Соціофобія", "Немає", "Безстрашний(а)" ]
BONUS_BAGGAGE = ["🛰 Супутниковий телефон", "🔋 Сонячна панель", "🧪 Універсальна сироватка", "🧥 Костюм хімзахисту", "🗝 Ключ від складу", "🗺 Карта ресурсів"]

SPECIAL_ABILITIES = [
    "🔄 Помінятися багажем з будь-ким.",
    "⏳ Помінятися віком або здоров'ям.",
    "📢 'Заткнути' одного гравця на 1 хвилину.",
    "🛡 Імунітет від вигнання в цьому раунді.",
    "📝 Змінити свою професію на нову випадкову.",
    "👁 Дізнатися секретну мету іншого гравця.",
    "🧨 Анулювати результати голосування (1 раз)."
]

# РОЗШИРЕНІ КАТАСТРОФИ
CATASTROPHES = [
    "🌋 Ядерна зима (10 років)", "🧟 Зомбі-апокаліпсис (5 років)", "🌊 Всесвітній потоп",
    "👽 Нашестя іншопланетян", "☀️ Гіперсонячний спалах", "❄️ Льодовиковий період",
    "🤖 Повстання ШІ", "🦠 Смертельний грибок", "🦖 Повернення динозаврів",
    "🌑 Місяць зійшов з орбіти", "💨 Кисневий голод", "🌋 Виверження супервулкана",
    "☣️ Глобальна пандемія невідомого вірусу", "🌌 Колапс магнітного поля Землі",
    "☄️ Падіння масивного астероїда", "🕯 Світ без електрики (всі пристрої згоріли)",
    "🌀 Нескінченні урагани та торнадо", "🏜 Глобальна засуха (зникнення прісної води)"
]

BUNKER_TYPES = [
    "📦 Звичайний бункер.", "🧬 Технологічний з ІНКУБАТОРАМИ.", "🧪 Експериментальний (ліки).",
    "🌿 Гідропонний (їжа).", "📚 Науковий (знання).", "🛠 Військовий (зброя).",
    "💀 ХАРДКОР: Закинутий бункер. Жодних запасів їжі, є хім. лабараторія.",
    "🏨 Люкс-бункер: Басейн, запаси делікатесів, кінотеатр.",
    "🏢 Підземне місто: Велике, але важко контролювати порядок.",
    "📡 Обсерваторія: Високо в горах, захищена від потопу, але мало місця.",
    "🏦 Банківське сховище: Неймовірно міцні двері, але немає джерел води.",
    "🚇 Сховище в метро: Багато тунелів, але великий ризик обвалів.",
    "🛸 Космічна станція: Повний захист від земних катастроф, але обмежений кисень."
]

BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "забагато мишей", "старе радіо", "грибок на стінах"]

SECRET_GOALS = [
    "🤫 Мета: Переконати всіх взяти найстаршого гравця.",
    "🤫 Мета: Вижити разом із 'Лікарем'.",
    "🤫 Мета: Вижити разом із 'Військовим'.",
    "🤫 Мета: Вигнати будь-кого 'Поліцейського'.",
    "🤫 Мета: Вижити будь-якою ціною.",
    "🤫 Мета: Взяти в бункер людину з найгіршим здоров'ям.",
    "🤫 Мета: Зробити так, щоб у бункері було 2 жінки.",
    "🤫 Мета: Зробити так, щоб у бункері було 2 чоловіка.",
    "🤫 Мета: Не допустити в бункер людину з багажем 'Зброя'."
]

# РОЗШИРЕНІ ІВЕНТИ
RANDOM_EVENTS = [
    "⚠️ ПОДІЯ: Землетрус! Всі міняються багажем по колу!",
    "⚠️ ПОДІЯ: Витік газу! Ті, хто хворі, мовчать 1 хв.",
    "⚠️ ПОДІЯ: Знайдено рюкзак! Хто перший напише 'БУНКЕР', отримує бонус!",
    "⚠️ ПОДІЯ: Аномальна зона! Кожен гравець має змінити свою Фобію на нову.",
    "⚠️ ПОДІЯ: Сонячна буря! Всі гравці старше 40 років втрачають право голосу на цей раунд.",
    "⚠️ ПОДІЯ: Мутація! Випадковий гравець змінює свою Професію.",
    "⚠️ ПОДІЯ: Психологічна атака! Кожен має відкрити свою Секретну мету (або збрехати про неї).",
    "⚠️ ПОДІЯ: Чутки про допомогу! Вигнання в цьому раунді скасовується.",
    "⚠️ ПОДІЯ: Обвал входу! Тепер у бункер зможе потрапити на одну людину менше."
]

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
        "players": []
    }
    await callback.message.answer(
        f"🎮 **Гру #{game_id} створено!**\n\n"
        f"🌍 **Катастрофа:** {games[game_id]['catastrophe']}\n"
        f"🛡 **Тип бункера:** {games[game_id]['bunker']}\n"
        f"❌ **Проблема:** {games[game_id]['prob']}\n\n"
        f"🔑 **Код:** `{game_id}`",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(Command("event"))
async def trigger_event(message: types.Message):
    event = random.choice(RANDOM_EVENTS)
    await message.answer(event)
    if "БУНКЕР" in event:
        active_bonuses[message.chat.id] = True

@dp.message(Command("vote"))
async def start_vote(message: types.Message):
    game_id = next(iter(games), None)
    if not game_id or not games[game_id]["players"]:
        return await message.answer("❌ Ще ніхто не приєднався!")
    await message.answer_poll(
        question="Кого виженемо?",
        options=games[game_id]["players"][:10],
        is_anonymous=True
    )

@dp.message(lambda message: message.text == "БУНКЕР")
async def catch_bonus(message: types.Message):
    if message.chat.id in active_bonuses:
        del active_bonuses[message.chat.id] 
        await message.reply(f"🎉 Бонус: **{random.choice(BONUS_BAGGAGE)}**")

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
    
    await state.clear()
    p_name = message.from_user.first_name
    if p_name not in games[game_id]["players"]:
        games[game_id]["players"].append(p_name)
    
    g = games[game_id]
    response = (
        f"🚨 **ВИ У ГРІ #{game_id}**\n\n"
        f"🌍 **Катастрофа:** {g['catastrophe']}\n"
        f"🛡 **Тип бункера:** {g['bunker']}\n"
        f"❌ **Проблема:** {g['prob']}\n\n"
        f"💼 **Ваша картка:**\n"
        f"• 👤 Стать: {random.choice(GENDERS)}\n"
        f"• 🛠 Професія: {random.choice(PROFESSIONS)}\n"
        f"• ❤️ Здоров'я: {random.choice(HEALTH_STATUS)}\n"
        f"• ⏳ Вік: {random.choice(AGES)}\n"
        f"• 🧠 Псих. стан: {random.choice(PSYCH)}\n"
        f"• 🎸 Хобі: {random.choice(HOBBIES)}\n"
        f"• 🎒 Багаж: {random.choice(BAGGAGE)}\n"
        f"• 😱 Фобія: {random.choice(PHOBIAS)}\n"
        f"✨ Здібність: {random.choice(SPECIAL_ABILITIES)}\n\n"
        f"🎯 **{random.choice(SECRET_GOALS)}**"
    )
    await message.answer(response, parse_mode="Markdown")

if __name__ == '__main__':
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
