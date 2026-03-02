import os
import logging
import json
from datetime import datetime, timedelta
import calendar
from dotenv import load_dotenv
import telebot
from telebot import types
import random
import string
import pytz
import threading
import time

# Настройка временной зоны
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
load_dotenv("info.env")

bot_token = os.getenv("BOT_TOKEN")
print(f"Загруженный токен: {bot_token}")  # Отладочный вывод

if not bot_token:
    raise ValueError("Токен бота не найден. Проверьте файл info.env.")

# Инициализируем бота
bot = telebot.TeleBot(bot_token)

# Константы
TASK_STATUS = [" ", "✓", "✗"]
DATA_FILE = "tasks_data.json"
MONTH_NAMES = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]
WEEKDAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


# Загрузка данных
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
    return {
        'user_tasks': {},
        'groups': {},
        'user_groups': {},
        'message_ids': {},
        'user_names': {}
    }


# Сохранение данных
def save_data():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'user_tasks': user_tasks,
                'groups': groups,
                'user_groups': user_groups,
                'message_ids': message_ids,
                'user_names': user_names
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")


# Инициализация данных
data = load_data()
user_tasks = data.get('user_tasks', {})
groups = data.get('groups', {})
user_groups = data.get('user_groups', {})
message_ids = data.get('message_ids', {})
user_names = data.get('user_names', {})


def generate_task_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def russian_date_format(date: datetime.date) -> str:
    return f"{date.day} {MONTH_NAMES[date.month - 1]} {WEEKDAY_NAMES[date.weekday()]}"


def get_moscow_time():
    return datetime.now(MOSCOW_TZ)


def safe_delete_message(chat_id, message_id):
    try:
        if message_id:
            bot.delete_message(chat_id, message_id)
    except telebot.apihelper.ApiTelegramException as e:
        if "message to delete not found" not in str(e):
            logger.error(f"Ошибка удаления сообщения: {e}")


def safe_edit_message(chat_id, message_id, text, reply_markup=None, parse_mode=None):
    try:
        if message_id:
            return bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" in str(e):
            return None
        if "message to edit not found" not in str(e):
            logger.error(f"Ошибка редактирования сообщения: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при редактировании сообщения: {e}")
    return None


def transfer_uncompleted_tasks():
    try:
        today = datetime.now(MOSCOW_TZ).date()
        logger.info(f"Проверка переноса задач на {today}")

        for user_id in list(user_tasks.keys()):
            # Пропускаем ботов
            if user_id.startswith('bot_'):
                continue

            # Собираем все невыполненные задачи из прошлого
            tasks_to_transfer = []
            dates_to_delete = []

            for date_str in list(user_tasks[user_id].keys()):
                try:
                    task_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if task_date >= today:
                        continue

                    for task in user_tasks[user_id][date_str]:
                        if task['status'] == 0:  # Невыполненная задача
                            # Добавляем пометку о переносе
                            transferred_task = task.copy()
                            transferred_task['transferred_from'] = date_str
                            tasks_to_transfer.append(transferred_task)
                            dates_to_delete.append((date_str, task['id']))
                except Exception as e:
                    logger.error(f"Ошибка обработки даты {date_str}: {e}")

            # Переносим задачи на сегодня
            if tasks_to_transfer:
                today_str = today.strftime("%Y-%m-%d")
                if today_str not in user_tasks[user_id]:
                    user_tasks[user_id][today_str] = []

                for task in tasks_to_transfer:
                    # Проверяем, нет ли уже такой задачи сегодня
                    if not any(t['id'] == task['id'] for t in user_tasks[user_id][today_str]):
                        user_tasks[user_id][today_str].append(task)

                # Удаляем перенесенные задачи из старых дат
                for date_str, task_id in dates_to_delete:
                    if date_str in user_tasks[user_id]:
                        user_tasks[user_id][date_str] = [t for t in user_tasks[user_id][date_str] if t['id'] != task_id]
                        if not user_tasks[user_id][date_str]:
                            del user_tasks[user_id][date_str]

            # Обновляем интерфейс пользователя, если он активен
            if user_id in message_ids:
                try:
                    show_day(int(user_id), today, message_ids[user_id])
                except Exception as e:
                    logger.error(f"Ошибка обновления интерфейса для пользователя {user_id}: {e}")

        save_data()
        logger.info("Перенос задач завершен")
    except Exception as e:
        logger.error(f"Ошибка при переносе задач: {e}")


