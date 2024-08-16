from telegram.ext import Updater, CommandHandler

TOKEN = '7380800891:AAE9okJyeQ-44fiO3atlO7QmSUjYqpPydQ0'

tasks = {}

def start(update, context):
    user_id = update.message.from_user.id
    if user_id not in tasks:
        tasks[user_id] = []
    message = ('Добро пожаловать!\n'
               '\n\n Для получения информации введите /help')
    update.message.reply_text(message)

def add(update, context):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        if user_id not in tasks:
            tasks[user_id] = []
        tasks[user_id].append(task_name)
        update.message.reply_text(f'Задача "{task_name}" добавлена.')
        list(update, context)
    else:
        update.message.reply_text('Укажите /add <название задачи>.')
    
def list(update, context):
    user_id = update.message.from_user.id
    if user_id in tasks and tasks[user_id]:
        task_list = ""
        for i in range(len(tasks[user_id])):
            task_list += f"{i+1}. {tasks[user_id][i]}\n"
        update.message.reply_text(f'Ваши задачи:\n{task_list}')
    else:
        update.message.reply_text('У вас нет задач.')

def edit(update, context):
    user_id = update.message.from_user.id
    try:
        task_number = int(context.args[0]) - 1  
        new_name = ' '.join(context.args[1:])
        if 0 <= task_number < len(tasks[user_id]) and new_name:
            old_task = tasks[user_id][task_number]
            tasks[user_id][task_number] = new_name
            update.message.reply_text(f'Задача обновлена на "{new_name}".')
            list(update, context)
        else:
            update.message.reply_text('Пожалуйста, укажите правильный номер задачи и новое название.')
    except (IndexError, ValueError):
        update.message.reply_text('Укажите /edit <номер> и <название>')

def delete(update, context):
    user_id = update.message.from_user.id
    try:
        task_number = int(context.args[0]) - 1 
        if 0 <= task_number < len(tasks[user_id]):
            removed_task = tasks[user_id].pop(task_number)  
            update.message.reply_text(f'Задача "{removed_task}" удалена.')
            list(update, context) 
        else:
            update.message.reply_text('Пожалуйста, укажите правильный номер задачи.')
    except (IndexError, ValueError):
        update.message.reply_text('Укажите /delete <номер задачи>')

def help(update, context):
    update.message.reply_text(
       "/start - Начать взаимодействие с ботом\n"
        "/add <название задачи> - Добавить новую задачу\n"
        "/list - Просмотреть все задачи\n"
        "/delete <номер задачи> - Удалить задачу\n"
        "/edit <номер задачи> <новое название> - Редактировать задачу\n"
        "/help - Показать список команд"
        )

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('add', add))
    dispatcher.add_handler(CommandHandler('list', list))
    dispatcher.add_handler(CommandHandler('delete', delete))
    dispatcher.add_handler(CommandHandler('edit', edit))
    dispatcher.add_handler(CommandHandler('help', help))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
