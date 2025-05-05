import os
import re
import json


def OCEL_collector_using_LLM(report_folder, filename,  saving_folder, level, client, assistant):
    filepath = os.path.join(report_folder, filename)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()

    extraction_request = """You will now receive a texutal description. Please extract event logs in the OCEL2.0 format from this textual description and return ONLY the log in OCEL2.0-json-format.
                       Be precise in the event names about what happened and don't give them only general names such as 'Update'. 
                       An example of an log in OCEL2.0 json format is provided in your knowledge base."""

    # Append the date and chunk descriptions to the summary_request string
    extraction_request += f"\n\nHere is the textual description: {text}\n"

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": extraction_request,
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
                cleaned_content = re.sub(r"^```json|```$", "", message_content.strip())

                ocel_log = json.loads(cleaned_content)

                # Construct output filename based on the event_id
                if level == 'event':
                    event_id = re.search(r'_event_(.+?)_textual_report', filepath).group(1)
                elif level == 'disjunct_event_groups':
                    event_id = re.search(r'Daily_report_(.+?).txt', filepath).group(1)
                elif level == 'intersecting_event_groups':
                    event_id = re.search(r'Object_report_(.+?).txt', filepath).group(1)
                elif level == 'Test_setup':
                    event_id = re.search(r'report_(.+?).txt', filepath).group(1)

                json_output_filename = f"OCEL_{event_id}.json"

                json_output_filepath = os.path.join(saving_folder, json_output_filename)

                # Write the OCEL2.0 log to a JSON file
                with open(json_output_filepath, "w") as f:
                    json.dump(ocel_log, f, indent=4)