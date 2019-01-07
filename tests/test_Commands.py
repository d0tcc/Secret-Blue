from __future__ import absolute_import
import unittest
from Commands import *
import GamesController
from Boardgamebox.Board import Board
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player

from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator


class TestCommands(unittest.TestCase):

    def setUp(self):
        # For use within the tests we nee some stuff. Starting with a Mockbot
        self.bot = Mockbot()
        # Some generators for users and chats
        self.ug = UserGenerator()
        self.cg = ChatGenerator()
        # And a Messagegenerator and updater (for use with the bot.)
        self.mg = MessageGenerator(self.bot)
        self.updater = Updater(bot=self.bot)
        GamesController.init()

    def test_ping(self):
        # Then register the handler with he updater's dispatcher and start polling
        self.updater.dispatcher.add_handler(CommandHandler("ping", command_ping))
        self.updater.start_polling()
        # create with random user
        update = self.mg.get_message(text="/ping")
        # We insert the update with the bot so the updater can retrieve it.
        self.bot.insertUpdate(update)
        # sent_messages is the list with calls to the bot's outbound actions. Since we hope the message we inserted
        # only triggered one sendMessage action it's length should be 1.
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "pong - v0.4")
        # Always stop the updater at the end of a testcase so it won't hang.
        self.updater.stop()

    def test_start(self):
        self.updater.dispatcher.add_handler(CommandHandler("start", command_start))
        self.updater.start_polling()
        update = self.mg.get_message(text="/start")
        self.bot.insertUpdate(update)
        self.assertEqual(len(self.bot.sent_messages), 2)
        start = self.bot.sent_messages[0]
        self.assertEqual(start['method'], "sendMessage")
        self.assertIn("Secret Blue is a social deduction game", start['text'])
        help = self.bot.sent_messages[1]
        self.assertEqual(help['method'], "sendMessage")
        self.assertIn("The following commands are available", help['text'])
        self.updater.stop()

    def test_symbols(self):
        self.updater.dispatcher.add_handler(CommandHandler("symbols", command_symbols))
        self.updater.start_polling()
        update = self.mg.get_message(text="/symbols")
        self.bot.insertUpdate(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("The following symbols can appear on the board:", sent['text'])
        self.updater.stop()

    def test_board_when_there_is_no_game(self):
        self.updater.dispatcher.add_handler(CommandHandler("board", command_board))
        self.updater.start_polling()
        update = self.mg.get_message(text="/board")
        self.bot.insertUpdate(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("There is no game in this chat. Create a new game with /newgame", sent['text'])
        self.updater.stop()

    def test_board_when_game_is_not_running(self):
        game = Game(-999, 12345)
        GamesController.games[-999] = game
        self.updater.dispatcher.add_handler(CommandHandler("board", command_board))
        self.updater.start_polling()
        chat = self.cg.get_chat(cid=-999)
        update = self.mg.get_message(chat=chat, text="/board")
        self.bot.insertUpdate(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("There is no running game in this chat. Please start the game with /startgame", sent['text'])
        self.updater.stop()

    def test_board_when_game_is_running(self):
        game = Game(-999, 12345)
        game.board = Board(5, game)
        GamesController.games[-999] = game
        self.updater.dispatcher.add_handler(CommandHandler("board", command_board))
        self.updater.start_polling()
        chat = self.cg.get_chat(cid=-999)
        update = self.mg.get_message(chat=chat, text="/board")
        self.bot.insertUpdate(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("--- Liberal acts ---", sent['text'])
        self.updater.stop()
