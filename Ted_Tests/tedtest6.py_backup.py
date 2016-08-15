
##3 MakerRobot Telegram bot --- author: Ted Moallem
## Drawing on assorted documents/examples as follows:
## https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples
## example: state_machine_bot.py
## http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart
## http://docs.peewee-orm.com/en/latest/peewee/querying.html#querying
## http://docs.peewee-orm.com/en/latest/peewee/example.html#creating-tables
## https://docs.python.org/2/library/stdtypes.html#dict
## https://github.com/funkypawz/telebot
## https://pypi.python.org/pypi/python-telegram-bot/4.0rc1
## https://core.telegram.org/bots/api#available-methods
## https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py

import telegram
import os
import logging
from telegram import Emoji, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram.ext import ConversationHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from peewee import *
from datetime import date

print(os.listdir(".")) #lists current directory contents

#Create the EventHandler and pass it your bot's token.
mrtoken = '238293993:AAGP-Q6GrLfEkaZS-2T-bix24rnsRWP7jh0'
updater = Updater(token=mrtoken)
    ####updater.stop() -- this would disable the updater, so no more bot until run the script again --
    ####see also: updater.idle() documentation
#Get the dispatcher to register handlers
dispatcher = updater.dispatcher

bot = telegram.Bot(token=mrtoken)
print(bot.getMe())
updates = bot.getUpdates()
print([u.message.text for u in updates])
print([u.message.photo for u in updates if u.message.photo])

#chat_id = bot.getUpdates()[-1].message.chat_id #need chat_id to reply to messages
#bot.sendMessage(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")
#bot.sendMessage(chat_id=chat_id, text="*bold* _italic_ [link](http://google.com).", parse_mode=telegram.ParseMode.MARKDOWN)
#bot.sendMessage(chat_id=chat_id, text="<b>bold</b> <i>italic</i> <a href="http://google.com">link</a>.", parse_mode=telegram.ParseMode.HTML)
#bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.PILE_OF_POO)
#bot.sendPhoto(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')
#bot.sendPhoto(chat_id=chat_id, photo=open('tests/test.png', 'rb'))
#bot.sendVoice(chat_id=chat_id, voice=open('tests/telegram.ogg', 'rb'))
#bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING) #To tell user that something is happening on bot's side
## For more...custom keyboards, download a file, etc. --- https://pypi.python.org/pypi/python-telegram-bot/4.0rc1
## also see: pydoc telegram.Bot (in terminal)


##_________________________________________________________________________________
# Enable logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


##_________________________________________________________________________________
## SETUP DATABASE

db = SqliteDatabase('makerwale.db')

class Person(Model):
    name = CharField()
    fullname = CharField()
    birthdate = DateField()
    school = CharField()
    section = CharField()
    is_student = BooleanField()

    class Meta:
        database = db # This model uses the "people.db" database.

