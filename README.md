# 🧮 Math Solver Bot

Rasmdagi matematik misollarni Google Gemini AI yordamida yechuvchi Telegram bot.

---

## 📁 Loyiha Tuzilmasi

```
math_solver_bot/
├── bot.py              # Asosiy bot kodi
├── .env.example        # Muhit o'zgaruvchilari namunasi
├── .env                # Sizning maxfiy kalitlaringiz (yarating, commit qilmang!)
├── requirements.txt    # Python kutubxonalari
└── README.md           # Ushbu fayl
```

---

## ⚙️ O'rnatish va Ishga Tushirish

### 1. Repozitoriyni klonlash
```bash
git clone <repo-url>
cd math_solver_bot
```

### 2. Virtual muhit yaratish (tavsiya etiladi)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlash
```bash
cp .env.example .env
```
Keyin `.env` faylini oching va qiymatlarni to'ldiring:

| O'zgaruvchi | Qayerdan olish | Misol |
|---|---|---|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) | `7412345678:AAF...` |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) | `AIzaSy...` |
| `CHANNEL_USERNAME` | Kanalingiz username'i | `@mening_kanalim` |

### 5. Botni ishga tushirish
```bash
python bot.py
```

---

## 🤖 Bot Qo'llanmasi

**Foydalanuvchi uchun:**
1. Botga `/start` yozing
2. Kanalga a'zo bo'ling (agar talab qilinsa)
3. Matematik misol tushirilgan rasmni yuboring
4. Bot yechimni qaytaradi ✅

---

## 🔒 Xavfsizlik

- `.env` faylini **hech qachon** Git'ga push qilmang
- `.gitignore` fayliga qo'shing:
  ```
  .env
  __pycache__/
  venv/
  ```

---

## 📦 Texnologiyalar

| Kutubxona | Versiya | Maqsad |
|---|---|---|
| `aiogram` | 3.x | Telegram Bot Framework |
| `google-generativeai` | 0.8.x | Gemini AI integratsiya |
| `Pillow` | 10.x | Rasm qayta ishlash |
| `python-dotenv` | 1.x | `.env` faylini o'qish |
