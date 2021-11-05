import unittest
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler
from telegram.ext import Updater
from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator

import flow
import conv_handlers

"""
This is an example to show how the ptbtest suite can be used.
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
"""


class TestConversation(unittest.TestCase):
    def setUp(self):
        self.bot = Mockbot()
        self.chat_generator = ChatGenerator()
        self.user_generator = UserGenerator()
        self.message_generator = MessageGenerator(self.bot)
        self.mg_get_message = self.message_generator.get_message
        self.updater = Updater(bot=self.bot)
        self.user = self.user_generator.get_user()
        # self.user2 = self.user_generator.get_user()
        self.chat = self.chat_generator.get_chat(type="group")  # Why group?
        # self.chat2 = self.chat_generator.get_chat(user=self.user)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(conv_handlers.conversation_registration)
        self.updater.start_polling()
        pass

    def test_reg(self):
        self.bot.insertUpdate(self.mg_get_message(user=self.user, chat=self.chat, text="/reg", parse_mode="HTML"))
        self.assertTrue(self.bot.sent_messages[-1]['text'].startswith("Отличное решение!"))

    def test_reg_handler(self):
        self.bot.insertUpdate(self.mg_get_message(user=self.user, chat=self.chat, text="Поехали"))
        self.assertTrue(self.bot.sent_messages[-1]['text'].lower().strip().startswith("шаг 1 из 7"))

    def test_user_name_handler(self):
        update = self.mg_get_message(user=self.user, chat=self.chat, text="David")
        self.bot.insertUpdate(update)
        # Check text "David"
        self.assertTrue(self.bot.sent_messages[-1]['text'].lower().strip().startswith("шаг 2 из 7"))
        # self.bot.insertUpdate(self.mg_get_message(user=self.user, chat=self.chat, text='Alex'))
        # Check text "Alex"
        # self.assertTrue(self.bot.sent_messages[-1]['text'].lower().strip().startswith("шаг 2 из 7"))
        # ERROR, the cov handler already at another state and waiting for int data (age)
    #
    # def test_reg(self, reply):
    #     self.assertTrue(reply['text'].startswith("Отличное решение!"))

    def test_reg_conv(self):
        self.test_reg()
        self.test_reg_handler()
        self.test_user_name_handler()
        self.bot.insertUpdate(self.mg_get_message(user=self.user, chat=self.chat, text="Общаться"))
        self.assertTrue(self.bot.sent_messages[-1]['text'].startswith("шаг 3 из 7"))

        # # now let's see what happens when another user in another chat starts conversating with the bot
        # self.bot.insertUpdate(self.mg_get_message(user=user2, chat=chat2, text="/reg", parse_mode="HTML"))
        # data = self.bot.sent_messages[-1]
        # self.assertEqual(data['chat_id'], chat2.id)
        # self.assertNotEqual(data['chat_id'], chat.id)
        # # and cancels his conv.
        # self.bot.insertUpdate(self.mg_get_message(user=user2, chat=chat2, text="Cancel"))
        # data = self.bot.sent_messages[-1]
        self.updater.stop()


if __name__ == '__main__':
    unittest.main()

# class TestRegCH(unittest.TestCase):
#     def setUp(self):
#         """
#         For use within the tests we need some stuff.
#         Starting with a Mockbot, some generators for users, chats, messages
#         and updater (for use with the bot.)
#         Then register the handler with he updater's dispatcher and start polling
#         We want to simulate a message. Since we don't care which user sends it we let the MessageGenerator
#         create random ones
#         """
#         self.bot = Mockbot()
#         self.ug = UserGenerator()
#         self.cg = ChatGenerator()
#         self.mg = MessageGenerator(self.bot)
#         self.updater = Updater(bot=self.bot)
#         self.dispatcher = self.updater.dispatcher
#         self.user = self.ug.get_user(first_name="David_test", last_name="Shiko_test")
#         self.chat = self.cg.get_chat(user=self.user)
#         self.dispatcher.add_handler(conv_handlers.conversation_registration, group=1)
#         self.updater.start_polling()
#
#     def test_CH(self):
#         update = self.mg.get_message(user=self.user, chat=self.chat, text="/reg", parse_mode="HTML")
#         self.bot.insertUpdate(update=update)
#         reply = self.bot.sent_messages[0]
#         self.assertTrue(reply['text'].startswith("Отличное решение!"))
#
#     def test_reg_confirm(self):
#         update = self.mg.get_message(user=self.user, chat=self.chat, text="Поехали", parse_mode="HTML")
#         self.bot.insertUpdate(update=update)
#         reply = self.bot.sent_messages[0]
#         self.assertTrue(reply['text'].startswith("шаг 1 из 7"))
#         self.updater.stop()
