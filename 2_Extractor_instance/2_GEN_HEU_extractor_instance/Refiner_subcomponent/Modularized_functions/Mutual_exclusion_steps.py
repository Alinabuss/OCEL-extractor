from nltk.stem import WordNetLemmatizer
import re
lemmatizer = WordNetLemmatizer()


def mutual_exclusion_steps(log):

    # Create lists
    forbidden_words = ['event', 'action', 'activity', 'attribute', 'value', 'id', 'code', 'resource', 'lifecycle', 'object']
    event_types = [event_type['name'].lower() for event_type in log['eventTypes']]
    object_labels = [object['id'].lower() for object in log['objects']]
    object_types = [obj_type['name'].lower() for obj_type in log['objectTypes']]

    object_attributes = []
    object_attribute_values = []
    for object in log['objects']:
        attributes = [attr for attr in object['attributes']]
        for attr in attributes:
            if attr['value'].lower() not in object_attribute_values:
                object_attribute_values.append(attr['value'].lower())
            if attr['name'].lower() not in object_attributes:
                object_attributes.append(attr['name'].lower())

    resources = []
    for event in log['events']:
        if 'attributes' in event.keys():
            attributes = [attr for attr in event['attributes']]
            for attr in attributes:
                if attr['name'] == 'resource':
                    if attr['value'] not in resources:
                        resources.append(attr['value'].lower())

    # print("Original list: ")
    # print(f"event_types: {set(event_types)}")
    # print(f"object_labels: {set(object_labels)}")
    # print(f"object_types: {set(object_types)}")
    # print(f"object_attributes: {set(object_attributes)}")
    # print(f"object_attribute_values: {set(object_attribute_values)}")
    # print(f"resources: {set(resources)}")
    # print()


    # Adapt resources --> remove resource if it is an event_type, or object_attribute_value
    removed_ressources = []
    for event in log['events']:
        if 'attributes' in event.keys():
            attributes = [attr for attr in event['attributes']]
            for attr in attributes:
                if attr['name'] == 'resource':
                    if attr['value'].lower() in event_types or attr['value'].lower() in object_attribute_values or attr['value'].lower() in forbidden_words:
                        attributes.remove(attr)
                        removed_ressources.append(attr['value'])
                        if attr['value'].lower() in resources:
                            resources.remove(attr['value'].lower())

            event['attributes'] = attributes

    # Adapt event types --> Remove event types that are object types --> Propagate changes to events
    removed_event_types = []
    kept_event_types = []
    for event_type in log['eventTypes']:
        if event_type['name'].lower() in object_types or event_type['name'].lower() in forbidden_words:
            removed_event_types.append(event_type['name'])
            if event_type['name'].lower() in event_types:
                event_types.remove(event_type['name'].lower())
        else:
            kept_event_types.append(event_type)

    log['eventTypes'] = kept_event_types
    for event in log['events']:
        if event['type'] in removed_event_types:
            event['type'] = 'dummy_activity'

    # Adapt object labels --> Remove object labels that are ressources or event types --> Propagate changes to object-to-object and evnt-to-object-relationships
    removed_object_id = []
    for obj in log['objects']:
        if obj['id'].lower() in resources or obj['id'].lower() in event_types or obj['id'].lower() in forbidden_words:
            removed_object_id.append(obj['id'])
            obj['id'] = 'object_instance_not_identified'
            if obj['id'].lower() in object_labels:
                object_labels.remove(obj['id'].lower())

    for obj in log['objects']:
        if 'relationships' in obj:
            relations = [rel for rel in obj['relationships']]
            for rel in relations:
                if rel['objectId'] in removed_object_id:
                    obj['relationships'].remove(rel)

    for event in log['events']:
        for rel in event['relationships']:
            if rel['objectId'] in removed_object_id:
                event['relationships'].remove(rel)

    # Adapt object types --> remove object types that are in forbidden words
    removed_object_types = []
    for obj in log['objectTypes']:
        if obj['name'].lower()  in forbidden_words:
            removed_object_types.append(obj['name'])
            if obj['name'] in log['objectTypes']:
                log['objectTypes'].remove(obj['name'])
            if obj['name'].lower() in object_types:
                object_types.remove(obj['name'].lower())

    for obj in log['objects']:
        if obj["type"] in removed_object_types:
            obj["type"] = "object_type_not_identified"


    # Adapt object attributes --> remove object attributes if they correspond to the object type
    removed_attributes_by_type = {}

    # Step 1: Replace attribute names in objectTypes and record changes
    for obj_type in log['objectTypes']:
        if 'attributes' in obj_type:
            object_type_name = obj_type['name']
            removed_attributes_by_type[object_type_name] = []

            for attr in obj_type['attributes']:
                attribute_name = attr['name']

                # Check for matching or substring relationship
                if object_type_name == attribute_name or \
                        object_type_name in attribute_name or \
                        attribute_name in object_type_name:
                    # Store the attribute name that is being replaced
                    removed_attributes_by_type[object_type_name].append(attr["name"])
                    attr['name'] = 'attribute_type_not_identified'

    # Step 2: Replace attribute names in objects based on corresponding object types
    for obj in log["objects"]:
        attributes = []
        object_type_name = obj['type']

        if object_type_name in removed_attributes_by_type:
            for attr in obj["attributes"]:
                if attr["name"] in removed_attributes_by_type[object_type_name]:
                    attr["name"] = "attribute_type_not_identified"
                attributes.append(attr)
            obj["attributes"] = attributes


    # Adapt attribute values --> remove attribute values that are object type, event type, object labels, timestamp
    removed_attr_values = []
    for obj in log["objects"]:
        new_attributes = []
        for attr in obj["attributes"]:
            value = attr["value"].lower()
            set1 = set(lemmatizer.lemmatize(word) for word in re.sub(r'[^\w\s]+', '', obj["id"]).split())
            set2 = set(lemmatizer.lemmatize(word) for word in re.sub(r'[^\w\s]+', '', attr["value"]).split())
            if value in object_types or value in event_types or value in object_labels or value in resources or value in forbidden_words or set1.issubset(set2) or set2.issubset(set1):
                removed_attr_values.append(attr["value"])
                if value in object_attribute_values:
                    object_attribute_values.remove(value)
            else:
                new_attributes.append(attr)

        obj["attributes"] = new_attributes
        
    removed_event_attr_values = []
    for event in log["events"]:
        new_attributes = []
        for attr in event["attributes"]:
            value = attr["value"].lower()
            if value in object_types or value in event_types or value in object_labels or value in resources or value in forbidden_words or value == event['time']:
                removed_event_attr_values.append(attr["value"])
            else:
                new_attributes.append(attr)

        event["attributes"] = new_attributes

    # print("Removed_entities: ")
    # print(f"removed_ressources: {set(removed_ressources)}")
    # print(f"removed_object_id: {set(removed_object_id)}")
    # print(f"removed_object_types: {set(removed_object_types)}")
    # print(f"removed_event_types: {set(removed_event_types)}")
    # print(f"removed_attr_values: {set(removed_attr_values)}")
    # print()

    return log