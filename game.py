from itertools import count


class Base(object):
    def __init__(self, displaychar): # (self) Initialise base object with a display charecter
        self.display = displaychar*2
    def render(self): # (str) Base render function
        return str(self.display)

class Empty(Base) : pass # for name purposes
class Player(Base):
    def __init__(self, displaychar): # (self) Initialise base object with a display charecter
        super().__init__(displaychar)
        self.board = None
    def __repr__(self): # (str) String representation of the object
        return "<%s(\"%s\")>"%(self.__class__.__name__, self.display)

    def hasboard(f): # (function) function wrapper to ensure wrapped function has board reference
        def func(self, *args, **kwargs): # (unknown) Check for board then return function output passing on *args and **kwargs
            if not self.board : raise ValueError("No board is assigned to player '%s'."%self)
            return f(self, *args, **kwargs)
        return func # retunr the wrapped function

    @hasboard
    def play(self): # (None) Make a play on the assigned board
        while True:
            try:
                print(self.render(), end="")
                x = int(input(":"))
                if self.board.drop(x, self): break # break on successfull play
            except ValueError:
                pass

class Board(Base):
    def __init__(self, player1, player2, width=7, height=6, connect=4): # (self) Initialise board with 2 players, width height and how many connected are required
        # baord atributes
        self.width = width
        self.height = height
        self.n = connect
        # initilaisation of data
        self._empty = Empty("░")
        self.data = [ [self._empty] * self.height for x in range(self.width)] # make an empty board
        self.winstate = None
        # store players reference and give them a reference to the board
        self.player1 = player1
        self.player2 = player2
        player1.board = self
        player2.board = self

    def __repr__(self): # (str) String representation of board object
        return "<%s(%s, %s, width=%s, height=%s, connect=%s)>"%(self.__class__.__name__, self.player1, self.player2, self.width, self.height, self.n)
    def __iter__(self): # (generator) Make a generator for each (x,y) point on the board
        for y in range(self.height):
            for x in range(self.width):
                yield x,y

    def render(self): # (str) Render the board
        lines = []
        y_old = None
        lines.append("".join("%02s"%x for x in range(self.width))) # show a column indexing
        for x,y in self:
            if not y == y_old: # if we have moved to a new row
                lines.append("")
                y_old = y
            lines[-1] += self.data[x][y].render() # adds the render of the object to the row
        return "\n".join(lines)

    def raw_get(self, x, y): # (Player or Base) Get the value at (x, y) regardless of validity
        try:
            return self.data[x][y] # data value
        except IndexError:
            return self._empty # default value

    def iswinningset(self, states): # (bool) Checks if the states are valid as a winner
        states = list(states) # generate all objects in the generator
        if len(set(states)) == 1: # remove all repetition with set therefore will have length 1 if all the same object (inbuilt calucaulation in c for better efficiency)
            if not states[0] == self._empty:
                self.winstate = states[0]
                return True
        return False

    def checkwin(self): # (bool) Check game winsate
        for x,y in self: # for each (x, y) make a board check making width*height*n checks. For n=width*height check will complete in O(n)
            if self.iswinningset(self.raw_get(x+n, y  ) for n in range(self.n)): return True # horizontal
            if self.iswinningset(self.raw_get(x  , y+n) for n in range(self.n)): return True # verticle
            if self.iswinningset(self.raw_get(x+n, y+n) for n in range(self.n)): return True # diagonal (dec)
            if self.iswinningset(self.raw_get(x+n, y-n) for n in range(self.n)): return True # diagonal (asc)
        return False

    def play(self): # (None) Main baord play loop
        while True:
            self.player1.play() # get the player to make a play
            print(self.render())
            if self.checkwin(): return self.winstate # return if a winner is found
            self.player1, self.player2 = self.player2, self.player1 # swap player1 and player2 for next iteration

    def drop(self, x, player): # (bool) Board modification helper to drop player "player" on the board at "x"
        if not (x < self.width and x >= 0) : return False # selected x is out of range self.width

        for n in count(0, 1): # counts up infinatly
            if n == self.height: # if at bottom of board
                self.data[x][n-1] = player
                break

            if self.raw_get(x, n).__class__ == Player: # if player is below point (x, y)
                if n == 0: return False
                self.data[x][n-1] = player
                break

        return True


if __name__ == '__main__': # if run as non imported
    # initilaise players and board
    p1 = Player("█")
    p2 = Player(" ")
    b = Board(p1, p2)
    winner = b.play() # get a winner from the board
    print("WINNER:",winner.render())