class Pet(Model):
    owner = ForeignKeyField(Person, related_name='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db # this model uses the "people.db" database

db.connect()
db.create_tables([Person, Pet], True)  ## 'True' argument makes peewee first check to see if the table exists before creating it.

##bob = Person(name='Bob', fullname='Robert Robertson', school='GMGS', section='9C', birthdate=date(1960, 1, 15), is_student=True)
##bob.save() # using .save() method to add person to the database; number of rows modified is returned.
##grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1), is_student=False) # using .create() method to add person to the database
##grandma.name = 'Grandma L.'
##grandma.save()  # Update grandma's name in the database.
##herb = Person.create(name='Herb', birthday=date(1950, 5, 5), is_student=False)
##herb.delete_instance() # return value of delete_instance() is the number of rows removed from the database.
###To get a single record from the database, use SelectQuery.get()
##grandma = Person.select().where(Person.name == 'Grandma L.').get()
###We can also use the equivalent shorthand Model.get():
##grandma = Person.get(Person.name == 'Grandma L.')
#
for person in Person.select().order_by(Person.birthdate.desc()):
    print(person.name, person.school, person.section, person.birthdate, person.is_student)
#
##query = Pet.select().where(Pet.animal_type == 'cat')
##for pet in query:
##    print pet.name, pet.owner.name    
#
##expression = (fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g') #use a SQL function to find all people whose names start with either an upper or lower-case G
##for person in Person.select().where(expression):
##    print person.name

#db.close() #when done with database, close the connection ???


####_________________________________________________________________________________
####_________________________________________________________________________________

## Some functon defs

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


## Implementing based on examples/conversationbot.py
#GENDER, PHOTO, LOCATION, BIO = range(4)
COMTYPE, NAME, PHOTO, DESCRIPTION = range(4)
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, 
    						text=' Namaste. Mera naam MakerRobot hai. '  
    							 ' Mere aadeshon hain: /post /ask /intro \n\n')
    reply_keyboard = [['POST', 'ASK', 'INTRO']]

    bot.sendMessage(update.message.chat_id,
                    text='Please choose one. (or send /stop)' ,
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return COMTYPE
def comtype(bot, update):
    user = update.message.from_user
    logger.info("Command type from %s: %s" % (user.first_name, update.message.text))

    bot.sendMessage(update.message.chat_id, text= " AAPKA NAAM KYA HAI ? " )
    return NAME
def name(bot, update):
    user = update.message.from_user
    logger.info("Name of %s user: %s" % (user.first_name, update.message.text))
    bot.sendMessage(update.message.chat_id,
                    text='Please send me a photo of your work or activities.')
    return PHOTO
def photo(bot, update):
    user = update.message.from_user
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    photo_file.download('user_photo.jpg')
    logger.info("Photo from %s: %s" % (user.first_name, 'user_photo.jpg'))
#    bot.sendMessage(update.message.chat_id, text='Gorgeous! Now, send me your location please, '
#                                                 'or send /skip to skip location.')
#    return LOCATION
    bot.sendMessage(update.message.chat_id, text= " Please describe your work or activities. " )
    return DESCRIPTION
def skip_photo(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a photo." % user.first_name)
    bot.sendMessage(update.message.chat_id, text='Theek hai. :( '
                                                 'Please describe your work or activities. ')
    return DESCRIPTION
# def location(bot, update):
#     user = update.message.from_user
#     user_location = update.message.location
#     logger.info("Location of %s: %f / %f"
#                 % (user.first_name, user_location.latitude, user_location.longitude))
#     bot.sendMessage(update.message.chat_id, text='Maybe I can visit you sometime! '
#                                                  'At last, tell me something about yourself.')
#     return BIO
def description(bot, update):
    user = update.message.from_user
    logger.info("Description of %s: %s" % (user.first_name, update.message.text))
    bot.sendMessage(update.message.chat_id,
                    text='Dhanyavad. Please post again soon!')
    return ConversationHandler.END



def stop(bot, update):
    user = update.message.from_user
    logger.info("User %s stopped the conversation." % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text='Bye! I hope we can talk again some day.')
    return ConversationHandler.END

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Add conversation handler with the states COMTYPE, NAME, PHOTO, DESCRIPTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            COMTYPE: [RegexHandler('^(Post|Ask|Intro)$', comtype)],
            NAME: [MessageHandler([Filters.text], name)],
            PHOTO: [MessageHandler([Filters.photo], photo),
                    CommandHandler('skip', skip_photo)],
            DESCRIPTION: [MessageHandler([Filters.text], description)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dispatcher.add_handler(conv_handler)
    # log all errors
    dispatcher.add_error_handler(error)



if __name__ == '__main__':
    main()





##_________________________________________________________________________________
##testing state_machine_bot functionality

MENU, AWAIT_CONFIRMATION, AWAIT_INPUT = range(3) # Define the different states a chat can be in

# Python 2 and 3 unicode differences
try:
    YES, NO = (Emoji.THUMBS_UP_SIGN.decode('utf-8'), Emoji.THUMBS_DOWN_SIGN.decode('utf-8'))
except AttributeError:
    YES, NO = (Emoji.THUMBS_UP_SIGN, Emoji.THUMBS_DOWN_SIGN)

#States/contexts/values are saved in a dict that save data temporarily -- maps chat_id to state/user_id/value
# Usually, you'd use persistence for this (e.g. sqlite).
state = dict()  # can be MENU, AWAIT_CONFIRMATION, or AWAIT_INPUT
context = dict()  # user_id
values = dict()  #settings value for the chat.

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

# Def for the /cancel command. Sets the state back to MENU and clears the context ---also added lines from ConversationHandler cancel function
def cancel(bot, update):
    chat_id = update.message.chat_id
    del state[chat_id]
    del context[chat_id]
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text='Bye! I hope we can talk again some day.')
    return ConversationHandler.END


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
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.  Type /start to begin.")
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
# Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
updater.idle()


















