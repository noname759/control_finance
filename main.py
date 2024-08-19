import json
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    if not os.path.exists(f"{user_id}.json"):
        with open(f"{user_id}.json", "w") as file:
            json.dump({"transactions": [], "settings": {}}, file)
    update.message.reply_text("Добро пожаловать в бот для контроля личных финансов! Чтобы начать, используйте команду /start.")

def add_transaction(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    update.message.reply_text("Введите транзакцию в формате: <сумма> <категория> <дата (YYYY-MM-DD)>\nПример: 100 еда 2024-08-18")
    context.user_data['adding_transaction'] = True

def handle_add_transaction(update: Update, context: CallbackContext) -> None:
    if 'adding_transaction' in context.user_data and context.user_data['adding_transaction']:
        user_id = str(update.message.chat_id)
        transaction_input = update.message.text
        try:
            amount, category, date_str = transaction_input.split()
            amount = float(amount)
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            transaction = f"{amount} {category} {date_str}"
            with open(f"{user_id}.json", "r") as file:
                data = json.load(file)
            data["transactions"].append(transaction)
            with open(f"{user_id}.json", "w") as file:
                json.dump(data, file)
            update.message.reply_text("Транзакция добавлена успешно!")
        except (ValueError, IndexError):
            update.message.reply_text("Неверный формат. Пожалуйста, используйте формат: <сумма> <категория> <дата (YYYY-MM-DD)>")
        context.user_data['adding_transaction'] = False

def view_transactions(update: Update, context: CallbackContext) -> None:
    keyboard = [['Сегодня', 'Неделя'], ['Месяц', 'Всё время']]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите период для просмотра транзакций:", reply_markup=reply_markup)

def handle_view_period(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    period = update.message.text.lower()
    with open(f"{user_id}.json", "r") as file:
        data = json.load(file)
    transactions = data["transactions"]

    if period == "сегодня":
        today = datetime.now().date()
        filtered_transactions = [t for t in transactions if datetime.strptime(t.split()[2], "%Y-%m-%d").date() == today]
        update.message.reply_text("Транзакции за сегодня:\n" + "\n".join(filtered_transactions))
    elif period == "неделя":
        week_ago = datetime.now().date() - timedelta(days=7)
        filtered_transactions = [t for t in transactions if datetime.strptime(t.split()[2], "%Y-%m-%d").date() >= week_ago]
        update.message.reply_text("Транзакции за последнюю неделю:\n" + "\n".join(filtered_transactions))
    elif period == "месяц":
        month_ago = datetime.now().date() - timedelta(days=30)
        filtered_transactions = [t for t in transactions if datetime.strptime(t.split()[2], "%Y-%m-%d").date() >= month_ago]
        update.message.reply_text("Транзакции за последний месяц:\n" + "\n".join(filtered_transactions))
    elif period == "всё время":
        update.message.reply_text("Транзакции за всё время:\n" + "\n".join(transactions))
    else:
        update.message.reply_text("Неверный период.")

def analyze_expenses(update: Update, context: CallbackContext) -> None:
    keyboard = [['По категориям', 'По датам'], ['Общий отчет']]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите тип отчета:", reply_markup=reply_markup)

def handle_analysis_type(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    report_type = update.message.text.lower()
    with open(f"{user_id}.json", "r") as file:
        data = json.load(file)
    transactions = data["transactions"]

    if report_type == "по категориям":
        categories = {}
        for transaction in transactions:
            parts = transaction.split()
            category = parts[1]
            amount = float(parts[0])
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount
        report = "\n".join([f"{category.capitalize()}: {amount}" for category, amount in categories.items()])
        update.message.reply_text("Расходы по категориям:\n" + report)
    elif report_type == "по датам":
        dates = {}
        for transaction in transactions:
            parts = transaction.split()
            date = parts[2]
            amount = float(parts[0])
            if date in dates:
                dates[date] += amount
            else:
                dates[date] = amount
        report = "\n".join([f"{date}: {amount}" for date, amount in dates.items()])
        update.message.reply_text("Расходы по датам:\n" + report)
    elif report_type == "общий отчет":
        total_month = 0
        total_year = 0
        now = datetime.now()
        for transaction in transactions:
            parts = transaction.split()
            date = datetime.strptime(parts[2], "%Y-%m-%d")
            amount = float(parts[0])
            if date.year == now.year:
                total_year += amount
                if date.month == now.month:
                    total_month += amount
        update.message.reply_text(f"Общие расходы:\nЗа месяц: {total_month}\nЗа год: {total_year}")
    else:
        update.message.reply_text("Неверный тип отчета.")

def settings(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    keyboard = [['USD', 'EUR', 'RUB'], ['Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите валюту:", reply_markup=reply_markup)

def handle_settings(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    selected_currency = update.message.text
    with open(f"{user_id}.json", "r") as file:
        data = json.load(file)
    data["settings"]["currency"] = selected_currency
    with open(f"{user_id}.json", "w") as file:
        json.dump(data, file)
    update.message.reply_text(f"Валюта успешно изменена на {selected_currency}!")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Доступные команды:\n- /start - Запуск бота\n"
                              "- /add - Добавление транзакций\n- /view - Просмотр транзакций\n"
                              "- /status - Анализ расходов\n- /settings - Настройки\n- /help - Справка")

def main() -> None:
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_transaction))
    dispatcher.add_handler(CommandHandler("view", view_transactions))
    dispatcher.add_handler(CommandHandler("status", analyze_expenses))
    dispatcher.add_handler(CommandHandler("settings", settings))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_add_transaction))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_view_period))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_analysis_type))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_settings))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
