import asyncio
import logging
import os
import io
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from aiogram.middleware.base import BaseMiddleware

# 1. Konfiguratsiya
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Loggingni sozlash
logging.basicConfig(level=logging.INFO)

# Gemini sozlamalari
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Middleware: Kanalga a'zolikni tekshirish ---
class CheckSubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return await handler(event, data)
            else:
                await self.send_subscription_msg(event)
        except TelegramBadRequest:
            await event.answer("Xatolik: Kanal topilmadi yoki bot kanal admini emas.")
        except Exception as e:
            logging.error(f"Middleware xatosi: {e}")
            await event.answer("Texnik xatolik yuz berdi.")

    async def send_subscription_msg(self, event):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
            [InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")]
        ])
        await event.answer("Botdan foydalanish uchun kanalimizga a'zo bo'ling:", reply_markup=keyboard)

# --- Handlers ---
@dp.message(CommandStart())
async def start_handler(msg: types.Message):
    await msg.answer("Salom! Matematik misol tushirilgan rasmni yuboring, men uni yechib beraman.")

@dp.message(F.photo)
@CheckSubscriptionMiddleware() # Har bir rasm uchun tekshiruv
async def solve_math_handler(msg: types.Message):
    await msg.answer("Rasmni tahlil qilmoqdaman, biroz kuting...")
    
    # Rasmni yuklab olish
    photo = msg.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)
    
    # Rasmni PIL formatiga o'tkazish
    img = Image.open(io.BytesIO(file_bytes.read()))
    
    try:
        # Gemini-ga yuborish
        response = model.generate_content([
            "Bu matematik misolni yechib ber. Javobni qadam-baqadam tushuntirib ber (o'zbek tilida).", 
            img
        ])
        await msg.answer(response.text)
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        await msg.answer("Kechirasiz, rasmni tahlil qilishda xatolik yuz berdi.")

# Ishga tushirish
async def main():
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
