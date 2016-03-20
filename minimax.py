"""
An implementation of the minimax algorithm to play out pokemon showdown matches.

Board State: 
[list of 12 pokemon objects]
"""
import copy
import simulate
MAX_DEPTH = 10
TEAMSZ = 1

def eval_function(gamestate):
    return gamestate[TEAMSZ:].count(None) - gamestate[:TEAMSZ].count(None)

def next_states(gamestate, ai_turn=True):
    """
    Active pokemon uses one of four moves -- decrease HP of opponent's active pokemon
    Swap active pokemon with any other non-fainted pokemon
    """
    curr, opponent = 0 if ai_turn else TEAMSZ, TEAMSZ if ai_turn else 0
    next = []
    if gamestate[curr] is None: #the active pokemon fainted last turn -- swap
        print "active pokemon fainted"
        for i,pokemon in enumerate(gamestate[curr+1:curr+TEAMSZ]):
            if pokemon is not None:
                next_ = copy.deepcopy(gamestate)
                next_[curr+i+1],next_[curr] = next_[curr],next_[curr+i+1]
                
                for m in next_[curr].moves:
                    next_atk = copy.deepcopy(next_)
                    dmg = simulate.calc_damage(next_[curr], next_[opponent], m)
                    next_atk[opponent].hp -= dmg
                    if next_atk[opponent].hp <= 0:
                        next_atk[opponent] = None
                    next.append(next_atk)
    else: 
        for m in gamestate[curr].moves:
            next_ = copy.deepcopy(gamestate)
            dmg = simulate.calc_damage(next_[curr], next_[opponent], m)
            #print "%s dealt %s dmg to %s" % (next_[curr], dmg, next_[opponent])
            next_[opponent].hp -= dmg
            if next_[opponent].hp <= 0:
                next_[opponent] = None
            next.append(next_)

        for i,pokemon in enumerate(gamestate[curr+1:curr+TEAMSZ]):
            if pokemon is not None:
                next_ = copy.deepcopy(gamestate)
                next_[curr+i+1],next_[curr] = next_[curr],next_[curr+i+1]
                next.append(next_)
    return next

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
