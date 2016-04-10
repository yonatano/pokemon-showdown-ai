"""
Used to simulate a random pokemon battle as per the rules of PokemonShowdown.
"""
import sys
import os
import re
import copy
import random
import operator
import simplejson as json

USE_STAT_MULT = False
TEAMSZ = 6

data = os.path.join(os.path.dirname(__file__), '../data')
data_types = json.loads(open('%s/type.json' % data, 'r').read())
data_moves = json.loads(open('%s/moves.json' % data, 'r').read())
data_pokemon = json.loads(open('%s/pokemon_.json' % data, 'r').read())
data_stage_mults = json.loads(open('%s/moves_stage_multipliers.json' % data, 'r').read())
type_names = sorted(data_types.keys())

def calc_damage(attacker, defender, move, crit=False):
    "calculate modifier and damage"
    stab = 1.5 if (move.type_ in attacker.types) else 1
    atk = attacker.get('spatk') if move.damage_class == 'special' else attacker.get('atk')
    def_ = defender.get('spdef') if move.damage_class == 'special' else defender.get('def_')
    type_ = reduce(operator.mul, [float(data_types[move.type_][type_names.index(t)]) for t in defender.types])
    #crit = (random.uniform(0, 1.0) < 1/16.0) ? 2 : 1
    #rand = random.uniform(0.85, 1.0)
    crit = 2 if crit else 1
    rand = 0.925
    modifier = stab * type_ * crit * rand
    damage = (2 * attacker.lvl + 10) / 250.0 * atk / float(def_) * move.base_power + 2
    damage *= modifier
    return int(damage)

class Pokemon:
    NUM_MULTS = 7
    STAGE_MULTS = {}

    def __init__(self, name, lvl=85, hp=0, thp=0, atk=0, def_=0, spatk=0, spdef=0, speed=0, types=[], move_names=[]):
        self.__class__.STAGE_MULTS = {Pokemon.stats()[i]: i for i in range(self.__class__.NUM_MULTS)}

        self.name = self.clean_name(name)
        self.lvl = int(lvl)
        self.hp = int(hp)
        self.totalhp = self.hp if int(thp) == 0 else int(thp)
        self.atk = int(atk)
        self.def_ = int(def_)
        self.spatk = int(spatk)
        self.spdef = int(spdef)
        self.speed = int(speed)
        self.accuracy = 1.0
        self.evasion = 1.0
        self.types = types
        self.moves = [Move(name) for name in move_names]
        self.stage_multipliers = {name: 0 for name in self.stats()}

    def get(self, stat):
        """get the Pokemon's stat and adjust for stage multiplier"""
        formula_stat = lambda base, mult: base * (2 + max(mult, 0)) / (2.0 - min(mult, 0))
        formula_acc = lambda base, mult: base * (3 + max(mult, 0)) / (3.0 - min(mult, 0))
        formula_eva = lambda base, mult: formula_acc(base, -mult)

        base = getattr(self, stat)
        mult = self.stage_multipliers[stat]
        if stat == 'accuracy':
            return formula_acc(base, mult)
        if stat == 'evasion':
            return formula_eva(base, mult)

        return formula_stat(base, mult)

    @staticmethod
    def clean_name(name):
        re_clean_name = re.compile(r"(.+?)\s")
        if re_clean_name.match(name):
            name = re_clean_name.match(name).groups()[0]
        return name

    def fill_avgs(self):
        pokemon = data_pokemon[self.name.lower()]
        formula_stat = lambda base, lvl, iv, ev: (((base + iv) * 2 + (ev ** 0.5) / 4.0) * lvl / 100.0) + 5
        formula_hp   = lambda base, lvl, iv, ev: formula_stat(base, lvl, iv, ev) + lvl + 5

        stats_ = {
                'hp': 'hp',
                'attack': 'atk',
                'defense': 'def_',
                'special-attack': 'spatk',
                'special-defense': 'spdef',
                'speed': 'speed',
        }
        for stat in pokemon['stats']:
            name = stats_[stat['stat']['name']]
            base = stat['base_stat']
            value = formula_stat(base, self.lvl, 31, 85) #IV:31 / EV:85 (averages)
            setattr(self, name, value)
        self.totalhp = self.hp

        if self.name == 'shedinja': #lol Pokemon is ridiculous
            self.hp = 1

        self.types = [t['type']['name'] for t in pokemon['types']]
        "pick four random moves"
        movelist = pokemon['moves'][:]
        random.shuffle(movelist)
        move_names = [m['move']['name'] for m in movelist[:4]]
        self.moves = [Move(m) for m in move_names]

    @staticmethod
    def stats():
        return ('atk', 'def_', 'spatk', 'spdef', 'speed',
                'accuracy', 'evasion')

    def attrs(self):
        return ('name', 'lvl', 'hp', 'totalhp', 'atk', 'def_', 
                'spatk', 'spdef', 'speed', 'accuracy', 'evasion', 
                'types', 'moves')

    def __hash__(self):
        return hash(self.attrs())

    def __values(self):
        #cmp_attrs = [a for a in self.attrs() if a not in ['hp', 'atk', 'def_', 'spatk', 'spdef', 'speed']]
        #cmp_attrs = ['name']
        return (getattr(self, attr) for attr in self.attrs())

    def __cmp__(self, other):
        for s, o in zip(self.__values(), other.__values()):
            c = cmp(s, o)
            if c:
                return c
        return 0

    def __eq__(self, other):
        other_vals = other.__values() if other is not None else ()
        return [v for v in self.__values()] == [v for v in other_vals]

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "<%s>" % self.__str__()

    def __str__(self):
        return "{0}: {1}%".format(self.name, int(self.hp / float(self.totalhp) * 100))

