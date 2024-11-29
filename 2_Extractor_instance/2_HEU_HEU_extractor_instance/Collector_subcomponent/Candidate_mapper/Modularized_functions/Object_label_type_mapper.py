from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import indirect_matching_over_position
import re

def object_label_type_mapper(doc, token_position_mapping):
    object_type_mapping = {}

    unmatched_object_labels_with_positions = [
        (matching, tuple(sum(token_position_mapping["object_labels_positions"][matching], ()))) for matching in
        token_position_mapping['object_labels_positions'].keys()]

    unmatched_object_types_with_positions = [
        (matching, tuple(sum(token_position_mapping["object_type_positions"][matching], ()))) for matching in
        token_position_mapping['object_type_positions'].keys()]

    # Check if object_type is integrated in the object label
    split_pattern = re.compile(r'\W+') # Regular expression to split on non-alphanumeric characters
    if len(unmatched_object_labels_with_positions) > 0:
        for obj_type in unmatched_object_types_with_positions:
            obj_type_words = set(split_pattern.split(obj_type[0].lower()))
            for label in unmatched_object_labels_with_positions:
                label_words = set(split_pattern.split(label[0].lower()))
                if obj_type_words.issubset(label_words):
                    object_type_mapping[label[0]] = obj_type[0]
                    for entry in unmatched_object_labels_with_positions:
                        if entry[0] == label[0]:
                            unmatched_object_labels_with_positions.remove(entry)


    #### Try direct matching
    if len(unmatched_object_labels_with_positions)>0:
        object_type_mapping = direct_matching_over_position(doc, object_type_mapping, unmatched_object_types_with_positions, unmatched_object_labels_with_positions, level = 'best_match')
        for value in unmatched_object_labels_with_positions.copy():
            if value[0] in object_type_mapping.keys():
                unmatched_object_labels_with_positions.remove(value)

    #### Try indirect matching
    if len(unmatched_object_labels_with_positions) > 0:
        object_type_mapping = indirect_matching_over_position(doc, object_type_mapping,unmatched_object_types_with_positions,unmatched_object_labels_with_positions, level='best_match')

    ### Map to object_type_not_identified for clear labels
    for obj in unmatched_object_labels_with_positions.copy():
        if obj[0] not in token_position_mapping['remaining_values_positions']:
            object_type_mapping[obj[0]] = "Object_type_not_identified"

    # Update token_position_mapping --> remove object labels that have not been used
    intermediate_list = list(token_position_mapping["object_labels_positions"].keys())
    for value in intermediate_list:
        if value not in object_type_mapping.keys():
            del token_position_mapping["object_labels_positions"][value]

    return object_type_mapping, token_position_mapping
