"""
Used to simulate a random pokemon battle as per the rules of PokemonShowdown.
"""
import random
import operator
import numpy as np
import simplejson as json


types = json.loads(open('data/type.json', 'r').read())
moves = json.loads(open('data/moves.json', 'r').read())
type_names = sorted(types.keys())

def calc_damage(attacker, defender, move, crit=False):
    "calculate modifier and damage"
    defender.affected = True
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

    def attrs(self):
        return ('name', 'lvl', 'hp', 'totalhp', 'atk', 'def_', 
                'spatk', 'spdef', 'speed', 'types', 'moves')

    def __hash__(self):
        return hash(self.attrs())

    def __values(self):
        return (getattr(self, attr) for attr in self.attrs())

    def __cmp__(self, other):
        for s, o in zip(self.__values(), other.__values()):
            c = cmp(s, o)
            if c:
                return c
        return 0

    def __eq__(self, other):
        return cmp(self, other) == 0

    def __lt__(self, other):
        return cmp(self, other) < 0

    def __gt__(self, other):
        return cmp(self, other) > 0

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

    def attrs(self):
        return ('name', 'base_power', 'pp', 'type_')

    def __hash__(self):
        return hash(self.attrs())

    def __values(self):
        return (getattr(self, attr) for attr in self.attrs())

    def __cmp__(self, other):
        for s, o in zip(self.__values(), other.__values()):
            c = cmp(s, o)
            if c:
                return c
        return 0

    def __eq__(self, other):
        return cmp(self, other) == 0

    def __repr__(self):
        return "<move: %s>" % self.__str__()

    def __str__(self):
        return self.name

def gen_team():
    team = []

    team.append(Pokemon('rayquaza', 100, 351, 200, 216, 336, 216, 226, ['dragon', 'flying'], ['draco-meteor', 'earthquake', 'dragon-ascent', 'extreme-speed']))
    team.append(Pokemon('lucario', 100, 281, 200, 176, 266, 176, 216, ['fighting', 'steel'], ['shadow-ball', 'close-combat', 'bullet-punch', 'crunch']))
    team.append(Pokemon('giratina', 100, 441, 259, 276, 212, 276, 216, ['dragon', 'ghost'], ['draco-meteor', 'earthquake', 'dragon-ascent', 'extreme-speed']))
    team.append(Pokemon('dragonite', 85, 276, 259, 192, 201, 201, 167, ['flying', 'dragon'], ['dragon-claw', 'dragon-pulse', 'superpower', 'aqua-tail']))
    team.append(Pokemon('heracross', 100, 301, 286, 186, 116, 226, 206, ['fighting', 'bug'], ['brick-break', 'tackle', 'body-slam', 'megahorn']))
    team.append(Pokemon('cubone', 100, 241, 136, 226, 116, 136, 106, ['ground'], ['earthquake', 'fire-blast', 'fire-punch', 'body-slam']))

    for i in range(6):
        team.append(avg_pokemon())

    return team

def avg_pokemon():
    return Pokemon('heracross', 100, 200, 286, 186, 116, 226, 206, ['fighting', 'bug'], ['brick-break', 'tackle', 'body-slam', 'megahorn'])