def schedule_task_transfer():
    while True:
        try:
            now = datetime.now(MOSCOW_TZ)
            # Запускаем перенос в начале каждого часа
            if now.minute == 0:
                transfer_uncompleted_tasks()
            # Ждем 1 минуту перед следующей проверкой
            time.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка в планировщике переноса задач: {e}")
            time.sleep(60)


# Запускаем фоновый поток для переноса задач
transfer_thread = threading.Thread(target=schedule_task_transfer, daemon=True)
transfer_thread.start()


def get_tasks_for_user(user_id: str, date: datetime.date) -> list:
    date_str = date.strftime("%Y-%m-%d")
    tasks = []

    # Добавляем задачи текущего пользователя
    if user_id in user_tasks and date_str in user_tasks[user_id]:
        for task in user_tasks[user_id][date_str]:
            task_with_owner = task.copy()
            task_with_owner['owner_name'] = user_names.get(user_id, f"")
            tasks.append(task_with_owner)

    # Добавляем задачи всех участников группы
    if user_id in user_groups:
        group_id = user_groups[user_id]
        for member_id in groups.get(group_id, {}).get('members', []):
            member_id = str(member_id)
            if member_id != user_id and member_id in user_tasks and date_str in user_tasks[member_id]:
                for task in user_tasks[member_id][date_str]:
                    task_with_owner = task.copy()
                    task_with_owner['owner_name'] = user_names.get(member_id, f"")
                    tasks.append(task_with_owner)

    return sorted(tasks, key=lambda x: (x['status'], x.get('order', 0)))


def update_group_tasks(group_id: str, date: datetime.date):
    if group_id not in groups:
        return

    for user_id in groups[group_id]['members']:
        user_id = str(user_id)
        if user_id in message_ids and not user_id.startswith('bot_'):
            show_day(int(user_id), date, message_ids[user_id])
    save_data()


def cleanup_user_messages(chat_id: int, user_id: str, keep_main_message=False):
    try:
        if user_id in message_ids:
            if keep_main_message:
                # Удаляем все сообщения, кроме главного
                for msg_id in list(message_ids.values()):
                    if msg_id != message_ids[user_id]:
                        safe_delete_message(chat_id, msg_id)
            else:
                # Удаляем все сообщения
                for msg_id in list(message_ids.values()):
                    safe_delete_message(chat_id, msg_id)
                message_ids.clear()
    except Exception as e:
        logger.error(f"Ошибка очистки сообщений: {e}")


def generate_day_markup(user_id: str, date: datetime.date, tasks: list) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()

    # Кнопки задач
    for i, task in enumerate(tasks, 1):
        btn_text = f"{i}. [{TASK_STATUS[task['status']]}] {task['text'][:15]}"
        if len(task['text']) > 15:
            btn_text += "..."

        # Все участники группы могут взаимодействовать с задачами
        callback_data = f"task_{date}_{task['id']}"

        row_buttons = [
            types.InlineKeyboardButton(btn_text, callback_data=callback_data),
            types.InlineKeyboardButton("✏️", callback_data=f"edit_{date}_{task['id']}"),
            types.InlineKeyboardButton("🗑️", callback_data=f"delete_{date}_{task['id']}")
        ]

        markup.row(*row_buttons)

    # Кнопки навигации
    prev_date = date - timedelta(days=1)
    next_date = date + timedelta(days=1)
    markup.row(
        types.InlineKeyboardButton(f"← {prev_date.day}", callback_data=f"day_{prev_date}"),
        types.InlineKeyboardButton("Сегодня", callback_data="day_today"),
        types.InlineKeyboardButton(f"{next_date.day} →", callback_data=f"day_{next_date}")
    )

    # Основные кнопки
    markup.row(
        types.InlineKeyboardButton("✏ Добавить задачу", callback_data=f"add_{date}"),
        types.InlineKeyboardButton("📅 Календарь", callback_data=f"calendar_{date.strftime('%Y-%m')}")
    )

    # Кнопка управления группой для владельца
    if user_id in user_groups and groups[user_groups[user_id]]['owner'] == user_id:
        markup.row(types.InlineKeyboardButton("👥 Управление группой", callback_data="group_manage"))

    # Кнопка перезапуска
    markup.row(types.InlineKeyboardButton("🔄 Перезапустить бота", callback_data="confirm_restart"))

    return markup


