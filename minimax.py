"""
An implementation of the minimax algorithm to play out pokemon showdown matches.

Board State: 
[list of 12 pokemon objects]
"""
import copy
MAX_DEPTH = 3

def eval_function(gamestate):
    #return gamestate[:6].count(None) - gamestate[6:].count(None)
    return gamestate

def next_states(boardstate):
    return [boardstate + 1, boardstate + 2, boardstate + 3]

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

    def populate_children(self):
        for state in next_states(self.gamestate):
            self.children.append(Node(state))

    def __str__(self, level=0):
        ret = "\t" * level + "{state:%s, val:%s}\n" % (self.gamestate, 
                                                           self.value)
        for c in self.children:
            ret += c.__str__(level+1)
        return ret

    def __repr__(self):
        return '<minimax tree node>'

def generate_tree(startstate):
    tree = Node(startstate)
    curr = [tree]
    for i in range(MAX_DEPTH):
        for c in curr:
            c.populate_children()
        curr_ = []
        [curr_.extend(c.children) for c in curr]
        curr = curr_
    return tree
