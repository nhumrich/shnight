from copy import copy
import random


class Game:
    def __init__(self, owner_id):
        self.status = 'open'
        self.hitler = None
        self.fascists = []
        self.players = []
        self.owner_id = owner_id
        self.add_player(owner_id)
        self.seating = {}
        self.elections = False
        self.votes = {'ja': [], 'nein': []}

    def toggle_elections(self):
        self.elections = not self.elections
        if not self.elections:
            self.reset_votes()

    def reset_votes(self):
        self.votes = {'ja': [], 'nein': []}

    def add_vote(self, user_id, user_is_for):
        if user_id in self.players:
            if user_id not in self.votes['ja'] and user_id not in self.votes['nein']:
                if user_is_for:
                    self.votes['ja'].append(user_id)
                else:
                    self.votes['nein'].append(user_id)

    def add_player(self, user_id):
        self.players.append(user_id)

    def remove_player(self, user_id):
        if user_id in self.players:
            self.players.remove(user_id)
            if self.owner_id == user_id and len(self.players) > 0:
                self.owner_id = random.choice(self.players)

    def get_seat(self, user_id):
        if self.status != 'closed':
            return 0
        return self.seating[user_id]

    def get_role(self, user_id):
        if user_id == self.hitler:
            return 2
        if user_id in self.fascists:
            return 1
        return 0

    def get_players(self):
        return self.players

    def end(self):
        self.hitler = None
        self.fascists = []
        self.status = 'open'

    def generate_seating(self):
        players = copy(self.players)
        for idx in range(len(players)):
            selection = random.choice(players)
            self.seating[selection] = idx
            players.remove(selection)

    def generate_roles(self):
        self.hitler = None
        self.fascists = []
        cur_players = copy(self.players)
        num_of_players = len(cur_players)
        self.status = 'starting'

        if num_of_players in (5, 6):
            num_of_fasc = 1
        else:
            num_of_fasc = num_of_players // 3

        for _ in range(num_of_fasc):
            p = random.choice(cur_players)
            self.fascists.append(p)
            cur_players.remove(p)

        hitty = random.choice(cur_players)
        self.hitler = hitty
        del cur_players
        self.status = 'closed'

