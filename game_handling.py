# Functions that handle playing the game
from util import *

from time import sleep
import stockfish

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions

FEN_DICTIONARY = {  # Translator for chess.com's piece format to the FEN format
    'br': 'r',  # black pieces
    'bn': 'n',
    'bb': 'b',
    'bk': 'k',
    'bq': 'q',
    'bp': 'p',
    'wr': 'R',  # white pieces
    'wn': 'N',
    'wb': 'B',
    'wk': 'K',
    'wq': 'Q',
    'wp': 'P',
}


# Wrapper that gets the next best move with the current position
def best_move(stock: stockfish.Stockfish, fen: str) -> str:
    stock.set_fen_position(fen)
    move = stock.get_best_move()
    return move


# Move a piece given a stockfish move command
def move_piece(driver: webdriver, move: str):
    # Parse the stockfish format
    origin = move[:2]
    destination = move[2:4]

    click_square(driver, origin)
    sleep(0.5)
    click_square(driver, destination)
    sleep(0.5)

    if len(move) == 5:  # 5th character indicates a promotion
        promote(driver, move[4])
        sleep(0.5)


# Format the board data into a valid FEN string for stockfish
def format_to_fen(board_info: list, moves) -> str:
    global FEN_DICTIONARY

    # An empty board with just coordinates: [['a1', 'b1', 'c1'...], ['a2', 'b2', 'c2'...]...]
    coords = [[f'{chr(int(letter + 1 + 96))}' + str(number + 1) for letter in range(8)] for number in range(8)]
    occupied_spaces = [square[1] for square in board_info]
    fen = ''

    # FEN formats from top down
    coords.reverse()
    for row in coords:
        counter = 0  # Counts how many spaces are between pieces in a row
        for square in row:
            if square in occupied_spaces:
                if counter != 0:
                    fen += str(counter)
                # Add the piece that is on that square to the FEN
                fen += board_info[occupied_spaces.index(square)][0]
                counter = 0
            else:
                counter += 1
        if counter != 0:
            fen += str(counter)
        fen += '/'  # new lines
    fen = fen[:-1]  # remove last slash
    fen += ' w'  # we always play with white
    # TODO: Add a check that allows the program to find castling rights
    fen += ' -'
    # Todo: Add a check for En Passant targets
    fen += ' -'
    # TODO: Add a check for Half-move Clock
    fen += ' 0'
    fen += f' {moves}'

    return fen


# Read the current position of the board based on page elements
def read_board(driver: webdriver) -> list:
    board = []

    entire_board = driver.find_element(By.XPATH, r'//*[@id="board-play-computer"]')
    board_elements = entire_board.find_elements(By.TAG_NAME, "div")

    # Temp folder to contain the board data
    elements = [elem.get_attribute('class') for elem in board_elements if
                'piece' in elem.get_attribute('class') and 'promotion' not in elem.get_attribute('class')]
    for element in elements:  # xpath strings, not objects
        # print(element)
        piece_type = FEN_DICTIONARY[[val for val in element.split(' ') if len(val) == 2][0]]
        # print(piece_type)
        raw_coord = ''.join([char for char in element if char.isnumeric()])  # number-number representation
        # print(raw_coord)
        coordinates = chr(ord('`') + int(raw_coord[0])) + raw_coord[1]  # format to letter-numeric representation
        # print(coordinates)

        board.append((piece_type, coordinates))

    return board


# Handle promotions
def promote(driver: webdriver, promotion_type: str):
    global FEN_DICTIONARY

    # wait for promotion window to show up
    # promotion_window = '//*[@id="board-liveGame-43127971435"]/div[37]'
    # wait_for_element(driver, promotion_window)
    sleep(0.5)

    # Order of selections is random, so we find the right one based on element class names
    choices = [f'//*[@id="board-play-computer"]/div[37]/div[{i}]' for i in range(1, 5)]
    choice = [choice for choice in choices if
              promotion_type in driver.find_element(By.XPATH, choice).get_attribute('class').split(' ')[1]][0]

    chosen_promotion = driver.find_element(By.XPATH, choice)
    chosen_promotion.click()


# Wait for your turn, also detects game over via bool
def wait_for_turn(driver: webdriver) -> bool:
    # Check if the game is already over
    game_over_popup = '//*[@id="game-over-modal"]/div/div[2]/div'
    if wait_for_element(driver, game_over_popup, patience=0.1):  # detect for game end
        return False

    # Allow a retry if we didn't successfully make a move
    patience = 10.0  # seconds to wait for the turn to change
    check_delay = 0.3  # seconds to wait between checks
    for _ in range(int(patience / check_delay)):
        # Check if the turn has changed
        last_move = driver.find_element(By.CLASS_NAME, 'selected')
        parent_element = last_move.find_element(By.XPATH, '..')
        if "black-move" in parent_element.get_attribute('class'):
            return True
        else:
            sleep(check_delay)
    else:
        print(f'Failed to detect turn change after {patience} seconds')
        return False

