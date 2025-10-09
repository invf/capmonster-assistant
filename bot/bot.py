import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or "ТВОЙ_ТОКЕН_БОТА"
CAP_KEY = os.getenv("CAPMONSTER_API_KEY") or None
CAP_URL = "https://api.capmonster.cloud"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Меню капч ---
captcha_types = {
    "recaptchav2": "🧠 Recaptcha V2",
    "binance": "🪙 Binance Captcha",
    "altcha": "⚙️ Altcha Captcha",
    "image2text": "📷 Image to Text",
    "datadome": "🧩 DataDome Slider"
}

def get_keyboard():
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=key)]
        for key, name in captcha_types.items()
    ]
    buttons.append([InlineKeyboardButton(text="🔁 Check All", callback_data="check_all")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Функція тестування капчі ---
async def test_captcha(session, captcha_type: str, client_key: str):
    payload = {"clientKey": client_key, "task": {}}

    if captcha_type == "recaptchav2":
        payload["task"] = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": "https://www.google.com/recaptcha/api2/demo",
            "websiteKey": "6Lf09xMUAAAAAKkM6KZtA_j4Qoe6OZ1zY2ZC7jG8"
        }
    elif captcha_type == "binance":
        payload["task"] = {"type": "BinanceTask", "websiteURL": "https://www.binance.com"}
    elif captcha_type == "altcha":
        payload["task"] = {
            "type": "AltchaTaskProxyless",
            "websiteURL": "https://altcha.org/demo/",
            "challengeScript": "https://altcha.org/captcha.js"
        }
    elif captcha_type == "image2text":
        payload["task"] = {
            "type": "ImageToTextTask",
            "body": "iVBOR..."  # короткий приклад зображення в base64
        }
    elif captcha_type == "datadome":
        payload["task"] = {"type": "DataDomeSliderTask", "websiteURL": "https://datadome.co/"}
    else:
        return "❌ Unsupported captcha type."

    # створення задачі
    async with session.post(f"{CAP_URL}/createTask", json=payload) as resp:
        data = await resp.json()
        if data.get("errorId") != 0:
            return f"❌ Error creating task: {data}"
        task_id = data["taskId"]

    # перевіряємо результат
    for _ in range(25):
        await asyncio.sleep(2)
        async with session.post(f"{CAP_URL}/getTaskResult", json={"clientKey": client_key, "taskId": task_id}) as r:
            res = await r.json()
            if res.get("status") == "ready":
                return f"✅ {captcha_types.get(captcha_type)} solved!\n<code>{res['solution']}</code>"
    return f"⚠️ Timeout for {captcha_types.get(captcha_type)}"

# --- Обробники ---
user_keys = {}  # {user_id: api_key}

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "👋 Welcome to CapMonster Validator!\n\n"
        "Send me your API key first to begin testing.",
        reply_markup=None
    )

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()
    user_id = message.from_user.id

    # якщо користувач ще не встановив ключ
    if not user_id in user_keys:
        user_keys[user_id] = text
        await message.answer("✅ API key saved! Now choose captcha type:", reply_markup=get_keyboard())
        return

    await message.answer("Send /start to reset or use the menu below.", reply_markup=get_keyboard())

@dp.callback_query()
async def handle_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in user_keys:
        await query.message.answer("⚠️ Please send your API key first.")
        return

    client_key = user_keys[user_id]
    captcha_type = query.data
    await query.message.edit_text(f"🔍 Testing {captcha_type}...", parse_mode="HTML")

    async with aiohttp.ClientSession() as session:
        if captcha_type == "check_all":
            results = []
            for key in captcha_types.keys():
                res = await test_captcha(session, key, client_key)
                results.append(res)
            text = "\n\n".join(results)
        else:
            text = await test_captcha(session, captcha_type, client_key)

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_keyboard())

# --- Запуск ---
async def main():
    print("🤖 CapMonster Validator Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
