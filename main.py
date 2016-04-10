import sys
import os
import re
import random
import string
import copy

from pokemonbot.simulator import simulate, minimax
from pokemonbot.browser.browser_handler import ShowdownBattle

if __name__ == "__main__":
    def random_name():
        chars = string.ascii_uppercase.lower() + string.digits
        return ''.join([random.choice(chars) for i in range(10)])

    re_turn = re.compile(r"^Turn\s[0-9]+")
    re_opp_moves = re.compile(r"The opposing\s(.+?)\sused\s(.+?)!$")
    re_opp_swaps = re.compile(r".+sent\sout\s(.+?)!$")
    re_opp_damaged = re.compile(r".*The opposing (.+?) lost (.+%)")
    re_opp_fainted = re.compile(r"The opposing\s(.+?)\sfainted!$")
    re_ai_fainted = re.compile(r"^(.+?)\sfainted!$")

    MAX_TURN_TIME = 120

    with ShowdownBattle(MAX_TURN_TIME) as showdown:
        showdown.set_name(random_name())
        showdown.challenge_user('lsturm123')
        showdown.wait_for_battle()

        ai_team = []
        opp_team = []

        p_active, o_active = showdown.get_active_pokemon()
        o_active = simulate.Pokemon(o_active[0])
        o_active.fill_avgs()
        opp_team.append(o_active)
        opp_team.extend([simulate.avg_pokemon() for p in range(5)])  

        def update_state(ai_team, opp_team):
            """pull the game state and do some standard updates"""
            p_active, o_active = showdown.get_active_pokemon()
            opp_pk = pokemon_from_team(opp_team, o_active[0])
            opp_pk.hp = opp_pk.totalhp * o_active[2] / 100.0
            ai_team = showdown.get_player_team()
            return ai_team, opp_team

        def pokemon_from_team(team, name):
            try:
                index = [p.name if p else None for p in team].index(name)
                return team[index]
            except ValueError:
                return None

        def make_move():
            print "computing optimal move:"
            gamestate = copy.deepcopy(ai_team) + copy.deepcopy(opp_team)
            opt_move = minimax.move_for_gamestate(gamestate, depth=4)
            print opt_move

            for action in opt_move:
                if action[0] == 'swap':
                    name = action[1]
                    index = [p.name if p is not None else None for p in ai_team].index(simulate.Pokemon(name).name)
                    ai_team[0], ai_team[index] = ai_team[index], ai_team[0]
                    showdown.battle_swap(index)

                if action[0] == 'move':
                    move_name = action[1]
                    if move_name == "hidden-power":
                        print ai_team[0].moves
                    index = [m.name for m in ai_team[0].moves].index(simulate.Move(move_name).name)
                    showdown.battle_use_move(index)

        for line in showdown.on_change(showdown.LOCATORS['battle-log-last-line'], 
                                       timeout=-1):
            print "LINE:", line
            if re_turn.match(line):
                print "\n"
                print "----%s | TEAMS:----" % line.upper()
                print "UPDATING STATE"
                ai_team, opp_team = update_state(ai_team, opp_team)
                print ai_team
                print opp_team

                make_move()
                print "AI MAKES MOVE HERE"

            """use descriptions from the battle log to update opponent team"""

            if re_opp_moves.match(line):
                """opponent's pokemon used a move -- add it to its list of moves.
                Also change stats / transform effects on opponent here as well.
                """
                pokemon_name, move_name = re_opp_moves.match(line).groups()
                move = simulate.Move(move_name)
                pk = pokemon_from_team(opp_team, pokemon_name)
                if move.name not in [m.name for m in pk.moves]:
                    pk.moves.append(move) # replace move instead of appending
                    print "...matched move: learned %s has move %s" % (pokemon_name, move_name)

            if re_opp_swaps.match(line):
                """opponent sent out a pokemon -- create it if it's not in the team,
                otherwise swap it with the active pokemon.
                """
                name = re_opp_swaps.match(line).groups()[0] #can we get the pokemon's level at this point?
                pk = simulate.Pokemon(name)
                pk.fill_avgs()
                if pk.name in [p.name if p is not None else None for p in opp_team]:
                    index = [p.name if p is not None else None for p in opp_team].index(pk.name)
                    opp_team[0], opp_team[index] = opp_team[index], opp_team[0]
                    print "...matched swap: %s swapped with %s" % (opp_team[index], opp_team[0])
                else: #switch active with the first placeholder pokemon and reset active
                    index = [p.name if p is not None else None for p in opp_team].index(simulate.avg_pokemon().name)
                    opp_team[0], opp_team[index] = opp_team[index], opp_team[0]
                    opp_team[0] = pk
                    print "...matched swap: learned that %s exists" % (opp_team[0])

            if re_opp_damaged.match(line):
                """opponent's pokemon was damaged, update hp of pokemon"""
                pokemon_name, damage = re_opp_damaged.match(line).groups()
                #damage_amt = int(damage.replace('%', '')) / 100.0
                #opp_team[0].hp -= int(damage_amt * o_active.hp)
                p_active, o_active = showdown.get_active_pokemon()
                pk = pokemon_from_team(opp_team, o_active[0])
                pk.hp = pk.totalhp * o_active[2] / 100.0
                print "...matched damage: reduced hp of %s to %s" % (pk.name, pk.hp)

            if re_opp_fainted.match(line):
                """opponent's pokemon was fainted, set to None"""
                opp_team[0] = None
                print "...matched opponent fainted: set active to None"

            if re_ai_fainted.match(line) and not re_opp_fainted.match(line):
                """ai's pokemon fainted"""
                ai_team[0] = None
                print "...matched ai fainted: set active to None"
                make_move() #must make move when our pokemon faints
                print "AI MAKES MOVE HERE"
            
            



