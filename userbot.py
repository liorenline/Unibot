from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8421493534:AAFZtFHyqCM1v-8yHhoIG2elAC1HQZgA44A"
MOD_CHAT = -5031104641

user_data = {}

def main_menu():
    return ReplyKeyboardMarkup(
        [["Повідомити знахідку"], ["Техпідтримка"], ["Наші соцмережі"]],
        resize_keyboard=True
    )

def yes_no():
    return ReplyKeyboardMarkup(
        [["Так", "Ні", "Назад"]],
        resize_keyboard=True
    )

def pr_button():
    return ReplyKeyboardMarkup(
        [["Відправити на модерацію", "Почати спочатку"], ["Головне меню"]],
        resize_keyboard=True
    )

async def send_question_for_status(update, user_id):
    status = user_data[user_id]["status"]

    if status == "where":
        await update.message.reply_text("Де була знайдена річ?", reply_markup=ReplyKeyboardRemove())
    elif status == "what":
        await update.message.reply_text("Що було знайдено?", reply_markup=ReplyKeyboardRemove())
    elif status == "ask_description":
        await update.message.reply_text("Додати опис?", reply_markup=yes_no())
    elif status == "description":
        await update.message.reply_text("Напишіть опис:", reply_markup=ReplyKeyboardRemove())
    elif status == "ask_photo":
        await update.message.reply_text("Додати фото?", reply_markup=yes_no())
    elif status == "photo":
        await update.message.reply_text("Надішліть фото:", reply_markup=ReplyKeyboardRemove())
    elif status == "support":
        await update.message.reply_text("Опишіть вашу проблему:", reply_markup=ReplyKeyboardRemove())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    user_data[user_id] = {
        "status": "menu",
        "history": [],
        "where": None,
        "what": None,
        "description": None,
        "photo": None,
        "contact": None
    }

    await update.message.reply_text("Оберіть дію:", reply_markup=main_menu())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("Натисніть /start")
        return

    if text == "Назад":
        hist = user_data[user_id]["history"]
        if hist:
            user_data[user_id]["status"] = hist.pop()
            await send_question_for_status(update, user_id)
        else:
            await update.message.reply_text("Нікуди повертатись.")
        return

    status = user_data[user_id]["status"]

    buttons_only = {
        "menu": ["Повідомити знахідку", "Техпідтримка", "Наші соцмережі"],
        "ask_description": ["Так", "Ні", "Назад"],
        "ask_photo": ["Так", "Ні", "Назад"],
        "preview_menu": ["Відправити на модерацію", "Почати спочатку", "Головне меню"]
    }

    if status in buttons_only and text not in buttons_only[status]:
        await update.message.reply_text("Натисніть кнопку.")
        await send_question_for_status(update, user_id)
        return

    if status == "menu" and text == "Повідомити знахідку":
        user_data[user_id]["history"].append("menu")
        user_data[user_id]["status"] = "where"
        await update.message.reply_text("Де була знайдена річ?", reply_markup=ReplyKeyboardRemove())
        return

    if status == "menu" and text == "Техпідтримка":
        user_data[user_id]["status"] = "support"
        await update.message.reply_text("Опишіть вашу проблему:", reply_markup=ReplyKeyboardRemove())
        return

    if status == "support":
        username = update.message.from_user.username
        uid = update.message.from_user.id
        msg = f"Техпідтримка:\nВід @{username} (ID: {uid})\n{text}"
        await context.bot.send_message(chat_id=MOD_CHAT, text=msg)
        user_data[user_id]["status"] = "menu"
        await update.message.reply_text("Ваше звернення передано модераторам.", reply_markup=main_menu())
        return

    if status == "menu" and text == "Наші соцмережі":
        await update.message.reply_text("Наші соцмережі: ...")
        return

    if status == "where":
        user_data[user_id]["history"].append("where")
        user_data[user_id]["where"] = text
        user_data[user_id]["status"] = "what"
        await update.message.reply_text("Що було знайдено?", reply_markup=ReplyKeyboardRemove())
        return

    if status == "what":
        user_data[user_id]["history"].append("what")
        user_data[user_id]["what"] = text
        user_data[user_id]["status"] = "ask_description"
        await update.message.reply_text("Додати опис?", reply_markup=yes_no())
        return

    if status == "ask_description":
        user_data[user_id]["history"].append("ask_description")
        if text == "Так":
            user_data[user_id]["status"] = "description"
            await update.message.reply_text("Напишіть опис:", reply_markup=ReplyKeyboardRemove())
            return
        else:
            user_data[user_id]["description"] = None
            user_data[user_id]["status"] = "ask_photo"
            await update.message.reply_text("Додати фото?", reply_markup=yes_no())
            return

    if status == "description":
        user_data[user_id]["history"].append("description")
        user_data[user_id]["description"] = text
        user_data[user_id]["status"] = "ask_photo"
        await update.message.reply_text("Додати фото?", reply_markup=yes_no())
        return

    if status == "ask_photo":
        user_data[user_id]["history"].append("ask_photo")
        if text == "Так":
            user_data[user_id]["status"] = "photo"
            await update.message.reply_text("Надішліть фото.", reply_markup=ReplyKeyboardRemove())
            return
        else:
            user_data[user_id]["photo"] = None
            user_data[user_id]["status"] = "preview"
            return

    if status == "photo":
        user_data[user_id]["history"].append("photo")

        if not update.message.photo:
            await update.message.reply_text("Це не фото. Надішліть фото ще раз.")
            return

        user_data[user_id]["photo"] = update.message.photo[-1].file_id
        user_data[user_id]["status"] = "preview"
        return

    if user_data[user_id]["status"] == "preview":
        user = update.message.from_user
        username = user.username
        contact = f"@{username}" if username else f"ID: {user.id}"
        user_data[user_id]["contact"] = contact

        ans = user_data[user_id]

        preview = ""
        if ans["where"]: preview += f"Де знайдено: {ans['where']}\n"
        if ans["what"]: preview += f"Що знайдено: {ans['what']}\n"
        if ans["description"]: preview += f"Опис: {ans['description']}\n"
        if ans["contact"]: preview += f"Контакт: {ans['contact']}\n"

        if ans["photo"]:
            await update.message.reply_photo(ans["photo"], caption=preview)
        else:
            await update.message.reply_text(preview)

        user_data[user_id]["status"] = "preview_menu"
        await update.message.reply_text("Готово. Чи бажаєте відправити на модерацію?", reply_markup=pr_button())
        return

    if text == "Головне меню":
        user_data[user_id] = {
            "status": "menu",
            "history": [],
            "where": None,
            "what": None,
            "description": None,
            "photo": None,
            "contact": None
        }
        await update.message.reply_text("Оберіть дію:", reply_markup=main_menu())
        return

    if text == "Почати спочатку":
        user_data[user_id]["status"] = "where"
        user_data[user_id]["history"] = []
        user_data[user_id]["where"] = None
        user_data[user_id]["what"] = None
        user_data[user_id]["description"] = None
        user_data[user_id]["photo"] = None
        user_data[user_id]["contact"] = None
        await update.message.reply_text("Де була знайдена річ?", reply_markup=ReplyKeyboardRemove())
        return

    if text == "Відправити на модерацію":
        ans = user_data[user_id]

        preview = ""
        if ans["where"]: preview += f"Де знайдено: {ans['where']}\n"
        if ans["what"]: preview += f"Що знайдено: {ans['what']}\n"
        if ans["description"]: preview += f"Опис: {ans['description']}\n"
        if ans["contact"]: preview += f"Контакт: {ans['contact']}\n"

        if ans["photo"]:
            await context.bot.send_photo(chat_id=MOD_CHAT, photo=ans["photo"], caption=preview)
        else:
            await context.bot.send_message(chat_id=MOD_CHAT, text=preview)

        user_data[user_id]["status"] = "menu"
        user_data[user_id]["history"] = []
        user_data[user_id]["where"] = None
        user_data[user_id]["what"] = None
        user_data[user_id]["description"] = None
        user_data[user_id]["photo"] = None
        user_data[user_id]["contact"] = None

        await update.message.reply_text("Надіслано модератору.", reply_markup=main_menu())
        return

    await update.message.reply_text("Я не розумію цю дію.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle))
app.run_polling()
