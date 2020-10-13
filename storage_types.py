import copy
import random
import json

from bisect import bisect


class Map2D(object):
    def __init__(self, width, height, default=None): # (self) Initialise 2d map width, height, and default value
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

    def copy(self): # (Map2D) Makes a shallow copy of the data
        new = Map2D(self.width, self.height, self.default)
        new.data = [x[:] for x in self.data]
        return new


class AIStorage(dict):
    def __init__(self, width, default, *args, **kwargs): # (self) Initialise defualt value based on width
        super().__init__(*args, **kwargs)
        self.width=width
        self.default=[default]*width


    def __repr__(self): # (str) String representation of the object
        return "<%s(width=%s, length=%s)>"%(self.__class__.__name__, self.width, len(self))

    def __getitem__(self, key): # (unknown) Gets the value with key "key" if not existoing add it and return default
        try:
            return super().__getitem__(key)
        except KeyError:
            self[key] = self.default.copy()
            return self[key]

    def make_choice(self, hash): # (int) Makes a choice between options based on stored wightings
        # if not self[hash]: return random.choice(range(self.width))
        weights = self[hash]
        total = 0
        cum_weights = [] # acumulative weights
        for w in weights:
            total += abs(w)+random.random()*10 # add a small randomness to prevent getting stuck in losing loop
            cum_weights.append(total)
        random_point = random.random() * total # represents a value in 0 < x < total
        out = bisect(cum_weights, random_point-1) # -1 as not to exceed max cum_wight value
        return out

    @classmethod
    def from_file(cls, file, width=7, default=0): # (AIStorage) Make the object from a file contaning the data
        open(file, "a").close() # make file if not exits
        with open(file, "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                data = {"width":width, "data":{}} # defautl value
            return cls(data["width"], default, data["data"])

    def to_file(self, file): # (None) Saves the data to a file in json format
        with open(file, "w") as f:
            json.dump({"width":self.width, "data":self}, f)
