from random import shuffle

class Game(object):
    def __init__(self, cid, initiator):
        self.playerlist = {}
        self.player_sequence = []
        self.cid = cid
        self.board = None
        self.initiator = initiator

    def add_player(self, uid, player):
        self.playerlist[uid] = player

    def get_hitler(self):
        for uid in self.playerlist:
            if self.playerlist[uid].role == "Hitler":
                return self.playerlist[uid]

    def get_fascists(self):
        fascists = []
        for uid in self.playerlist:
            if self.playerlist[uid].role == "Fascist":
                fascists.append(self.playerlist[uid])
        return fascists

    def shuffle_player_sequence(self):
        for uid in self.playerlist:
            self.player_sequence.append(self.playerlist[uid])
        shuffle(self.player_sequence)

    def remove_from_player_sequence(self, Player):
        for p in self.player_sequence:
            if p.uid == Player.uid:
                p.remove(Player)

    def print_roles(self):
        rtext = ""
        if self.board is None:
            #game was not started yet
            return rtext
        else:
            for p in self.playerlist:
                rtext += self.playerlist[p].name + "'s "
                if self.playerlist[p].is_dead:
                    rtext += "(dead) "
                rtext += "secret role was " + self.playerlist[p].role + "\n"
            return rtext