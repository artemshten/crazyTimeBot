import telebot
from telebot import types
import sqlite3
import time
import random

admin = [5360268210]
bot = telebot.TeleBot('7317210656:AAHuyea1QvClrObvrEeqHnPB-QGBJzbXFO8')
is_game_active = False
is_bonus_active = False
results = ['1','2','5','10','coin','cash','pach','crazy']
games = ['coin','cash','pach','crazy']
coin = ['2','2','2','2','2','3','3','3','3','5','5','5','5','10','10','10','25','25','25','50','50','100']
cash_emoji = ['🐇','🎯','🎁','⭐️','🍎','🧁']
cash = ['5','5','5','5','5','5','5','5','5','5','7','7','7','7','7','7','7','7','7','7','10','10','10','10','10','15','15','15','15','15','15','20','20','20','20','20','50','50','50','50','100','100','100']
crazy_3 = ['10','25','50']
crazy_4 = ['10','20','25','50']
crazy_6 = ['10','20','25','50','100','DOUBLE']

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
    conn.close()
    return result

def make_bet(db_path, id, amount):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, id))
    conn.commit()
    conn.close()

def add_balance1(db_path, id, amount):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, id))
    conn.commit()
    conn.close()
    return f'Successfully given {amount} to this user.'

def check_winners(db_path, result):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, username FROM game WHERE result = ?", (result,))
    winners = cursor.fetchall()
    if result == '1' or result == '2' or result == '5' or result == '10':
        result = int(result)+1
        win_message = f'The result of the game is {result-1}\nCongratulations to all the winners!\n\nWinners:\n'
        for i in winners:
            ids = i[0]
            win = i[1]*result
            username = i[2]
            win_message += f'@{username}: {win}\n'
            cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?",(win, ids))
            conn.commit()
        conn.close()
        return win_message
    elif result == 'crazy':
        conn.close()
        win_message = "IT'S A CRAAAZY TIME!!!"
        return win_message
    elif result == 'coin':
        conn.close()
        win_message = "It`s a coin flip."
        return win_message
    else:
        conn.close()
        return 'In work.'

