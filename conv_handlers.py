import config
from telegram import ext as tg_ext
import flow
from bot import bot
from telegram.ext.filters import Filters


# tg_ext.ConversationHandler intended to create a dialog between user and bot.
# It's waiting for user input before to continue.
# Entry point - function name to call if the event has come. States - dict of conversation stages.
# While not returned another state, the user will be staying in the same stage.
# State consist of handlers. (Only one) Handler catching update and processing it.
# Beware, tg_ext.Filters.text catching also a commands,
# so put it at the end of list to give chance to other handlers or add an additional filter by bitwise operator.

# Immediately after entering to the state it waiting for the update and pass it to the handler. If
# no appropriate handler, fallback will be activated and get the update (there is empty). Every handler (command,
# message, etc.) consists of two things: event and action (function to call). Handler forcibly passing update (event,
# message for example) to func and context in the params. To go back user must send key phrase, Handler inside the
# state will catch it and call the corresponding func, key phrase will be the update itself. 'config.back_r' goes
# back 2 steps to write to the user what he should answer. One stage will only wait for the message. Each stage does
# two things: processes the received message and sends a new message. (This annoys me also and violates the Python
# rule "one function, one action")

conversation_registration = tg_ext.ConversationHandler(

    entry_points=[tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.start_reg_r), callback=flow.start_reg)],

    states={

        0: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),  # &~ are means "and not"
            callback=flow.start_reg_handler)],

        1: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_name_handler)],

        2: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_goal_handler)],

        3: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_gender_handler)],

        4: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_age_handler)],

        5: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text | tg_ext.Filters.location & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_location_handler)],

        6: [tg_ext.MessageHandler(filters=tg_ext.Filters.photo, callback=flow.add_photo),
            tg_ext.MessageHandler(
                filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
                callback=flow.user_photos_handler), ],

        7: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_comment_handler)],

        8: [tg_ext.MessageHandler(
            filters=tg_ext.Filters.text & ~Filters.regex(config.start_reg_fallbacks_r),
            callback=flow.user_confirm_handler)]
    },
    # start_reg_r before conversations_r cuz a last one will be catch a first one
    fallbacks=[
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.back_r), callback=flow.go_back),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.back_r), callback=flow.go_next),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.start_reg_r), callback=flow.start_reg),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.cancel_r), callback=bot.end_conversation),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.another_conversation_r), callback=lambda *_: -1),
        # *_ -infinite args
    ]
)

conversation_partner = tg_ext.ConversationHandler(
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.conversationhandler.html#
    # telegram.ext.ConversationHandler.conversation_timeout
    conversation_timeout=3000,  # Value in seconds for dropping db connection and user temporary tables
    entry_points=[
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.start_search_r), callback=flow.start_search)],

    states={
        0: [
            tg_ext.MessageHandler(filters=tg_ext.Filters.text & ~Filters.regex(config.start_search_fallbacks_r),
                                  callback=flow.start_search_handler)],

        1: [
            tg_ext.MessageHandler(filters=tg_ext.Filters.text & ~Filters.regex(config.start_search_fallbacks_r),
                                  callback=flow.target_goal_handler)],

        2: [
            tg_ext.MessageHandler(filters=tg_ext.Filters.text & ~Filters.regex(config.start_search_fallbacks_r),
                                  callback=flow.target_gender_handler)],

        3: [
            tg_ext.MessageHandler(filters=tg_ext.Filters.text & ~Filters.regex(config.start_search_fallbacks_r),
                                  callback=flow.target_age_handler)],

        4: [
            tg_ext.MessageHandler(filters=tg_ext.Filters.text & ~Filters.regex(config.start_search_fallbacks_r),
                                  callback=flow.target_show_match_handler)],

        # See https://stackoverflow.com/a/61275118/11277611
        tg_ext.ConversationHandler.TIMEOUT: [
            tg_ext.TypeHandler(object,
                               callback=lambda _, context: context.user_data['NewUser'].connection.close())]
    },
    fallbacks=[
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.back_r), callback=flow.go_back),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.start_reg_r), callback=flow.start_reg),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.cancel_r), callback=bot.end_conversation),
        tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.conversations_r), callback=lambda *_: -1),
    ])

conversation_create_post = tg_ext.ConversationHandler(
    entry_points=[tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.create_post_r), callback=flow.create_post)],

    states={  # filters.all -To reply that format is incorrect
        0: [
            tg_ext.MessageHandler(filters=tg_ext.Filters.all & ~Filters.regex(config.create_post_fallbacks_r),
                                  callback=flow.show_sample_handler)],

        1:
            [tg_ext.MessageHandler(filters=tg_ext.Filters.text & ~Filters.regex(config.create_post_fallbacks_r),
                                   callback=flow.post_confirm_handler)], },
    fallbacks=[tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.create_post_r), callback=flow.create_post),
               tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.cancel_r), callback=bot.end_conversation),
               tg_ext.MessageHandler(filters=tg_ext.Filters.regex(config.conversations_r), callback=lambda *_: -1),
               ]
)
