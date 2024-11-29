import os
import openai
from tqdm import tqdm
import pm4py
import json
import shutil
import re


def generate_reports_grouped_by_date(dataset_folder, input_folder, saving_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model):
    # Read overall OCEL logs
    for filename in os.listdir(dataset_folder):
        if filename.endswith(".json"):  # Process only text files
            filepath = os.path.join(dataset_folder, filename)
            ocel = pm4py.read.read_ocel2_json(filepath)
            break

    # Initialize the dictionary to store dates and their corresponding event IDs
    events_by_date = {}

    # Iterate over each day in the event log
    for day, group in ocel.events.groupby(ocel.events['ocel:timestamp'].dt.date):
        # Extract the list of event IDs for the current day
        event_ids = group['ocel:eid'].tolist()
        # Store the event IDs in the dictionary with the date as the key
        events_by_date[day] = event_ids

    print("Grouped textual report creation intialized. Please be patient as this step can take a while.")

    for date, event_ids in tqdm(events_by_date.items(), desc="Processing daily reports", unit="daily reports"):
        # Initialize a list to store descriptions for the current date
        descriptions = []

        # Iterate over each event ID for the current date
        for event_id in event_ids:
            # Construct the filename pattern
            filename = f"OCEL_subset_event_{event_id}_textual_report.txt"
            filepath = os.path.join(input_folder, filename)

            # Check if the file exists
            if os.path.exists(filepath):
                # Read the content of the file
                with open(filepath, 'r') as file:
                    content = file.read()
                    # Append the content to the descriptions list
                    descriptions.append(content)

        chunk_size = 5
        for chunk_id, i in enumerate(range(0, len(descriptions), chunk_size), start=1):
            # Extract the current chunk of descriptions
            try:
                chunk_descriptions = descriptions[i:i + chunk_size]

                instructions = """You are a process mining expert. You will receive a couple of textual descriptions from the user with each describing an event that happened on the same date. 
                                                    Please combine those textual descriptions for the same date within one big daily report. The daily report should sound as natural as possible, but make sure that you don't forget any information (Timestamps, IDs, and object types are very important).
                                                    Also mention relationships between objects clearly. 
                                                    Furthermore, make sure that it stays clear which objects were involved in which specific event and return ONLY the summarized daily report without any other information. 
                                                    If you mention other dates as well, make sure that you re-mention the original date again so that no ambiguity between timestamps and dates can occur. Don't use bulletpoints.
                                                    """

                # Initialize the summary_request string
                summary_request = """In the following I give you a couple of event descriptions that all happened on the same date. Please summarize those descriptions as naturally as possible in a daily report.
                                                    However, make sure that you don't forget any information like timestamps, object types or IDs on the way.

                                                    Here are the single-event textual descriptions."""

                # Append the date and chunk descriptions to the summary_request string
                summary_request += f"\n\nTextual descriptions for date {date}:\n"

                # Append each description to the summary_request string
                for index, description in enumerate(chunk_descriptions, start=1):
                    summary_request += f"\nDescription {index}: {description}\n"

                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": summary_request}
                ]

                if api_type == "openai":
                    client = openai.OpenAI(api_key=openai_api_key)
                    response = client.chat.completions.create(
                        model=openai_model,
                        messages=messages
                    )

                elif api_type == "azure":
                    client = openai.AzureOpenAI(
                        api_key=azure_api_key,
                        api_version="2024-05-01-preview",
                        azure_endpoint=azure_endpoint
                    )
                    # Make the API call using the Azure OpenAI configuration
                    response = client.chat.completions.create(
                        model=azure_model,
                        messages=messages
                    )

                # Extract and print the response
                message_content = response.choices[0].message.content

                # Create the output filename using the chunk ID
                output_filename = f"Daily_report_{date}_chunk_{chunk_id}.txt"
                output_filepath = os.path.join(saving_folder, output_filename)

                # Save the message content to a text file, ignoring characters that cannot be encoded
                with open(output_filepath, "w", encoding='utf-8', errors='ignore') as file:
                    file.write(message_content)
            except:
                pass

    print("All daily reports created and saved to folder: ", saving_folder)