def makecrazytime(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('3', callback_data='3')
    button2 = types.InlineKeyboardButton('4', callback_data='4')
    button3 = types.InlineKeyboardButton('6', callback_data='6')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Select the number of sections on the wheel.', reply_markup=markup)

def makecoinflip(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Yes', callback_data='coin_yes')
    button2 = types.InlineKeyboardButton('No', callback_data='coin_no')
    markup.add(button1, button2)
    bot.send_message(message.chat.id, 'Do you want to pick color randomly?', reply_markup=markup)

def crazytime(call, sections):
    group = call.message.chat.id
    if sections == 3:
        bot.send_message(group, f'Spin the wheel! Available X: 10, 25, 50.')
    elif sections == 4:
        bot.send_message(group, f'Spin the wheel! Available X: 10, 20, 25, 50.')
    elif sections == 6:
        bot.send_message(group, f'Spin the wheel! Available X: 10, 20, 25, 50, 100, DOUBLE.')
        '''
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Left 🟢', callback_data='left')
        button2 = types.InlineKeyboardButton('Center 🔵', callback_data='center')
        button3 = types.InlineKeyboardButton('Right 🟡', callback_data='right')
        markup.add(button1,button2,button3)
        bot.send_message(group, 'Choose your color!', reply_markup=markup)
        '''

def coinflip(call, randomly):
    group = call.message.chat.id
    mes = bot.send_message(group, f'Multipliers for coin flip are...')
    time.sleep(3)
    bot.delete_message(group, mes.id)
    red = random.choice(coin)
    blue = random.choice(coin)
    while blue == red:
        blue = random.choice(coin)
    bot.send_message(group, f'Red 🔴: {red}\n\nBlue 🔵: {blue}')
    if randomly == True:
        time.sleep(2)
        mes = bot.send_message(group, 'The result of coin flip is...')
        time.sleep(2)
        lst2 = [red, blue]
        result = random.choice(lst2)
        bot.edit_message_text(group, mes.id, f'The result of coin flip is {result}')
        time.sleep(1)
    elif randomly == False:
        time.sleep(2)
        mes = bot.send_message(group, 'You can flip a coin')

def check_bonus_winners(db_path, game, x):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, username FROM game WHERE result = ?", (game,))
    winners = cursor.fetchall()
    win_message = f'The result of the bonus game is {x}X\nCongratulations to all the winners!\n\nWinners:\n'
    for i in winners:
        ids = i[0]
        win = i[1] * (x+1)
        username = i[2]
        win_message += f'@{username}: {win}\n'
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (win, ids))
        conn.commit()
    cursor.execute('DROP TABLE game')
    conn.commit()
    conn.close()
    return win_message

def active_bets(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game';")
    table_exists = cursor.fetchone()
    if table_exists:
        return True
    else:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    add_to_db('database.db', message.from_user.id)
    bot.send_message(message.chat.id, "Hello! It's a crazy time.")

@bot.message_handler(commands=['help'])
def help(message):
    add_to_db('database.db', message.from_user.id)
    bot.send_message(message.chat.id, "Available commands:\n/bet <amount> <result>\n/start_game\n/end_game <result>\n/end_bonus <game> <x>\n/balance")

@bot.message_handler(commands=['balance'])
def balance(message):
    add_to_db('database.db', message.from_user.id)
    balance = check_balance('database.db', message.from_user.id)
    bot.reply_to(message, f'Your balance is {balance}.')

@bot.message_handler(commands=['bet'])
def bet(message):
    add_to_db('database.db', message.from_user.id)
    global is_game_active
    if is_game_active == False:
        try:
            amount = message.text.split()[1]
            result = message.text.split()[2]
            if result in results:
                try:
                    amount = int(amount)
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS game ("
                                   "id INTEGER,"
                                   "username TEXT,"
                                   "amount NUMERIC NOT NULL,"
                                   "result TEXT NOT NULL)")
                    if check_balance('database.db', message.from_user.id) >= amount:
                        cursor.execute("INSERT INTO game (id, username, amount, result) VALUES (?,?,?,?)",
                                       (message.from_user.id, message.from_user.username, amount, result))
                        conn.commit()
                        bot.reply_to(message, f'The bet has been successfully placed.\nAmount: {amount}\nResult: {result}')
                        make_bet('database.db', message.from_user.id, amount)
                    elif check_balance('database.db', message.from_user.id) < amount:
                        bot.reply_to(message, 'Insufficient balance.')
                except ValueError:
                    bot.reply_to(message, 'The value must be a number.')
            else:
                bot.reply_to(message, 'Available bets: 1, 2, 5, 10,\ncoin, cash, pach, crazy.')
        except IndexError:
            bot.reply_to(message, 'Usage: /bet <amount> <result>.')
    else:
        bot.reply_to(message, 'Bets are closed.')

@bot.message_handler(commands=['start_game'])
def start_game(message):
    active_bets1 = active_bets('database.db')
    add_to_db('database.db', message.from_user.id)
    global is_game_active
    if active_bets1 == True:
        if is_game_active == False:
            is_game_active = True
            bot.send_message(message.chat.id, 'Bets are closed. We are spinning the wheel!')
        else:
            bot.reply_to(message, 'There is already an active game.')
    else:
        bot.reply_to(message, "There aren't any bets.")

@bot.message_handler(commands=['add_balance'])
def add_balance(message):
    add_to_db('database.db', message.from_user.id)
    if message.from_user.id in admin:
        try:
            amount = message.text.split()[1]
            try:
                amount = int(amount)
                try:
                    a = add_balance1('database.db', message.reply_to_message.from_user.id, amount)
                    bot.reply_to(message, a)
                except Exception as e:
                    bot.reply_to(message, 'You need to reply the user.')
            except ValueError:
                bot.reply_to(message, 'The value must be a number.')
        except IndexError:
            bot.reply_to(message, 'Usage: /add_balance <amount>. (reply to user)')
    else:
        bot.reply_to(message, 'Insufficient permissions.')

@bot.message_handler(commands=['end_game'])
def end_game(message):
    add_to_db('database.db', message.from_user.id)
    global is_game_active
    try:
        result = message.text.split()[1]
        if result in results:
            if is_game_active == True:
                is_game_active = False
                winners = check_winners('database.db', result)
                bot.send_message(message.chat.id, winners)
                if winners == "IT'S A CRAAAZY TIME!!!":
                    global is_bonus_active
                    is_bonus_active = True
                    makecrazytime(message)
                if winners == "It`s a coin flip.":
                    global is_bonus_active
                    is_bonus_active = True
                    makecoinflip(message)
                else:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    cursor.execute('DROP TABLE game')
                    conn.commit()
                    conn.close()
            else:
                bot.reply_to(message, 'There is no active game.')
        else:
            bot.reply_to(message, 'Available results: 1, 2, 5, 10,\ncoin, cash, pach, crazy.')
    except IndexError:
        bot.reply_to(message, 'Usage: /end_game <result>.')

@bot.message_handler(commands=['end_bonus'])
def end_bonus(message):
    add_to_db('database.db', message.from_user.id)
    global is_bonus_active
    if is_bonus_active == True:
        try:
            game = message.text.split()[1]
            x = message.text.split()[2]
            if game in games:
                if game == 'crazy':
                    if x in crazy_6:
                        x = int(x)
                        winners = check_bonus_winners('database.db', 'crazy', x)
                        bot.send_message(message.chat.id, winners)
                    else:
                        bot.send_message(message.chat.id, 'Available X: 10, 20, 25, 50, 100, DOUBLE.')
                elif game == 'coin':
                    if x in coin:
                        x = int(x)
                        winners = check_bonus_winners('database.db', 'coin', x)
                        bot.send_message(message.chat.id, winners)
                    else:
                        bot.send_message(message.chat.id, 'Available X: 2, 3, 5, 10, 25, 50, 100')
                else:
                    bot.send_message(message.chat.id, 'In work.')
            else:
                bot.send_message(message.chat.id, 'Available games: coin, cash, pach, crazy')
        except Exception as e:
            bot.send_message(message.chat.id, 'Usage: /end_bonus <bonus_game> <x>.')
    else:
        bot.send_message(message.chat.id, 'There is no active bonus game.')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == '3':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        crazytime(call, 3)
    elif call.data == '4':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        crazytime(call, 4)
    elif call.data == '6':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        crazytime(call, 6)
    elif call.data == 'left':
        pass
    elif call.data == 'center':
        pass
    elif call.data == 'right':
        pass
    elif call.data == 'coin_yes':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        coinflip(call, True)
    elif call.data == 'coin_no':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        coinflip(call, False)

bot.polling(none_stop=True)