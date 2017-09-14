import json
import logging as log

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import MainController
import GamesController
from Constants.Config import STATS
from Boardgamebox.Board import Board
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player
from Constants.Config import ADMIN

# Enable logging
log.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=log.INFO,
                filename='logs/logging.log')

logger = log.getLogger(__name__)

commands = [  # command description used in the "help" command
    '/help - Gives you information about the available commands',
    '/start - Gives you a short piece of information about Secret Hitler',
    '/symbols - Shows you all possible symbols of the board',
    '/rules - Gives you a link to the official Secret Hitler rules',
    '/newgame - Creates a new game',
    '/join - Joins an existing game',
    '/startgame - Starts an existing game when all players have joined',
    '/cancelgame - Cancels an existing game. All data of the game will be lost',
    '/board - Prints the current board with fascist and liberals tracks, presidential order and election counter'
]

symbols = [
    u"\u25FB\uFE0F" + ' Empty field without special power',
    u"\u2716\uFE0F" + ' Field covered with a card',  # X
    u"\U0001F52E" + ' Presidential Power: Policy Peek',  # crystal
    u"\U0001F50E" + ' Presidential Power: Investigate Loyalty',  # inspection glass
    u"\U0001F5E1" + ' Presidential Power: Execution',  # knife
    u"\U0001F454" + ' Presidential Power: Call Special Election',  # tie
    u"\U0001F54A" + ' Liberals win',  # dove
    u"\u2620" + ' Fascists win'  # skull
]


def command_symbols(bot, update):
    cid = update.message.chat_id
    symbol_text = "The following symbols can appear on the board: \n"
    for i in symbols:
        symbol_text += i + "\n"
    bot.send_message(cid, symbol_text)


def command_board(bot, update):
    cid = update.message.chat_id
    if cid in GamesController.games.keys():
        if GamesController.games[cid].board:
            bot.send_message(cid, GamesController.games[cid].board.print_board())
        else:
            bot.send_message(cid, "There is no running game in this chat. Please start the game with /startgame")
    else:
        bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")


def command_start(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid,
                     "\"Secret Hitler is a social deduction game for 5-10 people about finding and stopping the Secret Hitler."
                     " The majority of players are liberals. If they can learn to trust each other, they have enough "
                     "votes to control the table and win the game. But some players are fascists. They will say whatever "
                     "it takes to get elected, enact their agenda, and blame others for the fallout. The liberals must "
                     "work together to discover the truth before the fascists install their cold-blooded leader and win "
                     "the game.\"\n- official description of Secret Hitler\n\nAdd me to a group and type /newgame to create a game!")
    command_help(bot, update)


def command_rules(bot, update):
    cid = update.message.chat_id
    btn = [[InlineKeyboardButton("Rules", url="http://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf")]]
    rulesMarkup = InlineKeyboardMarkup(btn)
    bot.send_message(cid, "Read the official Secret Hitler rules:", reply_markup=rulesMarkup)


# pings the bot
def command_ping(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, 'pong - v0.3')


# prints statistics, only ADMIN
def command_stats(bot, update):
    cid = update.message.chat_id
    if cid == ADMIN:
        with open(STATS, 'r') as f:
            stats = json.load(f)
        stattext = "+++ Statistics +++\n" + \
                    "Liberal Wins (policies): " + str(stats.get("libwin_policies")) + "\n" + \
                    "Liberal Wins (killed Hitler): " + str(stats.get("libwin_kill")) + "\n" + \
                    "Fascist Wins (policies): " + str(stats.get("fascwin_policies")) + "\n" + \
                    "Fascist Wins (Hitler chancellor): " + str(stats.get("fascwin_hitler")) + "\n" + \
                    "Games cancelled: " + str(stats.get("cancelled")) + "\n\n" + \
                    "Total amount of groups: " + str(len(stats.get("groups"))) + "\n" + \
                    "Games running right now: "
        bot.send_message(cid, stattext)


# help page
def command_help(bot, update):
    cid = update.message.chat_id
    help_text = "The following commands are available:\n"
    for i in commands:
        help_text += i + "\n"
    bot.send_message(cid, help_text)


