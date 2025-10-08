import os
import aiohttp
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CAPMONSTER_KEY = os.getenv("CAPMONSTER_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Команда /start ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🧩 Samples", callback_data="samples")
    kb.button(text="💰 Balance", callback_data="balance")
    await msg.answer(
        "👋 Привіт! Надішли мені фото капчі, і я розпізнаю її через CapMonsterCloud.\n"
        "Або вибери дію нижче 👇",
        reply_markup=kb.as_markup()
    )

# --- Callback кнопки ---
@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    if call.data == "balance":
        r = requests.post("https://api.capmonster.cloud/getBalance", json={"clientKey": CAPMONSTER_KEY})
        data = r.json()
        if data.get("errorId") == 0:
            await call.message.answer(f"💰 Баланс CapMonsterCloud: {data['balance']} USD")
        else:
            await call.message.answer(f"⚠️ Помилка: {data}")
    elif call.data == "samples":
        kb = InlineKeyboardBuilder()
        kb.button(text="📷 Image sample", callback_data="sample_image")
        kb.button(text="🌐 reCAPTCHA demo", url="https://www.google.com/recaptcha/api2/demo")
        kb.button(text="🌐 hCaptcha demo", url="https://accounts.hcaptcha.com/demo")
        kb.button(text="🌐 GeeTest demo", url="https://demos.geetest.com/sensebot")
        await call.message.answer("🔗 Ось тестові капчі:", reply_markup=kb.as_markup())
    elif call.data == "sample_image":
        await call.message.answer_photo(
            "https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/data/captcha_sample.png",
            caption="📸 Надішли подібну капчу — я спробую її розпізнати!"
        )

# --- Основний обробник зображень ---
@dp.message()
async def solve_captcha(msg: types.Message):
    if not msg.photo:
        return await msg.answer("📸 Надішли саме зображення капчі.")
    
    file_id = msg.photo[-1].file_id
    file = await bot.get_file(file_id)
    photo = await bot.download_file(file.file_path)

    form = aiohttp.FormData()
    form.add_field("file", photo, filename="captcha.jpg")

    progress_msg = await msg.answer("🌀 Розпочинаю розгадування... 0%")
    progress = 0

    try:
        async with aiohttp.ClientSession() as session:
            # Створюємо запит до бекенду /solve_progress
            async with session.post(f"{BACKEND_URL}/solve_progress", data=form) as resp:
                # Імітуємо процес — поступово оновлюємо % під час очікування
                for i in range(1, 6):
                    progress += 20
                    await progress_msg.edit_text(f"🤔 Розгадую... {progress}%")
                    await asyncio.sleep(1)
                
                data = await resp.json()

                if data.get("status") == "ready":
                    text = data["solution"]["text"]
                    await progress_msg.edit_text(f"✅ Розпізнано: `{text}`", parse_mode="Markdown")
                elif data.get("status") == "timeout":
                    await progress_msg.edit_text("⚠️ Не вдалося розпізнати (timeout).")
                else:
                    await progress_msg.edit_text(f"❌ Помилка: {data}")
    except Exception as e:
        await progress_msg.edit_text(f"❌ Помилка: {e}")

# --- Запуск ---
async def main():
    print("🤖 Bot started and waiting for captchas...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
