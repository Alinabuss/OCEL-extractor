from fuzzywuzzy import fuzz
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import spacy
import numpy as np
from scipy.optimize import linear_sum_assignment
from datetime import datetime
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_md")

lemmatizer = WordNetLemmatizer()

extractors = {
    "object_type": lambda log: [obj_type['name'] for obj_type in log["objectTypes"] if obj_type['name'] not in "object_type_not_identified"],
    "object_instance": lambda log: [obj['id'] for obj in log['objects'] if obj['id'] not in 'object_instance_not_identified'],
    "event_type": lambda log: [event_type['name'] for event_type in log['eventTypes'] if event_type['name'] not in "dummy_activity"],
    "event_instance": lambda log: [{"Timestamp": event["time"], "Event_type": event["type"]} for event in log['events'] if event['type'] not in "dummy_activity"],
    "object_type_attribute_type": lambda log: [{"Object_type": obj_type['name'], "Object_attributes": [attr["name"] for attr in obj_type.get('attributes', []) if attr["name"] not in "attribute_type_not_identified"]} for obj_type in log["objectTypes"] if obj_type['name'] not in "object_type_not_identified"],
    "object_instance_object_type": lambda log: [{"Object_ID": obj["id"] ,"Object_type": obj["type"]} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified' and obj['type'] not in "object_type_not_identified"],
    "object_instance_attribute_type": lambda log: [{"Object_ID": obj['id'], "Object_attributes": [attr["name"] for attr in obj.get('attributes', []) if attr['name'] not in 'attribute_type_not_identified']} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified'],
    "object_instance_attribute_value": lambda log: [{"Object_ID": obj['id'], "Object_attributes": [attr["value"] for attr in obj.get('attributes', [])]} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified'],
    "object_to_object": lambda log: [{"Object_ID": obj['id'],"Object_relationships": [rel['objectId'] for rel in obj.get('relationships', [])]} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified'],
    "event_type_attribute_type": lambda log: [{"Event_type": event_type["name"],"Attributes": [attr['name'] for attr in event_type['attributes']]} for event_type in log['eventTypes'] if event_type['name'] not in "dummy:activity"],
    "event_instance_attribute_type": lambda log: [{"Timestamp": event["time"], "Event_type": event["type"], "Attributes": [attr['name'] for attr in event.get('attributes', []) if attr['name'] not in 'attribute_type_not_identified']} for event in log['events'] if event['type'] not in "dummy_activity"],
    "event_instance_attribute_value": lambda log: [{"Timestamp": event["time"],"Event_type": event["type"],"Attributes": [attr['value'] for attr in event.get('attributes', [])]} for event in log['events'] if event['type'] not in "dummy_activity"],
    "event_to_object": lambda log: [{"Timestamp": event["time"],"Event_type": event["type"],"Relationships": [rel['objectId'] for rel in event['relationships']]} for event in log['events'] if event['type'] not in "dummy_activity"],
    "object_type_attribute_type_rel": lambda log: [{"Object_type": obj_type['name'],"Object_attributes": [attr["name"] for attr in obj_type.get('attributes', []) if attr["name"] not in "attribute_type_not_identified"]} for obj_type in log["objectTypes"] if obj_type['name'] not in "object_type_not_identified"],
    "object_instance_object_type_rel": lambda log: [{"Object_ID": obj["id"] ,"Object_type": obj["type"]} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified' and obj['type'] not in "object_type_not_identified"],
    "object_instance_attribute_type_rel": lambda log: [{"Object_ID": obj['id'], "Object_attributes": [attr["name"] for attr in obj.get('attributes', []) if attr['name'] not in 'attribute_type_not_identified']} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified'],
    "object_instance_attribute_value_rel": lambda log: [{"Object_ID": obj['id'],"Object_attributes": [attr["value"] for attr in obj.get('attributes', [])]} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified'],
    "object_to_object_rel": lambda log: [{"Object_ID": obj['id'],"Object_relationships": [rel['objectId'] for rel in obj.get('relationships', [])]} for obj in log["objects"] if obj['id'] not in 'object_instance_not_identified'],
    "event_type_attribute_type_rel": lambda  log: [{"Event_type": event_type["name"],"Attributes": [attr['name'] for attr in event_type['attributes']]} for event_type in log['eventTypes'] if event_type['name'] not in "dummy_activity"],
    "event_instance_attribute_type_rel": lambda log: [{"Timestamp": event["time"], "Event_type": event["type"], "Attributes": [attr['name'] for attr in event.get('attributes', []) if attr['name'] not in 'attribute_type_not_identified']} for event in log['events'] if event['type'] not in "dummy_activity"],
    "event_instance_attribute_value_rel": lambda log: [{"Timestamp": event["time"],"Event_type": event["type"],"Attributes": [attr['value'] for attr in event.get('attributes', [])]} for event in log['events'] if event['type'] not in "dummy_activity"],
    "event_to_object_rel": lambda log: [{"Timestamp": event["time"],"Event_type": event["type"],"Relationships": [rel['objectId'] for rel in event['relationships']]} for event in log['events'] if event['type'] not in "dummy_activity"]
}

def calculate_semantic_similarity(text1, text2):
    # Create spaCy documents
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    # Check if either document has empty vectors
    if doc1.vector_norm == 0 or doc2.vector_norm == 0:
        return 0

    # Compute similarity
    return doc1.similarity(doc2)*100

def try_convert(value):
    try:
        return float(str(value))
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            return value


def perform_matching(extracted, original, extracted_keys, original_keys, threshold, matched_dict, second_round=False):
    # Initialize the similarity matrix with padding if necessary
    max_size = max(len(extracted), len(original))
    extracted = extracted + [''] * (max_size - len(extracted))
    original = original + [''] * (max_size - len(original))
    extracted_keys = extracted_keys + [''] * (max_size - len(extracted_keys))
    original_keys = original_keys + [''] * (max_size - len(original_keys))

    # Matrices to store similarities
    similarity_matrix = np.zeros((max_size, max_size))
    string_similarity_matrix = np.zeros((max_size, max_size))
    semantic_similarity_matrix = np.zeros((max_size, max_size))

    for i, extracted_entity in enumerate(extracted):
        for j, original_entity in enumerate(original):
            extracted_entity = try_convert(extracted_entity)
            original_entity = try_convert(original_entity)
            if not isinstance(extracted_entity, str) or not isinstance(original_entity, str):
                if extracted_entity == original_entity:
                    string_similarity = 100
                    semantic_similarity = 100
                else:
                    string_similarity = 0
                    semantic_similarity = 0
            else:
                # Calculate string similarity
                extracted_lemmatized = lemmatizer.lemmatize(re.sub(r'[^a-zA-Z0-9\s]', '', extracted_entity.lower()))
                original_lemmatized = lemmatizer.lemmatize(re.sub(r'[^a-zA-Z0-9\s]', '', original_entity.lower()))
                string_similarity = fuzz.partial_ratio(extracted_lemmatized, original_lemmatized)
                if string_similarity == 100:
                    if extracted_entity.lower() == original_entity.lower():  # Check for exact match
                        string_similarity = 100
                    else:
                        # Adjust similarity based on subset detection
                        if extracted_entity.lower() in original_entity.lower() or original_entity.lower() in extracted_entity.lower():
                            string_similarity -= 1

                # Calculate semantic similarity
                semantic_similarity = calculate_semantic_similarity(extracted_lemmatized, original_lemmatized)
                if semantic_similarity > 100:
                    semantic_similarity -= 1  # Avoid values over 100

            # Store the similarities in their respective matrices
            string_similarity_matrix[i, j] = string_similarity
            semantic_similarity_matrix[i, j] = semantic_similarity

            # Compute the maximum similarity and apply threshold logic
            max_similarity = max(string_similarity, semantic_similarity)

            if second_round:
                # In the second round, both similarities must be over threshold - 20 to consider a match
                if string_similarity < threshold or semantic_similarity < threshold:
                    similarity_matrix[i, j] = 0
                else:
                    similarity_matrix[i, j] = max_similarity
            else:
                # First round logic
                if max_similarity < threshold:
                    similarity_matrix[i, j] = 0
                else:
                    similarity_matrix[i, j] = max_similarity

    row_ind, col_ind = linear_sum_assignment(-similarity_matrix)

    # Match events based on the Hungarian algorithm results
    matched_rows = set()
    matched_cols = set()
    for i, j in zip(row_ind, col_ind):
        if similarity_matrix[i, j] >= threshold:
            matched_dict[original_keys[j]] = (extracted_keys[i], similarity_matrix[i, j])
            matched_rows.add(i)
            matched_cols.add(j)

    return matched_rows, matched_cols, matched_dict

def calculate_hungarian_matching(extracted_list, original_list, extracted_keys_list, original_keys_list, matched_original_dict, threshold):

    # First round of matching with the original threshold
    matched_rows, matched_cols, matched_original_dict = perform_matching(
        extracted_list, original_list, extracted_keys_list, original_keys_list, threshold, matched_original_dict
    )

    # Prepare lists of unmatched entities for the second round
    unmatched_extracted_list = [extracted_list[i] for i in range(len(extracted_list)) if i not in matched_rows]
    unmatched_original_list = [original_list[j] for j in range(len(original_list)) if j not in matched_cols]
    unmatched_extracted_keys_list = [extracted_keys_list[i] for i in range(len(extracted_keys_list)) if
                                     i not in matched_rows]
    unmatched_original_keys_list = [original_keys_list[j] for j in range(len(original_keys_list)) if
                                    j not in matched_cols]

    # Second round of matching with a threshold lowered by 20 and additional similarity conditions
    perform_matching(
        unmatched_extracted_list, unmatched_original_list, unmatched_extracted_keys_list, unmatched_original_keys_list,
        threshold-20, matched_original_dict, second_round=True
    )

    return matched_original_dict

def grouped_hungarian_matching(extracted_list, original_list, grouping_name, similarity_comparison_name, matched_original_dict, threshold, mapping = None):

    grouped_extracted_entities = defaultdict(list)
    grouped_original_entities = defaultdict(list)

    for entity in extracted_list:
        grouping_criteria = entity[grouping_name]
        grouped_extracted_entities[grouping_criteria].append(entity)

    for entity in original_list:
        grouping_criteria = entity[grouping_name]
        grouped_original_entities[grouping_criteria].append(entity)

    if not mapping: # One-to-one-mapping enforced

        mapping = {}
        for key_original in grouped_original_entities.keys():
            if key_original in grouped_extracted_entities.keys():
                mapping[key_original] = key_original

    for grouping_criteria_original, grouping_criteria_extracted in mapping.items():
        extracted_entities = grouped_extracted_entities[grouping_criteria_extracted]
        extracted_entities_for_similarity = [entity[similarity_comparison_name] for entity in extracted_entities]
        extracted_keys_list = [(entity[grouping_name], entity[similarity_comparison_name]) for entity in extracted_entities]

        original_entities = grouped_original_entities[grouping_criteria_original]
        original_entities_for_similarity = [entity[similarity_comparison_name] for entity in original_entities]
        original_keys_list = [(entity[grouping_name], entity[similarity_comparison_name]) for entity in original_entities]

        # Apply the Hungarian algorithm
        matched_original_dict = calculate_hungarian_matching(extracted_entities_for_similarity, original_entities_for_similarity,
                                                             extracted_keys_list, original_keys_list,
                                                             matched_original_dict, threshold)
    return matched_original_dict


def calculate_matches_missings_additionals(matched_original_dict, extracted_keys_list, original_keys_list, final_matched_original_dict = None):

    additional_entities = []
    missing_entities = []

    if not final_matched_original_dict:
        final_matched_original_dict = {k: v[0] for k, v in matched_original_dict.items() if v[0]}

    for extracted_entity in extracted_keys_list:
        if extracted_entity not in final_matched_original_dict.values():
            additional_entities.append(extracted_entity)

    for original_entity in original_keys_list:
        if original_entity not in final_matched_original_dict.keys():
            missing_entities.append(original_entity)

    return final_matched_original_dict, missing_entities, additional_entities

def grouped_calculation_of_matches_missing_additionals(extracted_list, original_list, grouping_name, similarity_comparison_name, matched_original_dict):

    extracted_keys_list = [(entity[grouping_name], entity[similarity_comparison_name]) for entity in extracted_list]
    original_keys_list = [(entity[grouping_name], entity[similarity_comparison_name]) for entity in original_list]
    final_matched_original_dict, missing_entities, additional_entities = calculate_matches_missings_additionals(matched_original_dict, extracted_keys_list, original_keys_list)

    return final_matched_original_dict, missing_entities, additional_entities


def extract_child_levels(data_list, grouping_name, similarity_comparison_name):
    child_level_list = []

    for item in data_list:
        grouping_value = item[grouping_name] if isinstance(grouping_name, str) else tuple(
            item[name] for name in grouping_name)
        if not item[similarity_comparison_name]:  # Check if the list is empty
            child_level_list.append({grouping_name: grouping_value, similarity_comparison_name: ''})
        else:
            for element in item[similarity_comparison_name]:
                child_level_list.append({grouping_name: grouping_value, similarity_comparison_name: element})

    return child_level_list

def correct_child_level_lists(list1, list2, grouping_name, similarity_comparison_name, mapping):
    data_list = []
    for element in list1:
        key = element[grouping_name]
        value = element[similarity_comparison_name]
        if key not in mapping.keys() and key not in mapping.values():
            data_list.append(element)
        elif value !='':
            data_list.append(element)
        elif value == '':
            for element2 in list2:
                key2 = element2[grouping_name]
                value2 = element2[similarity_comparison_name]
                if key in mapping.keys():
                    if mapping[key] == key2 and value2 == '':
                        data_list.append(element)
                elif key2 in mapping.keys():
                    if mapping[key2] == key and value2 == '':
                        data_list.append(element)

    return data_list


def calculate_parent_confusion_matrices(level, extracted_list, original_list, threshold):

    matched_original_dict = defaultdict(lambda: ("", 0))

    if level in {"object_type", "object_instance", "event_type"}:
        matched_original_dict = calculate_hungarian_matching(extracted_list, original_list, extracted_list, original_list, matched_original_dict, threshold)
        final_matched_original_dict, missing_entities, additional_entities = calculate_matches_missings_additionals(matched_original_dict, extracted_list, original_list)

    elif level == "event_instance":

        matched_original_dict = grouped_hungarian_matching(extracted_list, original_list, 'Timestamp', 'Event_type', matched_original_dict, threshold)
        final_matched_original_dict, missing_entities, additional_entities = grouped_calculation_of_matches_missing_additionals(extracted_list, original_list, 'Timestamp', 'Event_type', matched_original_dict)

    confusion_matrix = {
        "TP": len(final_matched_original_dict),
        "FP": len(additional_entities),
        "FN": len(missing_entities),
        "TN": 0,
        "OC": len(original_list),
        "NC": len(extracted_list)

    }

    print(f"Matches: {final_matched_original_dict}")
    print(f"Missing: {missing_entities}")
    print(f"Additional: {additional_entities}")
    print()

    return confusion_matrix, final_matched_original_dict


def calculate_child_confusion_matrices(level, extracted_list, original_list, grouping_name, similarity_comparison_name, mapping, threshold, case = None):
    matched_original_dict = defaultdict(lambda: ("", 0))

    if isinstance(extracted_list[0][similarity_comparison_name], (list, set)):
        original_list_prep = extract_child_levels(original_list, grouping_name, similarity_comparison_name)
        extracted_list_prep = extract_child_levels(extracted_list, grouping_name, similarity_comparison_name)
        original_list = correct_child_level_lists(original_list_prep, extracted_list_prep, grouping_name, similarity_comparison_name, mapping)
        extracted_list = correct_child_level_lists(extracted_list_prep, original_list_prep, grouping_name, similarity_comparison_name, mapping)

    if case == "rel":
        original_list = [entity for entity in original_list if entity[grouping_name] in mapping.keys()]
        extracted_list = [entity for entity in extracted_list if entity[grouping_name] in mapping.values()]

    matched_original_dict = grouped_hungarian_matching(extracted_list, original_list, grouping_name, similarity_comparison_name, matched_original_dict, threshold, mapping)
    final_matched_original_dict, missing_entities, additional_entities = grouped_calculation_of_matches_missing_additionals(extracted_list, original_list, grouping_name,similarity_comparison_name, matched_original_dict)

    # Allow for reverse order in O2O-relationships
    if level in ['object_to_object', 'object_to_object_rel']:
        intermediate_matched_dict = {}
        missing_list = []
        additional_list = []
        o2o_reverse_order = {}
        for rel in additional_entities:
            o2o_reverse_order[(rel[1], rel[0])] = (rel[0], rel[1])

        for entity in missing_entities:
            missing_list.append({"Object_ID": entity[0], "Object_relationships": entity[1]})
        for entity in additional_entities:
            additional_list.append({"Object_ID": entity[1], "Object_relationships": entity[0]})

        intermediate_matched_dict = grouped_hungarian_matching(additional_list, missing_list, grouping_name, similarity_comparison_name, intermediate_matched_dict, threshold,mapping)
        final_intermediate_matched_dict, missing_entities, additional_entities = grouped_calculation_of_matches_missing_additionals(additional_list, missing_list, grouping_name, similarity_comparison_name, intermediate_matched_dict)

        for entity in additional_entities.copy():
            additional_entities.remove(entity)
            additional_entities.append(o2o_reverse_order[entity])

        for key, value in final_intermediate_matched_dict.items():
            final_matched_original_dict[key] = (value[1], value[0])


    confusion_matrix = {
        "TP": len(final_matched_original_dict),
        "FP": len(additional_entities),
        "FN": len(missing_entities),
        "TN": 0,
        "OC": len(original_list),
        "NC": len(extracted_list)
    }

    print(f"Matches: {final_matched_original_dict}")
    print(f"Missing: {missing_entities}")
    print(f"Additional: {additional_entities}")
    print()

    return confusion_matrix

def confusion_matrix_creator(original_log, extracted_log, level, mapping=None, threshold=70):

    # Extract the original and extracted lists based on the level
    original_list = extractors[level](original_log)
    extracted_list = extractors[level](extracted_log)

    # Define a mapping dictionary for different levels
    level_mappings = {
        "parent": {
            "object_type": ("object_type",),
            "object_instance": ("object_instance",),
            "event_type": ("event_type",),
            "event_instance": ("event_instance",)
        },
        "absolute_child": {
            "object_type_attribute_type": ('Object_type', 'Object_attributes'),
            "object_instance_object_type": ('Object_ID', 'Object_type'),
            "object_instance_attribute_type": ('Object_ID', 'Object_attributes'),
            "object_instance_attribute_value": ('Object_ID', 'Object_attributes'),
            "object_to_object": ('Object_ID', 'Object_relationships'),
            "event_type_attribute_type": ('Event_type', 'Attributes'),
            "event_instance_attribute_type": (("Timestamp", "Event_type"), 'Attributes'),
            "event_instance_attribute_value": (("Timestamp", "Event_type"), 'Attributes'),
            "event_to_object": (("Timestamp", "Event_type"), "Relationships")
        },
        "relative_child": {
            "object_type_attribute_type_rel": ('Object_type', 'Object_attributes'),
            "object_instance_object_type_rel": ('Object_ID', 'Object_type'),
            "object_instance_attribute_type_rel": ('Object_ID', 'Object_attributes'),
            "object_instance_attribute_value_rel": ('Object_ID', 'Object_attributes'),
            "object_to_object_rel": ('Object_ID', 'Object_relationships'),
            "event_type_attribute_type_rel": ('Event_type', 'Attributes'),
            "event_instance_attribute_type_rel": (("Timestamp", "Event_type"), 'Attributes'),
            "event_instance_attribute_value_rel": (("Timestamp", "Event_type"), 'Attributes'),
            "event_to_object_rel": (("Timestamp", "Event_type"), "Relationships")
        }
    }

    print(f"Level: {level}")

    # Handle parent level
    if level in level_mappings["parent"]:
        confusion_matrix, mapping = calculate_parent_confusion_matrices(level, extracted_list, original_list, threshold)
        return confusion_matrix, mapping

    # Handle child levels (absolute and relative)
    for child_type in ["absolute_child", "relative_child"]:
        if level in level_mappings[child_type]:
            param1, param2 = level_mappings[child_type][level]
            case = "rel" if "rel" in level else None
            confusion_matrix = calculate_child_confusion_matrices(level, extracted_list, original_list, param1, param2, mapping, threshold, case)

            return confusion_matrix

    # Return None if level is not found
    return None