def show_day(chat_id: int, date: datetime.date, message_id: int = None):
    user_id = str(chat_id)
    tasks = get_tasks_for_user(user_id, date)

    # Формируем текст сообщения
    text = ""

    # Добавляем информацию о группе перед датой
    if user_id in user_groups:
        group = groups[user_groups[user_id]]
        text += f"Группа: {group['code']} (участников: {len(group['members'])})\n"

    text += f"*{russian_date_format(date)}*\n\n"

    text += "Нет задач на этот день.\n" if not tasks else ""

    for i, task in enumerate(tasks, 1):
        status = TASK_STATUS[task['status']]

        # Информация о переносе
        transferred_note = ""
        if 'transferred_from' in task:
            transferred_date = datetime.strptime(task['transferred_from'], "%Y-%m-%d").date()
            transferred_note = f" (перенесена с {transferred_date.strftime('%d.%m')})"

        # Информация о создании
        created_date = datetime.strptime(task['created_date'], "%Y-%m-%d").date()
        date_note = f" (с {created_date.strftime('%d.%m')})" if created_date != date and 'transferred_from' not in task else ""

        # Информация о выполнении
        completed_by = f" @{task['completed_by']}" if task.get('completed_by') else ""

        # Информация о владельце
        owner_note = ""
        if 'owner_name' in task and task['owner_name'] != user_names.get(user_id, ""):
            owner_note = f" [{task['owner_name']}]"

        text += f"{i}. [{status}]{owner_note} {task['text']}{transferred_note}{date_note}{completed_by}\n"

    markup = generate_day_markup(user_id, date, tasks)

    try:
        if message_id:
            msg = safe_edit_message(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            if msg:
                message_ids[user_id] = msg.message_id
        else:
            cleanup_user_messages(chat_id, user_id)
            msg = bot.send_message(
                chat_id,
                text,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            message_ids[user_id] = msg.message_id
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        bot.send_message(chat_id, "Произошла ошибка при отображении задач")


def show_calendar(chat_id: int, month_str: str, message_id: int = None):
    try:
        year, month = map(int, month_str.split('-'))
        user_id = str(chat_id)
        today = datetime.now().date()

        markup = types.InlineKeyboardMarkup()

        # Заголовок с месяцем и годом
        markup.row(types.InlineKeyboardButton(
            f"{MONTH_NAMES[month - 1]} {year}",
            callback_data="ignore"
        ))

        # Дни недели
        week_days = []
        for day in WEEKDAY_NAMES:
            week_days.append(types.InlineKeyboardButton(day, callback_data="ignore"))
        markup.row(*week_days)

        # Даты календаря
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            week_buttons = []
            for day in week:
                if day == 0:
                    week_buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
                else:
                    date = datetime(year, month, day).date()
                    tasks = get_tasks_for_user(user_id, date)
                    has_tasks = len(tasks) > 0
                    has_uncompleted = any(task['status'] == 0 for task in tasks)

                    # Определяем эмодзи для дня
                    if date == today:
                        emoji = "⭐"  # Сегодняшний день
                    elif has_uncompleted:
                        emoji = "🔴"  # Есть незавершенные задачи
                    elif has_tasks:
                        emoji = "🟢"  # Все задачи завершены
                    else:
                        emoji = "⚪"  # Нет задач

                    week_buttons.append(types.InlineKeyboardButton(
                        f"{emoji}{day}",
                        callback_data=f"day_{date}"
                    ))
            markup.row(*week_buttons)

        # Навигация по месяцам
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        markup.row(
            types.InlineKeyboardButton(
                "← Пред",
                callback_data=f"calendar_{prev_year}-{prev_month}"
            ),
            types.InlineKeyboardButton(
                "Сегодня",
                callback_data="day_today"
            ),
            types.InlineKeyboardButton(
                "След →",
                callback_data=f"calendar_{next_year}-{next_month}"
            )
        )

        markup.row(types.InlineKeyboardButton("Назад", callback_data="day_today"))

        if message_id:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Выберите дату:",
                reply_markup=markup
            )
        else:
            cleanup_user_messages(chat_id, user_id, keep_main_message=True)
            msg = bot.send_message(
                chat_id,
                "Выберите дату:",
                reply_markup=markup
            )
            message_ids[user_id] = msg.message_id
    except Exception as e:
        logger.error(f"Ошибка при отображении календаря: {e}")
        bot.send_message(chat_id, "Произошла ошибка при отображении календаря")


def handle_task(call):
    try:
        _, date_str, task_id = call.data.split('_')
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        user_id = str(call.from_user.id)
        date_str = date.strftime("%Y-%m-%d")

        # Находим задачу среди всех задач группы
        task = None
        owner_id = None

        # Сначала проверяем свои задачи
        if user_id in user_tasks and date_str in user_tasks[user_id]:
            for t in user_tasks[user_id][date_str]:
                if t['id'] == task_id:
                    task = t
                    owner_id = user_id
                    break

        # Если не нашли, проверяем задачи участников группы
        if not task and user_id in user_groups:
            group_id = user_groups[user_id]
            for member_id in groups[group_id]['members']:
                member_id = str(member_id)
                if member_id in user_tasks and date_str in user_tasks[member_id]:
                    for t in user_tasks[member_id][date_str]:
                        if t['id'] == task_id:
                            task = t
                            owner_id = member_id
                            break
                if task:
                    break

        if task and owner_id:
            # Переключаем статус
            task['status'] = (task['status'] + 1) % 3
            if task['status'] == 1:  # Если задача выполнена
                task['completed_by'] = call.from_user.username or str(call.from_user.id)
            elif task['status'] == 0:  # Если задача снова не выполнена
                task.pop('completed_by', None)

            # Сохраняем изменения у владельца задачи
            if owner_id in user_tasks and date_str in user_tasks[owner_id]:
                for i, t in enumerate(user_tasks[owner_id][date_str]):
                    if t['id'] == task_id:
                        user_tasks[owner_id][date_str][i] = task
                        break

            save_data()

            if user_id in user_groups:
                update_group_tasks(user_groups[user_id], date)
            else:
                show_day(call.message.chat.id, date, call.message.message_id)

            bot.answer_callback_query(call.id, "Статус задачи обновлен")
        else:
            bot.answer_callback_query(call.id, "Задача не найдена")
    except Exception as e:
        logger.error(f"Ошибка обработки задачи: {e}")
        bot.answer_callback_query(call.id, "Ошибка при обновлении задачи")


def add_task(call):
    try:
        _, date_str = call.data.split('_')
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        user_id = str(call.from_user.id)

        # Удаляем все сообщения, кроме главного
        cleanup_user_messages(call.message.chat.id, user_id, keep_main_message=True)

        msg = bot.send_message(
            call.message.chat.id,
            f"Введите текст задачи на {russian_date_format(date)}:",
            reply_markup=types.ForceReply()
        )

        # Сохраняем ID сообщения с запросом, чтобы потом удалить
        temp_msg_id = msg.message_id
        message_ids[f"{user_id}_temp"] = temp_msg_id

        bot.register_next_step_handler(msg, lambda m: process_task_text(m, date, temp_msg_id))
    except Exception as e:
        logger.error(f"Ошибка при добавлении задачи: {e}")
        bot.answer_callback_query(call.id, "Ошибка при добавлении задачи")


def process_task_text(message, date, temp_msg_id):
    try:
        user_id = str(message.from_user.id)
        date_str = date.strftime("%Y-%m-%d")

        # Удаляем сообщение с вводом текста и запросом
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, temp_msg_id)
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения: {e}")

        # Удаляем временный ID сообщения
        if f"{user_id}_temp" in message_ids:
            del message_ids[f"{user_id}_temp"]

        if user_id not in user_tasks:
            user_tasks[user_id] = {}
        if date_str not in user_tasks[user_id]:
            user_tasks[user_id][date_str] = []

        new_task = {
            'id': generate_task_id(),
            'text': message.text,
            'status': 0,
            'created_date': date_str,
            'order': len(user_tasks[user_id][date_str]),
            'shared': True,
            'user_name': user_names.get(user_id, str(user_id))
        }

        user_tasks[user_id][date_str].append(new_task)
        save_data()

        if user_id in user_groups:
            update_group_tasks(user_groups[user_id], date)
        else:
            show_day(message.chat.id, date)
    except Exception as e:
        logger.error(f"Ошибка при обработке текста задачи: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении задачи")


