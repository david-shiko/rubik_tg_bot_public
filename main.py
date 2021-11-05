import config
import DDL
import generation
import conv_handlers
import flow
import postconfig
from bot import bot
from postconfig import global_connection
from telegram import ext as tg_ext


def faq(update, _):
    update.message.reply_text('''Что дает мне регистрация?

Регистарция позволяет другим людям найти вас.
Когда вы ипсользуете команду "старт", вы ищете профили, которые уже зарегистрированы.
Что бы ваш профиль появлялся в результатах поиска у других людей - вам небходимо зарегистрироваться.


Зачем ставить оценивать посты?

Работа бота имеет смысл только если вы оцениваете посты.
Бот использует оценки, поставленные вами, что бы результат поиска был более подходящим.
Бот ищет людей, которые поставили оценки под теми же самыми постми,
под которыми их поставили вы.

@rubik_love_bot, собери свою любовь. Версия 0.95.
Автор - @david_shiko.
''')


def show_help(update, _):
    update.message.reply_text(f'Вот список команд, которые я понимаю:\n {config.commands}')


def test(update, _):
    pass


def reassign_db_connection(_, context):  # Not in use
    if not context.userd_data['connection'] or context.userd_data['connection'].closed:
        context.userd_data['connection'] = postconfig.DBConnectionManager.get_connection()


if __name__ == '__main__':
    DDL.create_db(connection=global_connection)
    updater = tg_ext.Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher
    # "Group" - specify execution order
    # dispatcher.add_handler(tg_ext.TypeHandler(type=tg_Update, callback=lambda update, context: None, group=-1)
    # dispatcher.add_error_handler(tg_ext.TypeHandler(type=object, callback=reassign_db_connection))
    dispatcher.add_handler(tg_ext.MessageHandler(tg_ext.Filters.regex(config.help_r), show_help))
    dispatcher.add_handler(tg_ext.CommandHandler('faq', faq))
    dispatcher.add_handler(tg_ext.CommandHandler('test', test, tg_ext.Filters.user(config.ADMINS)))
    dispatcher.add_handler(tg_ext.CommandHandler('gen_likes', generation.gen_likes, tg_ext.Filters.user(config.ADMINS)))
    dispatcher.add_handler(tg_ext.CommandHandler('gen_posts', generation.gen_posts, tg_ext.Filters.user(config.ADMINS)))
    dispatcher.add_handler(tg_ext.CommandHandler('gen_all', generation.gen_all, tg_ext.Filters.user(config.ADMINS)))
    dispatcher.add_handler(tg_ext.CommandHandler('drop_all', generation.drop_all, tg_ext.Filters.user(config.ADMINS)))
    dispatcher.add_handler(tg_ext.CommandHandler('get_post', flow.get_post))
    dispatcher.add_handler(tg_ext.CommandHandler('send', flow.send_posts, tg_ext.Filters.user(config.ADMINS)))
    dispatcher.add_handler(conv_handlers.conversation_registration, group=1)
    dispatcher.add_handler(conv_handlers.conversation_partner, group=1)
    dispatcher.add_handler(conv_handlers.conversation_create_post, group=1)
    dispatcher.add_handler(tg_ext.CallbackQueryHandler(flow.post_vote_handler, tg_ext.Filters.user(config.ADMINS), pattern=r'vote'))
    dispatcher.add_handler(tg_ext.CallbackQueryHandler(flow.additional_filters_handler, pattern=r'checkboxes'))
    # dispatcher.add_error_handler(callback=callable)
    updater.start_polling()
    updater.idle()
