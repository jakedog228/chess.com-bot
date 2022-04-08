# Chess.com bot
# Jakedog, 4/6/2022


from game_handling import *
from setup import *


def main():
    print('WARNING: USE AT YOUR OWN RISK. Although this will only play against bots, you might want to use an alt\n'
          'WARNING: Modification of this program to play against real players is not advised\n\n'
          'THIS IS FOR EDUCATIONAL PURPOSES ONLY\n')

    username = input('Chess.com Username: ')
    password = input('Chess.com Username: ')

    # Setup
    driver = setup_chrome_driver()
    login(driver, username, password)
    go_to_game(driver)
    print('\n')  # format around the WebDriver_manager logging

    stock = safe_stock()  # Stockfish engine

    turn = 1  # Count the amount of turns past
    while True:
        board = read_board(driver)
        fen = format_to_fen(board, turn)
        move = best_move(stock, fen)
        move_piece(driver, move)
        print(f'TURN {turn:02d}: {move[:2]} -> {move[2:]}')
        wait_for_turn(driver, turn)
        turn += 1


if __name__ == "__main__":

    main()
