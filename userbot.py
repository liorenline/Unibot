from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

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
        [["Відправити на модерацію", "Почати спочатку"]],
        resize_keyboard=True
    )


async def send_question_for_status(update: Update, user_id: int):
    status = user_data[user_id]["status"]

    messages = {
        "where": "Де була знайдена річ?",
        "what": "Що було знайдено?",
        "ask_description": "Додати опис?",
        "description": "Напишіть опис:",
        "ask_photo": "Додати фото?",
        "photo": "Надішліть фото:",
        "ask_contact": "Додати контакт?",
        "contact": "Введіть контакт:"
    }

    kb = {
        "where": ReplyKeyboardRemove(),
        "what": ReplyKeyboardRemove(),
        "description": ReplyKeyboardRemove(),
        "photo": ReplyKeyboardRemove(),
    }

    reply_markup = kb.get(status, yes_no())

    await update.message.reply_text(messages[status], reply_markup=reply_markup)


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
    msg = update.message

    if user_id not in user_data:
        await msg.reply_text("Натисніть /start")
        return

    text = msg.text
    status = user_data[user_id]["status"]

    buttons_only = {
        "menu": ["Повідомити знахідку", "Техпідтримка", "Наші соцмережі"],
        "ask_description": ["Так", "Ні", "Назад"],
        "ask_photo": ["Так", "Ні", "Назад"],
        "ask_contact": ["Так", "Ні", "Назад"],
        "preview_menu": ["Відправити на модерацію", "Почати спочатку"],
    }

    if text == "Назад":
        hist = user_data[user_id]["history"]
        if hist:
            user_data[user_id]["status"] = hist.pop()
            await send_question_for_status(update, user_id)
        else:
            await msg.reply_text("Нікуди повертатись.")
        return

    if status in buttons_only and text not in buttons_only[status]:
        await msg.reply_text("Натисніть кнопку.")
        await send_question_for_status(update, user_id)
        return

    if status == "menu":
        if text == "Повідомити знахідку":
            user_data[user_id]["history"].append("menu")
            user_data[user_id]["status"] = "where"
            await msg.reply_text("Де була знайдена річ?", reply_markup=ReplyKeyboardRemove())
        elif text == "Техпідтримка":
            await msg.reply_text("Звертайтесь до @Ivan_na_d")
        elif text == "Наші соцмережі":
            await msg.reply_text("Наші соцмережі: ...")
        return

    if status == "where":
        user_data[user_id]["history"].append("where")
        user_data[user_id]["where"] = text
        user_data[user_id]["status"] = "what"
        await msg.reply_text("Що було знайдено?", reply_markup=ReplyKeyboardRemove())
        return

    if status == "what":
        user_data[user_id]["history"].append("what")
        user_data[user_id]["what"] = text
        user_data[user_id]["status"] = "ask_description"
        await msg.reply_text("Додати опис?", reply_markup=yes_no())
        return

    if status == "ask_description":
        user_data[user_id]["history"].append("ask_description")
        if text == "Так":
            user_data[user_id]["status"] = "description"
            await msg.reply_text("Напишіть опис:", reply_markup=ReplyKeyboardRemove())
        else:
            user_data[user_id]["description"] = None
            user_data[user_id]["status"] = "ask_photo"
            await msg.reply_text("Додати фото?", reply_markup=yes_no())
        return

    if status == "description":
        user_data[user_id]["history"].append("description")
        user_data[user_id]["description"] = text
        user_data[user_id]["status"] = "ask_photo"
        await msg.reply_text("Додати фото?", reply_markup=yes_no())
        return

    if status == "ask_photo":
        user_data[user_id]["history"].append("ask_photo")
        if text == "Так":
            user_data[user_id]["status"] = "photo"
            await msg.reply_text("Надішліть фото", reply_markup=ReplyKeyboardRemove())
        else:
            user_data[user_id]["photo"] = None
            user_data[user_id]["status"] = "ask_contact"
            await msg.reply_text("Додати контакт?", reply_markup=yes_no())
        return


    if status == "photo":
        if msg.photo:
            user_data[user_id]["photo"] = msg.photo[-1].file_id
        user_data[user_id]["history"].append("photo")
        user_data[user_id]["status"] = "ask_contact"
        await msg.reply_text("Додати контакт?", reply_markup=yes_no())
        return


    if status == "ask_contact":
        user_data[user_id]["history"].append("ask_contact")
        if text == "Так":
            user_data[user_id]["status"] = "contact"
            await msg.reply_text("Введіть контакт:", reply_markup=ReplyKeyboardRemove())
        else:
            user_data[user_id]["contact"] = None
            user_data[user_id]["status"] = "preview"
        return


    if status == "contact":
        user_data[user_id]["history"].append("contact")
        user_data[user_id]["contact"] = text
        user_data[user_id]["status"] = "preview"

    # PREVIEW
    if user_data[user_id]["status"] == "preview":

        ans = user_data[user_id]
        preview = ""

        if ans["where"]: preview += f"Де знайдено: {ans['where']}\n"
        if ans["what"]: preview += f"Що знайдено: {ans['what']}\n"
        if ans["description"]: preview += f"Опис: {ans['description']}\n"
        if ans["contact"]: preview += f"Контакт: {ans['contact']}\n"

        if ans["photo"]:
            await msg.reply_photo(ans["photo"], caption=preview)
        else:
            await msg.reply_text(preview)

        user_data[user_id]["status"] = "preview_menu"
        await msg.reply_text("Готово. Надіслати на модерацію?", reply_markup=pr_button())
        return

    # START OVER
    if text == "Почати спочатку":
        for key in ["where", "what", "description", "photo", "contact"]:
            user_data[user_id][key] = None
        user_data[user_id]["history"] = []
        user_data[user_id]["status"] = "where"

        await msg.reply_text("Де була знайдена річ?", reply_markup=ReplyKeyboardRemove())
        return

    # SEND MODERATION
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

        await msg.reply_text("Надіслано модератору.", reply_markup=main_menu())
        user_data[user_id]["status"] = "menu"
        user_data[user_id]["history"] = []
        return

    await msg.reply_text("Я не розумію цю дію.")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle))

app.run_polling()
