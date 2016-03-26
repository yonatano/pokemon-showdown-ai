from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import random
import string

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
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    def get(self, locator):
        return driver.find_element(locator[0], locator[1])

    def get_mult(self, locator):
        return driver.find_elements(locator[0], locator[1])

    def on_change(self, locator, timeout):
        try:
            curr = None
            while True:
                if timeout != -1:
                    WebDriverWait(driver, timeout).until(
                        WaitOnTextChanged(locator, curr)
                    )
                    curr = self.get(locator).text
                    yield curr
                else: #wait indefinitely
                    while True:
                        try:
                            if WaitOnTextChanged(locator, curr)(driver):
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
            WebDriverWait(driver, timeout).until(
                WaitUntilEquals(locator, target, attr)
            )
            return True
        except (NoSuchElementException):
            pass
        except (TimeoutException):
            return False

    def get_when_present(self, locator, timeout, mult=False):
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.get(locator) if not mult else self.get_mult(locator)
        except (TimeoutException):
            return None

class ShowdownBattle(DynamicWebPage):
    def __init__(self, driver):
        self.driver = driver
        super(ShowdownBattle, self).__init__(driver)
        self.BASE = "http://play.pokemonshowdown.com"
        self.LOCATORS = {
            'setname_btn_open'      :(By.XPATH, '//button[@name="login"]'),
            'setname_txt'           :(By.XPATH, '//div[@class="ps-popup"]//input'),
            'setname_btn_submit'    :(By.XPATH, '//div[@class="ps-popup"]//button[@type="submit"]'),
            'curr_name'             :(By.XPATH, '//span[@class="username"]'),
            'startbattle_btn'       :(By.XPATH, '//button[@class="button mainmenu1 big"]'),
            'battle_moves_btns'     :(By.XPATH, '//div[@class="movemenu"]/button'),
            'battle_swap_btns'      :(By.XPATH, '//div[@class="switchmenu"]/button'),
            'turn_count'            :(By.XPATH, '(//h2[starts-with(text(), "Turn")])[last()]'),
            'player_active'         :(By.XPATH, '//div[@class="statbar rstatbar"]/strong'),
            'opponent_active'       :(By.XPATH, '//div[@class="statbar lstatbar"]/strong'),
        }

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()
        self.driver.quit()

    def load(self):
        self.driver.get(self.BASE)

    def on_change(self, locator, timeout=None):
        timeout = self.timeout if timeout is None else timeout
        return super(ShowdownBattle, self).on_change(locator, timeout)

    def wait_until_equals(self, locator, target, attr=None, timeout=None):
        timeout = self.timeout if timeout is None else timeout
        return super(ShowdownBattle, self).wait_until_equals(locator, target, attr, timeout)

    def get_when_present(self, locator, timeout=None):
        timeout = self.timeout if timeout is None else timeout
        return super(ShowdownBattle, self).get_when_present(locator, timeout)

    def get_all_when_present(self, locator, timeout=None):
        timeout = self.timeout if timeout is None else timeout
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

    def start_battle(self):
        startbattle_btn = self.get_when_present(self.LOCATORS['startbattle_btn'])
        startbattle_btn.click()
        self.wait_until_equals(self.LOCATORS['turn_count'], "Turn 1")

    def get_player_team(self):
        team = self.get_all_when_present(self.LOCATORS['battle_swap_btns'])
        team = [t.text for t in team]
        return team

    def get_active_pokemon(self):
        p_active = self.get_when_present(self.LOCATORS['player_active']).text.split(" ")
        o_active = self.get_when_present(self.LOCATORS['opponent_active']).text.split(" ")
        return p_active, o_active

    def battle_use_move(self, index):
        moves = self.get_all_when_present(self.LOCATORS['battle_moves_btns'])
        moves[index].click()
        #wait until move executed

    def battle_swap(self, index):
        team = self.get_all_when_present(self.LOCATORS['battle_swap_btns'])
        team[index].click()
        #wait until swap executed

if __name__ == "__main__":
    def random_name():
        chars = string.ascii_uppercase.lower() + string.digits
        return ''.join([random.choice(chars) for i in range(10)])

    driver = webdriver.Chrome(executable_path="chromedriver")
    with ShowdownBattle(driver) as showdown:
        showdown.set_name(random_name())
        showdown.start_battle()

        team = showdown.get_player_team()
        print "Player Team: {}".format(team)

        for turn in showdown.on_change(showdown.LOCATORS['turn_count'],
                                       timeout=-1):
            p_active, o_active = showdown.get_active_pokemon()
            print "Turn 1: %s VS %s" % (p_active, o_active)

