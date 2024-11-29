import os
import pm4py
import re
import json

def OCEL_reader(path):
    ocel_list = []
    # Get all json files from the input folder
    event_files = [f for f in os.listdir(path) if f.endswith('.json')]

    # Function to extract the numerical part of the filename
    #def extract_number(filename):
    #    match = re.search(r'(\d+)', filename)
    #    return int(match.group(1)) if match else float('inf')

    # Sort the files based on the numerical part
    #event_files.sort(key=extract_number)

    for event_file in event_files:
        filepath = os.path.join(path, event_file)
        with open(filepath, 'r') as file:
            ocel = json.load(file)
        #ocel = pm4py.read.read_ocel2_json(filepath)
        ocel_list.append(ocel)

    return ocel_list

