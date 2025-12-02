from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = 
MOD_CHAT = 

user_data = {}
MAX_LENGTH = 2000

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
        await update.message.reply_text("Опишіть де була знайдена річ. Якщо знайдено в аудиторії, то перевірте і напишіть номер, або хоча б розташування.", reply_markup=ReplyKeyboardRemove())
    elif status == "what":
        await update.message.reply_text("Назвіть що було знайдено. Зразок: гаманець, шапка, зошит.", reply_markup=ReplyKeyboardRemove())
    elif status == "ask_description":
        await update.message.reply_text("Ви хочете додати опис? \nОберіть кнопкою знизу", reply_markup=yes_no())
    elif status == "description":
        await update.message.reply_text("Напишіть опис. \n Постарайтесь детально описати. \nЯкщо це цінна річ, прибережіть пару фактів для питань до власника щоб переконатись чи це справжній власник.", reply_markup=ReplyKeyboardRemove())
    elif status == "ask_photo":
        await update.message.reply_text("Ви хочете додати фото знахідки? \nОберіть кнопкою знизу.", reply_markup=yes_no())
    elif status == "photo":
        await update.message.reply_text("Надішліть фото сюди.", reply_markup=ReplyKeyboardRemove())
    elif status == "ask_contact":
        await update.message.reply_text("Чи додавати ваш контакт(telegram user) до оголошення про знахідку? \nОберіть кнопкою знизу", reply_markup=yes_no())
    elif status == "support":
        await update.message.reply_text("Опишіть вашу проблему, це буде надіслано в техпідтримку:", reply_markup=ReplyKeyboardRemove())

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

    await update.message.reply_text("Добрий день. Вітаю вас в телеграм-боті для розшуку речей. Велике дякую за допомогу колегам більш розсіяним за вас). Надалі можете обирати дії:", reply_markup=main_menu())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("Натисніть /start")
        return

    if not update.message or not update.message.text:
        if user_data[user_id]["status"] == "photo":
            pass
        else:
            await update.message.reply_text("Будь ласка, надішліть текстове повідомлення.")
            return
    else:
        if len(text) > MAX_LENGTH:
            await update.message.reply_text(
                f"Ваше повідомлення занадто велике ({len(text)} символів). Максимум {MAX_LENGTH}."
            )
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
        "ask_contact": ["Так", "Ні", "Назад"],
        "preview_menu": ["Відправити на модерацію", "Почати спочатку", "Головне меню"]
    }

    if status in buttons_only and text not in buttons_only[status]:
        await update.message.reply_text("Натисніть кнопку.")
        await send_question_for_status(update, user_id)
        return

    if status == "menu" and text == "Повідомити знахідку":
        user_data[user_id]["history"].append("menu")
        user_data[user_id]["status"] = "where"
        await update.message.reply_text("Опишіть де була знайдена річ. Якщо знайдено в аудиторії, то перевірте і напишіть номер, або хоча б розташування.", reply_markup=ReplyKeyboardRemove())
        return

    if status == "menu" and text == "Техпідтримка":
        user_data[user_id]["status"] = "support"
        await update.message.reply_text("Опишіть вашу проблему, це буде надіслано в техпідтримку:", reply_markup=ReplyKeyboardRemove())
        return

    if status == "support":
        username = update.message.from_user.username
        uid = update.message.from_user.id
        user_text = update.message.text

        msg = (
            f"📩 Техпідтримка\n"
            f"Від: @{username if username else uid}\n\n"
            f"Повідомлення:\n{user_text}"
        )

        await context.bot.send_message(chat_id=MOD_CHAT, text=msg)

        user_data[user_id]["status"] = "menu"
        await update.message.reply_text("Ваше звернення передано модераторам. Дякуємо :) ", reply_markup=main_menu())
        return

    if status == "menu" and text == "Наші соцмережі":
        message = (
            "Бота розроблено Профбюро студентів Факультету прикладної математики та інформатики\n\n"
            "📌 <b>Канал втрачених речей:</b> <a href=\"https://t.me/+T7nmFgVuGn8wN2Yy\">перейти</a>\n"
            "📌 <b>Телеграм профбюро:</b> <a href=\"https://t.me/ami_profburo\">AMI Profburo</a>\n"
            "📌 <b>Instagram профбюро:</b> <a href=\"https://www.instagram.com/ami_profburo?igsh=MWdwaXg4dGdrNTQ1NA==\">@ami_profburo</a>\n"
            "📌 <b>Linktree:</b> <a href=\"https://linktr.ee/ami.profburo.lnu\">AMI Profburo</a>\n\n"
        )
        await update.message.reply_text(message, parse_mode="HTML")
        return

    if status == "where":
        user_data[user_id]["history"].append("where")
        user_data[user_id]["where"] = text
        user_data[user_id]["status"] = "what"
        await update.message.reply_text("Назвіть що було знайдено. Зразок: гаманець, шапка, зошит.", reply_markup=ReplyKeyboardRemove())
        return

    if status == "what":
        user_data[user_id]["history"].append("what")
        user_data[user_id]["what"] = text
        user_data[user_id]["status"] = "ask_description"
        await update.message.reply_text("Ви хочете додати опис? \nОберіть кнопкою знизу.", reply_markup=yes_no())
        return

    if status == "ask_description":
        user_data[user_id]["history"].append("ask_description")
        if text == "Так":
            user_data[user_id]["status"] = "description"
            await update.message.reply_text("Напишіть опис. \nПостарайтесь детально описати. \nЯкщо це цінна річ, прибережіть пару фактів для питань до власника щоб переконатись чи це справжній власник.", reply_markup=ReplyKeyboardRemove())
            return
        else:
            user_data[user_id]["description"] = None
            user_data[user_id]["status"] = "ask_photo"
            await update.message.reply_text("Ви хочете додати фото знахідки? \nОберіть кнопкою знизу.", reply_markup=yes_no())
            return

    if status == "description":
        user_data[user_id]["history"].append("description")
        user_data[user_id]["description"] = text
        user_data[user_id]["status"] = "ask_photo"
        await update.message.reply_text("Ви хочете додати фото знахідки? \nОберіть кнопкою знизу.", reply_markup=yes_no())
        return

    if status == "ask_photo":
        user_data[user_id]["history"].append("ask_photo")
        if text == "Так":
            user_data[user_id]["status"] = "photo"
            await update.message.reply_text("Надішліть фото сюди.", reply_markup=ReplyKeyboardRemove())
            return
        else:
            user_data[user_id]["photo"] = None
            user_data[user_id]["status"] = "ask_contact"
            await update.message.reply_text("Чи додавати ваш контакт(telegram user) до оголошення про знахідку? \nОберіть кнопкою знизу.", reply_markup=yes_no())
            return

    if status == "photo":
        user_data[user_id]["history"].append("photo")
        if not update.message.photo:
            await update.message.reply_text("На жаль, виникла якась помилка. \nЯ не зміг розпізнати фото. Вишліть, будь ласка, ще раз фото:)")
            return

        user_data[user_id]["photo"] = update.message.photo[-1].file_id
        user_data[user_id]["status"] = "ask_contact"
        await update.message.reply_text("Чи додавати ваш контакт(telegram user) до оголошення про знахідку? \nОберіть кнопкою знизу", reply_markup=yes_no())
        return

    if status == "ask_contact":
        user_data[user_id]["history"].append("ask_contact")

        if text == "Так":
            user = update.message.from_user
            user_data[user_id]["contact"] = f"@{user.username}" if user.username else f"ID: {user.id}"
        else:
            user_data[user_id]["contact"] = "Не вказано"

        user_data[user_id]["status"] = "preview"

        ans = user_data[user_id]
        preview = ""
        if ans["where"]: preview += f"Де знайдено: {ans['where']}\n"
        if ans["what"]: preview += f"Що знайдено: {ans['what']}\n"
        if ans["description"]: preview += f"Опис: {ans['description']}\n"
        preview += f"Контакт: {ans['contact']}\n"

        if ans["photo"]:
            await update.message.reply_photo(ans["photo"], caption=preview)
        else:
            await update.message.reply_text(preview)

        user_data[user_id]["status"] = "preview_menu"
        await update.message.reply_text("Готово. Бажаєте відправити на модерацію, чи ви помітили помилку і хочете почати спочатку? \nОберіть кнопкою знизу.", reply_markup=pr_button())
        return

    if user_data[user_id]["status"] == "preview_menu":

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
            await update.message.reply_text("Добрий день. Вітаю вас в телеграм-боті для розшуку речей. Велике дякую за допомогу колегам більш розсіяним за вас). Надалі можете обирати дії:", reply_markup=main_menu())
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

            await update.message.reply_text("Надіслано модератору. Через деякий час це повідомлення появиться в чаті знахідок. Надалі можете обирати дії:", reply_markup=main_menu())
            return

    await update.message.reply_text("Я не розумію цю дію.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle))
app.run_polling()
