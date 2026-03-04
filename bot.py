import os
import logging
from typing import Union

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Gemini ni sozlash
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')

if not all([BOT_TOKEN, GEMINI_API_KEY, CHANNEL_USERNAME]):
    logger.error("Iltimos, .env faylida barcha kerakli o'zgaruvchilarni to'ldiring")
    exit(1)

# Gemini sozlamalari
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Bot va dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Foydalanuvchining kanalga a'zoligini tekshirish funksiyasi
async def check_subscription(user_id: int) -> bool:
    """
    Foydalanuvchi belgilangan kanalga a'zo yoki yo'qligini tekshiradi.
    Qaytaradi: True agar a'zo bo'lsa, aks holda False.
    """
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # A'zo, admin yoki yaratuvchi bo'lsa True
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Subscription check error for user {user_id}: {e}")
        return False

# Start komandasi
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Salom! Matematik misol tushirilgan rasm yuboring.\n"
        f"Bot ishlashi uchun avval {CHANNEL_USERNAME} kanaliga a'zo bo'lishingiz kerak."
    )

# Rasm (foto) xabarini qayta ishlash
@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    logger.info(f"Rasm keldi: user_id={user_id}")

    # Majburiy a'zolikni tekshirish
    if not await check_subscription(user_id):
        # A'zo bo'lmaganlarga kanalga a'zo bo'lish tugmasini yuborish
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(
                text="🔔 Kanalga a'zo bo'lish",
                url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
            ),
            InlineKeyboardButton(
                text="✅ Tekshirish",
                callback_data="check_subscription"
            )
        )
        await message.answer(
            f"Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga a'zo bo'ling.",
            reply_markup=keyboard.as_markup()
        )
        return

    # A'zo bo'lsa, rasmni qayta ishlash
    await process_math_image(message)

# "Tekshirish" tugmasi bosilganda
@dp.callback_query(lambda c: c.data == "check_subscription")
async def callback_check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        # A'zo bo'libdi
        await callback.message.edit_text(
            "✅ A'zolik tasdiqlandi! Endi menga matematik misol rasmini yuborishingiz mumkin."
        )
    else:
        # Hali a'zo emas
        await callback.answer("Siz hali kanalga a'zo bo'lmagansiz!", show_alert=True)

    await callback.answer()

# Matematik misolni yechish
async def process_math_image(message: Message):
    """
    Rasmni yuklab oladi, Gemini API ga yuboradi va javobni foydalanuvchiga qaytaradi.
    """
    # Yuklab olish uchun eng katta rasmni olish
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    try:
        # Rasmni PIL Image formatiga o'tkazish (Gemini uchun)
        image = Image.open(io.BytesIO(file_bytes.getvalue()))

        # Gemini dan yechim so'rash
        prompt = "Matematik misolni yech va javobni batafsil tushuntirish bilan ber. Agar misol aniq bo'lmasa, iltimos, unda nima yozilganini aniqlab ber."
        response = model.generate_content([prompt, image])

        # Javobni foydalanuvchiga jo'natish
        if response.text:
            await message.reply(f"📝 **Yechim:**\n\n{response.text}")
        else:
            await message.reply("Kechirasiz, misolni tushunib bo'lmadi yoki javobni topa olmadim.")
    except Exception as e:
        logger.exception(f"Gemini API error: {e}")
        await message.reply("Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")

# Botni ishga tushirish
async def main():
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