def edit_task(call):
    try:
        _, date_str, task_id = call.data.split('_')
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        user_id = str(call.from_user.id)
        date_str = date.strftime("%Y-%m-%d")

        # Находим задачу среди всех задач группы
        task = None
        owner_id = None

        # Сначала проверяем свои задачи
        if user_id in user_tasks and date_str in user_tasks[user_id]:
            for t in user_tasks[user_id][date_str]:
                if t['id'] == task_id:
                    task = t
                    owner_id = user_id
                    break

        # Если не нашли, проверяем задачи участников группы
        if not task and user_id in user_groups:
            group_id = user_groups[user_id]
            for member_id in groups[group_id]['members']:
                member_id = str(member_id)
                if member_id in user_tasks and date_str in user_tasks[member_id]:
                    for t in user_tasks[member_id][date_str]:
                        if t['id'] == task_id:
                            task = t
                            owner_id = member_id
                            break
                if task:
                    break

        if task and owner_id:
            # Удаляем все сообщения, кроме главного
            cleanup_user_messages(call.message.chat.id, user_id, keep_main_message=True)

            msg = bot.send_message(
                call.message.chat.id,
                f"Введите новый текст задачи:",
                reply_markup=types.ForceReply()
            )

            # Сохраняем информацию о задаче для обработки ввода
            edit_data = {
                'user_id': user_id,
                'date': date,
                'task_id': task_id,
                'owner_id': owner_id
            }

            # Сохраняем ID сообщения с запросом, чтобы потом удалить
            temp_msg_id = msg.message_id
            message_ids[f"{user_id}_edit_temp"] = temp_msg_id

            bot.register_next_step_handler(msg, lambda m: process_edit_task_text(m, edit_data, temp_msg_id))
        else:
            bot.answer_callback_query(call.id, "Задача не найдена")
    except Exception as e:
        logger.error(f"Ошибка при редактировании задачи: {e}")
        bot.answer_callback_query(call.id, "Ошибка при редактировании задачи")


