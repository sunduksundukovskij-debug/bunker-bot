import random
import logging
import asyncio
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
active_bonuses = {} 

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- СПИСКИ ХАРАКТЕРИСТИК ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Астроном"]
HEALTH = ["Ідеальне, 25 років", "Астма, 45 років", "Травма ноги, 30 років", "Вагітність, 22 роки", "Здоровий, 55 років", "Сліпота на око, 40 років", "Безсоння, 28 років", "Алергія, 33 роки", "Діабет, 50 років"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Гітара", "Інструменти", "Запальничка", "Компас"]

# НОВА ХАРАКТЕРИСТИКА: ФОБІЇ
PHOBIAS = [
    "Клаустрофобія (боязнь замкненого простору)",
    "Ахлуофобія (боязнь темряви)",
    "Мізофобія (боязнь бруду та мікробів)",
    "Герпетофобія (боязнь плазунів)",
    "Агорафобія (боязнь відкритого простору)",
    "Ніктофобія (боязнь нічної пори)",
    "Танатофобія (страх смерті)",
    "Соціофобія (страх спілкування)"
]

BONUS_BAGGAGE = [
    "🛰 Супутниковий телефон", "🔋 Сонячна панель", "🧪 Універсальна сироватка", 
    "🧥 Костюм хімзахисту", "🗝 Ключ від складу їжі", "🗺 Карта прихованих ресурсів",
    "🔦 Потужний прожектор", "⛺️ Надувний намет"
]

SPECIAL_ABILITIES = [
    "🔄 Помінятися багажем з будь-ким.",
    "⏳ Помінятися віком/здоров'ям.",
    "📢 'Заткнути' одного гравця на 1 хвилину.",
    "🛡 Імунітет від вигнання в цьому раунді.",
    "📝 Змінити свою професію на нову випадкову.",
    "👁 Дізнатися секретну мету іншого гравця.",
    "🧨 Анулювати результати голосування (1 раз)."
]

CATASTROPHES = [
    "🌋 Ядерна зима (10 років)", "🧟 Зомбі-апокаліпсис (5 років)", "🌊 Всесвітній потоп",
    "👽 Нашестя іншопланетян", "☀️ Гіперсонячний спалах", "❄️ Льодовиковий період",
    "🤖 Повстання ШІ", "🦠 Смертельний грибок", "🦖 Повернення динозаврів",
    "🌑 Місяць зійшов з орбіти", "💨 Кисневий голод", "🌋 Виверження супервулкана"
]

BUNKER_TYPES = [
    "📦 Звичайний бункер.", "🧬 Технологічний з ІНКУБАТОРАМИ.", "🧪 Експериментальний (ліки).",
    "🌿 Гідропонний (їжа).", "📚 Науковий (знання).", "🛠 Військовий (зброя)."
]

BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "забагато мишей", "старе радіо", "грибок на стінах"]

SECRET_GOALS = [
    "🤫 Мета: Переконати всіх взяти найстаршого гравця.",
    "🤫 Мета: Вижити разом із 'Лікарем'.",
    "🤫 Мета: Вижити разом із 'Військовим' чи 'Поліцейським'.",
    "🤫 Мета: Вигнати будь-якого 'Військового' чи 'Поліцейського'.",
    "🤫 Мета: Вижити будь-якою ціною (навіть брехнею).",
    "🤫 Мета: Взяти в бункер людину з найгіршим здоров'ям.",
    "🤫 Мета: Зробити так, щоб у бункері було 2 жінки.",
    "🤫 Мета: Зробити так, щоб у бункері було 2 чоловіка.",
    "🤫 Мета: Не допустити в бункер людину з багажем 'Зброя'.",
    "🤫 Мета: Помінятися здібностями або багажем до кінця гри."
]

RANDOM_EVENTS = [
    "⚠️ ПОДІЯ: Землетрус! Всі міняються багажем по колу!",
    "⚠️ ПОДІЯ: Радіоперехват! Катастрофа триватиме вдвічі довше.",
    "⚠️ ПОДІЯ: Витік газу! Ті, хто хворі, мовчать 1 хв.",
    "⚠️ ПОДІЯ: Знайдено рюкзак! Хто перший напише 'БУНКЕР' великими літерами, отримує рідкісний бонус!",
    "⚠️ ПОДІЯ: Сканер виявив мутацію! Кожен має відкрити своє справжнє здоров'я."
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
        "players": [] # Сюди будемо додавати імена для голосування
    }
    await callback.message.answer(
        f"🎮 **Гру #{game_id} створено!**\n\n🌍 **Катастрофа:** {games[game_id]['catastrophe']}\n"
        f"🛡 **Тип бункера:** {games[game_id]['bunker']}\n"
        f"❌ **Проблема:** {games[game_id]['prob']}\n\n"
        f"🔑 **Код:** `{game_id}`\n\n*Для випадкової події:* `/event` \n*Для голосування:* `/vote` (коли всі зайдуть)",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(Command("event"))
async def trigger_event(message: types.Message):
    event = random.choice(RANDOM_EVENTS)
    await message.answer(event)
    if "Знайдено рюкзак" in event:
        active_bonuses[message.chat.id] = True

@dp.message(Command("vote"))
async def start_vote(message: types.Message):
    # Шукаємо останню створену гру в цьому чаті (спрощено)
    game_id = None
    for gid in games:
        game_id = gid # Беремо будь-який активний ID
    
    if not game_id or not games[game_id]["players"]:
        return await message.answer("❌ Ще ніхто не приєднався до гри!")

    await message.answer_poll(
        question="Кого виженемо з бункера?",
        options=games[game_id]["players"][:10], # Телеграм дозволяє до 10 варіантів
        is_anonymous=True,
        allows_multiple_answers=False
    )

@dp.message(lambda message: message.text == "БУНКЕР")
async def catch_bonus(message: types.Message):
    if message.chat.id in active_bonuses:
        del active_bonuses[message.chat.id] 
        bonus_item = random.choice(BONUS_BAGGAGE)
        await message.reply(f"🎉 **ШВИДКО!** Ти забрав рюкзак!\n\n✨ Бонус: **{bonus_item}**")

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
    
    # Додаємо ім'я гравця в список для голосування
    player_name = message.from_user.first_name
    if player_name not in games[game_id]["players"]:
        games[game_id]["players"].append(player_name)
    
    response = (
        f"🚨 **ВИ У ГРІ #{game_id}**\n\n"
        f"💼 **Ваша картка:**\n"
        f"• 🛠 Професія: {random.choice(PROFESSIONS)}\n"
        f"• ❤️ Здоров'я/Вік: {random.choice(HEALTH)}\n"
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
        await dp.start_polling(bot)
    asyncio.run(main())
    asyncio.run(main())
