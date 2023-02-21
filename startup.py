# Functions for setting up the board

from util import *

import stockfish
import undetected_chromedriver
from os.path import join
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


STOCKFISH_FILE = r'dependencies\stockfish_14.1_win_x64_avx2.exe'  # faster stockfish engine
BACKUP = r'dependencies\stockfish_14.1_win_x64_popcnt.exe'  # slower, but more stable


# Make a stockfish instance
def safe_stock() -> stockfish.Stockfish:
    global STOCKFISH_FILE, BACKUP
    try:
        stock = stockfish.Stockfish(path=join(module_path(), STOCKFISH_FILE))
    except Exception:
        stock = stockfish.Stockfish(path=join(module_path(), BACKUP))

    return stock


# Wrapper for chrome-based driver that bypasses cloudflare
def setup_chrome_driver() -> undetected_chromedriver.Chrome:
    driver = undetected_chromedriver.Chrome()
    driver.maximize_window()

    return driver


# Login to chess.com with a given account
def login(driver: webdriver, username: str, password: str):
    username_field = '//*[@id="username"]'
    password_field = '//*[@id="password"]'
    login_button = '//*[@id="login"]'

    driver.get('https://www.chess.com/login')
    wait_for_element(driver, username_field)

    driver.find_element(By.XPATH, username_field).send_keys(username)
    driver.find_element(By.XPATH, password_field).send_keys(password)
    sleep(1)
    driver.find_element(By.XPATH, login_button).click()

    wait_for_redirect(driver, 'https://www.chess.com/home')  # wait out cloudflare

    if driver.current_url != 'https://www.chess.com/home':
        print('COULD NOT LOGIN!')
        sys.exit()


# Open a bot game against "Francis"
def go_to_game(driver: webdriver):
    driver.get('https://www.chess.com/play/computer')

    sleep(0.5)

    # These buttons only show up sometimes
    try:
        okay_button = '/html/body/div[25]/div[2]/div/div/div[2]/div[2]/button'
        driver.find_element(By.XPATH, okay_button).click()
    except NoSuchElementException:
        pass
    try:
        skip_trial_button = '/html/body/div[1]/div[4]/div[2]/div/div/div[3]/button'
        driver.find_element(By.XPATH, skip_trial_button).click()
    except NoSuchElementException:
        pass

    # Change this for a different bot
    francis_bot = '//*[@id="board-layout-sidebar"]/div/section/div/div/div[5]/div[2]/div[6]'
    wait_for_element(driver, francis_bot)
    driver.find_element(By.XPATH, francis_bot).click()

    choose_button = '//*[@id="board-layout-sidebar"]/div/div[2]/button'
    driver.find_element(By.XPATH, choose_button).click()

    challenge_button = '//*[@id="board-layout-sidebar"]/div/section/div/div[2]/div[1]/div'
    wait_for_element(driver, challenge_button)
    driver.find_element(By.XPATH, challenge_button).click()

    play_button = '//*[@id="board-layout-sidebar"]/div/div[2]/button'
    driver.find_element(By.XPATH, play_button).click()
