from importlib import import_module
from multiprocessing import Queue
from threading import Thread
from time import sleep

from yaml import safe_load


class YamlPipelineExecutor(Thread):
    def __init__(self, pipeline_location: str):
        super().__init__()
        self._pipeline_location = pipeline_location
        self._workers = {}
        self._queue_consumers = {}
        self._downstream_queues = {}

    def _load_pipeline(self):
        with open(self._pipeline_location) as file:
            self._yaml_data: dict = safe_load(file)

    def _initialize_queues(self):
        self._queues = {
            queue["name"]: Queue() for queue in self._yaml_data["queues"]
        }

    def _initialize_workers(self):
        worker: dict
        for worker in self._yaml_data["workers"]:
            worker_class = getattr(
                import_module(worker["location"]), worker["class"]
            )
            input_queue = worker.get("input_queue")
            output_queues = worker.get("output_queues")
            worker_name = worker["name"]
            num_instances = worker.get("instances", 1)
            self._downstream_queues[worker_name] = output_queues
            if input_queue:
                self._queue_consumers[input_queue] = num_instances
            init_params = {
                "input_queue": self._queues.get(input_queue),
                "output_queues": [
                    self._queues.get(output_queue) 
                    for output_queue in output_queues
                    if self._queues.get(output_queue)
                ] if output_queues else []
            }
            input_values = worker.get("input_values")
            if input_values:
                init_params["input_values"] = input_values
            self._workers[worker_name] = [
                worker_class(**init_params) for _ in range(num_instances)
            ]

    def _join_workers(self):
        worker_name: str
        for worker_name in self._workers:
            worker_name.lower()
            worker_thread: Thread
            for worker_thread in self._workers[worker_name]:
                worker_thread.join()

    def process_pipeline(self):
        self._load_pipeline()
        self._initialize_queues()
        self._initialize_workers()

    def run(self):
        self.process_pipeline()
        while True:
            total_workers_alive = 0
            worker_stats = []
            to_del = []
            for worker_name in self._workers:
                total_worker_threads_alive = 0
                for worker_thread in self._workers[worker_name]:
                    if worker_thread.is_alive():
                        total_worker_threads_alive += 1
                total_workers_alive += total_worker_threads_alive
                if not total_worker_threads_alive:
                    if self._downstream_queues[worker_name]:
                        for output_queue in self._downstream_queues[worker_name]:
                            number_of_consumers = self._queue_consumers[output_queue]
                            for _ in range(number_of_consumers):
                                self._queues[output_queue].put("DONE")
                    to_del.append(worker_name)
                worker_stats.append([worker_name, total_worker_threads_alive])
            print(worker_stats)
            if not total_workers_alive:
                break
            for worker_name in to_del:
                del self._workers[worker_name]
            sleep(5)


if __name__ == "__main__":
    file_location = "pipelines/wiki_yahoo_scraper_pipeline.yaml"
    YamlPipelineExecutor(file_location).process_pipeline()
