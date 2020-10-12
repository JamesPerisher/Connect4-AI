class Map2D(object):
    def __init__(self, width, height, default=None): # (self) Initialise 2d map width height and default value
        # initialise map values
        self.width = width
        self.height = height
        self.default = default
        # make the map with the defualt
        self.data = [ [self.default] * self.height for x in range(self.width)] # make an empty board

    def __repr__(self): # (str) String representation of map object
        return "%s(width=%s, height=%s)"%(self.__class__.__name__, self.width, self.height)
    def __eq__(self, other): # (bool) Is one instance is equal to another
        if not isinstance(other, self): return False
        return self.data == other.data
    def __ne__(self, other): # (bool) Is one instance is NOT equal to another
        return not self.__eq__(other)
    def __iter__(self): # (generator) Make a generator for each (x,y) point on the board
        for y in range(self.height):
            for x in range(self.width):
                yield x,y

    def raw_get(self, x, y): # (unknown) Get the value at (x, y) regardless of validity of index [x][y]
        try:
            return self.data[x][y] # data value
        except IndexError:
            return self.default
