"""
An implementation of the minimax algorithm to play out pokemon showdown matches.

Game State: 
[list of 12 pokemon objects]
"""
import copy
import itertools
import simulate
import simplejson as json
MAX_DEPTH = 10
TEAMSZ = 6

def avg(l):
    return sum(l) / float(len(l)) if len(l) > 0 else 0

def eval_function(gamestate):
    team1,team2 = gamestate[:TEAMSZ], gamestate[TEAMSZ:]

    #penalize ai for pokemon with low % of total hp
    hp_ratio_1 = [float(p.hp) / p.totalhp for p in team1 if p is not None]
    hp_ratio_2 = [float(p.hp) / p.totalhp for p in team2 if p is not None]
    diff_hp = avg(hp_ratio_1) - avg(hp_ratio_2)

    #penalize ai for fainted pokemon
    diff_faint = len([p for p in team2 if p is None]) - len([p for p in team1 if p is None])
    diff_faint /= float(TEAMSZ) #normalize

    return diff_hp + diff_faint

def next_states(gamestate, ai_turn=True):
    """
    Active pokemon uses one of four moves -- decrease HP of opponent's active pokemon
    Swap active pokemon with any other non-fainted pokemon
    """
    curr, opponent = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
    next_states = []

    states_swap = transform_state_swap(gamestate, ai_turn)
    next_states.extend(states_swap)
    if gamestate[curr]:
        states_attack = transform_state_attack(gamestate, ai_turn)
        next_states.extend(states_attack)

    return next_states

def transform_state_attack(gamestate, ai_turn=True):
    """
    Given a game state, transform such that active pokemon 
    uses each of its moves.
    """
    curr, opp = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
    next_states = []

    active_pokemon = gamestate[curr]
    for i,move in enumerate(active_pokemon.moves):
        next_ = copy.deepcopy(gamestate)
        states = next_[curr].moves[i].use_move(next_, ai_turn)
        desc = [('move', move.name)]
        for state in states:
            next_states.append([state, desc])
    return next_states

def update_stat_stages(current, opponent, move):
    effect_lists = effects.get(move.name, [])
    if len(effect_lists) == 0:
        return None 
    effect_chance = move.effect_chance
    rand = simulate.random.randrange(1, 101)
    if effect_chance is None or rand <= effect_chance:
        for player in effect_lists:
            pokemon = current if player == "user" else opponent
            for i, effect in enumerate(effect_lists[player]):
                if effect != 0:
                    stat = get_effect_stat(i)
                    pokemon.stage_multipliers[stat]['count'] += effect
                    pokemon.stage_multipliers[stat]['count'] = 6 if pokemon.stage_multipliers[stat]['count'] > 6  else pokemon.stage_multipliers[stat]['count']
                    pokemon.stage_multipliers[stat]['count'] = -6 if pokemon.stage_multipliers[stat]['count'] < -6 else pokemon.stage_multipliers[stat]['count']
                    count = pokemon.stage_multipliers[stat]['count']
                    numerator_shift_val = count if count > 0 else 0
                    denomenator_shift_val = -count if count < 0 else 0
                    if i < 5: #there is a different equation for evasion and accuracy
                        pokemon.stage_multipliers[stat]['multiplier'] = (2 + numerator_shift_val)/(2.0 + denomenator_shift_val)
                    else:
                        if i == 5:
                            numerator_shift_val, denomenator_shift_val = denomenator_shift_val, numerator_shift_val
                        pokemon.stage_multipliers[stat]['multiplier'] = (3.0 + numerator_shift_val)/(3.0 + denomenator_shift_val)

def get_effect_stat(i):
    if i == 0:
        return 'attack'
    elif i == 1:
        return 'defense'
    elif i == 2:
        return 'special-attack'
    elif i == 3:
        return 'special-defense'
    elif i == 4: 
        return 'speed'
    elif i == 5:
        return 'evasion'
    else:
        return 'accuracy'


def transform_state_swap(gamestate, ai_turn=True):
    """
    Given a game state, transform such that active pokemon is swapped 
    with every other non-fainted pokemon.
    """
    curr, opp = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
    next_states = []

    for i,pokemon in enumerate(gamestate[curr+1:curr+TEAMSZ]):
        if pokemon is not None:
            next_ = copy.deepcopy(gamestate)
            if next_[curr] is not None:
                desc = [('swap', next_[curr+i+1].name)]
            else:
                desc = [('swap', next_[curr+i+1].name)]

            next_[curr+i+1],next_[curr] = next_[curr],next_[curr+i+1]
            next_states.append([next_, desc])

    return next_states

class Node:
    def __init__(self, gamestate, description="", is_ai=True):
        self.gamestate = copy.deepcopy(gamestate)
        self.value = 0
        self.children = []
        self.description = description
        self.is_ai = is_ai

    def backprop(self):
        """recursively calculate tree max/min's"""
        if self.children:
            func = max if self.is_ai else min
            self.value = func([c.backprop() for c in self.children])
        else:
            self.value = eval_function(self.gamestate)
        return self.value

    def populate_children(self, seen, ai_turn):
        next = next_states(self.gamestate, ai_turn)
        vals = lambda p: "/".join([str(getattr(p, attr)) for attr in p.attrs()])
        encode = lambda game: "|".join([vals(p) if p is not None else "FAINTED_PKMN" for p in game])
        next = [g for g in next if encode(g[0]) not in seen]
        seen.extend([encode(g[0]) for g in next])

        for state in next:
            self.children.append(Node(state[0], state[1], ai_turn))

    def __str__(self, level=0):
        ret = "\t" * level + "{[AI:%s] %s, %s, val:%s}\n" % (str(self.is_ai), str(self.gamestate),str(self.description), 
                                                           str(self.value))
        for c in self.children:
            ret += c.__str__(level+1)
        return ret

    def __repr__(self):
        return '<minimax tree node>'

def is_ai_turn(gamestate):
    """
    If a player has a fainted pokemon, that player moves first (swap).
    Otherwise, the player who moves first depends on the speed of the
    pokemon in play.
    """
    if gamestate[0] is None:
        return True

    if gamestate[TEAMSZ] is None:
        return False

    return gamestate[0].speed >= gamestate[TEAMSZ].speed

def generate_tree(startstate_, ai_turn=True, depth=MAX_DEPTH):
    startstate = copy.deepcopy(startstate_)
    tree = Node(startstate, is_ai=ai_turn)
    seen = []
    curr = [tree]
    for i in range(depth):
        for c in curr:
            if i % 2 == 0:
                ai_turn = is_ai_turn(c.gamestate)
            else:
                ai_turn = not c.is_ai
            c.populate_children(seen, ai_turn)
        curr_ = []
        [curr_.extend(c.children) for c in curr]
        curr = curr_
    return tree

def move_for_gamestate(gamestate, depth=MAX_DEPTH):
    ai_turn = is_ai_turn(gamestate)
    tree = generate_tree(gamestate, ai_turn, depth)
    tree.backprop()
    predicted_move = [c for c in tree.children if c.value == tree.value][0]
    if tree.is_ai:
        return predicted_move.description
    else:
        best_move = [c for c in predicted_move.children if c.value == predicted_move.value][0]
        return best_move.description

    return None
