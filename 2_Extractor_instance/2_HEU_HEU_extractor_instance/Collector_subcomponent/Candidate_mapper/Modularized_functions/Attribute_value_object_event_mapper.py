from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import indirect_matching_over_position

def attribute_value_object_event_mapper(doc, token_position_mapping, object_type_mapping, timestamp_activity_mapping):
    attribute_value_object_mapping = {}
    attribute_value_event_mapping = {}
    object_to_attribute_value_mapping = {}
    event_to_attribute_value_mapping = {}

    attribute_values_with_positions = []
    for attr_val in token_position_mapping['attribute_values_positions'].keys():
        for positions in token_position_mapping['attribute_values_positions'][attr_val]:
            if tuple([attr_val, positions]) not in attribute_values_with_positions:
                attribute_values_with_positions.append(tuple([attr_val, positions]))

    undefined_values_with_positions = []
    for attr_val in token_position_mapping['remaining_values_positions'].keys():
        for positions in token_position_mapping['remaining_values_positions'][attr_val]:
            if tuple([attr_val, positions]) not in undefined_values_with_positions:
                undefined_values_with_positions.append(tuple([attr_val, positions]))

    attribute_values_with_positions += undefined_values_with_positions

    objects_with_positions = [
        (matching, tuple(sum(token_position_mapping["object_labels_positions"][matching], ()))) for matching in
        token_position_mapping['object_labels_positions'].keys()]

    object_types_with_positions = [
        (matching, tuple(sum(token_position_mapping["object_type_positions"][matching], ()))) for matching in
        token_position_mapping['object_type_positions'].keys() if matching in object_type_mapping.values()]

    resource_with_positions = [
        (matching, tuple(sum(token_position_mapping["event_resources_positions"][matching], ()))) for matching in
        token_position_mapping['event_resources_positions'].keys()]

    lifecycle_with_positions = [
        (matching, tuple(sum(token_position_mapping["event_lifecylce_positions"][matching], ()))) for matching in
        token_position_mapping['event_lifecylce_positions'].keys()]


    potential_timestamps = set(ts for ts in timestamp_activity_mapping.keys() if ts != None)
    potential_events_with_positions = []
    for events in timestamp_activity_mapping.values():
        for event in events:
            if event not in potential_events_with_positions:
                potential_events_with_positions.append(event)


    # Reverse refined_activity_timestamp_mapping to map event types to their timestamps
    event_type_to_timestamp = {}
    for ts, events in timestamp_activity_mapping.items():
        for event in events:
            event_type_to_timestamp[event] = ts

    #### Try direct matching for objects

    if len(attribute_values_with_positions)>0:
        # Look if object in related token of attribute values
        attribute_value_object_mapping = direct_matching_over_position(doc, attribute_value_object_mapping, objects_with_positions, attribute_values_with_positions)
        for attr in attribute_values_with_positions.copy():
            if attr[0] in attribute_value_object_mapping.keys():
                attribute_values_with_positions.remove(attr)

    #### Try indidirect matching for objects
    if len(attribute_values_with_positions) > 0:
        attribute_value_object_mapping = indirect_matching_over_position(doc, attribute_value_object_mapping, objects_with_positions, attribute_values_with_positions)

        for attr in attribute_values_with_positions.copy():
            if attr[0] in attribute_value_object_mapping.keys():
                attribute_values_with_positions.remove(attr)

    #### Try direct matching for events
    if len(attribute_values_with_positions) > 0:
        attribute_value_event_mapping = direct_matching_over_position(doc, attribute_value_event_mapping,potential_events_with_positions, attribute_values_with_positions, case = 'with_position')

        for attr in attribute_values_with_positions.copy():
            if attr[0] in attribute_value_object_mapping.keys():
                attribute_values_with_positions.remove(attr)

    #### Remaining resources and lifecylce status attributes are mapped to events
    attribute_value_event_mapping = direct_matching_over_position(doc, attribute_value_event_mapping,potential_events_with_positions, resource_with_positions, case = 'with_position')
    attribute_value_event_mapping = direct_matching_over_position(doc, attribute_value_event_mapping,potential_events_with_positions, lifecycle_with_positions, case = 'with_position')


    #### Remaining clear attribute values are mapped to the last seen object
    for attr in attribute_values_with_positions.copy():
        if attr in undefined_values_with_positions:
            attribute_values_with_positions.remove(attr)

    for attr_value, attr_positions in attribute_values_with_positions:
        last_seen_object = None
        last_seen_object_type = None
        min_object_distance = float('inf')
        min_object_type_distance = float('inf')

        # Find the closest object before the attribute
        for obj, obj_positions in token_position_mapping["object_labels_positions"].items():
            for obj_position in obj_positions:
                if max(obj_position) < min(attr_positions):
                    distance = min(attr_positions) - max(obj_position)
                    if distance < min_object_distance:
                        min_object_distance = distance
                        last_seen_object = obj

        # Find the closest object type before the attribute
        for obj_type, obj_type_positions in token_position_mapping["object_type_positions"].items():
            if obj_type in object_type_mapping.values():
                for obj_type_position in obj_type_positions:
                    if max(obj_type_position) < min(attr_positions):
                        distance = min(attr_positions) - max(obj_type_position)
                        if distance < min_object_type_distance:
                            min_object_type_distance = distance
                            last_seen_object_type = obj_type


        # Check if the last seen entity was an object type
        if last_seen_object_type and min_object_type_distance <= min_object_distance:

            # Use the object_type_mapping to find the possible objects for this type
            possible_objects = [key for key, value in object_type_mapping.items() if value == last_seen_object_type]

            if len(possible_objects) > 1:
                closest_object = None
                min_distance = float('inf')

                for obj in possible_objects:
                    for o, obj_positions in token_position_mapping["object_labels_positions"].items():
                        for obj_position in obj_positions:
                            if o == obj and max(obj_position) < min(attr_positions):
                                distance = min(attr_positions) - max(obj_position)
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_object = obj

                # Map the attribute to the closest acceptable object
                if closest_object:
                    attribute_value_object_mapping[attr_value] = [closest_object]

            elif len(possible_objects) == 1:
                # If only one object is possible, directly map it
                attribute_value_object_mapping[attr_value] = [possible_objects[0]]

        # If a specific object was found, map it directly to the attribute
        elif last_seen_object:
            attribute_value_object_mapping[attr_value] = [last_seen_object]

    #### Reverse dictionaries
    for attr, objects in attribute_value_object_mapping.items():
        for obj in objects:
            if obj not in object_to_attribute_value_mapping:
                object_to_attribute_value_mapping[obj] = []
            object_to_attribute_value_mapping[obj].append(attr)

    for attr, events in attribute_value_event_mapping.items():
        for event in events:
            if event not in event_to_attribute_value_mapping:
                event_to_attribute_value_mapping[event] = []
            event_to_attribute_value_mapping[event].append(attr)

    return object_to_attribute_value_mapping, event_to_attribute_value_mapping