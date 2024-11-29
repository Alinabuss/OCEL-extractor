import json
import os
import re
from Collector_subcomponent.OCEL_constructor.Modularized_functions.OCEL_object_types_constructor import OCEL_object_types_constructor
from Collector_subcomponent.OCEL_constructor.Modularized_functions.OCEL_event_types_constructor import OCEL_event_types_constructor
from Collector_subcomponent.OCEL_constructor.Modularized_functions.OCEL_objects_constructor import OCEL_objects_constructor
from Collector_subcomponent.OCEL_constructor.Modularized_functions.OCEL_events_constructor import OCEL_events_constructor



def OCEL_constructor(mapping, filepath, saving_folder, level, printing = False):

    os.makedirs(saving_folder, exist_ok=True)

    # Create object_types, event_types, objects, and events lists
    object_types = OCEL_object_types_constructor(mapping)
    event_types = OCEL_event_types_constructor(mapping)
    objects = OCEL_objects_constructor(mapping)
    events = OCEL_events_constructor(mapping)


    # Create the OCEL2.0 log structure
    ocel_log = {
        "objectTypes": object_types,
        "eventTypes": event_types,
        "objects": objects,
        "events": events
    }

    # Construct output filename based on the event_id
    if level == 'event':
        event_id = re.search(r'_event_(.+?)_textual_report', filepath).group(1)
    elif level == 'disjunct_event_groups':
        event_id = re.search(r'Daily_report_(.+?).txt', filepath).group(1)
    elif level == 'intersecting_event_groups':
        event_id = re.search(r'Object_report_(.+?).txt', filepath).group(1)
    elif level == "Test_setup":
        event_id = re.search(r'report_(.+?).txt', filepath).group(1)


    json_output_filename = f"OCEL_{event_id}.json"
    json_output_filepath = os.path.join(saving_folder, json_output_filename)

    # Write the OCEL2.0 log to a JSON file
    with open(json_output_filepath, "w") as f:
        json.dump(ocel_log, f, indent=4)

    if printing:
        print("OCEL: ", ocel_log)
        print()


