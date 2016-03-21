"""
Used to simulate a random pokemon battle as per the rules of PokemonShowdown.
"""
import random
import operator
import numpy as np
import simplejson as json


types = json.loads(open('type.json', 'r').read())
moves = json.loads(open('moves.json', 'r').read())
type_names = sorted(types.keys())

def calc_damage(attacker, defender, move, crit=False):
    "calculate modifier and damage"
    stab = 1.5 if (move.type_ in attacker.types) else 1
    atk = attacker.spatk if (move.type_ in attacker.types) else attacker.atk
    def_ = attacker.spdef if (move.type_ in attacker.types) else attacker.def_
    type_ = reduce(operator.mul, [float(types[move.type_][type_names.index(t)]) for t in defender.types])
    #crit = (random.uniform(0, 1.0) < 1/16.0) ? 2 : 1
    #rand = random.uniform(0.85, 1.0)
    crit = 2 if crit else 1
    rand = 0.925
    modifier = stab * type_ * crit * rand
    damage = (2 * attacker.lvl + 10) / 250.0 * atk / def_ * move.base_power + 2
    damage *= modifier
    return int(damage)

class Pokemon:
    def __init__(self, name, lvl, hp, atk, def_, spatk, spdef, speed, types, move_names):
        self.name = name
        self.lvl = lvl
        self.hp = hp
        self.totalhp = hp
        self.atk = atk
        self.def_ = def_
        self.spatk = spatk
        self.spdef = spdef
        self.speed = speed
        self.types = types
        self.moves = [Move(name) for name in move_names]

    def __repr__(self):
        return "<%s>" % self.__str__()

    def __str__(self):
        return "%s hp:%s" % (self.name, self.hp)

class Move:
    def __init__(self, name, base_power=None, accuracy=None, pp=None, type_=None):
        move = moves[name]
        self.name = name
        self.base_power = move['power'] if not base_power else base_power
        self.accuracy = move['accuracy'] if not accuracy else accuracy 
        self.pp = move['pp'] if not pp else pp
        self.type_ = move['type']['name'] if not type_ else type_

def gen_team():
    team = []
    for i in range(2):
        team.append(Pokemon('pikachu%s' % i, 100, 411, 146, 116, 136, 136, 216, ['electric'], ['thunder', 'thunder-punch']))
    for i in range(2):
        team.append(Pokemon('gengar%s' % i, 100, 261, 166, 156, 296, 186, 256, ['ghost', 'poison'], ['shadow-ball', 'shadow-punch']))
    #arceus = Pokemon('arceus', 100, 381, 276, 276, 276, 276, 276, ['normal'], ['judgment', 'acrobatics'])
    return team




