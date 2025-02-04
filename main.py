from game_handling import *
from startup import *


DEFAULT_CATEGORY = 'Master'
DEFAULT_BOT = 'Francis'


def main():
    # Get initial game condition from CLI
    bot_category = input(f'Bot Category (default={DEFAULT_CATEGORY}): ') or DEFAULT_CATEGORY
    bot_name = input(f'Bot Name (default={DEFAULT_BOT}): ') or DEFAULT_BOT  # default n/a if category is not Master

    username = input('Chess.com Username: ')
    password = input('Chess.com Password: ')
    print()

    # Setup
    print('loading browser...')
    driver = setup_chrome_driver()
    login(driver, username, password)
    go_to_game(driver, bot_category, bot_name)
    print('game loaded!')
    print()

    print('loading Stockfish...')
    stock = safe_stock()  # Stockfish engine
    print('Stockfish loaded!')
    print()

    print(f'--- Starting game against {bot_name} ---')
    turn = 1  # Count the amount of turns past
    while True:
        board = read_board(driver)
        fen = format_to_fen(board, turn)
        move = best_move(stock, fen)
        print(f'TURN {turn:02d}: {move[:2]} -> {move[2:]}')
        move_piece(driver, move)
        keep_playing = wait_for_turn(driver)
        if not keep_playing:
            break
        turn += 1

    print(f'--- Finished game against {bot_name} ---')
    input('\nExit Program (Press any Key) > ')
    driver.close()


if __name__ == "__main__":
    main()
