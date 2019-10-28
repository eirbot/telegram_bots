#! /bin/env python

"""
Telegram bot to add and list borrow.
"""

from emprunt import Borrow, BorrowList
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Updater,
    Filters,
)
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ParseMode
)
import os
import logging

HELP_TEXT = """
Bonjour, je suis `Emprunt'eirbot`.

Voici les commandes disponibles :

Pour **ajouter un élément** :
/add
/add <something> `by` <someone>

Pour **supprimer un élément** :
/returned <id>
/returned <something>
/r

Pour **lister les éléments** :
/list
/l

Pour **obtenir de l'aide** :
/help
/h
"""

# Set up logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(message)s',
    level=logging.INFO)
log = logging.getLogger()

bot_updater = Updater(token=os.environ["EMPRUNT_BOT_TOKEN"], use_context=True)
log.info("Bot updated")

DESCRIPTION, NAME, COMMIT = range(3)
DEFAULT_BORROW = {
    "description": None,
    "borrower": None,
    "user": None
}
CURRENT_BORROW = DEFAULT_BORROW


# defining bot commands
def add_borrow(update, context):
    # resetting the global variable
    global CURRENT_BORROW
    CURRENT_BORROW = DEFAULT_BORROW

    args = " ".join(update.message.text.split(" ")[1:])
    print(args)
    if not args:  # nothing added, need to ask
        update.message.reply_text("What's the name of the borrowed object ?")
        return DESCRIPTION

    splitted_args = args.split(" by ")
    print(splitted_args)
    if len(splitted_args) == 2:  # All has been added
        user = update.message.from_user
        CURRENT_BORROW["description"] = splitted_args[0]
        CURRENT_BORROW["borrower"] = splitted_args[1]
        CURRENT_BORROW["user"] = "{} <{}> ({})".format(user.full_name, user.username, user.id)
        add_borrow_commit()
        update.message.reply_text(
            'Noted ! `{}` Borrowed {}.'.format(
                CURRENT_BORROW["borrower"],
                CURRENT_BORROW["description"]),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
        return ConversationHandler.END
        
    else:
        update.message.reply_text(
            "**Invalid syntax**\n"
            + "You can use\n"
            + "`/add <object> by <borrower>`\n"
            + "or\n"
            + "`/add`",
            parse_mode='Markdown'
        )
    return ConversationHandler.END


def add_borrow_description(update, context):
    global CURRENT_BORROW
    description = update.message.text
    CURRENT_BORROW["description"] = description
    update.message.reply_text(
        "Who **borrowed** `{}` ?".format(description),
        parse_mode='Markdown'
    )
    return NAME


def add_borrow_name(update, context):
    global CURRENT_BORROW
    borrower = update.message.text
    CURRENT_BORROW["borrower"] = borrower
    update.message.reply_text(
        'Noted ! `{}` Borrowed {}.'.format(borrower,
                                           CURRENT_BORROW["description"]),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    user = update.message.from_user
    CURRENT_BORROW["user"] = "{} <{}> ({})".format(user.full_name, user.username, user.id)
    add_borrow_commit()
    return ConversationHandler.END


def add_borrow_commit():
    Store.add_new(*CURRENT_BORROW.values())


def list_borrow(update, context):
    nb_borrowed = len(Store.borrowed_items())
    nb_items = Store.len()
    if nb_items == 0:
        text = "The BorrowList is **empty**."
    else:
        text = "The BorrowList contains {} item{} in which {} are still borrowed.".format(
            nb_items, "s" if nb_items > 1 else "", nb_borrowed)
    for b in Store.borrowed_items():
        text += "\n {}. `{}` borrowed by `{}`".format(
            b.data["id"],
            b.data["description"],
            b.data["borrower_name"])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown'
    )

def help_command(update, context):
    """Display help for commands"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=HELP_TEXT,
        parse_mode='Markdown')

def returned_borrow(update, context):
    returned_object = " ".join(update.message.text.split(" ")[1:])
    if returned_object.isdigit():
        id = int(returned_object)
    else:
        id = Store.getBorrowIdByDesc(returned_object)

    if not id:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="`{}` has not been found".format(returned_object),
            parse_mode='Markdown'
        )

    else:
        if id < Store.len():
            Store.store[id].setReturned()
            Store.save()
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="`{}` is back !".format(
                    Store.store[id].data["description"]),
                parse_mode='markdown'
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="The id `{}` has not been found !".format(id),
                parse_mode='markdown'
            )


# Adding bot commands
dispatcher = bot_updater.dispatcher
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler('add', add_borrow)],
        states={
            DESCRIPTION: [
                MessageHandler(Filters.text, add_borrow_description)
            ],
            NAME: [
                MessageHandler(Filters.text, add_borrow_name)
            ],
        },
        fallbacks=[]
    )
                       )
dispatcher.add_handler(CommandHandler('list', list_borrow))
dispatcher.add_handler(CommandHandler('l', list_borrow))
dispatcher.add_handler(CommandHandler('returned', returned_borrow))
dispatcher.add_handler(CommandHandler('r', returned_borrow))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(CommandHandler('h', help_command))

Store = BorrowList()

bot_updater.start_polling()