def process_edit_task_text(message, edit_data, temp_msg_id):
    try:
        user_id = str(message.from_user.id)
        date_str = edit_data['date'].strftime("%Y-%m-%d")

        # Удаляем сообщение с вводом текста и запросом
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, temp_msg_id)
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения: {e}")

        # Удаляем временный ID сообщения
        if f"{user_id}_edit_temp" in message_ids:
            del message_ids[f"{user_id}_edit_temp"]

        # Обновляем задачу у владельца
        owner_id = edit_data['owner_id']
        if owner_id in user_tasks and date_str in user_tasks[owner_id]:
            for task in user_tasks[owner_id][date_str]:
                if task['id'] == edit_data['task_id']:
                    task['text'] = message.text
                    save_data()

                    if user_id in user_groups:
                        update_group_tasks(user_groups[user_id], edit_data['date'])
                    else:
                        show_day(message.chat.id, edit_data['date'])
                    break
    except Exception as e:
        logger.error(f"Ошибка при обработке нового текста задачи: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обновлении задачи")


def delete_task(call):
    try:
        _, date_str, task_id = call.data.split('_')
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        user_id = str(call.from_user.id)
        date_str = date.strftime("%Y-%m-%d")

        # Находим задачу среди всех задач группы
        task_found = False
        owner_id = None

        # Сначала проверяем свои задачи
        if user_id in user_tasks and date_str in user_tasks[user_id]:
            for i, task in enumerate(user_tasks[user_id][date_str]):
                if task['id'] == task_id:
                    del user_tasks[user_id][date_str][i]
                    task_found = True
                    owner_id = user_id
                    break

        # Если не нашли, проверяем задачи участников группы
        if not task_found and user_id in user_groups:
            group_id = user_groups[user_id]
            for member_id in groups[group_id]['members']:
                member_id = str(member_id)
                if member_id in user_tasks and date_str in user_tasks[member_id]:
                    for i, task in enumerate(user_tasks[member_id][date_str]):
                        if task['id'] == task_id:
                            del user_tasks[member_id][date_str][i]
                            task_found = True
                            owner_id = member_id
                            break
                if task_found:
                    break

        if task_found and owner_id:
            # Удаляем пустые даты
            if owner_id in user_tasks and date_str in user_tasks[owner_id] and not user_tasks[owner_id][date_str]:
                del user_tasks[owner_id][date_str]

            save_data()

            if user_id in user_groups:
                update_group_tasks(user_groups[user_id], date)
            else:
                show_day(call.message.chat.id, date, call.message.message_id)

            bot.answer_callback_query(call.id, "Задача удалена")
        else:
            bot.answer_callback_query(call.id, "Задача не найдена")
    except Exception as e:
        logger.error(f"Ошибка при удалении задачи: {e}")
        bot.answer_callback_query(call.id, "Ошибка при удалении задачи")


