from time import sleep
import re
import requests
import simplejson as json
from lxml import html


LADDERS = ['uu', 'ubers', 'ou', 'ru', 'nu', 'pu']

def download_pokemon():
    num_pokemon = 721
    f = open('pokemon.json', 'r+')
    pokemon = {} if len(f.read()) == 0 else json.loads(f.read())
    start = max(1, len( pokemon.keys() ))
    for i in xrange(start, num_pokemon + 1):
        try:
            r = requests.get("http://pokeapi.co/api/v2/pokemon/%s" % i).json()
            print "getting pokemon %s %s/%s" % (r['name'], i, num_pokemon)
            pokemon[r['name']] = r

            if '-' in r['name']:
                shorter_name = re.findall(r'(.+?)\-')[0]
                pokemon[shorter_name] = r

            sleep(100 / 1000.0)
        except: #probably got rate-limited
            f.write(json.dumps(pokemon, indent=4))
            f.close()
            print "saving and quitting... failed on %s" % i

    f.write(json.dumps(pokemon, indent=4))
    f.close()

def download_moves():
    num_moves = 639
    movelist = requests.get("http://pokeapi.co/api/v2/move/?limit=%s" % num_moves)
    movelist = movelist.json()['results']
    moves = {}

    for i,m in enumerate(movelist):
        print "getting move %s %s/%s" % (m['name'], i, num_moves)
        r = requests.get(m['url']).json()
        r['power'] = 0 if not r['power'] else r['power']
        moves[r['name']] = r

        sleep(100 / 1000.0)

    f = open('moves.json', 'w')
    f.write(json.dumps(moves, indent=4))
    f.close()

def download_ladder(ladder_type):
    URL = "http://pokemonshowdown.com/ladder/%s" % ladder_type
    page = requests.get(URL)
    xml = html.fromstring(page.content)
    return [name.text for name in xml.xpath('//div[@class="pfx-body ladder"]/div/table/tr/td[2]/a')]

def get_replay_urls(user):
    URL = "http://replay.pokemonshowdown.com/replay/search/?output=html&user=%s" % user
    page = requests.get(URL)
    xml = html.fromstring(page.content)
    return xml.xpath('//ul[@class="linklist"]/li/a/@href')

def get_effects():
    effect_dictionary = {}
    #list order = attack,defense,special attack,special defense,speed,evasion,accuracy

    effect_moves = json.loads(open('effect_moves.json', 'r').read())
    for move in effect_moves:
        user_list = [0,0,0,0,0,0,0]
        opponent_list = [0,0,0,0,0,0,0]
        
        for stat in effect_moves[move]['stat_changes']:
            pokemon_affected = stat['stat']['pokemon']
            list_ = user_list if pokemon_affected == 'user' else opponent_list
            list_ = [0,0,0,0,0,0,0] if pokemon_affected == 'ally' or pokemon_affected == 'both' else list_ #need to handle special cases
            add_effect_to_list(list_, stat['stat']['name'], stat['change'])
        effect_dictionary[move] = {'user': user_list, 'opponent':opponent_list}

    f = open('move_effects.json', 'w')
    f.write(json.dumps(effect_dictionary, indent=4))  
    f.close()

def add_effect_to_list(list_, stat_name, stat_change):
    if stat_name == 'attack':
        list_[0] = stat_change
    elif stat_name == 'defense':
        list_[1] = stat_change
    elif stat_name == 'special-attack':
        list_[2] = stat_change
    elif stat_name == 'special-defense':
        list_[3] = stat_change
    elif stat_name == 'speed':
        list_[4] = stat_change
    elif stat_name == 'evasion':
        list_[5] = stat_change
    elif stat_name == 'accuracy':
        list_[6] = stat_change
    else:
        print "error, unknown stat name: " + stat_name

def get_all_effect_moves():
    data_moves = json.loads(open('moves.json', 'r').read())
    effect_moves = {}
    for move in enumerate(data_moves):
        move_name = move[1]
        if len(data_moves[move_name]['stat_changes']) > 0:
            effect_moves[move_name] = data_moves[move_name]
    f = open('effect_moves.json', 'w')
    f.write(json.dumps(effect_moves, indent=4))
    f.close


def get_and_format_replay(replay_url):
    URL = "http://replay.pokemonshowdown.com/%s" % replay_url
    page = requests.get(URL)
    xml = html.fromstring(page.content)
    replay_raw = xml.xpath('//script[@class="log"]')

    replay_raw = True #delme

    if replay_raw:
        replay = {}
        #instructions = replay_raw[0].text
        instructions = open('sample_replay', 'r').read() #delme
        search_replay = lambda key: re.compile(r"^\|%s\|(.+?)$" % key, re.M)

        #player names
        players_rgx = search_replay('player\|p[0-9]')
        replay['players'] = [p.split('|')[0] for p in players_rgx.findall(instructions)]

        #player teams
        teams_rgx = search_replay('poke\|p[1-2]')
        teams = [p.split(',')[0] for p in teams_rgx.findall(instructions)]
        replay['team_1'], replay['team_2'] = teams[:len(teams) >> 1], teams[len(teams) >> 1:]

        print json.dumps(replay, indent=4)

    

if __name__ == "__main__":
    download_pokemon()
