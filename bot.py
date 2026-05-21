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

# --- СПИСКИ ДАНИХ (Коротко для економії місця, залиште свої повні списки) ---
CATASTROPHES_DATA = [
    {"name": "🌋 Ядерна зима", "desc": "Радіоактивний попіл закрив сонце. Температура -50°C.", "range": (20, 50)},
    {"name": "🧟 Зомбі-апокаліпсис", "desc": "Світ кишить зараженими.", "range": (2, 7)},
    {"name": "🌊 Всесвітній потоп", "desc": "Танення льодовиків.", "range": (10, 20)}
]
HEALTH_STATUS = ["Астма", "Травма ноги", "Сліпота", "Безсоння", "Алергія", "Діабет"]
PROFESSIONS = ["Лікар", "Агроном", "Інженер", "Кухар", "Програміст", "Електрик"]
# ... (Інші ваші списки: AGES, GENDERS, PSYCH, HOBBIES, BAGGAGE, PHOBIAS, SECRET_GOALS, SPECIAL_ABILITIES)

RANDOM_EVENTS = [
    {"text": "⚠️ Землетрус! Гравці з відкритим багажем міняються ним!", "type": "earthquake"},
    {"text": "⚠️ Викид радіації! Усі здорові гравці отримують випадкову хворобу!", "type": "radiation"}
]

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def find_game_id(user_id):
    for g_id in games:
        if user_id in games[g_id]["players"]:
            return g_id
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

# --- ОСНОВНА ЛОГІКА ---
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
        "players": {}, "active_players": [], "revealed": {"bag": [], "prof": [], "health": []},
        "event_triggered": False
    }
    await callback.message.answer(f"🎮 **Гру #{game_id} створено!**\n🔑 Код: `{game_id}`")
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
    # Реєструємо гравця
    games[game_id]["players"][u_id] = message.from_user.first_name
    if u_id not in games[game_id]["active_players"]:
        games[game_id]["active_players"].append(u_id)
    
    # Створюємо картку
    player_cards[u_id] = {
        "prof": random.choice(PROFESSIONS), "health": "Ідеальне", 
        "bag": "Ніж", "hobby": "Риболовля", "phobia": "Немає",
        "spec": "Імунітет", "age": "25 років", "gender": "Чоловік", 
        "psych": "Спокійний", "goal": "Вижити", "spec_used": False
    }
    
    await state.clear()
    await message.answer(f"✅ Ви приєдналися до гри #{game_id}!\nТепер ви можете писати повідомлення іншим гравцям прямо сюди.", reply_markup=get_reveal_keyboard(game_id))

# --- ВИПРАВЛЕНИЙ ЧАТ (ПЕРЕСИЛАННЯ ПОВІДОМЛЕНЬ) ---
@dp.message(F.text & ~F.text.startswith('/'))
async def game_chat(message: types.Message):
    u_id = message.from_user.id
    g_id = find_game_id(u_id)
    
    if g_id:
        sender_name = games[g_id]["players"][u_id]
        chat_text = f"💬 **{sender_name}**: {message.text}"
        
        # Надсилаємо всім, крім самого себе
        for player_id in games[g_id]["players"]:
            if player_id != u_id:
                try:
                    await bot.send_message(player_id, chat_text, parse_mode="Markdown")
                except Exception as e:
                    logging.error(f"Не вдалося надіслати повідомлення {player_id}: {e}")
        
        # Підтвердження для відправника (щоб ви бачили, що повідомлення пішло)
        await message.reply("📤 *Повідомлення надіслано іншим*", parse_mode="Markdown")
    else:
        await message.answer("⚠️ Ви не перебуваєте в активній грі. Натисніть /start.")

# --- ЛОГІКА ПОДІЙ (Радіація) ---
@dp.callback_query(F.data.startswith("game_event_"))
async def cb_event(callback: types.CallbackQuery):
    g_id = callback.data.split("_")[2]
    if games[g_id].get("event_triggered"): return await callback.answer("❌ Вже було!", show_alert=True)
    
    games[g_id]["event_triggered"] = True
    event = random.choice(RANDOM_EVENTS)
    
    for p_id in games[g_id]["players"]:
        await bot.send_message(p_id, f"🔥 **ПОДІЯ!**\n{event['text']}")

    if event["type"] == "radiation":
        summary = "☢️ **Наслідки опромінення:**\n"
        for u_id in games[g_id]["active_players"]:
            if player_cards[u_id]["health"] == "Ідеальне":
                new_disease = random.choice(HEALTH_STATUS)
                player_cards[u_id]["health"] = new_disease
                summary += f"☣️ {games[g_id]['players'][u_id]} -> **{new_disease}**\n"
        
        for p_id in games[g_id]["players"]:
            await bot.send_message(p_id, summary)
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