def confirm_restart(call):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Да, перезапустить", callback_data="do_restart"),
            types.InlineKeyboardButton("Отмена", callback_data="cancel_restart")
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Вы уверены, что хотите перезапустить бота? Все несохраненные данные могут быть потеряны.",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка при подтверждении перезапуска: {e}")
        bot.answer_callback_query(call.id, "Ошибка при подтверждении перезапуска")


def do_restart(call):
    try:
        user_id = str(call.from_user.id)
        cleanup_user_messages(call.message.chat.id, user_id)
        handle_start(call.message)
    except Exception as e:
        logger.error(f"Ошибка при перезапуске: {e}")
        bot.answer_callback_query(call.id, "Ошибка при перезапуске")


def cancel_restart(call):
    try:
        show_day(call.message.chat.id, datetime.now().date(), call.message.message_id)
    except Exception as e:
        logger.error(f"Ошибка при отмене перезапуска: {e}")
        bot.answer_callback_query(call.id, "Ошибка при отмене перезапуска")


def group_manage(call):
    try:
        user_id = str(call.from_user.id)
        if user_id in user_groups and groups[user_groups[user_id]]['owner'] == user_id:
            group_id = user_groups[user_id]
            group = groups[group_id]

            text = f"""
            👥 Управление группой {group['code']}
            ----------------------------
            Участников: {len(group['members'])}
            ----------------------------
            Код для подключения: <b>{group['code']}</b>
            ----------------------------
            """

            markup = types.InlineKeyboardMarkup()

            # Кнопка для удаления группы
            markup.row(types.InlineKeyboardButton("🗑️ Удалить группу", callback_data="confirm_delete_group"))

            # Кнопка для просмотра участников
            markup.row(types.InlineKeyboardButton("👥 Список участников", callback_data="show_members"))

            # Кнопка назад
            markup.row(types.InlineKeyboardButton("Назад", callback_data="day_today"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            bot.answer_callback_query(call.id, "У вас нет прав для управления группой")
    except Exception as e:
        logger.error(f"Ошибка при управлении группой: {e}")
        bot.answer_callback_query(call.id, "Ошибка при управлении группой")


@bot.callback_query_handler(func=lambda call: call.data == 'confirm_delete_group')
def confirm_delete_group(call):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Да, удалить", callback_data="do_delete_group"),
            types.InlineKeyboardButton("Отмена", callback_data="group_manage")
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Вы уверены, что хотите удалить группу? Все участники будут отключены.",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка при подтверждении удаления группы: {e}")
        bot.answer_callback_query(call.id, "Ошибка при подтверждении удаления группы")


@bot.callback_query_handler(func=lambda call: call.data == 'do_delete_group')
def do_delete_group(call):
    try:
        user_id = str(call.from_user.id)
        if user_id in user_groups and groups[user_groups[user_id]]['owner'] == user_id:
            group_id = user_groups[user_id]

            # Удаляем группу у всех участников
            for member_id in groups[group_id]['members']:
                member_id = str(member_id)
                if member_id in user_groups:
                    del user_groups[member_id]

            # Удаляем саму группу
            del groups[group_id]
            save_data()

            bot.answer_callback_query(call.id, "Группа удалена")
            handle_start(call.message)
        else:
            bot.answer_callback_query(call.id, "У вас нет прав для удаления группы")
    except Exception as e:
        logger.error(f"Ошибка при удалении группы: {e}")
        bot.answer_callback_query(call.id, "Ошибка при удалении группы")


@bot.callback_query_handler(func=lambda call: call.data == 'show_members')
def show_members(call):
    try:
        user_id = str(call.from_user.id)
        if user_id in user_groups and groups[user_groups[user_id]]['owner'] == user_id:
            group_id = user_groups[user_id]
            group = groups[group_id]

            text = f"👥 Участники группы {group['code']}:\n\n"
            for i, member_id in enumerate(group['members'], 1):
                member_id = str(member_id)
                # Получаем имя пользователя или используем "Участник [ID]" в качестве fallback
                username = user_names.get(member_id, f"Участник {member_id}")

                # Добавляем отметку владельца
                if member_id == group['owner']:
                    username += " 👑 (владелец)"

                text += f"{i}. {username}\n"

            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("Назад", callback_data="group_manage"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "У вас нет прав для просмотра участников")
    except Exception as e:
        logger.error(f"Ошибка при показе участников: {e}")
        bot.answer_callback_query(call.id, "Ошибка при показе участников")


@bot.callback_query_handler(func=lambda call: call.data in ['create_group', 'join_group'])
def handle_group_actions(call):
    try:
        if call.data == 'create_group':
            create_group(call)
        else:
            join_group(call)
    except Exception as e:
        logger.error(f"Ошибка обработки групповых действий: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте снова")


def join_group(call):
    try:
        # Удаляем все сообщения, кроме главного
        cleanup_user_messages(call.message.chat.id, str(call.from_user.id), keep_main_message=True)

        msg = bot.send_message(
            call.message.chat.id,
            "Введите код группы для подключения:",
            reply_markup=types.ForceReply()
        )

        # Сохраняем ID сообщения с запросом, чтобы потом удалить
        temp_msg_id = msg.message_id
        message_ids[f"{call.from_user.id}_temp"] = temp_msg_id

        bot.register_next_step_handler(msg, lambda m: process_group_code(m, temp_msg_id))
    except Exception as e:
        logger.error(f"Ошибка при подключении к группе: {e}")
        bot.answer_callback_query(call.id, "Ошибка при подключении к группе")


def process_group_code(message, temp_msg_id):
    try:
        user_id = str(message.from_user.id)
        group_code = message.text.strip().upper()

        # Удаляем сообщение с вводом кода и запросом
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, temp_msg_id)
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения: {e}")

        # Удаляем временный ID сообщения
        if f"{user_id}_temp" in message_ids:
            del message_ids[f"{user_id}_temp"]

        # Ищем группу с таким кодом
        group_found = None
        for group_id, group in groups.items():
            if group['code'] == group_code:
                group_found = group_id
                break

        if group_found:
            # Добавляем пользователя в группу
            if user_id not in groups[group_found]['members']:
                groups[group_found]['members'].append(user_id)

            user_groups[user_id] = group_found
            save_data()

            bot.send_message(
                message.chat.id,
                f"Вы успешно присоединились к группе {group_code}",
                reply_to_message_id=message_ids.get(user_id)
            )

            show_day(message.chat.id, datetime.now().date())
        else:
            bot.send_message(
                message.chat.id,
                "Группа с таким кодом не найдена",
                reply_to_message_id=message_ids.get(user_id)
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке кода группы: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при подключении к группе")


# Обновляем функцию handle_start для сохранения имен пользователей
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        user_id = str(message.from_user.id)
        # Сохраняем имя пользователя
        user_name = message.from_user.first_name
        if message.from_user.last_name:
            user_name += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_name += f" (@{message.from_user.username})"
        user_names[user_id] = user_name

        # Инициализация данных пользователя
        if user_id not in user_tasks:
            user_tasks[user_id] = {}

        # Очищаем все предыдущие сообщения
        cleanup_user_messages(message.chat.id, user_id)

        text = "📅 Добро пожаловать в планировщик дел!\n\n"
        markup = types.InlineKeyboardMarkup()

        if user_id in user_groups:
            group_code = groups[user_groups[user_id]]['code']
            text += f"Вы в группе: {group_code}\n"
            markup.row(types.InlineKeyboardButton("Открыть планировщик", callback_data="day_today"))
        else:
            text += "Вы не состоите в группе\n"
            markup.row(
                types.InlineKeyboardButton("Создать группу", callback_data="create_group"),
                types.InlineKeyboardButton("Присоединиться", callback_data="join_group")
            )

        msg = bot.send_message(
            message.chat.id,
            text,
            reply_markup=markup
        )
        message_ids[user_id] = msg.message_id
        save_data()  # Сохраняем обновленные данные
    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при запуске бота")


def create_group(call):
    try:
        user_id = str(call.from_user.id)

        # Создаем новую группу
        group_id = f"group_{user_id}_{datetime.now().timestamp()}"
        group_code = str(abs(hash(group_id)))[:6].upper()

        groups[group_id] = {
            'owner': user_id,
            'members': [user_id],
            'code': group_code
        }
        user_groups[user_id] = group_id
        save_data()

        # Показываем сообщение с кодом группы
        text = f"""
        🎉 Группа создана!
        ---------------------
        Код группы: <b>{group_code}</b>
        ---------------------
        Отправьте этот код другим пользователям для подключения.
        """

        msg = bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML"
        )
        message_ids[user_id] = msg.message_id

        # Показываем основной интерфейс
        show_day(call.message.chat.id, datetime.now().date())
    except Exception as e:
        logger.error(f"Ошибка при создании группы: {e}")
        bot.answer_callback_query(call.id, "Ошибка при создании группы")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == 'day_today':
            show_day(call.message.chat.id, datetime.now().date(), call.message.message_id)
        elif call.data.startswith('day_'):
            date_str = call.data[4:]
            if date_str == "today":
                date = datetime.now().date()
            else:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            show_day(call.message.chat.id, date, call.message.message_id)
        elif call.data == 'create_group':
            create_group(call)
        elif call.data == 'join_group':
            join_group(call)
        elif call.data.startswith('task_'):
            handle_task(call)
        elif call.data.startswith('add_'):
            add_task(call)
        elif call.data == 'confirm_restart':
            confirm_restart(call)
        elif call.data == 'do_restart':
            do_restart(call)
        elif call.data == 'cancel_restart':
            cancel_restart(call)
        elif call.data == 'group_manage':
            group_manage(call)
        elif call.data.startswith('edit_'):
            edit_task(call)
        elif call.data.startswith('delete_'):
            delete_task(call)
        elif call.data.startswith('calendar_'):
            show_calendar(call.message.chat.id, call.data[9:], call.message.message_id)
        elif call.data == 'ignore':
            bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Ошибка обработки callback: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте снова")


