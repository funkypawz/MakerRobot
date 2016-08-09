
##3 MakerRobot Telegram bot --- author: Ted Moallem
## Drawing on assorted documents/examples as follows:
## https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples
## example: state_machine_bot.py
## http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart
##


##import telegram

import logging
from telegram import Emoji, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

updater = Updater(token='238293993:AAGP-Q6GrLfEkaZS-2T-bix24rnsRWP7jh0')
    ####updater.stop() -- this would disable the updater, so no more bot until run the script again --
    ####see also: updater.idle() documentation
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
##_________________________________________________________________________________
##_________________________________________________________________________________

## Some functon defs
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm MakerRobot, please talk to me!")

def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)

def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)

def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answerInlineQuery(update.inline_query.id, results)

##_________________________________________________________________________________
##testing state_machine_bot functionality
# Define the different states a chat can be in
MENU, AWAIT_CONFIRMATION, AWAIT_INPUT = range(3)

# Python 2 and 3 unicode differences
try:
    YES, NO = (Emoji.THUMBS_UP_SIGN.decode('utf-8'), Emoji.THUMBS_DOWN_SIGN.decode('utf-8'))
except AttributeError:
    YES, NO = (Emoji.THUMBS_UP_SIGN, Emoji.THUMBS_DOWN_SIGN)

# States are saved in a dict that maps chat_id -> state
state = dict()
# Sometimes you need to save data temporarily
context = dict()
# This dict is used to store the settings value for the chat.
# Usually, you'd use persistence for this (e.g. sqlite).
values = dict()

# Example handler. Will be called on the /set command and on regular messages
def set_value(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text
    chat_state = state.get(chat_id, MENU)
    chat_context = context.get(chat_id, None)

    # Since the handler will also be called on messages, we need to check if
    # the message is actually a command
    if chat_state == MENU and text[0] == '/':
        state[chat_id] = AWAIT_INPUT  # set the state
        context[chat_id] = user_id  # save the user id to context
        bot.sendMessage(chat_id,
                        text="Please enter your settings value or send "
                        "/cancel to abort",
                        reply_markup=ForceReply())
    # If we are waiting for input and the right user answered
    elif chat_state == AWAIT_INPUT and chat_context == user_id:
        state[chat_id] = AWAIT_CONFIRMATION

        # Save the user id and the answer to context
        context[chat_id] = (user_id, update.message.text)
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton(YES), KeyboardButton(NO)]],
            one_time_keyboard=True)
        bot.sendMessage(chat_id, text="Are you sure?", reply_markup=reply_markup)
    # If we are waiting for confirmation and the right user answered
    elif chat_state == AWAIT_CONFIRMATION and chat_context[0] == user_id:
        del state[chat_id]
        del context[chat_id]
        if text == YES:
            values[chat_id] = chat_context[1]
            bot.sendMessage(chat_id, text="Changed value to %s." % values[chat_id])
        else:
            bot.sendMessage(chat_id,
                            text="Value not changed: %s." % values.get(chat_id, '<not set>'))

# Def for the /cancel command. Sets the state back to MENU and clears the context
def cancel(bot, update):
    chat_id = update.message.chat_id
    del state[chat_id]
    del context[chat_id]

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="Use /set to test this bot.")


####_________________________________________________________________________________
####Creat Handlers, add them to dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
#echo_handler = MessageHandler([Filters.text], echo)
#dispatcher.add_handler(echo_handler)
caps_handler = CommandHandler('caps', caps, pass_args=True)
dispatcher.add_handler(caps_handler)
inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

updater.dispatcher.add_handler(CommandHandler('set', set_value))  ## state_machine_bot command
updater.dispatcher.add_handler(MessageHandler([Filters.text], set_value)) ## state_machine_bot answer and confirmation

updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
updater.dispatcher.add_handler(CommandHandler('start', help))
updater.dispatcher.add_handler(CommandHandler('help', help))


##_________________________________________________________________________________
##_________________________________________________________________________________










##_________________________________________________________________________________
##_________________________________________________________________________________

## NOTE: Unknown command handler must be added last. If you added it sooner, it would be triggered before the CommandHandlers had a chance to look at the update.
## Once an update is handled, all further handlers are ignored. To circumvent this, you can pass the keyword argument group (int) to add_handler with a value other than 0.
def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
    ####bot.sendVoice(chat_id=update.message.chat_id, voice=open('../tests/data/telegram.ogg', 'rb'))
    ####custom_keyboard = [[ telegram.Emoji.THUMBS_UP_SIGN,
    ##                     telegram.Emoji.THUMBS_DOWN_SIGN,
    ##                     telegram.Emoji.PILE_OF_POO ]]
    ##reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    ##bot.sendMessage(chat_id=update.message.chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)
    ####reply_markup = telegram.ReplyKeyboardHide()
    ##bot.sendMessage(chat_id=update.message.chat_id, text="I'm back.", reply_markup=reply_markup)
    ####bot.sendPhoto(chat_id=update.message.chat_id, photo='http://makerwale.in/wp-content/uploads/2016/05/makerwale_logo.jpg')

unknown_handler = MessageHandler([Filters.command], unknown)
dispatcher.add_handler(unknown_handler)



## Start the Bot
updater.start_polling()
# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()


















