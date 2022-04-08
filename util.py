# Functions that other functions rely on

import sys
from os.path import dirname

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


# Clicks on the area of the board, even if there is no object there
def click_square(driver: webdriver, square: str):
    numeric_form = str(ord(square[0])-96) + square[1]  # ex: b3 -> 23
    x, y = int(numeric_form[0]), 8-int(numeric_form[1])  # y is inverse because the board starts at the bottom left

    board_object = driver.find_element(By.XPATH, r'//*[@id="board-vs-personalities"]')
    size = board_object.size

    square_size = size['height']//8  # height and width in pixels of every square
    square_coordinates = (x * square_size, y * square_size)

    # Click on the board, with the position of the square as an offset
    action = ActionChains(driver)
    action.move_to_element_with_offset(board_object, square_coordinates[0]-1, square_coordinates[1]+1)
    action.click()
    action.perform()


def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if hasattr(sys, "frozen"):
        return dirname(sys.executable)

    return dirname(__file__)


# Wait for the existence of a given element, or return if element exists
def wait_for_element(driver: webdriver, element: str, patience=10.0) -> bool:
    try:
        WebDriverWait(driver, patience).until(expected_conditions.presence_of_element_located((By.XPATH, element)))
    except TimeoutException:
        return False  # loading took too much time
    return True


# Wait for a redirect, used in logging in
def wait_for_redirect(driver: webdriver, url: str, patience=8):
    try:
        WebDriverWait(driver, patience).until(expected_conditions.url_matches(url))
    except TimeoutException:
        pass
