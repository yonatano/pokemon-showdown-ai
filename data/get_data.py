from time import sleep
import re
import requests
import simplejson as json
from lxml import html


LADDERS = ['uu', 'ubers', 'ou', 'ru', 'nu', 'pu']

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

        sleep(200 / 1000.0)

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
    attack_1 = ['ancient-power','bulk-up', 'coil', 'curse', 'dragon-dance','growth','hone-claws','howl','meditate','metal-claw', 'meteor-mash', 'ominous-wind', 'power-up-punch',
    'rage', 'rototiller','sharpen','shift-gear','silver-wind','work-up']
    attack_2 = ['acupressure', 'fell-stinger', 'shell-smash', 'swagger', 'swords-dance']
    attack_3 = ['belly-drum']
    attack_min_1 = ['aurora-beam','baby-doll-eyes','growl','noble-roar','parting-shot','play-nice','play-rough','secret-power','superpower',
    'tickle','venom-drench']
    attack_min_2 = ['charm','feather-dance','kings-shield','memento']
    defense_1 = ['ancient-power','bulk-up','coil','cosmic-power','curse','defend-order','defense-curl','diamond-storm','flower-shield','harden','magnetic-flux',
    'ominous-wind','silver-wind','skull-bash','steel-wing','stockpile','withdraw']
    defense_2 = ['acid-armor','acupressure','barrier','iron-defense']
    defense_3 = ['cotton-guard']
    defense_min_1 = ['acid','close-combat','crunch','crush-claw','dragon-ascent','iron-tail','leer','razor-shell','rock-smash','secret-power','shell-smash',
    'superpower','tail-whip','tickle','v-create']
    defense_min_2 = ['screech']
    Sp_attack_1 = ['ancient-power', 'calm-mind', 'charge-beam','fiery-dance','flatter','growth','ominous-wind','rototiller','silver-wind','quiver-dance','work-up']
    Sp_attack_2 = ['acupressure','geomancy','nasty-plot','shell-smash']
    Sp_attack_3 = ['tail-glow']
    Sp_attack_min_1 = ['confide','mist-ball','moonblast','mystical-fire','noble-roar','parting-shot','secret-power','snarl','struggle-bug','venom-drench']
    Sp_attack_min_2 = ['captivate','draco-meteor','eerie-impulse','leaf-storm','memento','overheat','psycho-boost']
    Sp_deffense_1 = ['ancient-power','aromatic-mist','calm-mind','charge','cosmic-power','defend-order','magnetic-flux','ominous-wind','quiver-dance','silver-wind','stockpile']
    Sp_deffense_2 = ['acupressure','amnesia','geomancy']
    Sp_deffense_min_1 = ['acid','bug-buzz','close-combat','crunch','dragon-ascent','earth-power','energy-ball','flash-cannon','focus-blast','luster-purge',
    'psychic','shadow-ball','shell-smash','v-create']
    Sp_deffense_min_2 = ['acid-spray','fake-tears','metal-sound','seed-flare']
    speed_1 = ['ancient-power','dragon-dance','flame-charge','ominous-wind','quiver-dance','silver-wind']
    speed_2 = ['acupressure','agility','autotomize','geomancy','rock-polish','shell-smash','shift-gear']
    speed_min_1 = ['bubble','bubble-beam','bulldoze','constrict','curse','glaciate','hammer-arm','icy-wind','low-sweep','mud-shot','rock-tomb','secret-power','sticky-web','v-create','venom-drench']
    speed_min_2 = ['cotton-spore','scary-face','string-shot']
    evasion_1 = ['double-team']
    evasion_2 = ['minimize','acupressure']
    evasion_min_1 = ['defog']
    evasion_min_2 = ['gravity', 'sweet-scent']
    accuracy_1 = ['hone-claws','coil']
    accuracy_2 = ['acupressure']
    accuracy_min_1 = ['flash','kinesis','leaf-tornado','mirror-shot','mud-bomb','mud-slap','muddy-water','night-daze','octazooka','sand-attack','secret-power','smokescreen']
    place_holder = []

    effects_list = [attack_1,attack_2,attack_3,attack_min_1,attack_min_2,place_holder,defense_1,defense_2,defense_3,defense_min_1,defense_min_2,place_holder,Sp_attack_1,Sp_attack_2,Sp_attack_3,
    Sp_attack_min_1,Sp_attack_min_2,place_holder,Sp_deffense_1,Sp_deffense_2,place_holder,Sp_deffense_min_1,Sp_deffense_min_2,place_holder,speed_1,speed_2,place_holder,speed_min_1,speed_min_2,place_holder,
    evasion_1,evasion_2,place_holder,evasion_min_1,evasion_min_2,place_holder,accuracy_1,accuracy_2,place_holder,accuracy_min_1]
    
    effects_helper(effect_dictionary, effects_list)
    f = open('move_effects.json', 'w')
    f.write(json.dumps(effect_dictionary, indent=4))  
    f.close()

def effects_helper(dict_, effects_list):
    for i,move_list in enumerate(effects_list):
        value = get_value(i)
        effect_index = get_effect_index(i)
        for move in move_list:
            if move in dict_:
                dict_[move][effect_index] = value
            else:
                effects = [0,0,0,0,0,0,0]
                effects[effect_index] = value
                dict_[move] = effects

def get_value(index):
    if index % 6 == 0:
        return 1
    elif index % 6 == 1:
        return 2
    elif index % 6 == 2:
        return 3
    elif index % 6 == 3:
        return -1
    elif index % 6 == 4:
        return -2
    else:
        return -3

def get_effect_index(index):
    num_per_type = 6
    if index < num_per_type:
        return 0
    elif index < num_per_type*2:
        return 1
    elif index < num_per_type*3:
        return 2
    elif index < num_per_type*4:
        return 3
    elif index < num_per_type*5:
        return 4
    elif index < num_per_type*6:
        return 5
    else:
        return 6


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
    """f = open('ladders.json', 'w')
    ladders = {l:download_ladder(l) for l in LADDERS[:1]}
    f.write(json.dumps(ladders, indent=4, sort_keys=True))
    """
    download_moves()
