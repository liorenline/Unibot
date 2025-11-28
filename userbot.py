from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8421493534:AAFZtFHyqCM1v-8yHhoIG2elAC1HQZgA44A"

user_data = {}

def main_menu():
    return ReplyKeyboardMarkup(
        [["Повідомити знахідку"], ["Техпідтримка"], ["Наші соцмережі"]],
        resize_keyboard=True
    )

def yes_no():
    return ReplyKeyboardMarkup(
        [["Так", "Ні"]],
        resize_keyboard=True
    )

def pr_button():
    return ReplyKeyboardMarkup(
        [["Відправити на модерацію", "Почати спочатку"]],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    user_data[user_id] = {
        "status": "menu",
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

    status = user_data[user_id]["status"]

    if status == "menu" and text == "Повідомити знахідку":
        user_data[user_id]["status"] = "where"
        await update.message.reply_text("Де була знайдена річ?")
        return

    if status == "menu" and text == "Техпідтримка":
        await update.message.reply_text("Звертайтесь до @Ivan_na_d")
        return

    if status == "menu" and text == "Наші соцмережі":
        await update.message.reply_text("Наші соцмережі: ...")
        return

    if status == "where":
        user_data[user_id]["where"] = text
        user_data[user_id]["status"] = "what"
        await update.message.reply_text("Що було знайдено?")
        return

    if status == "what":
        user_data[user_id]["what"] = text
        user_data[user_id]["status"] = "ask_description"
        await update.message.reply_text("Додати опис?", reply_markup=yes_no())
        return

    if status == "ask_description":
        if text == "Так":
            user_data[user_id]["status"] = "description"
            await update.message.reply_text("Напишіть опис:")
            return
        else:
            user_data[user_id]["description"] = None
            user_data[user_id]["status"] = "ask_photo"
            await update.message.reply_text("Додати фото?", reply_markup=yes_no())
            return

    if status == "description":
        user_data[user_id]["description"] = text
        user_data[user_id]["status"] = "ask_photo"
        await update.message.reply_text("Додати фото?", reply_markup=yes_no())
        return

    if status == "ask_photo":
        if text == "Так":
            user_data[user_id]["status"] = "photo"
            await update.message.reply_text("Надішліть фото.")
            return
        else:
            user_data[user_id]["photo"] = None
            user_data[user_id]["status"] = "ask_contact"
            await update.message.reply_text("Додати контакт?", reply_markup=yes_no())
            return

    if status == "photo":
        if update.message.photo:
            user_data[user_id]["photo"] = update.message.photo[-1].file_id
        user_data[user_id]["status"] = "ask_contact"
        await update.message.reply_text("Додати контакт?", reply_markup=yes_no())
        return

    if status == "ask_contact":
        if text == "Так":
            user_data[user_id]["status"] = "contact"
            await update.message.reply_text("Введіть контакт:")
            return
        else:
            user_data[user_id]["contact"] = None
            user_data[user_id]["status"] = "preview"

    if status == "contact":
        user_data[user_id]["contact"] = text
        user_data[user_id]["status"] = "preview"

    if user_data[user_id]["status"] == "preview":
        ans = user_data[user_id]

        preview = ""
        if ans["where"]:
            preview += f"Де знайдено: {ans['where']}\n"
        if ans["what"]:
            preview += f"Що знайдено: {ans['what']}\n"
        if ans["description"]:
            preview += f"Опис: {ans['description']}\n"
        if ans["contact"]:
            preview += f"Контакт: {ans['contact']}\n"

        if ans["photo"]:
            await update.message.reply_photo(ans["photo"], caption=preview)
        else:
            await update.message.reply_text(preview)

        user_data[user_id]["status"] = "menu"
        await update.message.reply_text("Готово. Чи бажаєте відправити на модерацію?.", reply_markup=pr_button())
        return

    await update.message.reply_text("Я не розумію цю дію.")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle))
app.run_polling()
