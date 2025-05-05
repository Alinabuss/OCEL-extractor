import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pm4py

# Specify folder-path to dataset
dataset_folder = "Data/Order_management/"

def create_train_test_split(dataset_folder, n_train):

    # Create folder structure
    training_dataset_folder = os.path.join(dataset_folder, "Training_data/")
    validation_dataset_folder = os.path.join(dataset_folder, "Validation_data/")
    test_dataset_folder = os.path.join(dataset_folder, "Lilac_fire/")
    os.makedirs(training_dataset_folder, exist_ok=True)
    os.makedirs(validation_dataset_folder, exist_ok=True)
    os.makedirs(test_dataset_folder, exist_ok=True)

    # Read overall OCEL logs
    for filename in os.listdir(dataset_folder):
        if filename.endswith(".xml"):  # Process only text files
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_xml(filepath)
            break
        elif filename.endswith(".json") or filename.endswith(".jsonocel"):  # Process only text files
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_json(filepath)
            break
        elif filename.endswith(".sqlite"):  # Process only text files
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_sqlite(filepath)
            break

    # Seperate training data
    idxs = ocel.events['ocel:eid'].to_list()
    idxs_train = idxs[:n_train]
    idxs_val = idxs[n_train:n_train*2]
    idxs_test = idxs[n_train*2:]
    training_ocel = pm4py.filtering.filter_ocel_events(ocel, idxs_train)
    validation_ocel = pm4py.filtering.filter_ocel_events(ocel, idxs_val)
    test_ocel = pm4py.filtering.filter_ocel_events(ocel, idxs_test)

    # Save train and test event logs in OCEL2.0 format
    pm4py.write_ocel2_json(training_ocel, os.path.join(training_dataset_folder, "Training_data.json"))
    pm4py.write_ocel2_json(validation_ocel, os.path.join(validation_dataset_folder, "Validation_data.json"))
    pm4py.write_ocel2_json(test_ocel, os.path.join(test_dataset_folder, "Lilac_fire.json"))

    print("Train-Validation-Test-split created.")


if __name__ == "__main__":
    create_train_test_split(dataset_folder, n_train=100)



