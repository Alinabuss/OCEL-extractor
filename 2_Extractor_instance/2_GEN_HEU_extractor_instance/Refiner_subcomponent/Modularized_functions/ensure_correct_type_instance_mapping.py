def ensure_correct_mapping_for_types(log, types_category, instance_category):
    identified_object_types = {obj_type['name'] for obj_type in log[types_category]}
    used_object_types = {obj['type'] for obj in log[instance_category]}
    log[types_category] = [obj_type for obj_type in log[types_category] if obj_type['name'] in used_object_types]
    new_object_types = [{'name': obj_type, 'attributes': []} for obj_type in used_object_types if
                        obj_type not in identified_object_types]
    log[types_category].extend(new_object_types)
    return log

def ensure_correct_mapping_for_attributes(log, types_category, instance_category):
    object_type_mapping = {}
    for obj_type in log[types_category]:
        attributes = {attr["name"]: attr["type"] for attr in obj_type["attributes"]}
        object_type_mapping[obj_type["name"]] = attributes

    # Create a reverse mapping from attributes to object types (used to remove unnecessary attributes later)
    object_attribute_usage = {obj_type["name"]: set() for obj_type in log[types_category]}

    # Iterate over objects to adapt object types
    for obj in log[instance_category]:
        obj_type_name = obj["type"]
        if obj_type_name in object_type_mapping and 'attributes' in obj:
            # Collect attribute names and types for the current object type
            existing_attributes = object_type_mapping[obj_type_name]

            # Check and update object type attributes
            for attribute in obj["attributes"]:
                attr_name = attribute["name"]
                attr_value = attribute["value"]

                type_name_mapping = {
                    'str': 'string',
                    'int': 'integer',
                    'float': 'float',
                    'bool': 'boolean',
                    # Add other types as needed
                }

                # Convert attr_value to a type for accurate detection
                try:
                    if isinstance(attr_value, str):
                        # Check if the string represents a number
                        if attr_value.strip().replace('.', '', 1).isdigit() or (
                                '.' in attr_value and attr_value.replace('.', '', 1).isdigit()):
                            # Convert to float
                            attr_value = float(attr_value)
                except ValueError:
                    pass

                # Determine the full type name
                attr_type_abr = type(attr_value).__name__
                attr_type = type_name_mapping.get(attr_type_abr, attr_type_abr)

                # If the attribute type is not correct or not in the object type attributes
                if attr_name not in existing_attributes.keys():
                    # Update or add attribute type
                    existing_attributes[attr_name] = attr_type

                # Track the usage of this attribute in the object type
                object_attribute_usage[obj_type_name].add(attr_name)

            # Update objectTypes with the updated attributes
            for obj_type in log[types_category]:
                if obj_type["name"].lower() == obj_type_name:
                    obj_type["attributes"] = [{"name": k, "type": v} for k, v in existing_attributes.items()]
                    break

    # Remove attributes from object types that are not used in any objects
    for obj_type in log[types_category]:
        obj_type_name = obj_type["name"]
        existing_attributes = object_type_mapping[obj_type_name]
        used_attributes = object_attribute_usage[obj_type_name]

        # Filter out attributes that are not used in any objects
        obj_type["attributes"] = [{"name": k, "type": v} for k, v in existing_attributes.items() if
                                  k in used_attributes]


    return log

def ensure_correct_relationships(log):
    object_instances = [obj['id'] for obj in log['objects']]

    for obj in log['objects']:
        if 'relationships' in obj:
            relationships = obj['relationships']
            rel_to_keep=[]
            for rel in relationships:
                if rel['objectId'] in object_instances and rel['objectId'] != obj['id']:
                    rel_to_keep.append(rel)

            obj['relationships'] = rel_to_keep

    for event in log['events']:
        if 'relationships' in event:
            relationships = event['relationships']
            rel_to_keep = []
            for rel in relationships:
                if rel['objectId'] in object_instances:
                    rel_to_keep.append(rel)

            event['relationships'] = rel_to_keep

    return log


def ensure_correct_type_instance_mapping(log):

    #### Adapt existence of object/event types in object/event types list and objects/events list
    log = ensure_correct_mapping_for_types(log, 'objectTypes', 'objects')
    log = ensure_correct_mapping_for_types(log, 'eventTypes', 'events')

    ##### Adapt the existence of object attributes in object types list and objects list
    log = ensure_correct_mapping_for_attributes(log, 'objectTypes', 'objects')
    log = ensure_correct_mapping_for_attributes(log, 'eventTypes', 'events')

    #### Ensure that objects and events are only related to objects that actually exist and are not related to themselves
    log = ensure_correct_relationships(log)

    return log