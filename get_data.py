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

def get_and_format_replay(replay_url):
    #URL = "http://replay.pokemonshowdown.com/%s" % replay_url
    #page = requests.get(URL)
    #xml = html.fromstring(page.content)
    #replay_raw = xml.xpath('//script[@class="log"]')

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
