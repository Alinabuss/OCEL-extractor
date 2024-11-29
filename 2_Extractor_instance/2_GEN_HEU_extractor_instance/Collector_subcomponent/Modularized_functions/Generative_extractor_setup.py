import openai

def generative_extractor_setup(api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model):

    instructions = """You are a process mining expert. You will now receive a couple of textual descriptions. Please extract event logs in the OCEL2.0 json format from these textual desciptions.
       An example on how the OCEL2.0 format looks like is in your knowledge base. However, here is an overview of the general structure:

       {
       "objectTypes": [
           {
               "name": "",
               "attributes": [
                   {
                       "name": "",
                       "type": ""
                   }
               ]
           }
       ],
       "eventTypes": [
           {
               "name": "",
               "attributes": [
                   {
                       "name": "",
                       "type": ""
                   },
                   {
                       "name": "",
                       "type": ""
                   }
               ]
           }
       ],
       "objects": [
           {
               "id": "",
               "type": "",
               "attributes": [
                   {
                       "name": "",
                       "time": "",
                       "value": ""
                   }
               ],
               "relationships": [
               {
                       "objectId": "",
                       "qualifier": ""
                   }
               ]
           }
       ],
       "events": [
           {
               "id": ,
               "type": "",
               "time": "YYYY-MM-DDTHH:MM:SSZ",
               "attributes": [
                   {
                       "name": "",
                       "value": ""
                   },
                   {
                       "name": "",
                       "value": ""
                   }
               ],
               "relationships": [
                   {
                       "objectId": "",
                       "qualifier": ""
                   }
               ]
           }
       ]
       }

       You must extract objects, object types, event types, timestamps and event-to-object relationship to create a minimal OCEL2.0 log.
       For objects, use names and IDs that you found in the text as object IDs and don't come up with own object IDs.
       If possible and necessary, please also extract object and event attributes as well as object-to-object relationships. However, these categories are optional.
       Return ONLY the extracted event log in OCEL2.0 format without any other text or information.
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
    vector_store = client.beta.vector_stores.create(name="Example OCEL2.0-logs")

    # Ready the files for upload to OpenAI
    example_filepath = "Collector_subcomponent/Example_ocel/example_ocel.json"
    file_streams = [open(example_filepath, "rb")]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    return client, assistant