def delete_webhook_safely():
    """Безопасное удаление вебхука с несколькими попытками"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            result = bot.remove_webhook()
            logger.info(f"Попытка {attempt + 1}: Вебхук удален")
            time.sleep(1)
            # Дополнительная проверка
            bot.get_webhook_info()
            return True
        except Exception as e:
            logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
            time.sleep(2)
    return False

def check_webhook_status():
    """Проверяет статус вебхука"""
    try:
        webhook_info = bot.get_webhook_info()
        if webhook_info.url:
            logger.info(f"Обнаружен вебхук: {webhook_info.url}")
            return True
        else:
            logger.info("Вебхук не активен")
            return False
    except Exception as e:
        logger.error(f"Ошибка проверки вебхука: {e}")
        return False

def force_delete_webhook(bot):
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Удаляем вебхук
            bot.remove_webhook()
            logger.info(f"Попытка {attempt + 1}: Вебхук удалён")

            # Проверяем статус вебхука
            webhook_info = bot.get_webhook_info()
            if not webhook_info.url:
                logger.info("Вебхук успешно отключён")
                return True
            else:
                logger.warning(f"Вебхук всё ещё активен: {webhook_info.url}")
                time.sleep(2)
        except Exception as e:
            logger.error(f"Ошибка при удалении вебхука (попытка {attempt + 1}): {e}")
            time.sleep(2)

    logger.error("Не удалось удалить вебхук после нескольких попыток")
    return False

if __name__ == '__main__':
    logger.info("Бот запущен")
    try:
        # Принудительно удаляем вебхук
        if not force_delete_webhook(bot):
            logger.error("Не удалось удалить вебхук. Завершаем работу.")
            exit(1)

        # Запускаем polling
        logger.info("Запускаем polling...")
        while True:
            try:
                transfer_uncompleted_tasks()
                bot.polling(none_stop=True, timeout=30, interval=2)
            except telebot.apihelper.ApiTelegramException as e:
                if "webhook is active" in str(e):
                    logger.warning("Вебхук снова активен. Пытаемся удалить...")
                    force_delete_webhook(bot)
                    time.sleep(5)
                else:
                    logger.error(f"API ошибка: {e}")
                    time.sleep(10)
            except Exception as e:
                logger.error(f"Общая ошибка: {e}")
                time.sleep(10)
            finally:
                save_data()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        save_data()


