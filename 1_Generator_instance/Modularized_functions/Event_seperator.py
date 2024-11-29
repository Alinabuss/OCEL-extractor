import pm4py
import os
from tqdm import tqdm

def event_seperator(dataset_folder):
    # Define path to OCEL2.0-file in xml-, sqlite-, or jsonocel-formt
    saving_folder = os.path.join(dataset_folder, 'Datasubsets/Event_subsets/')
    os.makedirs(saving_folder, exist_ok=True)

    for filename in os.listdir(dataset_folder):
        if filename.endswith(".xml"):
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_xml(filepath)
            break
        elif filename.endswith(".json") or filename.endswith(".jsonocel"):
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_json(filepath)
            break
        elif filename.endswith(".sqlite"):
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_sqlite(filepath)
            break

    print("Event log seperation intialized. Please be patient as this step can take a while.")

    # Iterate over each event_id and filter the event log
    for event_id in tqdm(ocel.events["ocel:eid"], desc="Processing files", unit="file"):
        # Filter events based on event_id
        filtered_ocel = pm4py.filtering.filter_ocel_events(ocel, [event_id])

        # Construct output filename based on the event_id
        output_filename = f"OCEL_subset_event_{event_id}.json"

        output_filepath = os.path.join(saving_folder, output_filename)

        # Save filtered event log in OCEL2.0 format
        pm4py.write_ocel2_json(filtered_ocel, output_filepath)

    print(f"All event logs seperated per event and saved to: {saving_folder}")
