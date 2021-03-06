import re
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from ..simulator import simulate

class WaitOnTextChanged(object):
    """
    Yield new values of locator until text hasn't changed for x seconds.
    """
    def __init__(self, locator, curr):
        self.locator = locator
        self.curr = curr

    def __call__(self, driver):
        element = EC._find_element(driver, self.locator)
        return element.text != self.curr

class WaitUntilEquals(object):
    def __init__(self, locator, target, attr):
        self.locator = locator
        self.target = target
        self.attr = attr

    def __call__(self, driver):
        elem = EC._find_element(driver, self.locator)
        cmp_ = elem.text if self.attr is None else elem.get_attribute(self.attr)
        return cmp_ == self.target

class DynamicWebPage(object):
    """
    A simple webpage class. Lets you access values of locators as attributes,
    waits until page is loaded. Provides a generator interface to respond to
    real-time changes in the page.
    """
    def __init__(self, driver):
        self.driver = driver

    def get(self, locator):
        return self.driver.find_element(locator[0], locator[1])

    def get_mult(self, locator):
        return self.driver.find_elements(locator[0], locator[1])

    def on_change(self, locator, timeout):
        try:
            curr = None
            while True:
                if timeout != -1:
                    WebDriverWait(self.driver, timeout).until(
                        WaitOnTextChanged(locator, curr)
                    )
                    curr = self.get(locator).text
                    yield curr
                else: #wait indefinitely
                    while True:
                        try:
                            if WaitOnTextChanged(locator, curr)(self.driver):
                                curr = self.get(locator).text
                                yield curr
                        except (NoSuchElementException):
                            continue
        except (TimeoutException, NoSuchElementException):
            yield None

    def wait_until_equals(self, locator, target, attr, timeout):
        """
        Waits until the locator has the target value
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                WaitUntilEquals(locator, target, attr)
            )
            return True
        except (NoSuchElementException):
            pass
        except (TimeoutException):
            return False

    def get_when_present(self, locator, timeout, mult=False):
            try:
                while True:
                    if timeout != -1:
                        WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located(locator)
                        )
                        return self.get(locator) if not mult else self.get_mult(locator)
                    else:
                        while True:
                            try:
                                if EC.presence_of_element_located(locator):
                                    return self.get(locator) if not mult else self.get_mult(locator)
                            except:
                                continue
            except (TimeoutException):
                return None

class ShowdownBattle(DynamicWebPage):
    def __init__(self, timeout):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome(executable_path="chromedriver", 
                                       chrome_options=chrome_options)
        super(ShowdownBattle, self).__init__(self.driver)
        self.BASE = "http://play.pokemonshowdown.com"
        self.LOCATORS = {
            'setname_btn_open'      :(By.XPATH, '//button[@name="login"]'),
            'setname_txt'           :(By.XPATH, '//div[@class="ps-popup"]//input'),
            'setname_btn_submit'    :(By.XPATH, '//div[@class="ps-popup"]//button[@type="submit"]'),
            'searchname_btn_open'   :(By.XPATH, '//button[@class="button mainmenu5 onlineonly"]'),
            'challenge_user_btn'    :(By.XPATH, '//div[@class="ps-popup"]//button[@name="challenge"]'),
            'challenge_user_confirm':(By.XPATH, '//div[@class="pm-window pm-window-%s"]//button[@name="makeChallenge"]'),      
            'curr_name'             :(By.XPATH, '//span[@class="username"]'),
            'startbattle_btn'       :(By.XPATH, '//button[@class="button mainmenu1 big"]'),
            'battle_moves_btns'     :(By.XPATH, '//div[@class="movemenu"]/button'),
            'battle_swap_btns'      :(By.XPATH, '//div[@class="switchmenu"]/button'),
            'turn_count'            :(By.XPATH, '(//h2[starts-with(text(), "Turn")])[last()]'),
            'player_active'         :(By.XPATH, '//div[@class="statbar rstatbar"]'),
            'opponent_active'       :(By.XPATH, '//div[@class="statbar lstatbar"]'),
            'tooltip'               :(By.XPATH, '//div[@class="tooltip"]'),
            'battle-log'            :(By.XPATH, '//div[@class="battle-log"]/div[@class="inner"]'),
            'battle-log-last-line'  :(By.XPATH, '(//div[@class="battle-log"]/div[@class="inner"]/*)[last()]')
        }
        self.timeout = timeout


        


    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()
        self.driver.quit()

    def load(self):
        self.driver.get(self.BASE)

    def on_change(self, locator, timeout=None):
        timeout = self.timeout if not timeout else timeout
        return super(ShowdownBattle, self).on_change(locator, timeout)

    def wait_until_equals(self, locator, target, attr=None, timeout=None):
        timeout = self.timeout if not timeout else timeout
        return super(ShowdownBattle, self).wait_until_equals(locator, target, attr, timeout)

    def get_when_present(self, locator, timeout=None):
        timeout = self.timeout if not timeout else timeout
        return super(ShowdownBattle, self).get_when_present(locator, timeout)

    def get_all_when_present(self, locator, timeout=None):
        timeout = self.timeout if not timeout else timeout
        return super(ShowdownBattle, self).get_when_present(locator, timeout, mult=True)

    def set_name(self, name):
        setname_btn_open = self.get_when_present(self.LOCATORS['setname_btn_open'])
        setname_btn_open.click()
        setname_txt = self.get_when_present(self.LOCATORS['setname_txt'])
        setname_txt.send_keys(name)
        setname_btn = self.get_when_present(self.LOCATORS['setname_btn_submit'])
        setname_btn.click()
        self.wait_until_equals(self.LOCATORS['curr_name'], " {}".format(name), 
                attr='data-name') #confirm name updated

    def challenge_user(self, name):
        searchname_btn_open = self.get_when_present(self.LOCATORS['searchname_btn_open'])
        searchname_btn_open.click()
        searchname_txt = self.get_when_present(self.LOCATORS['setname_txt'])
        searchname_txt.send_keys(name)
        searchname_btn = self.get_when_present(self.LOCATORS['setname_btn_submit'])
        searchname_btn.click()
        challenge_user_btn = self.get_when_present(self.LOCATORS['challenge_user_btn'])
        challenge_user_btn.click()
        challenge_locator = (self.LOCATORS['challenge_user_confirm'][0], self.LOCATORS['challenge_user_confirm'][1] % name)
        challenge_user_confirm = self.get_when_present(challenge_locator)
        challenge_user_confirm.click()

    def start_battle(self):
        startbattle_btn = self.get_when_present(self.LOCATORS['startbattle_btn'])
        startbattle_btn.click()
        self.wait_until_equals(self.LOCATORS['turn_count'], "Turn 1")

    def wait_for_battle(self):
        self.wait_until_equals(self.LOCATORS['turn_count'], "Turn 1")

    def get_battle_log(self):
        log = self.get_when_present(self.LOCATORS['battle-log']).text.split('\n')
        return log

    def get_player_team(self):
        team = []
        team_btns = self.get_all_when_present(self.LOCATORS['battle_swap_btns'])
        for pk in team_btns:
            actions = ActionChains(self.driver)
            actions.move_to_element(pk)
            actions.perform()
            tooltip = self.get_when_present(self.LOCATORS['tooltip'])

            tooltip_lvl     = tooltip.find_element_by_xpath('(.//h2/small)[last()]').text
            tooltip_hp      = tooltip.find_element_by_xpath('(.//p)[1]').text
            tooltip_types   = tooltip.find_elements_by_xpath('.//h2/img')
            tooltip_stats   = tooltip.find_element_by_xpath('(.//p)[3]').text
            tooltip_moves   = tooltip.find_element_by_xpath('(.//p)[4]').text
            #tooltip_ab_itm  = tooltip.find_element_by_xpath('.//(p)[2]').text

            name     = pk.text
            _hp      = re.findall(r'\(([0-9]+)/([0-9]+)\)', tooltip_hp)
            if len(_hp) == 0:
                team.append(None)
                continue
            else:
                _hp = _hp[0]
            lvl      = re.findall(r'[0-9]+$', tooltip_lvl)[0]
            hp, thp  = _hp[0], _hp[1]
            types    = [t.get_attribute('alt') for t in tooltip_types]
            types    = [t.lower() for t in types if t not in ['F', 'M']]
            stats    = [s.strip() for s in tooltip_stats.split('/')]
            stats    = [re.findall(r'^[0-9]+',s)[0] for s in stats]
            moves    = [m.strip() for m in tooltip_moves.split('\n')]
            moves    = [re.findall(r'\s(.+?)($|\()', m)[0][0].strip() for m in moves] #fix move regex to ignore pp (1/10)

            #print (name, lvl, thp, stats[0], stats[1], stats[2], stats[3], stats[4], types, moves)
            pokemon = simulate.Pokemon(name, lvl, hp, thp, stats[0], stats[1], 
                                              stats[2], stats[3], stats[4], types, moves)
            team.append(pokemon)
    
        return team

    def get_active_pokemon(self):
        p_active = self.get_when_present(self.LOCATORS['player_active'])
        o_active = self.get_when_present(self.LOCATORS['opponent_active'])

        p_name, p_lvl = p_active.find_element_by_xpath('.//strong').text.split(" ")
        p_hp = p_active.find_element_by_xpath('.//div[@class="hpbar"]/div[@class="hptext"]').text
        p_stat = [el.text for el in p_active.find_elements_by_xpath('.//div[@class="hpbar"]/div[@class="status"]/span')]

        o_name, o_lvl = o_active.find_element_by_xpath('.//strong').text.split(" ")
        o_hp = o_active.find_element_by_xpath('.//div[@class="hpbar"]/div[@class="hptext"]').text
        o_stat = [el.text for el in o_active.find_elements_by_xpath('.//div[@class="hpbar"]/div[@class="status"]/span')]

        return (p_name, int(p_lvl[1:]), int(p_hp[:-1]), p_stat), (o_name, int(o_lvl[1:]), int(o_hp[:-1]), o_stat)

    def battle_use_move(self, index):
        moves = self.get_all_when_present(self.LOCATORS['battle_moves_btns'])
        moves[index].click()
        #wait until move executed

    def battle_swap(self, index):
        team = self.get_all_when_present(self.LOCATORS['battle_swap_btns'])
        team[index].click()
        #wait until swap executed

