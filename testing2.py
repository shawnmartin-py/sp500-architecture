from threading import Event, Thread
from time import sleep


class EventVar(Event):
    def __init__(self):
        super().__init__()
        self.__value = None

    @property
    def value(self):
        self.wait()
        return self._value

    @value.setter
    def value(self, value):
        if not self._value:
            self._value = value
            self.set()


var = EventVar()


def consumer(i):
    sleep(i)
    print(var.value)


def producer():
    sleep(4)
    var.value = "Apple"


threads = []

for i in range(10):
    t = Thread(target=consumer, args=[i])
    threads.append(t)
    t.start()

thread = Thread(target=producer)
thread.start()



for t in threads:
    t.join()


