from itertools import count

from storage_types import Map2D
import hashlib

class Base(object):
    def __init__(self, displaychar): # (self) Initialise base object with a display charecter
        self.display = displaychar*2 # render char
    def render(self): # (str) Base render function
        return str(self.display)

class Empty(Base) : pass # for name purposes
class Player(Base):
    def __init__(self, displaychar): # (self) Initialise base object with a display charecter
        super().__init__(displaychar)
        self.board = None # baord refernce
    def __repr__(self): # (str) String representation of the object
        return "<%s(\"%s\")>"%(self.__class__.__name__, self.display)

    def hasboard(f): # (function) function wrapper to ensure wrapped function has board reference
        def func(self, *args, **kwargs): # (unknown) Check for board then return function output passing on *args and **kwargs
            if not self.board : raise ValueError("No board is assigned to player '%s'."%self)
            return f(self, *args, **kwargs)
        return func # retunr the wrapped function

    @hasboard
    def play(self): # (True) Make a play on the assigned board; return play validity
        while True:
            try:
                print(self.render(), end="")
                x = int(input(":"))
                if self.board.drop(x, self): break # break on successfull play
            except ValueError:
                pass
        return True

class AIPlayer(Player):
    def __init__(self, ai_storage, displaychar=" "): # (self) make player based ai
        super().__init__(displaychar)
        self.ai_storage = ai_storage # AIStorage component
        self.moves = dict() # moves for this player

    @Player.hasboard
    def play(self): # (bool) ai play logic; return play validity
        view_map = self.board.copy() # Map2D of the board

        for x,y in view_map: # make a Map2D of the board from players perspective 1 = self, 2=other, 0 = empt
            if view_map.data[x][y]==self.board.player1:
                view_map.data[x][y] = 1
            elif view_map.data[x][y]==self.board.player2:
                view_map.data[x][y] = 2
            elif view_map.data[x][y]==self.board.default:
                view_map.data[x][y] = 0

        # compress view_map with hash as only differentiation of states needs to be stored
        view_hash = hashlib.sha224(str(view_map.data).encode()).hexdigest() # is relivly short representation of what this player can see
        # calculate and log a move
        play = self.ai_storage.make_choice(view_hash)
        self.moves[view_hash] = play

        if not self.board.drop(play, self): # if the move fails punish self and reward other
            self.board.winner = self.board.player2
            return False
        return True

class BestChoiceAIPlayer(AIPlayer):
    def __init__(self, ai_storage, displaychar=" "): # (self) Initialise BestChoiceAIPlayer
        super().__init__(ai_storage, displaychar)
        self.ai_storage.make_choice = self.make_choice # overrides ai_storage's decision maker

    def make_choice(self, view_hash): # (int) makes choice acording to best knows option
        weights = self.ai_storage[view_hash]
        values = list(range(self.ai_storage.width))
        sorted_choices = sorted(zip(weights, values))
        return sorted_choices[-1][1] # get the value formthe sorted options



class Board(Map2D):
    def __init__(self, player1, player2, width=7, height=6, connect=4): # (self) Initialise board with 2 players, width height and how many connected are required
        Map2D.__init__(self, width, height, Empty("░")) # make the 2d map of board values
        # baord atributes
        self.n = connect
        self.winstate = None
        # store players reference and give them a reference to the board
        self.player1 = player1
        self.player2 = player2
        player1.board = self
        player2.board = self

    def __repr__(self): # (str) String representation of board object
        return "<%s(%s, %s, width=%s, height=%s, connect=%s)>"%(self.__class__.__name__, self.player1, self.player2, self.width, self.height, self.n)

    def render(self): # (str) Render the board
        lines = []
        y_old = None
        lines.append("".join("%02s"%x for x in range(self.width))) # show column indexing
        for x,y in self:
            if not y == y_old: # if we have moved to a new row
                lines.append("")
                y_old = y
            lines[-1] += self.data[x][y].render() # adds the render of the object to the row
        print("\n".join(lines))

    def iswinningset(self, states): # (bool) Checks if the "states" are valid as a winner
        states = list(states) # generate all objects in the generator
        if len(set(states)) == 1: # remove all repetition with set therefore will have length 1 if all the same object (inbuilt calucaulation in c for better efficiency)
            if not states[0] == self.default:
                self.winstate = states[0]
                return True
        return False

    def checkwin(self): # (bool) Check game winsate
        isfull = True # all spaces ocupied no winner
        for x,y in self: # for each (x, y) make a board check making width*height*n checks. For n=width*height check will complete in O(n)
            if self.data[x][y] == self.default:
                isfull=False
            if self.iswinningset(self.raw_get(x+n, y  ) for n in range(self.n)): return True # horizontal
            if self.iswinningset(self.raw_get(x  , y+n) for n in range(self.n)): return True # verticle
            if self.iswinningset(self.raw_get(x+n, y+n) for n in range(self.n)): return True # diagonal (dec)
            if self.iswinningset(self.raw_get(x+n, y-n) for n in range(self.n)): return True # diagonal (asc)
        self.winstate = self.default
        return isfull

    def play(self): # (None) Main baord play loop
        while True:
            if not self.player1.play(): return self.winstate # get the player to make a play
            self.render() # render
            if self.checkwin(): return self.winstate # if winner return the winner
            self.player1, self.player2 = self.player2, self.player1 # swap player1 and player2 for next iteration

    def drop(self, x, player): # (bool) Board modification helper to drop player "player" on the board at "x"; return drop validity
        if not (x < self.width and x >= 0) : return False # selected x is out of range self.width

        for n in count(0, 1): # counts up infinatly
            if n == self.height: # if at bottom of board
                self.data[x][n-1] = player
                break

            if isinstance(self.raw_get(x, n), Player): # if player is below point (x, y)
                if n == 0: return False # if column is full
                self.data[x][n-1] = player
                break

        return True

class NoRenderBoard(Board): # Board with no render function
    def render(self):
        pass
