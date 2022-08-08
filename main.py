# -*- coding: utf-8 -*-
"""
This Example will show you how to use register_next_step handler.
"""

import telebot
import pygsheets
from telebot import types
from datetime import datetime


service_file = r'seanloggerbot-03442d11fe84.json'
gc = pygsheets.authorize(service_file=service_file)
sheetname = 'TimeLogger'
sh = gc.open(sheetname)
wks = sh.worksheet_by_title('Sheet1')
wksnames = sh.worksheet_by_title('Sheet2')

API_TOKEN = '5557989674:AAFQlL05vig5Hj3mkics-DX_dQmIo1AhPQI'

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}

print("Bot getting started..")

class User:
    def __init__(self, name):
        self.timein = name
        self.timeout = None

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.reply_to(message, """
Hi! Welcome to SeanLogger_bot.\n
Type /timein to login
Type /timeout to logout
Type /status to check details
""")


# Timein
@bot.message_handler(commands=['timein'])
def process_timein(message):
    username = message.chat.username
    finduser = wksnames.find(username)
    nofind = int(len(finduser))
    if nofind >= 1:
        try:
            now = datetime.now()
            date = now.strftime('%m/%d/%y')
            date_time = now.strftime("%I:%M:%S%p")
            time = now.strftime("%I:%M:%S%p")
            chat_id = message.chat.id
            timein = message.text
            user = User(timein)
            user_dict[chat_id] = user
            user.timein = date_time

            if timein == "/timein":
                user_first_name = str(message.chat.first_name)
                user_last_name = str(message.chat.last_name)
                full_name = user_first_name + " "+ user_last_name
                grecord = wks.get_all_records()
                num = 2
                for i in range(len(grecord)):
                    num+=1
                    if full_name == grecord[i].get("Name") and date == grecord[i].get("Date"):
                        bot.reply_to(message, f'You have already TIMED IN')
                        break
                else: 
                    wks.update_value((num, 1), full_name)
                    wks.update_value((num, 2), date)
                    wks.update_value((num, 3), time)
                    # Timelogger = []
                    # Timelogger.append(str(full_name))
                    # Timelogger.append(str(date))
                    # Timelogger.append(str(time))    
                    bot.reply_to(message, f'User Timein: {str(date_time)}')
                          
        except Exception as e:
            bot.reply_to(message, 'Something went wrong. Please try again')

    else:
        bot.reply_to(message, 'Only Intern member can use this bot')


# Timeout
@bot.message_handler(commands=['timeout'])
def process_timeout(message):
    try:    
        now2 = datetime.now()
        date = now2.strftime('%m/%d/%y')
        time = now2.strftime("%I:%M:%S%p")
        date_time2 = now2.strftime("%I:%M:%S%p") 
        user_first_name = str(message.chat.first_name)
        user_last_name = str(message.chat.last_name)
        full_name = user_first_name + " "+ user_last_name
        chat_id = message.chat.id
        timeout = message.text 
        user = User(timeout)
        user = user_dict[chat_id]
        user.timeout = date_time2

        if timeout == "/timeout":
            grecord = wks.get_all_records()
            num = 1
            for i in range(len(grecord)):
                num += 1
                if full_name == grecord[i].get("Name") and date == grecord[i].get("Date") and grecord[i].get("Timeout")== '':
                    wks.update_value((num,4),time)
                    bot.reply_to(message, f'User Timeout: {str(date_time2)}')
                    break
                elif full_name == grecord[i].get("Name") and date == grecord[i].get("Date") and grecord[i].get("Timeout")!= '':
                    bot.reply_to(message, 'You have already TIMED OUT')


    except Exception as e:
        bot.reply_to(message, 'Something went wrong. Please try again')



# Status
@bot.message_handler(commands=['status'])  
def process_status(message):
    getusername = message.chat.username
    user_first_name = str(message.chat.first_name) 
    user_last_name = str(message.chat.last_name)
    full_name = user_first_name + " "+ user_last_name
    now = datetime.now()
    date = now.strftime('%m/%d/%y')
    grecord = wks.get_all_records()
    num = 1
    for i in range(len(grecord)):
        num += 1
        if full_name == grecord[i].get("Name") and date == grecord[i].get("Date") and grecord[i].get("Timein")!= '' and grecord[i].get("Timeout")!= '':
            bot.reply_to(message, f'Date {date}\nTimein: {grecord[i].get("Timein")}\nTimeout: {grecord[i].get("Timeout")}')
            break
        elif full_name == grecord[i].get("Name") and date == grecord[i].get("Date") and grecord[i].get("Timein")!= '' and grecord[i].get("Timeout")== '':
            bot.reply_to(message, f'Date {date}\nTimein: {grecord[i].get("Timein")}\nTimeout: NONE')
            break
    else:
        bot.reply_to(message, "You haven't TIMED IN yet today")


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()
