import re
import requests
import simplejson as json
from lxml import html


LADDERS = ['uu', 'ubers', 'ou', 'ru', 'nu', 'pu']

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

    #replay_urls = get_replay_urls('pokemonisfun')
    get_format_replay("")
