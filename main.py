from time import perf_counter

from decouple import config
from yaml_reader import YamlPipelineExecutor


def main():
    start = perf_counter()
    pipeline_location = config("PIPELINE_LOCATION")
    yaml_pipeline_executor = YamlPipelineExecutor(pipeline_location)
    yaml_pipeline_executor.start()
    yaml_pipeline_executor.join()
    print(f"Run in {perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()