def generate_reports_grouped_by_object(dataset_folder, input_folder, saving_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model):
    # Read overall OCEL logs
    for filename in os.listdir(dataset_folder):
        if filename.endswith(".json"):  # Process only text files
            with open(os.path.join(dataset_folder, filename)) as json_file:
                ocel = json.load(json_file)
                break

    print("Intersecting grouped report creation initialized.")

    # Group events by object instances
    events_by_object = {}

    # Iterate over events and their relationships
    for event in ocel['events']:
        for relationship in event['relationships']:
            object_id = relationship['objectId']

            # Initialize the object group if not present
            if object_id not in events_by_object:
                events_by_object[object_id] = []

            # Append the event description to the object group
            events_by_object[object_id].append(event['id'])

    # Process the events grouped by objects
    for object_id, event_ids in tqdm(events_by_object.items(), desc="Processing object reports", unit="object reports"):
        descriptions = []
        object_type = [obj['type'] for obj in ocel['objects'] if obj['id'] == object_id][0]

        # Collect descriptions for each event related to the object
        for event_id in event_ids:
            filename = f"OCEL_subset_event_{event_id}_textual_report.txt"
            filepath = os.path.join(input_folder, filename)

            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    content = file.read()
                    descriptions.append(content)

        chunk_size = 5
        for chunk_id, i in enumerate(range(0, len(descriptions), chunk_size), start=1):
            chunk_descriptions = descriptions[i:i + chunk_size]

            instructions = """You are a process mining expert. You will receive a couple of textual descriptions from the user, each describing an event related to the same object. 
                                                    Please combine those textual descriptions for the same object within one report. The report should sound as natural as possible, but make sure that you don't forget any information 
                                                    (Timestamps, IDs, and object types are very important). Mention relationships between objects clearly, and ensure that it is clear which objects were involved in which specific event. 
                                                    Return ONLY the summarized report without any additional information."""

            summary_request = f"""In the following, I give you a couple of event descriptions that are all related to the object {object_id}. Please summarize those descriptions as naturally as possible.
                                                        Make sure that you don't forget any information like timestamps, object types, or IDs.

                                                        Here are the single-event textual descriptions."""

            # Append the date and chunk descriptions to the summary_request string
            summary_request += f"\n\nTextual descriptions for for object {object_id}:\n"

            for index, description in enumerate(chunk_descriptions, start=1):
                summary_request += f"\nDescription {index}: {description}\n"

            messages = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": summary_request}
            ]

            # Generate the summary based on the API type
            if api_type == "openai":
                client = openai.OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model=openai_model,
                    messages=messages
                )
            elif api_type == "azure":
                client = openai.AzureOpenAI(
                    api_key=azure_api_key,
                    api_version="2024-05-01-preview",
                    azure_endpoint=azure_endpoint
                )
                response = client.chat.completions.create(
                    model=azure_model,
                    messages=messages
                )

            message_content = response.choices[0].message.content

            clean_object_type = object_type.replace(" ", "").replace(":", "_")
            clean_object_id = object_id.replace(" ", "").replace(":", "_")[:25]

            output_filename = f"Object_report_{clean_object_type}_{clean_object_id}_chunk_{chunk_id}.txt"
            output_filepath = os.path.join(saving_folder, output_filename)

            # Save the message content to a text file
            if message_content != None:
                with open(output_filepath, "w", encoding='utf-8', errors='ignore') as file:
                    file.write(message_content)

    print("All grouped reports by object created and saved to folder: ", saving_folder)


def grouped_report_creator_with_openai(dataset_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model, level):
    input_folder = os.path.join(dataset_folder, 'Textual_descriptions/Event_reports/')

    if level == "disjunct":

        saving_folder = os.path.join(dataset_folder, "Textual_descriptions/Disjunct_grouped_reports/")
        os.makedirs(saving_folder, exist_ok=True)

        generate_reports_grouped_by_date(dataset_folder, input_folder, saving_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model)



    elif level == 'intersecting':
        saving_folder = os.path.join(dataset_folder, "Textual_descriptions/Intersecting_grouped_reports/")
        os.makedirs(saving_folder, exist_ok=True)

        generate_reports_grouped_by_object(dataset_folder, input_folder, saving_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model)



    elif level == "Test_setup":

        # Paths
        input_folder = os.path.join(dataset_folder, 'Textual_descriptions/Event_reports/')
        saving_folder = os.path.join(dataset_folder, "Textual_descriptions/Test_reports/")
        subfolder_1 = os.path.join(input_folder, 'descriptions_for_daily_grouping')
        subfolder_2 = os.path.join(input_folder, 'descriptions_for_object_grouping')

        # Create necessary folders
        os.makedirs(saving_folder, exist_ok=True)
        os.makedirs(subfolder_1, exist_ok=True)
        os.makedirs(subfolder_2, exist_ok=True)

        # Get the list of all descriptions (files) from the input folder
        descriptions = sorted(os.listdir(input_folder))  # Sort to ensure consistency

        # Ensure we're only dealing with files and not subdirectories
        descriptions = [file for file in descriptions if os.path.isfile(os.path.join(input_folder, file))]

        #### First third of the reports are directly copied into the saving folder
        for file in descriptions[:334]:
            old_event_id = re.search(r'_event_(.+?)_textual_report', file)
            new_filename = f"Event_report_{old_event_id.group(1)}.txt"
            shutil.copy(os.path.join(input_folder, file), os.path.join(saving_folder, new_filename))
        print("First 334 files successfully copied.")

        # Divide the remaining 666 descriptions
        remaining_descriptions = descriptions[334:]

        # Copy 333 descriptions to descriptions_for_daily_grouping
        for i, file in enumerate(remaining_descriptions[:333]):
            shutil.copy(os.path.join(input_folder, file), os.path.join(subfolder_1, file))

        # Copy the last 333 descriptions to descriptions_for_object_grouping
        for i, file in enumerate(remaining_descriptions[333:]):
            shutil.copy(os.path.join(input_folder, file), os.path.join(subfolder_2, file))

        #### Second third of the reports is grouped per day and then copied into the saving folder
        generate_reports_grouped_by_date(dataset_folder, subfolder_1, saving_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model)

        #### Third third of the reports is grouped per object and then copied into the saving folder
        generate_reports_grouped_by_object(dataset_folder, subfolder_2, saving_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model)












