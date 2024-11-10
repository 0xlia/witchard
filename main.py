from game import WitchardGame
import sys

def main():
    game = WitchardGame(num_players=4)
    game.start_game()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
