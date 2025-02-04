# Functions for setting up the board

from util import *

import stockfish
import undetected_chromedriver
from os.path import join
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


STOCKFISH_FILE = r'dependencies\stockfish-windows-x86-64-avx2.exe'  # faster stockfish engine
BACKUP = r'dependencies\stockfish-windows-x86-64-popcnt.exe'  # slower, but more stable


# Make a stockfish instance
def safe_stock() -> stockfish.Stockfish:
    global STOCKFISH_FILE, BACKUP
    try:
        stock = stockfish.Stockfish(path=join(module_path(), STOCKFISH_FILE))
    except FileNotFoundError:
        try:
            stock = stockfish.Stockfish(path=join(module_path(), BACKUP))
        except FileNotFoundError:
            print('Stockfish executable not found, download from: https://stockfishchess.org/download/')
            sys.exit()

    return stock


# Wrapper for chrome-based driver that bypasses cloudflare
def setup_chrome_driver() -> undetected_chromedriver.Chrome:
    driver = undetected_chromedriver.Chrome()
    # driver.maximize_window()

    return driver


# Login to chess.com with a given account
def login(driver: webdriver, username: str, password: str):
    username_field = '//*[@id="username-input-field"]/div/input'
    password_field = '//*[@id="password-input-field"]/div/input'
    login_button = '//*[@id="login"]'

    driver.get('https://www.chess.com/login')
    wait_for_element(driver, username_field)

    driver.find_element(By.XPATH, username_field).send_keys(username)
    driver.find_element(By.XPATH, password_field).send_keys(password)
    sleep(1)
    driver.find_element(By.XPATH, login_button).click()

    valid_login = wait_for_redirect(driver, 'https://www.chess.com/home')  # wait out cloudflare

    if not valid_login:
        print('COULD NOT LOGIN!')
        sys.exit()


# Open a bot game against "Francis"
def go_to_game(driver: webdriver, bot_category: str, bot_name: str):
    driver.get('https://www.chess.com/play/computer')

    sleep(0.5)

    # Sometimes there's a popup at this point, close it if there is one
    try:
        driver.find_element(By.CSS_SELECTOR, 'button[aria-label=Close]').click()
    except (ElementNotInteractableException, ElementNotInteractableException):
        pass

    # click on the correct category
    wait_for_element(driver, 'bot-group-accordion-component', element_type=By.CLASS_NAME)
    for category in driver.find_elements(By.CLASS_NAME, 'bot-group-accordion-component'):
        if bot_category in category.text:
            category.click()
            correct_category = category
            break
    else:
        print('COULD NOT FIND BOT CATEGORY!')
        sys.exit()

    # click on the correct bot
    bot_selector = f'li[data-bot-selection-name={bot_name}]'
    wait_for_element(driver, bot_selector, element_type=By.CSS_SELECTOR)
    correct_category.find_element(By.CSS_SELECTOR, bot_selector).click()

    # click on the play button
    choose_button = '//*[@id="board-layout-sidebar"]/div/div[2]/div/div[3]/button'
    wait_for_element(driver, choose_button)
    driver.find_element(By.XPATH, choose_button).click()

    # Wait for the game to load
    assert wait_for_element(driver, 'eco-opening-name', element_type=By.CLASS_NAME), 'Game did not load!'
