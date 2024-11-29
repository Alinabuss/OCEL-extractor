import os
import shutil
import pm4py
import json
import re

def comparison_sets_creator(dataset_folder):

    # Creation of comparison folder
    comparison_folder = os.path.join(dataset_folder, "Comparison_sets/")
    textual_event_descriptions_folder = os.path.join(dataset_folder, "Textual_descriptions/Event_reports/")
    os.makedirs(comparison_folder, exist_ok=True)

    # Copy extracted logs file into comparison folder
    extracted_log_source_file = os.path.join(dataset_folder, "Extracted_logs/final_event_log.json")
    extracted_log_destination_file = os.path.join(dataset_folder, "Comparison_sets/extracted_log.json")
    shutil.copy(extracted_log_source_file, extracted_log_destination_file)
    with open(extracted_log_destination_file, 'r') as file:
        extracted_log_json = json.load(file)

    # Find event_ids that should be compared
    idxs = []
    pattern = r'OCEL_subset_event_(.+?)_textual_report\.txt'
    for filename in os.listdir(textual_event_descriptions_folder):
        match = re.match(pattern, filename)
        if match:
            # Extract the event_id and add it to the list
            event_id = match.group(1)  # Convert the extracted ID to an integer
            idxs.append(str(event_id))

    # Create subset (max_logs) of original log and copy it to the comparison folder as well
    for filename in os.listdir(dataset_folder):
        if filename.endswith(".json") or filename.endswith(".jsonocel"):
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_json(filepath)
            break

    filtered_original_log = pm4py.filtering.filter_ocel_events(ocel, idxs)
    output_filepath = os.path.join(comparison_folder, "original_log.json")
    pm4py.write_ocel2_json(filtered_original_log, output_filepath)
    with open(output_filepath, 'r') as file:
        original_log_json = json.load(file)

    return original_log_json, extracted_log_json




