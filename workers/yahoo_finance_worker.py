from datetime import datetime
from multiprocessing import Queue
from queue import Empty
from random import random
from threading import Thread
from time import sleep

from lxml.html import fromstring
from requests import get


class YahooFinancePriceScheduler(Thread):
    def __init__(
        self, 
        input_queue: "Queue[str]",
        output_queues: "list[Queue[tuple[str, float, datetime] | str]]",
        **kwargs
    ):
        super().__init__(**kwargs)
        self._input_queue = input_queue
        self._output_queues = output_queues
        self.start()

    def run(self):
        while True:
            try:
                value = self._input_queue.get(timeout=10)
            except Empty:
                break
            if value == "DONE":
                break
            price = YahooFinancePriceWorker(value).get_price()
            if price:
                for output_queue in self._output_queues:
                    output_queue.put((value, price, datetime.now()))
            sleep(random())
        


class YahooFinancePriceWorker:
    def __init__(self, symbol: str):
        self._symbol = symbol
        self._url = f"https://finance.yahoo.com/quote/{symbol}"

    def get_price(self) -> float | None:
        response = get(self._url)
        if response.status_code != 200:
            return
        page_contents = fromstring(response.text)
        raw_price = page_contents.xpath(
            '//*[@id="quote-header-info"]/div[3]/div[1]/div/fin-streamer[1]'
        )[0].text.replace(",", "")
        price = float(raw_price)
        if not price:
            print("Error with: ", self._symbol)
            print("Value: ", raw_price, " -> ", price)
            print(response.status_code)
        return price


if __name__ == "__main__":
    print(YahooFinancePriceWorker("AAPL").get_price())
   