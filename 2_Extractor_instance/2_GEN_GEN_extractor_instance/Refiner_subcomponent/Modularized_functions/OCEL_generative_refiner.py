import openai
import json
import os

def OCEL_generative_refiner(dataset_folder, api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model):

    saving_folder = os.path.join(dataset_folder, "Extracted_logs/")
    concatenated_log_filepath = os.path.join(saving_folder, "concatenated_event_log.json")

    instructions = """You are a process mining expert. You will now receive an concatenated event log in ocel2.0 format over your knowledge base.
        Please refine this concatenated ocel2.0 log by for example cleaning the different names, merging similar entities and ensuring a correct correspondence between the different parts of the log.
        Don't merge any events that happened at different timestamps.
        Return ONLY the refined event log in OCEL2.0 format without any other text or information.
        """

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

    # Create a vector store called
    vector_store = client.beta.vector_stores.create(name="Concatenated OCEL2.0-logs")


    file_streams = [open(concatenated_log_filepath, "rb")]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    refinement_request = """Please refine the log in your knowledge base. Return ONLY the refined event log in OCEL2.0 format without any other text or information."""


    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": refinement_request,
            }
        ]
    )

    # Use the create and poll SDK helper to create a run and poll the status of
    # the run until it's in a terminal state.

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    if messages and len(messages) > 0:
        if messages[0].content and len(messages[0].content) > 0:
            if hasattr(messages[0].content[0], 'text'):
                message_content = messages[0].content[0].text.value

                start_index = message_content.find('{')
                end_index = message_content.rfind('}') + 1
                refined_ocel = json.loads(message_content[start_index:end_index])

                # Save final refined OCEL log
                output_path = os.path.join(saving_folder, "final_event_log.json")
                # Write the OCEL2.0 log to a JSON file
                with open(output_path, "w") as f:
                    json.dump(refined_ocel, f, indent=4)
