import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def collect_object_names_and_types_per_event_type(log):
    # Dictionary to hold event types and their corresponding objects with names and types
    event_type_objects = {}

    for event in log["events"]:
        event_type = event["type"]
        if event_type not in event_type_objects:
            event_type_objects[event_type] = []

        object_types = {}
        for relationship in event["relationships"]:
            object_id = relationship["objectId"]
            for obj in log["objects"]:
                if obj["id"] == object_id:
                    # Check if 'name' key exists; if not, use 'id' as a fallback
                    name = obj.get("name", obj["id"])
                    obj_type = obj.get("type", "Unknown")
                    object_types[name] = obj_type
                    break

        if object_types:
            event_type_objects[event_type].append(object_types)

    # print("Event Types and Object Types:")
    # print(event_type_objects)

    return event_type_objects

def map_event_types_to_related_object_types(event_type_objects):

    # Create a new dictionary to map event types to combinations of related object types
    event_type_combinations = {}
    for event_type, objects_list in event_type_objects.items():
        # Collect combinations of object types
        combinations = []
        seen_combinations = set()

        for obj_dict in objects_list:
            # Count the occurrences of each type
            type_counts = {}
            for obj_type in obj_dict.values():
                if obj_type not in type_counts:
                    type_counts[obj_type] = 0
                type_counts[obj_type] += 1

            # Create a replicated list based on type counts
            replicated_types = []
            for obj_type, count in type_counts.items():
                replicated_types.extend([obj_type] * count)

            combination = frozenset(replicated_types)
            if combination not in seen_combinations:
                combinations.append(replicated_types)
                seen_combinations.add(combination)

        event_type_combinations[event_type] = combinations

    # print("Event Type to Related Object Types Mapping:")
    # print(event_type_combinations)

    return event_type_combinations

def filter_event_types_to_unknown_object_types(event_type_combinations):
    # Filter out event types that are not related to 'Object_type_not_identified'
    filtered_event_types = {event_type: types for event_type, types in event_type_combinations.items()
                            if any('Object_type_not_identified' in t for t in types)}

    return filtered_event_types

def group_event_types_by_the_number_of_related_objects(filtered_event_types):
    # Group event types by the number of related objects
    grouped_event_types = {}

    for event_type, types_list in filtered_event_types.items():
        # Count the number of objects in each type set
        counts = {}
        for obj_set in types_list:
            count = len(obj_set)
            if count not in counts:
                counts[count] = []
            counts[count].append(obj_set)

        # Keep only count-groups with at least one entry with 'Object_type_not_identified'
        # and one entry without it
        filtered_counts = {}
        for count, obj_sets in counts.items():
            has_oidn = any('Object_type_not_identified' in obj_set for obj_set in obj_sets)
            no_oidn = any('Object_type_not_identified' not in obj_set for obj_set in obj_sets)
            if has_oidn and no_oidn:
                filtered_counts[count] = obj_sets

        if filtered_counts:
            grouped_event_types[event_type] = filtered_counts

    # print("Grouped Event Types with Mixed 'Object_type_not_identified' Presence:")
    # print(grouped_event_types)

    return grouped_event_types

def create_intermediate_replacement_mapping(grouped_event_types):
    # Dictionary to hold intermediate replacement mapping
    intermediate_mapping = {}

    # Iterate over event types and their grouped counts
    for event_type, count_groups in grouped_event_types.items():
        # Dictionary to hold replacements for each count
        replacements = {}

        for count, groups in count_groups.items():
            # Initialize a dictionary to map identified element sets to possible replacements
            replacement_mapping = {}

            for group in groups:
                if 'Object_type_not_identified' in group:
                    identified_elements = [element for element in group if element != 'Object_type_not_identified']
                    group_tuple = tuple(group)

                    if group_tuple not in replacement_mapping:
                        replacement_mapping[group_tuple] = []

                    for other_group in groups:
                        if group == other_group:
                            continue
                        other_group_set = set(other_group)
                        if 'Object_type_not_identified' not in other_group_set:
                            # Check if this group can replace the identified elements
                            if set(identified_elements).issubset(other_group_set):
                                replacement_mapping[group_tuple].append(other_group)

            if replacement_mapping:
                # Convert list of lists to list of lists of lists for the final structure
                final_replacements = {}
                for key, value_lists in replacement_mapping.items():
                    final_replacements[key] = value_lists

                replacements[count] = final_replacements

        if replacements:
            intermediate_mapping[event_type] = replacements

    return intermediate_mapping


