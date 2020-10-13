from game import Player
from game import AIPlayer
from game import BestChoiceAIPlayer
from game import Board
from storage_types import AIStorage


def play(): # (None) play a best choice ai against human
    aip = AIStorage.from_file("monte_carlo_storage.json") # load current AI leaning from file

    p1 = Player("█")
    # p1 = AIPlayer(" ")
    p2 = BestChoiceAIPlayer(aip, " ")
    b = Board(p1, p2)

    b.render() # show empty board
    print("winner:", b.play().render())


if __name__ == '__main__':
    play() # play if run as main file
