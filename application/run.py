from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time

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
    def __init__(self, driver, wait_limit=10):
        self.driver = driver
        self.wait_limit = wait_limit

    def get(self, locator):
        return driver.find_element(locator[0], locator[1])

    def on_change(self, locator):
        try:
            while True:
                curr = self.get(locator).text
                WebDriverWait(driver, self.wait_limit).until(
                    WaitOnTextChanged(locator, curr)
                )
                yield self.get(locator).text
        except (TimeoutException, NoSuchElementException):
            yield None

    def wait_until_equals(self, locator, target, attr):
        """
        Waits until the locator has the target value
        """
        try:
            WebDriverWait(driver, self.wait_limit).until(
                WaitUntilEquals(locator, target, attr)
            )
            return True
        except (NoSuchElementException):
            pass
        except (TimeoutException):
            return False

    def get_when_present(self, locator):
        try:
            WebDriverWait(driver, self.wait_limit).until(
                EC.presence_of_element_located(locator)
            )
            return driver.find_element(locator[0], locator[1])
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
            'battle_log'            :(By.XPATH, '//div[@class="battle-log"]'),
            'battle_moves_btns'     :(By.XPATH, '//div[@class="movemenu"]/button')
        }

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()
        self.driver.quit()

    def load(self):
        self.driver.get(self.BASE)

    def on_change(self, locator):
        yield super(ShowdownBattle, self).on_change(locator)

    def wait_until_equals(self, locator, target, attr=None):
        return super(ShowdownBattle, self).wait_until_equals(locator, target, attr)

    def get_when_present(self, locator):
        return super(ShowdownBattle, self).get_when_present(locator)

    def set_name(self, name):
        setname_btn_open = self.get_when_present(self.LOCATORS['setname_btn_open'])
        setname_btn_open.click()
        setname_txt = self.get_when_present(self.LOCATORS['setname_txt'])
        setname_txt.send_keys(name)
        setname_btn = self.get_when_present(self.LOCATORS['setname_btn_submit'])
        setname_btn.click()
        print "clicked thing"
        self.wait_until_equals(self.LOCATORS['curr_name'], " {}".format(name), 
                attr='data-name') #confirm name updated
        print "done waiting"

    def start_battle(self):
        startbattle_btn = self.get_when_present(self.LOCATORS['startbattle_btn'])
        startbattle_btn.click()
        battle_log = self.get_when_present(self.LOCATORS['battle_log'])


if __name__ == "__main__":
    driver = webdriver.Chrome(executable_path="chromedriver")
    with ShowdownBattle(driver) as showdown:
        showdown.set_name('yonatano')
        showdown.start_battle()
        time.sleep(5)


