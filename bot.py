"""
Masala Yechuvchi Bot  (@masala_yechuvchi_bot)
==============================================
Foydalanuvchi yuborgan rasmdagi matematik misolni
Google Gemini AI yordamida yechib beruvchi bot.

Bot nomi     : Masala Yechuvchi
Bot username : @masala_yechuvchi_bot
Stack        : aiogram 3.x + Google Gemini API
"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

import google.generativeai as genai
from PIL import Image
import io

# ─────────────────────────────────────────────
# 1. SOZLAMALAR (Configuration)
# ─────────────────────────────────────────────

# .env faylidan maxfiy ma'lumotlarni yuklash
load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "@kanal_username")  # @ bilan

# Logging sozlamasi — barcha muhim voqealar consolega chiqariladi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 2. GEMINI API SOZLAMASI
# ─────────────────────────────────────────────

# Gemini API kalitini ro'yxatdan o'tkazish
genai.configure(api_key=GEMINI_API_KEY)

# gemini-1.5-flash — tez va rasmlarni qo'llab-quvvatlovchi model
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# ─────────────────────────────────────────────
# 3. BOT VA DISPATCHER YARATISH
# ─────────────────────────────────────────────

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ─────────────────────────────────────────────
# 4. YORDAMCHI FUNKSIYALAR (Helpers)
# ─────────────────────────────────────────────


async def is_subscribed(user_id: int) -> bool:
    """
    Foydalanuvchi kanalga a'zo ekanligini tekshiradi.

    Args:
        user_id: Telegram foydalanuvchi ID raqami

    Returns:
        True  → a'zo
        False → a'zo emas yoki xatolik
    """
    try:
        # get_chat_member — foydalanuvchi statusini qaytaradi:
        # member, administrator, creator, left, kicked, restricted
        member = await bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id,
        )
        # "left" yoki "kicked" bo'lsa — a'zo emas
        return member.status not in ("left", "kicked")
    except Exception as e:
        logger.warning(f"A'zolikni tekshirishda xatolik (user_id={user_id}): {e}")
        return False


def build_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Kanalga a'zo bo'lish va tekshirish tugmalarini yaratadi.

    Returns:
        InlineKeyboardMarkup: 2 ta tugmali klaviatura
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                # 1-tugma: kanalga o'tish linki
                InlineKeyboardButton(
                    text="📢 Kanalga a'zo bo'lish",
                    url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}",
                )
            ],
            [
                # 2-tugma: a'zo bo'lgandan keyin tekshirish
                InlineKeyboardButton(
                    text="✅ A'zo bo'ldim, tekshir!",
                    callback_data="check_subscription",
                )
            ],
        ]
    )
    return keyboard


async def solve_math_from_image(image_bytes: bytes) -> str:
    """
    Rasm baytlarini Gemini API'ga yuborib, matematik misolni yechadi.

    Args:
        image_bytes: Rasmning xom bayt ma'lumotlari

    Returns:
        Gemini'dan kelgan yechim matni
    """
    try:
        # Baytlardan PIL Image obyektini yaratish
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Gemini'ga yuboriladigan so'rov matni (prompt)
        prompt = (
            "Siz matematik misol yechuvchi ekspertsiz.\n"
            "Rasmda matematik misol bor. Quyidagilarni bajaring:\n"
            "1. Rasmda ko'ringan misolni aniq yozing.\n"
            "2. Bosqichma-bosqich yechimini ko'rsating.\n"
            "3. Oxirida to'g'ri javobni alohida yozing.\n\n"
            "Javobingizni o'zbek tilida bering."
        )

        logger.info("Gemini API'ga so'rov yuborilmoqda...")

        # Gemini'ga rasm + prompt yuborish (multimodal so'rov)
        response = gemini_model.generate_content([prompt, pil_image])

        logger.info("Gemini API'dan javob olindi.")
        return response.text

    except Exception as e:
        logger.error(f"Gemini API xatoligi: {e}")
        return f"❌ Rasmni tahlil qilishda xatolik yuz berdi:\n<code>{str(e)}</code>"


# ─────────────────────────────────────────────
# 5. HANDLERLAR (Message & Callback Handlers)
# ─────────────────────────────────────────────


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    /start komandasi uchun handler.
    Foydalanuvchini salomlaydi va bot haqida ma'lumot beradi.
    """
    user_name = message.from_user.full_name
    logger.info(f"Yangi foydalanuvchi: {user_name} (ID: {message.from_user.id})")

    await message.answer(
        f"👋 Salom, <b>{user_name}</b>!\n\n"
        "🧮 <b>Masala Yechuvchi</b>ga xush kelibsiz!\n\n"
        "Men rasmdagi matematik misollarni yechib beraman.\n\n"
        "📌 <b>Qanday ishlash kerak?</b>\n"
        "1️⃣ Matematik misol tushirilgan rasmni yuboring\n"
        "2️⃣ Men uni tahlil qilib, yechimini ko'rsataman\n\n"
        "▶️ Boshlash uchun rasm yuboring!"
    )