class Move:
    def __init__(self, name, base_power=None, accuracy=None, pp=None, type_=None, placeholder=False):
        self.set_attrs(name, base_power, accuracy, pp, type_)
        self.placeholder = placeholder

    def set_attrs(self, name, base_power, accuracy, pp, type_):
        name = name.lower().replace(' ', '-')

        #edge-case
        if "hidden-power" in name:
            hidden_pwr = name.split("hidden-power-")
            type_ = hidden_pwr[1] if len(hidden_pwr) > 1 else "normal"
            name = "hidden-power"

        move = data_moves[name]
        self.name = name
        self.base_power = move['power'] if not base_power else base_power
        self.accuracy = move['accuracy'] if not accuracy else accuracy
        self.pp = move['pp'] if not pp else pp
        self.type_ = move['type']['name'] if not type_ else type_
        self.special = (move['damage_class']['name'] == "special")

        self.base_power = int(self.base_power) if self.base_power is not None else 0
        self.accuracy = int(self.accuracy) if self.accuracy is not None else 0
        self.pp = int(self.pp) if self.pp is not None else 0
        self.damage_class = move['damage_class']['name']
        self.effect_chance = 1.0 if move['effect_chance'] is None else move['effect_chance'] / 100.0
        self.has_effect = move['effect_chance'] is not None

    def use_move(self, gamestate, ai_turn=True):
        """
        Simulate the change in game state after using this move. Returns a list of possible resultant game states.
        """
        results = []
        gamestate = copy.deepcopy(gamestate)
        curr, opp = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
        active_self = gamestate[curr]
        active_opp = gamestate[opp]

        if self.pp <= 0 or active_self is None:
            return []

        if self.has_effect:
            """this move has an abstract effect"""
            pass #implement later, for Protect, etc.

        if self.name in data_stage_mults and USE_STAT_MULT:
            """this move invokes a stat stage multiplier"""
            mults = data_stage_mults[self.name]
            for stat, mult_self, mult_opp in zip(active_self.stats(), mults['user'], 
                                             mults['opponent']):
                curr_self = active_self.stage_multipliers[stat]
                active_self.stage_multipliers[stat] = max(min(6, curr_self + mult_self), -6) #clamp multiplier between -6, 6
                if active_opp is not None:
                    curr_opp = active_opp.stage_multipliers[stat]
                    active_opp.stage_multipliers[stat] = max(min(6, curr_opp + mult_opp), -6)

        if self.base_power > 0 and active_opp is not None:
            """this move does some damage"""
            dmg = calc_damage(active_self, active_opp, self)
            hit_rate = self.accuracy * active_self.accuracy / active_opp.evasion
            active_opp.hp -= dmg * min(100.0, hit_rate) / 100.0 #weight damage by move accuracy

            if active_opp.hp <= 0:
                gamestate[opp] = None

        self.pp -= 1
        results.append(gamestate)
        return results

    def attrs(self):
        return ('name', 'base_power', 'pp', 'type_')

    def __hash__(self):
        return hash(self.attrs())

    def __values(self):
        cmp_attrs = ['name']
        return (getattr(self, attr) for attr in self.attrs())

    def __cmp__(self, other):
        for s, o in zip(self.__values(), other.__values()):
            c = cmp(s, o)
            if c:
                return c
        return 0

    def __eq__(self, other):
        other_vals = other.__values() if other is not None else ()
        return [v for v in self.__values()] == [v for v in other_vals]

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "<move: %s>" % self.__str__()

    def __str__(self):
        return self.name

def gen_team():
    team = []

    team.append(Pokemon('rayquaza', 100, 351, 351, 200, 216, 336, 216, 226, ['dragon', 'flying'], ['draco-meteor', 'earthquake', 'dragon-ascent', 'extreme-speed']))
    team.append(Pokemon('lucario', 100, 281, 281, 200, 176, 266, 176, 216, ['fighting', 'steel'], ['shadow-ball', 'close-combat', 'bullet-punch', 'crunch']))
    team.append(Pokemon('giratina', 100, 441, 441, 259, 276, 212, 276, 216, ['dragon', 'ghost'], ['draco-meteor', 'earthquake', 'dragon-ascent', 'extreme-speed']))
    team.append(Pokemon('dragonite', 85, 276, 276, 259, 192, 201, 201, 167, ['flying', 'dragon'], ['dragon-claw', 'dragon-pulse', 'superpower', 'aqua-tail']))
    team.append(Pokemon('heracross', 100, 301, 301, 286, 186, 116, 226, 206, ['fighting', 'bug'], ['brick-break', 'tackle', 'body-slam', 'megahorn']))
    team.append(Pokemon('cubone', 100, 241, 241, 136, 226, 116, 136, 106, ['ground'], ['earthquake', 'fire-blast', 'fire-punch', 'body-slam']))

    for i in range(6):
        team.append(avg_pokemon())

    return team

def avg_pokemon():
    return Pokemon('?', 100, 200, 200, 286, 186, 116, 226, 206, ['normal'], ['brick-break', 'tackle', 'body-slam', 'megahorn'])

def e_team():
    team = []
    team.append(Pokemon('heracross', 100, 301, 301, 286, 186, 116, 226, 206, ['fighting', 'bug'], ['growth', 'superpower', 'body-slam', 'megahorn']))
    team.append(Pokemon('cubone', 100, 241, 241, 136, 226, 116, 136, 106, ['ground'], ['meteor-mash', 'tickle', 'fire-punch', 'body-slam']))

    return team


