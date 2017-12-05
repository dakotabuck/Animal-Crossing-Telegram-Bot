# Telegram bot for Animal Crossing Pocket Camp
# chatroom for the Furry community.
#
# Author: Dakota the Buck
#   https://twitter.com/dakotathebuck
#
# Purpose:
#   To moderate the ACPC chatroom and manage
#   the chat's friend code registry.

# Import OS for file operations
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# Initializing the bot with BotFather's token.
from telegram.ext import Updater
updater = Updater(token = '507076263:AAHcj5n7AYv6M4dDJ1VYNDp-RjbLXHf2OHk')
dispatcher = updater.dispatcher
selected_command = {}

# Setting up logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO)

# Function for parsing input for functions
def parse_message(bot, update):
    command = selected_command[update.message.chat_id]
    #bot.send_message(chat_id = update.message.chat_id, text = update.message.text)
    if command == 'getcode':
        getcode(bot, update, update.message.text)
    elif command == 'setcode':
        addcode(bot, update, update.message.text)
    elif command == 'report':
        report(bot, update, update.message.text)

# Function for /start
def start(bot, update):
    chat_file = open('chat_id/' + update.message.from_user.username + '.txt', 'w')
    chat_file.write(str(update.message.chat_id))
    chat_file.close()

    bot.send_message(chat_id=update.message.chat_id,
                     text='Thank you for initiating the AC: Pocket Camp friend code bot!')

    button_menu(bot, update)

def button_menu(bot, update):
    selected_command[update.message.chat_id] = ''
    button_row = InlineKeyboardMarkup([[
            InlineKeyboardButton('Get Code', callback_data='getcode'),
            InlineKeyboardButton('Set Code', callback_data='setcode')
        ], [
            InlineKeyboardButton('Anonymous Group Abuse Report', callback_data='report')
        ],
        [
            InlineKeyboardButton('About & Help', callback_data='gethelp')
        ]])
    
    bot.send_message(chat_id=update.message.chat_id,
                     text='Please select from the following options:',
                     reply_markup=button_row)

def button_pressed(bot, update):
    query = update.callback_query

    selected_command[query.message.chat.id] = query.data

    if query.data == 'getcode':
        query.message.reply_text('Enter username of the person to request code for!\n'
                                  + 'Please note: the subject will be notified!')
    elif query.data == 'setcode':
        button_row = InlineKeyboardMarkup([[
            InlineKeyboardButton('Remove your code', callback_data='removecode')
        ]])
        bot.send_message(chat_id=query.message.chat_id,
                         text='What is your AC: Pocket Camp friend code?',
                         reply_markup=button_row)
    elif query.data == 'gethelp':
        send_help(bot, query)
    elif query.data == 'removecode':
        remove_code(bot, query)
    elif query.data == 'report':
        query.message.reply_text('Please type your report and send it.'
                         +' Your identity will be kept private, '+
                         'and only moderators will be able to view '+
                         'the report. Please include specific @ handles '+
                         'and times at which the abuse occurred. If you ' +
                         'don\'t want to report anonymously, simply send '+
                         'a private message to @dakotabuck, @misterlovegood, '+
                         'or @pankeye.')

def send_help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        text='Usage:\n'
        +'<b>Get Code</b>: look up a user\'s Pocket Camp '
        +'friend code by telegram @ handle. <i>This '
        +'notifies the user you looked up that their '
        +'friend code was requested and by whom</i>.\n'
        +'<b>Set Code</b>: use this to set your own Pocket '
        +'Camp code so that others can look you up! \n'
        +'<b>Anonymous Group Abuse Report</b>: use this '
        +'when you want to report channel abuse, but don\'t'
        +'want to contact a mod directly. If the issue is '
        +'about a mod, please send a private message to another '
        +'mod to ensure that the reported mod does not read '
        +'your report.',
        parse_mode='html'
    )
    button_menu(bot, update)

def format_code(code):
    return code[0:3] + ' ' + code[3:7] + ' ' + code[7:11]


# Function for /addcode
def addcode(bot, update, args):
    # Define the input code
    text_code = ''.join(args)

    # Temp var for sanitation
    char = ''

    # Iterate through the input and pick out numbers
    for num in text_code:
        if num.isnumeric():
            char += num

    # 11 is the length of a Nintendo friend code
    if char.__len__() == 11:
        # Logs the given data to the file, overwriting everything else
        userfile = open('userdata/' + update.message.from_user.username + '.txt', 'w')
        userfile.write(str(char))
        userfile.close()
        bot.send_message(chat_id=update.message.chat_id,
                         text = 'Thank you for adding or changing your code!\n'
                         + 'Please verify this is correct: ' + format_code(char))
    else:
        # If the length of the number is not 11, throw an error
        bot.send_message(chat_id=update.message.chat_id, text = 'Inputted code ' + str(char) + ' is not valid.')
    button_menu(bot, update)

# Function for anonymous reports
def report(bot, update, args):
    text_report = ''.join(args)
    reportfile = open('reports/' + str(update.update_id) + '.txt', 'w')
    reportfile.write(text_report)
    reportfile.close()

    bot.send_message(chat_id=update.message.chat_id,
                     text='Thank you for your report. The mods have been notified.')

    notify_conversation = open('chat_id/dakotabuck.txt', 'rU')
    notify_conversation_id = notify_conversation.read();
    notify_conversation.close()
    bot.send_message(chat_id=notify_conversation_id, text='Anonymous report sent. ID: ' + str(update.update_id))
    button_menu(bot, update)
    print(update)

# Function for /getcode
def getcode(bot, update, args):
    filepath = 'userdata/' + ''.join(args) + '.txt'
    if not os.path.isfile(filepath):
        bot.send_message(chat_id=update.message.chat_id, text='The specified user has not yet registered their friend code!')
        return False

    requestedfile = open(filepath, 'rU')
    friendcode = requestedfile.read(11)
    friendcode = format_code(friendcode)
    bot.send_message(chat_id=update.message.chat_id, text='@' + ''.join(args) + '\'s ACPC friendcode is as follows:')
    bot.send_message(chat_id=update.message.chat_id, text = friendcode)
    requestedfile.close()

    notify_conversation = open('chat_id/' + ''.join(args) + '.txt', 'rU')
    notify_conversation_id = notify_conversation.read();
    notify_conversation.close()
    bot.send_message(chat_id=notify_conversation_id, text='@' + update.message.from_user.username + ' just received your friend code!')
    button_menu(bot, update)


# Function for command not recognized
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text = 'Invalid command, saltlick')


# Event Handling
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# /start handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
updater.start_polling()

# General Message input handler
input_handler = MessageHandler(Filters.text, parse_message)
dispatcher.add_handler(input_handler)

# Button Pressed handler
button_handler = CallbackQueryHandler(button_pressed)
dispatcher.add_handler(button_handler)

# /addcode handler
addcode_handler = CommandHandler('addcode', addcode, pass_args=True)
dispatcher.add_handler(addcode_handler)

# /getcode handler
getcode_handler = CommandHandler('getcode', getcode, pass_args=True)
dispatcher.add_handler(getcode_handler)

# Invalid command handler
# !IMPORTANT! MUST BE THE LAST HANDLER DEFINED
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)