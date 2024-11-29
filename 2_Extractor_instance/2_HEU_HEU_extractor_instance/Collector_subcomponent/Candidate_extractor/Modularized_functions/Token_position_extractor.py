from collections import defaultdict

def find_positions(doc, candidate_object_labels):
    # Tokenize the document
    tokens = [token.text for token in doc]

    # Create a list of tokenized candidate labels
    candidate_labels = [label.split() for label in candidate_object_labels]

    # Initialize a dictionary to store matches
    matches = {label: [] for label in candidate_object_labels}

    # Iterate through candidate labels to find matches
    for label, tokens_list in zip(candidate_object_labels, candidate_labels):
        len_label = len(tokens_list)
        for i in range(len(tokens) - len_label + 1):
            if tokens[i:i + len_label] == tokens_list:
                if len_label == 1:
                    # If the label consists of a single token
                    matches[label].append((i,))
                else:
                    # If the label consists of multiple tokens
                    matches[label].append(tuple(range(i, i + len_label)))

    return matches


def merge_dicts(dicts, filter_list):
    merged_dict = defaultdict(set)

    # Merging values from the input dictionaries based on the filter list
    for d in dicts:
        for key, value in d.items():
            if key in filter_list:
                merged_dict[key].update(value)

    intermediat_dict = {}

    # Process each key's set of tuples
    for key, value_set in merged_dict.items():
        merged_tuples = []

        # Sort tuples to make processing easier
        sorted_tuples = sorted(value_set, key=lambda x: (len(x), x))

        for current_tuple in sorted_tuples:
            found = False
            for i, merged_tuple in enumerate(merged_tuples):
                # Check if the current tuple is a subset of an existing merged tuple
                if set(current_tuple).issubset(merged_tuple):
                    found = True
                    break
                # Check if the current tuple intersects with an existing merged tuple
                elif set(current_tuple).intersection(merged_tuple):
                    # Merge the two tuples
                    merged_tuples[i] = merged_tuple.union(current_tuple)
                    found = True
                    break
                elif set(current_tuple) in merged_tuples:
                    found = True
                    break
            if not found:
                merged_tuples.append(set(current_tuple))

        # Convert sets back to tuples and assign to final_dict
        intermediat_dict[key] = [tuple(t) for t in merged_tuples]

    # Remove duplicates from positions
    final_dict = {key: list(set(value)) for key, value in intermediat_dict.items()}

    return final_dict


def token_position_extractor(doc, timestamps_to_text, timestamps_to_positions, event_resources_with_positions, object_labels_with_positions, candidate_activities_with_positions, candidate_object_types_with_positions, candidate_attributes_with_positions, clear_attribute_values_with_positions, event_lifecylce_status_with_positions, remaining_values_with_positions):

    #### Find matches in text
    text_to_timestamps = {}
    timestamp_texts = []
    for ts, text in timestamps_to_text.items():
        text_to_timestamps[text] = ts
        timestamp_texts.append(text)
    intermediate_timestamp_position_mapping = find_positions(doc, timestamp_texts)
    timestamp_position_mapping = {}
    for ts, position in intermediate_timestamp_position_mapping.items():
        timestamp_position_mapping[text_to_timestamps[ts]] = position

    #activities_position_mapping = find_positions(doc, [activity for activity in candidate_activities_with_positions.keys()])
    object_labels_position_mapping = find_positions(doc, [label for label in object_labels_with_positions.keys()])
    object_type_position_mapping = find_positions(doc, [label for label in candidate_object_types_with_positions.keys()])
    attribute_position_mapping = find_positions(doc, [attr for attr in candidate_attributes_with_positions.keys()])
    clear_attribute_value_position_mapping = find_positions(doc, [val for val in clear_attribute_values_with_positions.keys()])
    resource_position_mapping = find_positions(doc, [res for res in event_resources_with_positions.keys()])
    lifecycle_position_mapping = find_positions(doc, [status for status in event_lifecylce_status_with_positions.keys()])
    remaining_value_position_mapping = find_positions(doc, [val for val in remaining_values_with_positions.keys()])

    #### Merge dicts
    timestamps = [ts for ts in timestamps_to_text.keys()]
    timestamp_position_mapping = merge_dicts([timestamp_position_mapping, timestamps_to_positions], timestamps)
    #activities_position_mapping = merge_dicts([activities_position_mapping, candidate_activities_with_positions], [activity for activity in candidate_activities_with_positions.keys()])
    object_labels_position_mapping = merge_dicts([object_labels_position_mapping, object_labels_with_positions], [label for label in object_labels_with_positions.keys()])
    object_type_position_mapping = merge_dicts([object_type_position_mapping, candidate_object_types_with_positions], [label for label in candidate_object_types_with_positions.keys()])
    attribute_position_mapping = merge_dicts([attribute_position_mapping, candidate_attributes_with_positions], [attr for attr in candidate_attributes_with_positions.keys()])
    clear_attribute_value_position_mapping = merge_dicts([clear_attribute_value_position_mapping, clear_attribute_values_with_positions], [val for val in clear_attribute_values_with_positions.keys()])
    resource_position_mapping = merge_dicts([resource_position_mapping, event_resources_with_positions], [res for res in event_resources_with_positions.keys()])
    lifecycle_position_mapping = merge_dicts([lifecycle_position_mapping, event_lifecylce_status_with_positions], [status for status in event_lifecylce_status_with_positions.keys()])
    remaining_value_position_mapping = merge_dicts([remaining_value_position_mapping, remaining_values_with_positions], [val for val in remaining_values_with_positions.keys()])

    #### Collect all token positions
    token_position_mapping = {
        "timestamp_positions": timestamp_position_mapping,
        "activity_positions": candidate_activities_with_positions,
        "object_labels_positions": object_labels_position_mapping,
        "object_type_positions": object_type_position_mapping,
        "attributes_positions": attribute_position_mapping,
        "attribute_values_positions": clear_attribute_value_position_mapping,
        "event_resources_positions": resource_position_mapping,
        "event_lifecylce_positions": lifecycle_position_mapping,
        "remaining_values_positions": remaining_value_position_mapping
    }

    return token_position_mapping