from collections import Counter


def extract_potential_replacement_types_per_event_type_count_group(intermediate_mapping):
    potential_replacements = {}

    for event_type, count_groups in intermediate_mapping.items():
        replacements = {}

        for count, replacement_mapping in count_groups.items():
            final_replacements = {}

            for group_with_unknown, replacement_groups in replacement_mapping.items():
                if isinstance(group_with_unknown, list):
                    group_with_unknown = tuple(group_with_unknown)

                # Count elements in the group
                group_counter = Counter(group_with_unknown)

                # Remove 'Object_type_not_identified' from the counter
                group_counter.pop('Object_type_not_identified', None)

                # Aggregate all replacement elements
                aggregated_remaining_elements = Counter()

                for replacement_group in replacement_groups:
                    if isinstance(replacement_group, list):
                        replacement_counter = Counter(replacement_group)

                        # Calculate potential replacements by subtracting group_counter from replacement_counter
                        remaining_elements = replacement_counter - group_counter

                        # Update the aggregated counter
                        aggregated_remaining_elements.update(remaining_elements)
                    else:
                        raise TypeError(f"Expected list for replacement_group but got {type(replacement_group)}")

                # Convert remaining elements to list and store in final_replacements
                if aggregated_remaining_elements:
                    final_replacements[group_with_unknown] = list(aggregated_remaining_elements.elements())
                else:
                    final_replacements[group_with_unknown] = []

            if final_replacements:
                replacements[count] = final_replacements

        if replacements:
            potential_replacements[event_type] = replacements

    return potential_replacements


def extract_relevant_objects_for_replacement_per_event_type_count_group(event_type_objects, grouped_event_types):
    # Create a dictionary to store relevant objects for each event type and count group
    relevant_objects = {}

    # Iterate through the event_type_objects to find relevant objects
    for event_type, obj_lists in event_type_objects.items():
        if event_type in grouped_event_types:
            # Get the count groups for the current event type
            count_groups = grouped_event_types[event_type]
            relevant_objects[event_type] = {}

            for count, obj_dicts in count_groups.items():
                # Find relevant objects for the specific count group
                relevant_objects[event_type][count] = []
                for obj_dict in obj_lists:
                    if len(obj_dict) == count and 'Object_type_not_identified' in obj_dict.values():
                        relevant_objects[event_type][count].append(obj_dict)

    return relevant_objects

def replace_unknown_object_types_with_potential_replacements_if_len_1(log, replacements, relevant_objects, event_type, count, unknown_element_structure):
    replacement_type = replacements[0]

    # Print the replacement type
    # print(f"Replacement type for event type '{event_type}' with count {count}: {replacement_type}")

    # Get the relevant objects for this event type and count
    relevant_objs = relevant_objects.get(event_type, {}).get(count, [])

    # Dynamically filter the relevant objects based on the provided tuple
    filtered_relevant_objs = [
        obj_dict for obj_dict in relevant_objs
        if set(obj_dict.values()) == set(unknown_element_structure)
    ]

    # Iterate through relevant objects and replace 'Object_type_not_identified' with the replacement type
    for obj_dict in filtered_relevant_objs:
        for obj_id, obj_type in obj_dict.items():
            if obj_type == "Object_type_not_identified":
                # Replace the type in the log["objects"] list
                for obj in log["objects"]:
                    if obj["id"] == obj_id:
                        obj["type"] = str(replacement_type)
                        #print(f"Replaced type for object ID '{obj_id}' with '{replacement_type}'. Case: Len = 1'")

