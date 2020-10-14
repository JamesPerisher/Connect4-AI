import copy
import random
import sqlite3

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


class AIStorage(): # There is no risk of SQL injection as no data comes from the client
    def __init__(self, conn, c, width, default): # (self) Make object
        self.conn = conn
        self.c = c
        self.width=width

        self.default=[default]*width # Initialise the default value
        self.make_database() # Initialise the database

    def make_database(self): # (None) Make the database table if not existing
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS board_data_{:} (
        id	INTEGER PRIMARY KEY AUTOINCREMENT,
        boardstate	TEXT,
        {:}
        );""".format(self.width, ",\n".join(["        column_%s	INTEGER" % x for x in range(self.width)]))) # create self.width columns in the database acording to board size

    def save(self): # (None) Save the database to file
        self.conn.commit()

    def isvalue(self, hash): # (bool) Check if hash exists in the table
        self.c.execute("SELECT id FROM board_data_{:} WHERE boardstate=\"{:}\"".format(self.width, hash))
        return not len(self.c.fetchall()) == 0

    def __getitem__(self, hash):  # (unknown) Gets the value with key "key" if not existoing add it and return default
        self.c.execute("SELECT * FROM board_data_{:} WHERE boardstate=\"{:}\"".format(self.width, hash))
        try:
            return self.c.fetchall()[0][2::] # If can't get item doesnt exist yet
        except Exception as e:
            cc = self.default.copy()
            self.new(hash, cc)
            return cc

    def new(self, hash, values): # (bool) makes new database entry
        if self.isvalue(hash): return False # already exists ignore
        self.c.execute("INSERT INTO board_data_{:} VALUES (NULL, \"{:}\", {:})".format(self.width, hash, ", ".join(str(x) for x in values)))
        return True

    def add(self, hash, index, amount): # (None) Add amount to a datapoint in the db
        new_value = self[hash][index] + amount
        self.c.execute("UPDATE board_data_{:} SET column_{:}={:} WHERE boardstate=\"{:}\"".format(self.width, index, new_value, hash))


    def make_choice(self, hash): # (int) Makes a choice between options based on stored wightings
        weights = self[hash]
        offset = min(weights)
        weights = [x+offset for x in weights]
        total = 0
        cum_weights = [] # acumulative weights
        for w in weights:
            total += abs(w)+random.random()*10 # add a small randomness to prevent getting stuck in losing loop
            cum_weights.append(total)
        random_point = random.random() * total # represents a value in 0 < x < total
        out = bisect(cum_weights, random_point-1) # -1 as not to exceed max cum_wight value
        return out

    @classmethod
    def from_db(cls, db_file, width=7, default=0): # (AIStorage) Make AIStorage object from a database file
        conn = sqlite3.connect("database.db") # make connection to db
        c = conn.cursor() # get a cursor
        return cls(conn, c, width, default)