@dp.message(F.photo)
async def handle_photo(message: Message) -> None:
    """
    Foydalanuvchi rasm yuborganida ishga tushadigan handler.

    Logika:
    1. Kanalga a'zolikni tekshir
    2. A'zo bo'lmasa → obuna so'rov xabari yuboriladi
    3. A'zo bo'lsa → rasmni yuklab, Gemini'ga yuborib, javobni qaytaradi
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    logger.info(f"Rasm qabul qilindi | Foydalanuvchi: {user_name} (ID: {user_id})")

    # ── Qadam 1: A'zolikni tekshirish ──
    subscribed = await is_subscribed(user_id)

    if not subscribed:
        logger.info(f"Foydalanuvchi {user_id} kanalga a'zo emas.")
        await message.answer(
            "⛔ <b>Botdan foydalanish uchun avval kanalga a'zo bo'ling!</b>\n\n"
            f"📢 Kanal: {CHANNEL_USERNAME}\n\n"
            "A'zo bo'lgandan so'ng \"✅ A'zo bo'ldim, tekshir!\" tugmasini bosing.",
            reply_markup=build_subscription_keyboard(),
        )
        return  # A'zo bo'lmasa, keyingi qadamlarga o'tilmaydi

    # ── Qadam 2: Rasmni yuklab olish ──

    # Telegram bir rasmni bir necha o'lchamda saqlaydi,
    # [-1] eng yuqori sifatli (katta) versiyani beradi
    photo = message.photo[-1]

    # Foydalanuvchiga kutish xabari
    wait_msg = await message.answer(
        "⏳ <b>Rasm tahlil qilinmoqda...</b>\n"
        "Iltimos, biroz kuting."
    )

    try:
        # Rasmni bayt ko'rinishida yuklab olish
        file_info = await bot.get_file(photo.file_id)
        file_bytes_io = await bot.download_file(file_info.file_path)
        image_bytes = file_bytes_io.read()

        logger.info(f"Rasm yuklandi: {len(image_bytes)} bayt")

        # ── Qadam 3: Gemini'ga yuborish va javob olish ──
        solution = await solve_math_from_image(image_bytes)

        # ── Qadam 4: Javobni foydalanuvchiga yuborish ──

        # Kutish xabarini o'chirish
        await wait_msg.delete()

        await message.answer(
            f"✅ <b>Yechim topildi!</b>\n\n"
            f"{solution}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔄 Yangi misol uchun rasm yuboring."
        )
        logger.info(f"Javob muvaffaqiyatli yuborildi | Foydalanuvchi: {user_id}")

    except Exception as e:
        logger.error(f"Rasmni qayta ishlashda xatolik: {e}")
        await wait_msg.delete()
        await message.answer(
            "❌ <b>Xatolik yuz berdi!</b>\n"
            "Iltimos, rasmni qaytadan yuboring yoki boshqa rasm sinab ko'ring."
        )


@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery) -> None:
    """
    "A'zo bo'ldim, tekshir!" tugmasi bosilganida ishga tushadigan handler.

    Foydalanuvchining a'zoligini qayta tekshiradi va natijaga qarab javob beradi.
    """
    user_id = callback.from_user.id

    logger.info(f"A'zolik tekshiruvi so'raldi | Foydalanuvchi: {user_id}")

    # Callback'ga javob berish (Telegram spinner'ni to'xtatish uchun zarur)
    await callback.answer()

    subscribed = await is_subscribed(user_id)

    if subscribed:
        logger.info(f"Foydalanuvchi {user_id} a'zolikni tasdiqladi.")

        # Eski xabarni yangi xabar bilan almashtirish
        await callback.message.edit_text(
            "🎉 <b>A'zoligingiz tasdiqlandi!</b>\n\n"
            "Endi menga matematik misol tushirilgan rasm yuboring, "
            "men uni yechib beraman! 🧮"
        )
    else:
        logger.info(f"Foydalanuvchi {user_id} hali kanalga a'zo emas.")

        # Xabarni o'zgartirmasdan, faqat alert ko'rsatish
        await callback.answer(
            "❌ Siz hali kanalga a'zo emassiz!\n"
            "Iltimos, avval a'zo bo'ling.",
            show_alert=True,  # Katta oynachada ko'rsatish
        )


@dp.message(~F.photo)
async def handle_non_photo(message: Message) -> None:
    """
    Rasm bo'lmagan har qanday xabarga javob beruvchi handler.
    Foydalanuvchiga nima qilish kerakligini eslatadi.
    """
    # /start komandasiga bu handler ishlamasligi kerak
    if message.text and message.text.startswith("/"):
        return

    await message.answer(
        "📸 Iltimos, faqat <b>matematik misol tushirilgan rasm</b> yuboring!\n\n"
        "Matn, fayl yoki boshqa turdagi xabarlar qabul qilinmaydi."
    )


# ─────────────────────────────────────────────
# 6. BOTNI ISHGA TUSHIRISH (Entry Point)
# ─────────────────────────────────────────────


async def main() -> None:
    """Asosiy asinxron funksiya — botni ishga tushiradi."""

    logger.info("=" * 50)
    logger.info("Masala Yechuvchi Bot (@masala_yechuvchi_bot) ishga tushmoqda...")
    logger.info(f"Kanal: {CHANNEL_USERNAME}")
    logger.info("=" * 50)

    # Polling rejimida botni ishga tushirish
    # skip_updates=True — bot o'chiq turgan vaqtdagi xabarlarni o'tkazib yuboradi
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (KeyboardInterrupt).")
