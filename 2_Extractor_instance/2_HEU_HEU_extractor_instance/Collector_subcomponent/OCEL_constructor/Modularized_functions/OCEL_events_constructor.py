import re

event_id_counter = 1

def OCEL_events_constructor(mapping):

    global event_id_counter
    events = []

    # Create initial events that consists of only of event id, event type and timestamp
    for timestamp, activities in mapping["timestamp_activity_mapping"].items():
        for activity in activities:
            events.append({"id": event_id_counter,
                            "type": activity,
                            "time": timestamp,
                            "attributes": [],
                            "relationships": []})
            event_id_counter +=1

    # Add event attributes to events
    for mapped_event, attr_values in mapping['event_to_attribute_value_mapping'].items():
        for attr_val in attr_values:
            for event in events:
                if event['type'] == mapped_event:
                    attribute = {
                        "name": mapping["attribute_value_mapping"][attr_val],
                        "value": attr_val
                        }

                    event['attributes'].append(attribute)

    # Add E2O-relationships
    for mapped_event, objects in mapping['e2o_relationship_mapping'].items():
        for obj in objects:
            for event in events:
                if event['type'] == mapped_event:
                    relationship = {"objectId": obj, "qualifier": None}
                    event["relationships"].append(relationship)

    # Correct event type (remove position argument)
    for event in events:
        event['type'] = event['type'][0]

    return events