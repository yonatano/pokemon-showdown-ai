"""
An implementation of the minimax algorithm to play out pokemon showdown matches.

Board State: 
[list of 12 pokemon objects]
"""
import copy
import simulate
MAX_DEPTH = 10
TEAMSZ = 2

def eval_function(gamestate):
    team1,team2 = gamestate[:TEAMSZ], gamestate[TEAMSZ:]

    #penalize ai for pokemon with low % of total hp
    hp_ratio_1 = [float(p.hp) / p.totalhp for p in team1 if p is not None]
    hp_ratio_2 = [float(p.hp) / p.totalhp for p in team2 if p is not None]
    diff_hp = sum(hp_ratio_1) / len(hp_ratio_1) - sum(hp_ratio_2) / len(hp_ratio_2)

    #penalize ai for fainted pokemon
    diff_faint = team1.count(None) - team2.count(None)
    diff_faint /= float(TEAMSZ) #normalize

    return diff_hp + diff_faint

def next_states(gamestate, ai_turn=True):
    """
    Active pokemon uses one of four moves -- decrease HP of opponent's active pokemon
    Swap active pokemon with any other non-fainted pokemon
    """
    curr, opponent = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
    next_states = []

    if gamestate[curr] is None: #active pokemon fainted last turn
        states_swap = transform_state_swap(gamestate, ai_turn)
        for state in states_swap: #force a swap and then attack or swap
            states_attack = transform_state_attack(state, ai_turn)
            states_swap = transform_state_swap(state, ai_turn)
            next_states.extend(states_attack + states_swap)
    else: #possible moves are attack with active or swap it out
        states_attack = transform_state_attack(gamestate, ai_turn)
        states_swap = transform_state_swap(gamestate, ai_turn)
        next_states.extend(states_attack + states_swap)
    return next_states

def transform_state_attack(gamestate, ai_turn=True):
    """
    Given a game state, transform such that active pokemon 
    uses each of its moves.
    """
    curr, opp = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
    next_states = []

    active_pokemon = gamestate[curr]
    for move in active_pokemon.moves:
        next_ = copy.deepcopy(gamestate)
        dmg = simulate.calc_damage(active_pokemon, next_[opp], move)
        next_[opp].hp -= dmg
        if next_[opp].hp <= 0:
            next_[opp] = None
        next_states.append(next_)

    return next_states

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
            next_[curr+i+1],next_[curr] = next_[curr],next_[curr+i+1]
            next_states.append(next_)

    return next_states

class Node:
    def __init__(self, gamestate):
        self.gamestate = copy.deepcopy(gamestate)
        self.value = 0
        self.children = []

    def backprop(self, max_=True):
        """recursively calculate tree max/min's"""
        if self.children:
            func = max if max_ else min
            self.value = func([c.backprop(not max_) for c in self.children])
        else:
            self.value = eval_function(self.gamestate)
        return self.value

    def populate_children(self, ai_turn=True):
        for state in next_states(self.gamestate, ai_turn):
            self.children.append(Node(state))

    def __str__(self, level=0):
        ret = "\t" * level + "{state:%s, val:%s}\n" % (str(self.gamestate), 
                                                           str(self.value))
        for c in self.children:
            ret += c.__str__(level+1)
        return ret

    def __repr__(self):
        return '<minimax tree node>'

def generate_tree(startstate, ai_turn=True, depth=MAX_DEPTH):
    tree = Node(startstate)
    curr = [tree]
    for i in range(depth):
        print "DEPTH: %s" % i
        for c in curr:
            c.populate_children(ai_turn)
        curr_ = []
        [curr_.extend(c.children) for c in curr]
        curr = curr_
        print "%s children" % len(curr)
        ai_turn = not ai_turn
    return tree
