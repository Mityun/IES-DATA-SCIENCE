import math
from random import random

INITIAL_MONEY = 5
INITIAL_WATER_LEVEL = 5
INITIAL_PROD_LEVEL = 3

def error():
    assert False


class Player():
    def __init__(self, player_id, name):
        self.id = player_id
        self.name = name
        self.money = INITIAL_MONEY
        self.prod_level = INITIAL_PROD_LEVEL
        self.lobster_count = 0
        self.yacht = list()
        self.choice = None
        self.clean = 0
        self.ready = False

    def get_stat(self):
        return '''Текущий бюджет равен {}$ 
         Уровень производства {}
         Съедено лобстеров - {}
         Имеющиеся яхты: {}'''.format(self.money, self.prod_level, self.lobster_count, ", ".join(self.yacht))

    def buy_lobster(self):
        if self.money >= 5:
            self.money -= 5
            self.lobster_count += 1
            return True
        else:
            return False

    def buy_yacht(self, yacht_name):
        if self.money >= 18:
            self.money -= 18
            self.yacht += [yacht_name]
            return True
        else:
            return False

    def upgrade_prod_level(self):
        if self.money >= 5:
            self.money -= 5
            self.prod_level += 1
            return True
        else:
            return False

    def clean_lake(self):
        if self.money >= 5:
            self.money -= 5
            self.clean += 1
            return True
        else:
            return False

    def make_choice(self, choice):
        self.choice = choice
        return True


class Lake:
    def __init__(self):
        self.water_level = INITIAL_WATER_LEVEL
        self.turn = 0
        self.players = dict()

    def get_stat(self):
        return f"#result Ход: {self.turn}. Уровень озера: {self.water_level} \n  " \
               f"Яхты на озере: \n {', '.join(self.get_yacht())}\n"


    def get_yacht(self):
        x = sum([self.players[i].yacht for i in self.players], start=[])
        x.sort(key=random)
        return x

    def is_ready(self):
        for i in self.players:
            if not self.players[i].ready:
                return False
        return True

    def add_player(self, *args, **kwargs):
        assert self.turn == 0
        player = Player(*args, **kwargs)
        self.players[player.id] = player

    def proceed_round(self):
        water_coef = math.ceil(self.water_level / 20)
        for i in self.players:
            player = self.players[i]
            if player.choice == 'pollute':
                choice_coef = 2
                self.water_level -= 3
            else:
                choice_coef = 1
            player.money += water_coef * choice_coef * player.prod_level
            self.water_level += 3 * player.clean
            player.choice = None
            player.clean = 0
            player.ready = False
        self.turn += 1
