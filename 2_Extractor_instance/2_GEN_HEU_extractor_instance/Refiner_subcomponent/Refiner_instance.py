import os
import json
from Refiner_subcomponent.Modularized_functions.OCEL_reader import OCEL_reader
from Refiner_subcomponent.Modularized_functions.OCEL_concatenator import OCEL_concatenator
from Refiner_subcomponent.Modularized_functions.Object_refiner import object_refiner
from Refiner_subcomponent.Modularized_functions.Event_refiner import  event_refiner
from Refiner_subcomponent.Modularized_functions.Mutual_exclusion_steps import mutual_exclusion_steps
from Refiner_subcomponent.Modularized_functions.remove_very_similar_entities_over_all_categories import remove_very_similar_entities_over_all_categories
from Refiner_subcomponent.Modularized_functions.Name_cleaner import clean_all_names
from Refiner_subcomponent.Modularized_functions.ensure_correct_type_instance_mapping import ensure_correct_type_instance_mapping
import nltk

nltk.download('wordnet')

def OCEL_heuristic_refiner_component(dataset_folder):

    extracted_event_log_path = os.path.join(dataset_folder, "Extracted_logs/GEN_subsets/")
    saving_folder = os.path.join(dataset_folder, "Extracted_logs/")

    # Extract original and extracted event logs into sets
    OCEL_list = OCEL_reader(extracted_event_log_path)

    # Concatenate all elements in the extracted event log set to one new OCEL
    log = OCEL_concatenator(OCEL_list, saving_folder)

    # Application of refinement steps multiple times
    no_change = False
    counter = 0
    while no_change == False and counter < 5:
        ocel_start = log.copy()
        log = clean_all_names(log)
        log = mutual_exclusion_steps(log)
        log = remove_very_similar_entities_over_all_categories(log)
        log = object_refiner(log)
        log = event_refiner(log)
        log = ensure_correct_type_instance_mapping(log)
        counter += 1
        print(f"{counter}. refinement iteration concluded")
        if ocel_start == log:
            no_change = True
            print("Refinement concluded as there are no more changes")
        elif counter == 5:
            print("No more iterations")




    # Save final refined OCEL log
    output_path = os.path.join(saving_folder, "final_event_log.json")
    # Write the OCEL2.0 log to a JSON file
    with open(output_path, "w") as f:
        json.dump(log, f, indent=4)
    #pm4py.write.write_ocel2_json(refined_log, output_path)






