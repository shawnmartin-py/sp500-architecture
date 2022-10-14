from datetime import datetime
from multiprocessing import Queue
from queue import Empty
from threading import Thread

from decouple import config
from sqlalchemy.engine.url import URL
from sqlmodel import create_engine, insert

from models import Price


class SqliteMasterScheduler(Thread):
    def __init__(
        self,
        input_queue: "Queue[tuple[str, float, datetime] | str]",
        **kwargs
    ):
        kwargs.pop("output_queues", None)
        super().__init__(**kwargs)
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            try:
                values = self._input_queue.get(timeout=10)
            except Empty:
                break
            if values == "DONE":
                break
            SqliteWorker(*values).insert_into_db()


class SqliteWorker:
    def __init__(self, symbol: str, price: float, extracted_time: datetime):
        self._symbol = symbol
        self._price = price
        self._extracted_time = extracted_time
        url = URL.create(
            drivername="sqlite",
            host=config("DB_HOST"),
            database=config("DB_NAME")
        )
        self._engine = create_engine(url)

    def insert_into_db(self):
        with self._engine.connect() as connection:
            connection.execute(
                insert(Price).values(
                    symbol=self._symbol,
                    price=self._price,
                    extracted_time=self._extracted_time
                )
            )
            connection.commit()
            print(f"Inserted: {self._symbol}")


if __name__ == "__main__":
    sqlite_worker = SqliteWorker("AAPL", 157.28, datetime.now())
    sqlite_worker.insert_into_db()