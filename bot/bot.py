import os, aiohttp, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv(".env.bot")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/solve")

bot, dp = Bot(BOT_TOKEN), Dispatcher()

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("👋 Надішли зображення капчі — розв’яжу через CapMonsterCloud 🔮")

@dp.message()
async def solve(m: types.Message):
    if not m.photo:
        return await m.answer("📸 Надішли саме зображення.")
    file_id = m.photo[-1].file_id
    file = await bot.get_file(file_id)
    photo = await bot.download_file(file.file_path)

    form = aiohttp.FormData(); form.add_field("file", photo, filename="captcha.jpg")
    async with aiohttp.ClientSession() as s:
        async with s.post(BACKEND_URL, data=form) as resp:
            data = await resp.json()
            await m.answer(f"✅ Розв’язано: `{data.get('solution',{}).get('text','—')}`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
