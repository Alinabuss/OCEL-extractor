import os
import json

def OCEL_concatenator(Log_list, saving_folder):

    os.makedirs(saving_folder, exist_ok=True)
    output_name = "concatenated_event_log.json"
    json_output_filepath = os.path.join(saving_folder, output_name)

    # Define empty list for all OCEL-categories
    object_types = []
    objects = []
    event_types = []
    events = []

    # Concatenate information from logs into lists
    for log in Log_list:
        if log['objectTypes'] != None:
            for obj in log["objectTypes"]:
                dict = {}
                dict["name"] = obj["name"]
                dict["attributes"] = obj["attributes"]
                object_types.append(dict)
        if log['objects'] != None:
            for obj in log["objects"]:
                dict = {}
                dict["id"] = obj["id"]
                dict["type"] = obj["type"]
                dict["attributes"] = obj["attributes"]
                dict["relationships"]=obj["relationships"]
                objects.append(dict)
        if log['eventTypes'] != None:
            for event in log["eventTypes"]:
                dict={}
                dict["name"] = event["name"]
                dict["attributes"] = event["attributes"]
                event_types.append(dict)
        if log['events'] != None:
            for event in log["events"]:
                dict = {}
                dict["id"] = event["id"]
                dict["type"] = event["type"]
                dict["time"] = event["time"]
                dict["attributes"] = event["attributes"]
                dict["relationships"] = event["relationships"]
                events.append(dict)

    # Merge objectTypes by name and attributes
    merged_object_types = {}
    for obj_type in object_types:
        name = obj_type['name']
        attributes = obj_type['attributes']

        if name not in merged_object_types:
            # Use a set of tuples for existing attributes
            merged_object_types[name] = set((attr['name'], attr['type']) for attr in attributes)
        else:
            # Merge attributes only if both 'name' and 'type' match
            existing_attributes = merged_object_types[name]
            existing_attr_pairs = existing_attributes.copy()  # Copy existing attributes set

            # Add new attributes
            new_attributes = set((attr['name'], attr['type']) for attr in attributes)
            merged_object_types[name].update(new_attributes - existing_attr_pairs)

    # Convert merged_object_types back to list format
    object_types = [{'name': name, 'attributes': [{'name': attr[0], 'type': attr[1]} for attr in attrs]}
                    for name, attrs in merged_object_types.items()]

    # Merge objects by id, type, attributes, and relationships
    merged_objects = {}
    for obj in objects:
        obj_id = obj['id']
        obj_type = obj['type']
        obj_attributes = obj.get('attributes', [])
        obj_relationships = obj.get('relationships', [])

        # Create a unique key based on id and type
        key = (obj_id, obj_type)

        if key not in merged_objects:
            merged_objects[key] = {
                'attributes': obj_attributes,
                'relationships': obj_relationships
            }
        else:
            # Merge attributes only if all fields match (name, time, value)
            existing_attributes = merged_objects[key]['attributes']
            existing_attr_pairs = {(attr['name'], attr.get('time', ''), attr.get('value', '')) for attr in
                                   existing_attributes}
            for attr in obj_attributes:
                if (attr['name'], attr.get('time', ''), attr.get('value', '')) not in existing_attr_pairs:
                    existing_attributes.append(attr)
                    existing_attr_pairs.add((attr['name'], attr.get('time', ''), attr.get('value', '')))

            # Merge relationships by checking unique (objectId, qualifier) pairs
            existing_relationships = merged_objects[key]['relationships']
            existing_rel_pairs = {(rel['objectId'], rel['qualifier']) for rel in existing_relationships}
            for rel in obj_relationships:
                if (rel['objectId'], rel['qualifier']) not in existing_rel_pairs:
                    existing_relationships.append(rel)
                    existing_rel_pairs.add((rel['objectId'], rel['qualifier']))

    # Convert merged_objects back to list format
    objects = [
        {'id': obj_id, 'type': obj_type, 'attributes': data['attributes'], 'relationships': data['relationships']} for
        (obj_id, obj_type), data in merged_objects.items()]


    # Drop duplicates from event types and event instances by name/ID only
    event_types = list({d['name']: d for d in event_types}.values())
    events = list({d['id']: d for d in events}.values())

    # Order events according to ID
    #events = sorted(events, key=lambda x: int(x['id']))

    # Create the OCEL2.0 log structure
    ocel_log = {
        "objectTypes": object_types,
        "eventTypes": event_types,
        "objects": objects,
        "events": events
    }

    # Write the OCEL2.0 log to a JSON file
    with open(json_output_filepath, "w") as f:
        json.dump(ocel_log, f, indent=4)

    return ocel_log
