from game import Player
from game import AIPlayer
from game import RandomPlayer
from game import BestChoiceAIPlayer
from game import Board
from game import NoRenderBoard
from storage_types import AIStorage



def play(aip): # (None) play a best choice ai against human
    p1 = Player("█")
    p2 = BestChoiceAIPlayer(aip, " ")
    b = Board(p1, p2)
    b.render()

    return b.play()


def playrand(aip, win_log): # (None) play a best choice ai against human
    p1 = RandomPlayer("█")
    # p1 = AIPlayer(" ")
    p2 = BestChoiceAIPlayer(aip, " ")
    b = NoRenderBoard(p1, p2)

    win_log[b.play().render()] += 1


if __name__ == '__main__':
    # PLay ai vs random
    aip = AIStorage.from_db("database.db") # load current AI leaning from database
    win_log = {"██":0, "  ":0, "░░":0}
    for i in range(100):
        playrand(aip, win_log) # play if run as main file
    print(win_log)

    # play human vs ai
    print("winner", play(aip).render())
