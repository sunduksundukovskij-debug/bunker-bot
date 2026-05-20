import random
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАЛАШТУВАННЯ ---
# Токен зчитується з налаштувань Environment на Render
API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

games = {}
active_bonuses = {}

class GameStates(StatesGroup):
    waiting_for_code = State()

# --- ДАНІ ГРИ ---
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик", "Вчитель", "Поліцейський", "Психолог", "Мисливець", "Пілот", "Хімік", "Архітектор", "Слюсар", "Журналіст", "Астроном", "Уфолог", "Вірусолог", "Радіолог", "Спелеолог"]
HEALTH_STATUS = ["Ідеальне", "Астма", "Травма ноги", "Вагітність", "Здоровий(а)", "Сліпота на одне око", "Безсоння", "Алергія", "Діабет", "Погана імунна система", "Безплодя", "1 нога", "Заражений(а)", "Міцний імунітет", "Витривалий(а)", "Швидка регенерація", "Чудовий зір", "Атлетична статура", "Відсутність хронічних хвороб"]
AGES = ["18 років", "22 роки", "25 років", "30 років", "33 роки", "40 років", "45 років", "50 років", "55 років", "60 років", "90 років", "70 років", "85 років"]
GENDERS = ["Чоловік", "Жінка"]
PSYCH = ["Спокійний", "Панікер", "Агресивний", "Оптиміст", "Параноїк", "Лідер", "Меланхолік", "Цинік", "Азартний", "Добряк"]
HOBBIES = ["Стрільба", "Гітара", "Садівництво", "Виживання", "Бокс", "Малювання", "Риболовля", "Паркур", "Кулінарія", "Йога"]
BAGGAGE = ["Ніж", "Аптечка", "Насіння", "Рація", "Ліхтарик", "Рушниця", "Протигаз", "Набір (юний хімік)", "Еліксир Молодості(-10р)", "Гітара", "Інструменти", "Запальничка", "Компас", "📦 Ящик консервів", "🥖 Сухпайок", "🍶 Запас води"]
PHOBIAS = ["Клаустрофобія", "Ахлуофобія (темрява)", "Мізофобія (бруд)", "Герпетофобія (плазуни)", "Соціофобія", "Немає", "Безстрашний(а)"]
BONUS_BAGGAGE = ["🛰 Супутниковий телефон", "🔋 Сонячна панель", "🧪 Універсальна сироватка", "🧥 Костюм хімзахисту", "🗝 Ключ від складу", "🗺 Карта ресурсів"]
SPECIAL_ABILITIES = ["🔄 Помінятися багажем.", "⏳ Помінятися віком або здоров'ям.", "📢 'Заткнути' гравця.", "🛡 Імунітет від вигнання.", "📝 Змінити професію.", "👁 Дізнатися секретну мету.", "🧨 Анулювати голосування."]
CATASTROPHES = ["Ядерна зима", "Зомбі-апокаліпсис", "Всесвітній потоп", "Нашестя іншопланетян", "Гіперсонячний спалах", "Льодовиковий період", "Повстання ШІ", "Смертельний грибок", "Повернення динозаврів", "Місяць зійшов з орбіти", "Кисневий голод", "Виверження супервулкана", "Глобальна пандемія", "Колапс магнітного поля", "Падіння астероїда", "Світ без електрики", "Нескінченні урагани", "Глобальна засуха"]
BUNKER_TYPES = ["📦 Звичайний бункер.", "🧬 Технологічний з ІНКУБАТОРАМИ.", "🧪 Експериментальний.", "🌿 Гідропонний.", "📚 Науковий.", "🛠 Військовий.", "💀 ХАРДКОР: Закинутий.", "🏨 Люкс-бункер.", "🏢 Підземне місто.", "📡 Обсерваторія.", "🏦 Банківське сховище.", "🚇 Сховище в метро.", "🛸 Космічна станція."]
BUNKER_PROBLEMS = ["зламаний генератор", "протікає дах", "немає вентиляції", "забагато мишей", "старе радіо", "грибок на стінах"]
SECRET_GOALS = ["🤫 Мета: Переконати взяти найстаршого.", "🤫 Мета: Вижити з 'Лікарем'.", "🤫 Мета: Вижити з 'Військовим'.", "🤫 Мета: Вигнати 'Поліцейського'.", "🤫 Мета: Вижити будь-якою ціною.", "🤫 Мета: Взяти людину з найгіршим здоров'ям.", "🤫 Мета: Зробити 2 жінки або 2 чоловіка в бункері.", "🤫 Мета: Не допустити гравця зі 'Зброєю'."]
RANDOM_EVENTS = ["⚠️ Землетрус! Всі міняються багажем.", "⚠️ Витік газу! Хворі мовчать 1 хв.", "⚠️ Знайдено рюкзак! Хто напише 'БУНКЕР', отримує бонус.", "⚠️ Аномальна зона! Зміна Фобії.", "⚠️ Сонячна буря! Гравці 40+ втрачають голос.", "⚠️ Мутація! Випадкова зміна Професії.", "⚠️ Психологічна атака! Відкрити Секретну мету.", "⚠️ Чутки про допомогу! Вигнання скасовано.", "⚠️ Обвал! Мінус одне місце в бункері."]

# --- КОМАНДИ ---
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
    games[game_id] = {"catastrophe": random.choice(CATASTROPHES), "bunker": random.choice(BUNKER_TYPES), "prob": random.choice(BUNKER_PROBLEMS), "players": []}
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n🌍 Катастрофа: {games[game_id]['catastrophe']}\n🛡 Тип: {games[game_id]['bunker']}\n❌ Проблема: {games[game_id]['prob']}\n🔑 Код: `{game_id}`", parse_mode="Markdown")
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
    await state.clear()
    p_name = message.from_user.first_name
    if p_name not in games[game_id]["players"]: games[game_id]["players"].append(p_name)
    g = games[game_id]
    response = (f"🚨 **ВИ У ГРІ #{game_id}**\n\n🌍 {g['catastrophe']}\n🛡 {g['bunker']}\n❌ {g['prob']}\n\n"
                f"👤 Стать: {random.choice(GENDERS)}\n🛠 Професія: {random.choice(PROFESSIONS)}\n❤️ Здоров'я: {random.choice(HEALTH_STATUS)}\n⏳ Вік: {random.choice(AGES)}\n🧠 Псих. стан: {random.choice(PSYCH)}\n🎸 Хобі: {random.choice(HOBBIES)}\n🎒 Багаж: {random.choice(BAGGAGE)}\n😱 Фобія: {random.choice(PHOBIAS)}\n✨ Здібність: {random.choice(SPECIAL_ABILITIES)}\n\n🎯 **{random.choice(SECRET_GOALS)}**")
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("vote"))
async def start_vote(message: types.Message):
    game_id = next(iter(games), None)
    if game_id and games[game_id]["players"]:
        await message.answer_poll(question="Кого виженемо?", options=games[game_id]["players"], is_anonymous=True)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
