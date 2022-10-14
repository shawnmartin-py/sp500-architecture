from multiprocessing import Queue
from typing import Generator
from threading import Thread

from bs4 import BeautifulSoup
from requests import get


class WikiWorkerMasterScheduler(Thread):
    def __init__(self, output_queues: "list[Queue[str]]", **kwargs):
        kwargs.pop("input_queue")
        self._input_values = kwargs.pop("input_values")
        super().__init__(**kwargs)
        self._output_queues = output_queues
        self.start()

    def run(self):
        for entry in self._input_values:
            wiki_worker = WikiWorker(entry)
            symbol_counter = 0
            for symbol in wiki_worker.get_sp_500_companies():
                for output_queue in self._output_queues:
                    output_queue.put(symbol)
                symbol_counter += 1
                # if symbol_counter >= 5:
                #     break

class WikiWorker:
    def __init__(self, url):
        self._url = url

    @staticmethod
    def _extract_company_symbols(page_html) -> Generator[str, None, None]:
        soup = BeautifulSoup(page_html, "lxml")
        table = soup.find(id="constituents")
        table_rows = table.find_all("tr")
        for table_row in table_rows[1:]:
            yield table_row.find("td").text.strip("\n")

    def get_sp_500_companies(self) -> Generator[str, None, None]:
        response = get(self._url)
        if response.status_code != 200:
            print("Couldn't get entries")
            return []
        yield from self._extract_company_symbols(response.text)


if __name__ == "__main__":
    for symbol in WikiWorker().get_sp_500_companies():
        print(symbol)
        

