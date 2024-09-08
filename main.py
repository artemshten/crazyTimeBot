import telebot
import sqlite3

bot = telebot.TeleBot('7317210656:AAHuyea1QvClrObvrEeqHnPB-QGBJzbXFO8')

def add_to_db(db_path, id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE id=?", (id,))
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
    else:
        cursor.execute("INSERT INTO users (id) VALUES (?)", (id,))
        conn.commit()
        conn.close()

def check_balance(db_path, id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    return result

@bot.message_handler(commands=['start'])
def start(message):
    add_to_db('database.db', message.from_user.id)
    bot.send_message(message.chat.id, "Hello! It's a crazy time")

@bot.message_handler(commands=['help'])
def help(message):
    add_to_db('database.db', message.from_user.id)
    bot.send_message(message.chat.id, "Available commands:\n/bet <amount> <result>\n/start_game\n/end_game <result>\n/balance")

@bot.message_handler(commands=['balance'])
def balance(message):
    add_to_db('database.db', message.from_user.id)
    balance = check_balance('database.db', message.from_user.id)
    bot.reply_to(message, f'Your balance is {balance}')

@bot.message_handler(commands=['bet'])
def bet(message):
    try:
        amount = message.text.split()[1]
        result = message.text.split()[2]
        try:
            amount = int(amount)
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS game ("
                           "id INTEGER PRIMARY KEY UNIQUE,"
                           "amount NUMERIC NOT NULL,"
                           "result TEXT NOT NULL)")
            if check_balance('database.db', message.from_user.id) >= int(amount):
                cursor.execute("INSERT INTO game (id, amount, result) VALUES (?,?,?)",
                               (message.from_user.id, amount, result))
                conn.commit()
                bot.reply_to(message, f'The bet has been successfully placed\nAmount: {amount}\nResult: {result}')
            if check_balance('database.db', message.from_user.id) < int(amount):
                bot.reply_to(message, 'Insufficient balance')
        except Exception:
            bot.reply_to(message, 'The value must be a number')
    except IndexError:
        bot.reply_to(message, 'Usage: /bet <amount> <result>')


bot.polling(none_stop=True)