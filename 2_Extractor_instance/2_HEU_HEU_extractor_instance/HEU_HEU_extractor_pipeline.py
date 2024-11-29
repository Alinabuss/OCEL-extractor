import time
from Collector_subcomponent.Collector_instance import OCEL_heuristic_collector_component
from Refiner_subcomponent.Refiner_instance import OCEL_heuristic_refiner_component

# Specify folder-path to dataset
dataset_folder = "Data/Age_of_empire/Test_data/"

# Definition of OCEL_event_level_extractor pipeline
def OCEL_HEU_HEU_extractor(dataset_folder, level):

    OCEL_heuristic_collector_component(dataset_folder, level)
    OCEL_heuristic_refiner_component(dataset_folder)

if __name__ == "__main__":
    start_time = time.time()
    OCEL_HEU_HEU_extractor(dataset_folder, level = 'Test_setup')
    end_time = time.time()
    elapsed_time = end_time - start_time
    # Convert elapsed time to hours, minutes, and seconds
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Execution time: {int(hours)}h {int(minutes)}m {int(seconds)}s")