from Constants import players, pile
import random

class Board(object):
    def __init__(self, playercount, game):
        self.state = State()
        self.num_players = playercount
        self.fascist_track_actions = players[self.num_players]["track"]
        self.policies = random.sample(pile, len(pile))
        self.game = game
        self.discards = []
        self.previous = []

    def print_board(self):
        board = "--- Liberal acts ---\n"
        for i in range(5):
            if i < self.state.liberal_track:
                board += u"\u2716\uFE0F" + " " #X
            elif i >= self.state.liberal_track and i == 4:
                board += u"\U0001F54A" + " " #dove
            else:
                board += u"\u25FB\uFE0F" + " " #empty
        board += "\n--- Fascist acts ---\n"
        for i in range(6):
            if i < self.state.fascist_track:
                board += u"\u2716\uFE0F" + " " #X
            else:
                action = self.fascist_track_actions[i]
                if action == None:
                    board += u"\u25FB\uFE0F" + " "  # empty
                elif action == "policy":
                    board += u"\U0001F52E" + " " # crystal
                elif action == "inspect":
                    board += u"\U0001F50E" + " " # inspection glass
                elif action == "kill":
                    board += u"\U0001F5E1" + " " # knife
                elif action == "win":
                    board += u"\u2620" + " " # skull
                elif action == "choose":
                    board += u"\U0001F454" + " " # tie

        board += "\n--- Election counter ---\n"
        for i in range(3):
            if i < self.state.failed_votes:
                board += u"\u2716\uFE0F" + " " #X
            else:
                board += u"\u25FB\uFE0F" + " " #empty

        board += "\n--- Presidential order  ---\n"
        for player in self.game.player_sequence:
            board += player.name + " " + u"\u27A1\uFE0F" + " "
        board = board[:-3]
        board += u"\U0001F501"
        board += "\n\nThere are " + str(len(self.policies)) + " policies left on the pile."
        if self.state.fascist_track >= 3:
            board += "\n\n" + u"\u203C\uFE0F" + " Beware: If Hitler gets elected as Chancellor the fascists win the game! " + u"\u203C\uFE0F"
        if len(self.state.not_hitlers) > 0:
            board += "\n\nWe know that the following players are not Hitler because they got elected as Chancellor after 3 fascist policies:\n"
            for nh in self.state.not_hitlers:
                board += nh.name + ", "
            board = board[:-2]
        return board


class State(object):
    """Storage object for game state"""
    def __init__(self):
        self.liberal_track = 0
        self.fascist_track = 0
        self.failed_votes = 0
        self.president = None
        self.nominated_president = None
        self.nominated_chancellor = None
        self.chosen_president = None
        self.chancellor = None
        self.dead = 0
        self.last_votes = {}
        self.game_endcode = 0
        self.drawn_policies = []
        self.player_counter = 0
        self.veto_refused = False
        self.not_hitlers = []