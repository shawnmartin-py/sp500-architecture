from functools import cached_property, lru_cache
from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor
from time import sleep







class GetAPIKey(Thread):
    def __init__(self):
        super().__init__()
        self.event = Event()
        self.start()

    def run(self):
        sleep(5)
        self.value = "Result from API call"
        self.event.set()

    @property
    def key(self):
        self.event.wait()
        return self.value


@lru_cache(1)
def get_api_key_worker():
    return GetAPIKey()



def fn(*args):
    while True:
        worker = get_api_key_worker()
        print(worker.key)
        break


with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(fn, range(5))


exit()





threads = []

for i in range(5):
    t = Thread(target=fn)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("finished")