def replace_unknown_object_types_with_potential_replacements_if_len_greater_1(log, replacements, relevant_objects, event_type, count, unknown_element_structure):

    # Get the relevant objects for this event type and count
    relevant_objs = relevant_objects.get(event_type, {}).get(count, [])

    # Dynamically filter the relevant objects based on the provided tuple
    filtered_relevant_objs = [
        obj_dict for obj_dict in relevant_objs
        if set(obj_dict.values()) == set(unknown_element_structure)
    ]

    #print("filtered_relevant_objects: ", filtered_relevant_objs)

    object_types_NER = {}
    for replacement_type in replacements:
        # print(f"Analyzing object names for replacement type '{replacement_type}':")
        object_names = [obj["id"] for obj in log["objects"] if obj["type"] == replacement_type]

        entities_found = set()
        for name in object_names:
            doc = nlp(name)
            entities = {ent.label_: [] for ent in doc.ents}
            for ent in doc.ents:
                entities[ent.label_].append(ent.text)
            if entities:
                entities_found.update(entities.keys())
            # print(f"Object name '{name}' has entities: {entities}")

        # Convert entities_found to a list of entity types
        entity_types = list(entities_found)
        # Store the results for each replacement type
        object_types_NER[replacement_type] = entity_types if entity_types else []
        # print("object_types_NER: ", object_types_NER)

    # Check for intersections between different keys' entity type lists
    entity_types_lists = list(object_types_NER.values())
    intersection_found = False

    for i in range(len(entity_types_lists)):
        for j in range(i + 1, len(entity_types_lists)):
            if set(entity_types_lists[i]).intersection(entity_types_lists[j]):
                #print("Intersection found")
                intersection_found = True

    if not intersection_found:
        #print("All entity type lists are intersection-free.")

        for obj_dict in filtered_relevant_objs:
            for obj_id, obj_type in obj_dict.items():
                if obj_type == "Object_type_not_identified":
                    obj = next((o for o in log["objects"] if o["id"] == obj_id), None)
                    if obj:
                        name = obj["id"]
                        doc = nlp(name)
                        entities = {ent.label_: [] for ent in doc.ents}
                        for ent in doc.ents:
                            entities[ent.label_].append(ent.text)
                        #print(f"Object ID '{obj_id}' with type '{obj_type}' has entities: {entities}")

                        # Compare NER results with replacement types
                        for replacement_type, replacement_types_ner in object_types_NER.items():
                            if set(replacement_types_ner).intersection(entities.keys()):
                                # Replace the type in the log["objects"] list
                                obj["type"] = replacement_type
                                #print(f"Replaced type for object ID '{obj_id}' with '{replacement_type}. Case: Len > 1'")




def replace_unknown_object_types_with_potential_replacements(log, potential_replacements, relevant_objects):
    # Iterate over potential replacements
    for event_type, count_groups in potential_replacements.items():
        for count, replacement_group in count_groups.items():
            for unknown_element_structure, replacements in replacement_group.items():
                if len(replacements) == 1:
                    replace_unknown_object_types_with_potential_replacements_if_len_1(log, replacements, relevant_objects, event_type, count, unknown_element_structure)
                elif len(replacements) > 1:
                    replace_unknown_object_types_with_potential_replacements_if_len_greater_1(log, replacements, relevant_objects, event_type, count, unknown_element_structure)
    return log


def event_object_type_refiner(log):

    event_type_objects = collect_object_names_and_types_per_event_type(log)
    event_type_combinations = map_event_types_to_related_object_types(event_type_objects)
    filtered_event_types = filter_event_types_to_unknown_object_types(event_type_combinations)
    grouped_event_types = group_event_types_by_the_number_of_related_objects(filtered_event_types)
    intermediate_mapping = create_intermediate_replacement_mapping(grouped_event_types)
    potential_replacements = extract_potential_replacement_types_per_event_type_count_group(intermediate_mapping)
    relevant_objects = extract_relevant_objects_for_replacement_per_event_type_count_group(event_type_objects, grouped_event_types)
    refined_log = replace_unknown_object_types_with_potential_replacements(log, potential_replacements, relevant_objects)

    return refined_log