def command_newgame(bot, update):
    cid = update.message.chat_id
    game = GamesController.games.get(cid, None)
    groupType = update.message.chat.type
    if groupType not in ['group', 'supergroup']:
        bot.send_message(cid, "You have to add me to a group first and type /newgame there!")
    elif game:
        bot.send_message(cid, "There is currently a game running. If you want to end it please type /cancelgame!")
    else:
        GamesController.games[cid] = Game(cid, update.message.from_user.id)
        with open(STATS, 'r') as f:
            stats = json.load(f)
        if cid not in stats.get("groups"):
            stats.get("groups").append(cid)
            with open(STATS, 'w') as f:
                json.dump(stats, f)
        bot.send_message(cid, "New game created! Each player has to /join the game.\nThe initiator of this game (or the admin) can /join too and type /startgame when everyone has joined the game!")


def command_join(bot, update):
    groupName = update.message.chat.title
    cid = update.message.chat_id
    groupType = update.message.chat.type
    game = GamesController.games.get(cid, None)
    fname = update.message.from_user.first_name

    if groupType not in ['group', 'supergroup']:
        bot.send_message(cid, "You have to add me to a group first and type /newgame there!")
    elif not game:
        bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
    elif game.board:
        bot.send_message(cid, "The game has started. Please wait for the next game!")
    elif update.message.from_user.id in game.playerlist:
        bot.send_message(game.cid, "You already joined the game, %s!" % fname)
    elif len(game.playerlist) >= 10:
        bot.send_message(game.cid, "You have reached the maximum amount of players. Please start the game with /startgame!")
    else:
        uid = update.message.from_user.id
        player = Player(fname, uid)
        try:
            bot.send_message(uid, "You joined a game in %s. I will soon tell you your secret role." % groupName)
            game.add_player(uid, player)
        except Exception:
            bot.send_message(game.cid,
                             fname + ", I can\'t send you a private message. Please go to @thesecrethitlerbot and click \"Start\".\nYou then need to send /join again.")
        log.info("%s (%d) joined a game in %d" % (fname, uid, game.cid))
        if len(game.playerlist) > 4:
            bot.send_message(game.cid, fname + " has joined the game. Type /startgame if this was the last player and you want to start with %d players!" % len(game.playerlist))
        elif len(game.playerlist) == 1:
            bot.send_message(game.cid, "%s has joined the game. There is currently %d player in the game and you need 5-10 players." % (fname, len(game.playerlist)))
        else:
            bot.send_message(game.cid, "%s has joined the game. There are currently %d players in the game and you need 5-10 players." % (fname, len(game.playerlist)))


def command_startgame(bot, update):
    log.info('command_startgame called')
    cid = update.message.chat_id
    game = GamesController.games.get(cid, None)
    if not game:
        bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
    elif game.board:
        bot.send_message(cid, "The game is already running!")
    elif update.message.from_user.id != game.initiator or bot.getChatMember(cid, update.message.from_user.id).status not in ("administrator", "creator"):
        bot.send_message(game.cid, "Only the initiator of the game or a group admin can start the game with /startgame")
    elif len(game.playerlist) < 5:
        bot.send_message(game.cid, "There are not enough players (min. 5, max. 10). Join the game with /join")
    else:
        player_number = len(game.playerlist)
        MainController.inform_players(bot, game, game.cid, player_number)
        MainController.inform_fascists(bot, game, player_number)
        game.board = Board(player_number, game)
        log.info(game.board)
        log.info("len(games) Command_startgame: " + str(len(GamesController.games)))
        game.shuffle_player_sequence()
        game.board.state.player_counter = 0
        bot.send_message(game.cid, game.board.print_board())
        #group_name = update.message.chat.title
        #bot.send_message(ADMIN, "Game of Secret Hitler started in group %s (%d)" % (group_name, cid))
        MainController.start_round(bot, game)

def command_cancelgame(bot, update):
    log.info('command_cancelgame called')
    cid = update.message.chat_id
    if cid in GamesController.games.keys():
        game = GamesController.games[cid]
        status = bot.getChatMember(cid, update.message.from_user.id).status
        if update.message.from_user.id == game.initiator or status in ("administrator", "creator"):
            MainController.end_game(bot, game, 99)
        else:
            bot.send_message(cid, "Only the initiator of the game or a group admin can cancel the game with /cancelgame")
    else:
        bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
