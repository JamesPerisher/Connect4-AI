import time

class LoadingBar:
    def __init__(self, items=100, speed=0, width=30, speed_units="kb", averge_len=10):
        self.timestart = time.time()
        self.oldtime = self.timestart
        self.elapsedtime = 0
        self.completed = 0
        self.items = items
        self.speed = speed
        self.width = width
        self.percent = 0

        self.speeds = list()
        self.speed_units = speed_units
        self.averge_len = averge_len

    def update(self, items, speed):
        now = time.time()
        if not len(self.speeds) < self.averge_len : self.speeds.pop(0)
        self.completed = items
        since_last = now-self.oldtime + 0.001
        self.oldtime = now
        self.speed = round(speed/since_last, 2)
        self.speeds.append(self.speed)
        self.percent = self.completed / self.items
        self.percent = round(self.completed/self.items, 2)
        self.elapsedtime = round(now - self.timestart, 2)
        return self

    def complete(self):
        self.update(self.items, self.speeds[-1])
        return self


    def print(self, start="    "):
        solidp = round(self.percent*100)
        full = round((self.width*2) *self.percent)
        average_speed = round(sum(self.speeds)/len(self.speeds), 2)
        units = " %s/s"%self.speed_units

        line = "{:}|{:}{:}|  {:>5}/{:<5} [{:>7.2%}] in {:>5.2f}s ({:>6.2f}{:}/s) average {:>5.2f}{:}/s{:<100}".format(start,
        ("█"*(full//2))+"▌"*(full%2), " "*(self.width-full+(full//2)),
        self.completed, self.items, self.percent,
        self.elapsedtime, self.speed, self.speed_units,
        average_speed, self.speed_units, " ")

        print(line, end="\r")
        return self
