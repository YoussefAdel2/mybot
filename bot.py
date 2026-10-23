import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          CallbackQueryHandler, ContextTypes)

TOKEN = os.environ["TOKEN"]
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")

# ======================= عدّل هنا بس =======================
# كل "خانة" ليها نص وأزرار. نوع الزر:
#   menu = يفتح خانة تانية
#   file = يبعت للمستخدم ملف من فولدر files
#   text = يبعت رسالة نصية
#   url  = يفتح رابط
MENUS = {
    "main": {
        "text": "أهلاً بيك 👋\nاختار من القائمة:",
        "buttons": [
            ("📁 الملفات", "menu", "files"),
            ("ℹ️ عنّا", "text", "ده بوت تجريبي، عدّل الكلام ده من bot.py"),
            ("🌐 الموقع", "url", "https://example.com"),
        ],
    },
    "files": {
        "text": "📁 اختار الملف اللي عاوزه:",
        "buttons": [
            ("📄 ملف تجريبي", "file", "sample.txt"),
            ("📂 قسم تاني", "menu", "more"),
        ],
    },
    "more": {
        "text": "📂 ده قسم جديد، زوّد فيه اللي تحبه.",
        "buttons": [
            ("📄 ملف تجريبي", "file", "sample.txt"),
        ],
    },
}
# ===========================================================

def build_keyboard(menu_name):
    rows = []
    for i, (label, kind, value) in enumerate(MENUS[menu_name]["buttons"]):
        if kind == "url":
            rows.append([InlineKeyboardButton(label, url=value)])
        else:
            rows.append([InlineKeyboardButton(label, callback_data=f"{menu_name}:{i}")])
    if menu_name != "main":
        rows.append([InlineKeyboardButton("🔙 رجوع للرئيسية", callback_data="home")])
    return InlineKeyboardMarkup(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MENUS["main"]["text"], reply_markup=build_keyboard("main"))

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "home":
        await q.edit_message_text(MENUS["main"]["text"], reply_markup=build_keyboard("main"))
        return

    try:
        menu_name, idx = q.data.split(":")
        _, kind, value = MENUS[menu_name]["buttons"][int(idx)]
    except (ValueError, KeyError, IndexError):
        return

    if kind == "menu":
        await q.edit_message_text(MENUS[value]["text"], reply_markup=build_keyboard(value))
    elif kind == "text":
        await q.message.reply_text(value)
    elif kind == "file":
        path = os.path.join(FILES_DIR, value)
        if not os.path.exists(path):
            await q.message.reply_text("⚠️ الملف مش موجود.")
            return
        with open(path, "rb") as f:
            if value.lower().endswith((".jpg", ".jpeg", ".png")):
                await q.message.reply_photo(f)
            else:
                await q.message.reply_document(f)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(on_button))
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = os.environ["RENDER_EXTERNAL_URL"]  # Render بيحطه تلقائي

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"{BASE_URL}/{TOKEN}",
)
