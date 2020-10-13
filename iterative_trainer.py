from game import AIPlayer
from game import NoRenderBoard
from game import Board
from storage_types import AIStorage

from loadingbar import LoadingBar # windows cmd loadingbar render helper
from itertools import count # infinite counter


DEFAULT_WEIGHTING = 0 # default weighting
WEIGHTING = 1 # how much a loss or win affects the ai
BATCH_SIZE = 5000 # number of games to do between saves

def train(default_weighting, weighting, batch_size):
    while True: # train forever
        aip = AIStorage.from_file("monte_carlo_storage.json", 7, default_weighting) # load current AI leaning from file
        lb = LoadingBar(batch_size, 0, 30, "games", batch_size//100) # configure a loading bar

        for n,i in enumerate(range(batch_size)): # for each game
            if n % 10 == 0: # updates the loadingbar every 10 games
                lb.update(n, 1)
                lb.print()

            # make 2 AIPlayers and add them to a NoRenderBoard
            p1 = AIPlayer(aip, "█")
            p2 = AIPlayer(aip, " ")
            b = NoRenderBoard(p1, p2)

            if b.player1 == b.play(): # if a player has won
                for key in b.player1.moves:
                    aip[key][b.player1.moves[key]] += weighting # reward the player
            else: # the attemped play was invalid punish it
                for key in b.player1.moves:
                    aip[key][b.player1.moves[key]] -= weighting # punish the player

            for key in b.player2.moves:
                aip[key][b.player2.moves[key]] -= weighting # punish the losing player

            # force clear ram
            del p1
            del p2
            del b

        # finsish and forget loading bar
        lb.complete()
        lb.print()
        del lb
        # save progress and notify user
        aip.to_file("monte_carlo_storage.json")
        print("save")

        del aip
        # clear old object


if __name__ == '__main__':
    train(DEFAULT_WEIGHTING, WEIGHTING, BATCH_SIZE)
