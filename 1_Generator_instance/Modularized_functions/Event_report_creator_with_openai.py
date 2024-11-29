import openai
import os
import re
from tqdm import tqdm
import time

def create_and_save_answer(input_folder, saving_folder, event_file, client, assistant, summary_request, list_of_not_generated_files):
    #print(f"Report creation started for {event_file}")

    filepath = os.path.join(input_folder, event_file)

    # Ensure filepath is an absolute path
    filepath = os.path.abspath(filepath)

    # Create a vector store called "Financial Statements"
    vector_store = client.beta.vector_stores.create(name="OCEL2.0-logs")

    # Ready the files for upload to OpenAI
    file_streams = [open(filepath, "rb")]


    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )


    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": summary_request,
            }
        ]
    )

    # Use the create and poll SDK helper to create a run and poll the status of
    # the run until it's in a terminal state.

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    #print("Vector store: ", vector_store)

    run_status_page = client.beta.threads.runs.list(thread_id=thread.id)
    runs = list(run_status_page)  # Convert to list if needed
    latest_run_status = runs[-1]  # Get the latest run status

    incomplete_counter = 0
    while latest_run_status.status == 'incomplete':
        if incomplete_counter<3:
            print("Run incomplete. Waiting...")
            #print("Latest Run Status:", latest_run_status)
            time.sleep(10)  # Wait before polling again
            run_status_page = client.beta.threads.runs.list(thread_id=thread.id)
            runs = list(run_status_page)  # Convert to list if needed
            latest_run_status = runs[-1]  # Get the latest run status
            incomplete_counter +=1
        else:
            print("Run aborted")
            break

    if latest_run_status.status == 'failed':
        #print("Run failed with error:", latest_run_status.last_error.message)
        message_content = ""
        list_of_not_generated_files.append(event_file)

    elif latest_run_status.status == 'completed':
        #print("Completed!")

        if event_file in list_of_not_generated_files:
            list_of_not_generated_files.remove(event_file)

        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        if messages and len(messages) > 0:
            if messages[0].content and len(messages[0].content) > 0:
                if hasattr(messages[0].content[0], 'text'):
                    message_content = messages[0].content[0].text.value

        message_content = re.sub(r'【.*?】', '', message_content)
        #print("Text for ", event_file, ": ", message_content)
        if 'Sorry' in message_content or 'sorry' in message_content or 'apologize' in message_content or 'log' in message_content:
            message_content = ""
            list_of_not_generated_files.append(event_file)

    else:
        #print("Unexpected status:", latest_run_status.status)
        message_content = ""
        list_of_not_generated_files.append(event_file)


    # Extract the original filename and create the new filename
    original_filename = os.path.basename(filepath)
    base_filename = os.path.splitext(original_filename)[0]
    output_filename = f"{base_filename}_textual_report.txt"
    output_filepath = os.path.join(saving_folder, output_filename)

    # Ensure saving_folder is an absolute path
    output_filepath = os.path.abspath(output_filepath)

    #print("message_content: ", message_content)

    # Save the message content to a text file, ignoring characters that cannot be encoded
    with open(output_filepath, "w", encoding='utf-8', errors='ignore') as file:
        file.write(message_content)

    # print(f"Description saved to {output_filepath}")

    # Close the file streams
    for file_stream in file_streams:
        file_stream.close()

    return list_of_not_generated_files


