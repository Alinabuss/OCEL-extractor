import os
import json

#### Reductions: Only one (non-empty) object attribute per object, only one object-to-object relationship per object, and a maximum of five event-to-object relationships per event
def event_reducer(dataset_folder):

    # Get all json files from the input folder
    event_files = [f for f in os.listdir(dataset_folder) if f.endswith('.json')]

    for event_file in event_files:
        filepath = os.path.join(dataset_folder, event_file)
        with open(filepath, 'r') as file:
            ocel = json.load(file)

        updated_objects = []
        object_types_dict = {ot['name']: ot for ot in ocel['objectTypes']}
        object_ids_in_events = set()

        # Process events and limit relationships to a maximum of 5
        for event in ocel['events']:
            if ':' in event['id']:
                event['id'] = event['id'].replace(':', '_')

            if 'relationships' in event:
                # Keep only the first 5 object relationships
                event['relationships'] = event['relationships'][:5]

                # Collect object IDs that are still in use in events
                object_ids_in_events.update(rel['objectId'] for rel in event['relationships'])

        # Update objects list to only include those that are in event relationships
        for obj in ocel['objects']:
            if obj['id'] in object_ids_in_events:
                # Handle attributes
                if 'attributes' in obj:
                    non_empty_attributes = [attr for attr in obj['attributes'] if
                                            attr['value'] != "" and attr['value'] != 'X']
                    if non_empty_attributes:
                        # Keep only the first non-empty attribute
                        obj['attributes'] = [non_empty_attributes[0]]
                    else:
                        # If all attributes are empty, keep none
                        obj['attributes'] = []

                    # Update object types to reflect this change
                    obj_type = obj['type']
                    if obj_type in object_types_dict:
                        ot = object_types_dict[obj_type]
                        # Remove empty attributes from the object type
                        ot['attributes'] = [attr for attr in ot['attributes'] if
                                            attr['name'] in {attr['name'] for attr in obj['attributes']}]

                # Handle relationships
                if 'relationships' in obj and len(obj['relationships']) > 1:
                    # Keep only the first relationship
                    first_relationship = obj['relationships'][0]
                    obj['relationships'] = [first_relationship]

                updated_objects.append(obj)

        # Filter objects list to only those referenced by events
        ocel['objects'] = [obj for obj in updated_objects if obj['id'] in object_ids_in_events]

        # Update object types based on filtered objects
        updated_object_types = {obj['type'] for obj in ocel['objects']}
        ocel['objectTypes'] = [ot for ot in ocel['objectTypes'] if ot['name'] in updated_object_types]

        # Save the updated file
        with open(filepath, 'w') as file:
            json.dump(ocel, file, indent=2)

# Usage example:
# event_reducer('/path/to/dataset_folder')



