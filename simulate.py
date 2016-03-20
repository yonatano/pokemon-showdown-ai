"""
Used to simulate a random pokemon battle as per the rules of PokemonShowdown.
"""
import random
import operator
import numpy as np
import simplejson as json


types = json.loads(open('types.json', 'r').read())
type_names = types.keys()

def calc_damage(attacker, defender, move, crit):
    "calculate modifier and damage"
    stab = (move.type == attacker.type) ? 1.5 : 1
    type_ = reduce(operator.mul, [types[move.type][type_names.index(t)] for t in defender.types])
    #crit = (random.uniform(0, 1.0) < 1/16.0) ? 2 : 1
    rand = random.uniform(0.85, 1.0)
    modifier = stab * type_ * crit * rand
    damage = (2 * attacker.level + 10) / 250.0 * attacker.atk / attacker.def * move.base + 2
    damage *= modifier
    return damage

class Pokemon:
    def __init__(self, name, hp, atk, def_, speed, types):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.def_ = def_
        self.speed = speed
        self.types = types

class Move:
    def __init__(self, name, base_power, accuracy, pp, type_):
        self.name = name
        self.base_power = base_power
        self.accuracy = accuracy
        self.pp = pp
        self.type_ = type_