def event_report_creator_with_openai(dataset_folder, max_reports, api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model):

    input_folder = os.path.join(dataset_folder, 'Datasubsets/Event_subsets/')
    saving_folder = os.path.join(dataset_folder, "Textual_descriptions/Event_reports/")
    os.makedirs(saving_folder, exist_ok=True)

    instructions = """You are a process mining expert. Use your knowledge base to summarize the provided OCEL2.0-logs in natural language. The report should describe all activities in the event log as well as all objects that were involved in the corresponding activity. Please make it sound as natural and human-like as possible by writing everything in one text without using bullet points. Ensure that you summarize all activities mentioned in the OCEL2.0-log properly,
    but don't come up with any new activities. Integrate all timestamps, object types and object labels/IDs, relationships and attributes in an intuitive way into the text. Don't add the event ID. If an object corresponds to a person, always mention the person togehter with its object type.
    Use only standard utf-8 characters. Don't mention the events, objects, types, relationships, and attributes specifically, but rather integrate them implicitly into the text. Never put events into quotation marks or mention the word 'event' itself.
    Make the description as concise and as short as possible and leave out unnecessary descriptions that are not specified within the log. 
    Write everything in an objective tone where you simply describe what happened. Don't refer to the uploaded log, but rather describe it in a natural way without leaving any details out. Don't put any events, attributes or types into parentheses. 
    It is very important that the generation is lossless, and all object IDs, types, attributes and relationships are included.
    
    Here are some examples on how your answers could look like:
    'The manager named XY opened a vacancy for the position of Manager on May 20, 2019 at 12:26:57 UTC, with the ID Vacancy[550001] - Manager.'
    'The applicant XY submitted an application on May 20, 2019 at 12:26:57 UTC, with the ID Application[550001].'
    'A vehicle with ID "vh5" was booked for a transport document with ID "td3" on May 26, 2023, at 09:53:25 UTC. The transport document with ID "td3" had 3.0 containers and was in transit. However, on June 13, 2023, at 09:00:00 UTC, its status changed to "shipped". The vehicle with ID "vh5" had a departure date of June 13, 2023, at 11:00:00 UTC.'
    """

    summary_request = """Please create based on the OCEL2.0-logs in your knowledge base textual descriptions of the event logs.  Your answer should consist only of the textual description without mentioning the OCEL-log or its objects and events it is based on.  The descriptions should be as short as possible. Nevertheless, be very exact with all details provided in the log and integrate all timestamps, events, object types, object labels/IDs, attributes, and relationships in an intuitive way into the text. 
    If you mention a person that corresponds to an object, always also mention the persons object type.
    Don't refer specifically to the uploaded log, but rather describe it in a natural way without leaving any details out. Never put events into quotation marks or mention the word 'event' itself.  It is very important that the generation is lossless, and all timestamps, object types and IDs are included."""

    if api_type == "openai":

        client = openai.OpenAI(api_key=openai_api_key)

        assistant = client.beta.assistants.create(
            name="Process mining Assistant",
            instructions=instructions,
            model=openai_model,
            tools=[{"type": "file_search"}],
        )

    elif api_type == "azure":

        client = openai.AzureOpenAI(
            api_key=azure_api_key,
            api_version="2024-05-01-preview",
            azure_endpoint=azure_endpoint
        )

        assistant = client.beta.assistants.create(
            name="Process mining Assistant",
            instructions=instructions,
            model=azure_model,
            tools=[{"type": "file_search"}],
        )

    # Get all json files from the input folder
    event_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    counter = 0
    for event_file in event_files:
        file_path = os.path.join(input_folder, event_file)
        file_size = os.path.getsize(file_path)  # Get the file size in bytes
        if file_size > 2 * 1024:  # Check if file size is greater than 2KB
            #print("removed event files: ", event_file)
            counter += 1
            os.remove(file_path)  # Delete the file
            event_files.remove(event_file)

    if counter>0:
        print(f"Deleted {counter} files, because they were larger than 2KB")

    #print("Event files list: ", event_files[:max_reports])


    # If max_reports is None, process all files; otherwise, limit to max_reports
    if max_reports is None:
        max_reports = len(event_files)

    print("Textual report creation intialized. Please be patient as this step can take a while.")

    # Process each file with a progress bar
    list_of_not_generated_files = []
    for event_file in tqdm(event_files[:max_reports], desc="Processing files", unit="file"):
        list_of_not_generated_files = create_and_save_answer(input_folder, saving_folder, event_file, client, assistant,
                                                             summary_request, list_of_not_generated_files)
        #print("Generated event files: ", event_file)

    if list_of_not_generated_files == []:
        print("All event reports created and saved to folder: ", saving_folder)
    else:
        print("1. Generation of textual descriptions concluded.")
        print("Attention!! For the following files, the generation failed: ", list_of_not_generated_files)
        print("Regeneration of missing files starts now.")


    i=1
    while list_of_not_generated_files != []:
        i +=1
        for event_file in tqdm(list_of_not_generated_files[:], desc="Processing files", unit="file"):
            list_of_not_generated_files = create_and_save_answer(input_folder, saving_folder, event_file, client,
                                                                 assistant, summary_request, list_of_not_generated_files)
        print(f"{i}. Generation of textual descriptions concluded.")
        if list_of_not_generated_files != []:
            print("Attention!! For the following files, the generation still failed: ", list_of_not_generated_files)
            print("Regeneration of missing files starts now.")

    print("All event reports created and saved to folder: ", saving_folder)
