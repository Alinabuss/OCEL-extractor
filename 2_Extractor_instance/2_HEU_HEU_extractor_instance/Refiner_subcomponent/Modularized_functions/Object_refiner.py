import inflect
from collections import defaultdict, Counter
import re
import difflib
import spacy
from nltk.stem import WordNetLemmatizer
from fuzzywuzzy import fuzz
from Refiner_subcomponent.Modularized_functions.Event_Object_Type_refiner import event_object_type_refiner

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load spaCy's English language model
nlp = spacy.load("en_core_web_md")

def remove_object_types_that_only_appear_once(log):
    obj_type_counter = Counter()

    for obj in log['objects']:
        obj_type_counter[obj['type']] +=1

    log['objectTypes'] = [obj_type for obj_type in log['objectTypes'] if obj_type_counter[obj_type['name']] > 1]

    for obj in log['objects']:
        if obj_type_counter[obj['type']]==1:
            obj['type'] = 'object_type_not_identified'

    return log

def remove_object_attributes_that_only_appear_once(log):
    attribute_counter = Counter()

    # First pass: Count occurrences of each attribute name
    for obj in log['objects']:
        if 'attributes' in obj:
            for attr in obj['attributes']:
                attribute_counter[attr['name']] += 1

    # Second pass: Remove attributes that only appear once and replace them
    for obj in log['objects']:
        if 'attributes' in obj:
            # Filter attributes to keep only those that appear more than once
            obj['attributes'] = [
                attr if attribute_counter[attr['name']] > 1 else {'name': 'attribute_type_not_identified',
                                                                  'value': attr['value']}
                for attr in obj['attributes']
            ]

    # Update object types to reflect changes
    for obj_type in log['objectTypes']:
        if 'attributes' in obj_type:
            obj_type['attributes'] = [
                attr for attr in obj_type['attributes'] if attribute_counter[attr['name']] > 1
            ]

    # Return the refined log
    return log

def replace_object_types_if_subsets(log):
    # Create a dictionary to map object IDs to their types
    id_to_type = {obj["id"]: obj["type"] for obj in log["objects"]}

    # Iterate through objects
    for obj in log["objects"]:
        current_id = obj["id"]
        # Check if an object type is a substring of any object type name
        for obj_type in log["objectTypes"]:
            if obj_type["name"] in current_id:
                # Replace type with the identified object type
                obj["type"] = obj_type["name"]
                # Update the id_to_type mapping
                id_to_type[current_id] = obj["type"]
                break  # No need to check further once a match is found

    return log



def assimilate_formatting_for_same_object_types(log):
    type_groups = defaultdict(list)
    id_mapping = {}

    # Group objects by their type, excluding 'object_type_not_identified'
    for obj in log["objects"]:
        if obj["type"] != 'object_type_not_identified':
            type_groups[obj["type"]].append(obj)

    # Process each type group
    for obj_type, objs in type_groups.items():
        if len(objs) > 1:
            id_list = [obj["id"] for obj in objs]

            # Create patterns for each ID
            patterns = []
            letter_segments = []

            for id_str in id_list:
                # Replace digits with [number] and non-common letters with [letter]
                id_str_pattern = re.sub(r'[A-Za-z]+', 'letter', id_str)  # Replace letters
                id_str_pattern = re.sub(r'\d+', 'number', id_str_pattern)  # Replace digits
                patterns.append(id_str_pattern)

                # Extract letter segments
                segments = re.findall(r'[A-Za-z]+', id_str)
                letter_segments.append(segments)

            # Find the most common pattern
            common_pattern = Counter(patterns).most_common(1)[0][0]

            letter_list = []
            for id_str in id_list:
                regex_pattern = re.escape(common_pattern).replace(r'number', r'\d+').replace(r'letter', r'[A-Za-z]+')
                pattern = re.compile(regex_pattern)
                if pattern.match(id_str):
                    letter_list.append(re.findall(r'[A-Za-z]+', id_str))

            consistent_letters = []
            if letter_list:
                transposed_letter_list = list(zip(*letter_list))
                for segment_group in transposed_letter_list:
                    if len(set(segment_group)) == 1:  # All segments are the same
                        consistent_letters.append(segment_group[0])
                    else:
                        consistent_letters.append('letter')

            # Update common pattern with the correct position
            f_string_template = re.sub(r'letter', '{}', common_pattern)
            if len(consistent_letters) == f_string_template.count('{}'):
                common_pattern = f_string_template.format(*consistent_letters)

            #print(f"Object-type '{obj_type} has most common pattern: {common_pattern}'")

            for obj in objs:
                id_str = obj["id"]

                specific_id_regex = re.sub(r'[A-Za-z]+', 'letter', id_str)  # Replace letters
                specific_id_regex = re.sub(r'\d+', 'number', specific_id_regex)  # Replace digits

                # Find all letter segments in id_str
                segments = re.findall(r'[A-Za-z]+', id_str)
                for i, segment in enumerate(segments):
                    if segment not in consistent_letters:
                        segments[i] = 'letter'

                specific_f_string_template = re.sub(r'letter', '{}', specific_id_regex)
                if len(segments) == specific_f_string_template.count('{}'):
                    # Format the f-string template with segments
                    specific_id_regex = specific_f_string_template.format(*segments)

                # Check if the id_str matches the common pattern
                if specific_id_regex == common_pattern:
                    #print(f"Correct object '{id_str}' has pattern '{specific_id_regex}'")
                    obj["id"] = id_str  # No change needed
                else:
                    #print(f"Wrong Object '{id_str} has pattern '{specific_id_regex}'.")

                    # Create a regex pattern to find matching parts in specific_id_regex
                    common_pattern_regex = re.escape(common_pattern).replace(r'number', r'\d+').replace(r'letter', r'[A-Za-z]+')
                    common_pattern_compiled = re.compile(common_pattern_regex)

                    if common_pattern in specific_id_regex:
                        #print(f"[Case: common_pattern in specific_id_regex]'")
                        # Find the longest substring of specific_id_regex that matches the common pattern
                        match = common_pattern_compiled.search(id_str)
                        matched_substring = match.group()

                        # Find matching part in the original id_str
                        specific_pattern_regex_compiled = re.compile(
                            re.escape(matched_substring).replace(r'letter', r'[A-Za-z]+').replace(r'number', r'\d+'))
                        specific_match = specific_pattern_regex_compiled.search(id_str)
                        if specific_match:
                            adjusted_id = specific_match.group().strip()
                            obj["id"] = adjusted_id
                        else:
                            obj["id"] = id_str.strip()

                    elif specific_id_regex in common_pattern:
                        #print(f"[Case: specific_id_regex in common_pattern]'")
                        diff = difflib.ndiff(specific_id_regex, common_pattern)
                        diff_chars = [char[2:] for char in diff if char.startswith('+ ')]
                        diff_str = ''.join(diff_chars)
                        if not 'letter' in diff_str and not 'number' in diff_str:
                            # Initialize the f-string template
                            f_string_template = re.sub(r'number', '{}', common_pattern)
                            f_string_template = re.sub(r'letter', '{}', f_string_template)

                            # Find all segments of letters and numbers, preserving the order
                            segments = re.findall(r'[A-Za-z]+|\d+', id_str)
                            for segment in segments:
                                if segment in consistent_letters:
                                    segments.remove(segment)

                            # Ensure that the number of placeholders matches the number of segments
                            if len(segments) == f_string_template.count('{}'):
                                # Format the f-string template with segments
                                adjusted_id = f_string_template.format(*segments)
                                obj["id"] = adjusted_id
                            else:
                                obj["id"] = id_str.strip()

                # Track the mapping from old ID to new ID
                id_mapping[id_str] = obj["id"]

    # Update events to propagate changes in object IDs
    for event in log["events"]:
        for relationship in event["relationships"]:
            original_id = relationship["objectId"]
            if original_id in id_mapping:
                relationship["objectId"] = id_mapping[original_id]

    for obj in log["objects"]:
        if 'relationships' in obj:
            for relationship in obj["relationships"]:
                original_id = relationship["objectId"]
                if original_id in id_mapping:
                    relationship["objectId"] = id_mapping[original_id]

    return log


def adapt_object_types_based_on_similar_object_names(log):
    # Create a dictionary to map object names (with numbers) to their types
    object_name_to_types = {}
    for obj in log["objects"]:
        obj_name = obj["id"].lower()
        clean_name = re.sub(r'\d+', '', obj_name)  # Clean name without numbers for comparison
        if clean_name not in object_name_to_types and clean_name != "":
            object_name_to_types[clean_name] = []
        if clean_name != "":
            object_name_to_types[clean_name].append(obj["type"])

    # Initialize similarity groups
    similarity_groups = []

    # Iterate over object names and assign to similarity groups
    for name in object_name_to_types.keys():
        added_to_group = False

        # Compare with existing similarity groups
        for group in similarity_groups:
            for existing_name in group:
                # Calculate the similarity between names
                string_similarity = fuzz.partial_ratio(name, existing_name)

                if string_similarity == 100:
                    if re.sub(r'\d+', '', name).lower() == re.sub(r'\d+', '', existing_name).lower():  # Check for exact match
                        string_similarity = 100
                    else:
                        # Adjust similarity based on subset detection (still high values but not perfect values anymore)
                        if re.sub(r'\d+', '', name).lower() in re.sub(r'\d+', '', existing_name).lower() or re.sub(
                                r'\d+', '', existing_name).lower() in re.sub(r'\d+', '', name).lower():
                            length_diff = abs(len(name) - len(existing_name))
                            deduction = min(length_diff, 20)  # Cap the maximum deduction
                            string_similarity -= deduction

                #print(f"{name}:{existing_name} = {string_similarity}")
                if string_similarity > 95:
                    group.add(name)
                    added_to_group = True
                    break
            if added_to_group:
                break

        # If not added to any group, create a new group
        if not added_to_group:
            similarity_groups.append({name})

    # Create a mapping for the most prominent object type for each group
    name_to_prominent_type = {}
    for group in similarity_groups:
        all_types = []
        for name in group:
            all_types.extend(object_name_to_types[name])
        if all_types:  # Ensure there is at least one type to avoid errors
            most_common_type = Counter(all_types).most_common(1)[0][0]
            for name in group:
                name_to_prominent_type[name] = most_common_type

    # Update object types based on the most prominent type
    for obj in log["objects"]:
        obj_name = obj["id"].lower()
        clean_name = re.sub(r'\d+', '', obj_name)
        if clean_name in name_to_prominent_type:
            obj["type"] = name_to_prominent_type[clean_name]

    # Create a dictionary for similarity groups with type counts
    group_type_counts = {}
    for group in similarity_groups:
        group_key = frozenset(group)
        group_type_counts[group_key] = {}

    for obj in log["objects"]:
        obj_name = obj["id"].lower()
        clean_name = re.sub(r'\d+', '', obj_name)
        obj_type = obj["type"]
        for group in similarity_groups:
            if clean_name in group:
                group_key = frozenset(group)
                if obj_type not in group_type_counts[group_key]:
                    group_type_counts[group_key][obj_type] = 0
                group_type_counts[group_key][obj_type] += 1
                break

    return log, group_type_counts


def adapt_object_names_based_on_similarity_groups(log, similarity_groups):
    # Create a dictionary to map object names to their attributes
    object_name_to_attributes = {}
    for obj in log["objects"]:
        obj_name = obj["id"].lower()
        if obj_name not in object_name_to_attributes:
            object_name_to_attributes[obj_name] = obj["attributes"]

    # Reverse mapping: attribute name to object names
    attribute_to_names = {}
    for name, attributes in object_name_to_attributes.items():
        for attr in attributes:
            attr_name = attr["value"].lower()
            if attr_name not in attribute_to_names:
                attribute_to_names[attr_name] = set()
            attribute_to_names[attr_name].add(name)

    # Analyze similarity groups
    type_to_groups = {}
    for group_key, type_counts in similarity_groups.items():
        for obj_type in type_counts.keys():
            if obj_type not in type_to_groups:
                type_to_groups[obj_type] = []
            type_to_groups[obj_type].append(group_key)

    # Check for problematic types and fix them
    for obj_type, groups in type_to_groups.items():
        if len(groups) > 1:  # Type is assigned to more than one group
            # Find the group with the lower count
            group_counts = {group: sum(similarity_groups[group].values()) for group in groups}
            correct_group = max(group_counts, key=group_counts.get)
            problematic_groups = [group for group in groups if group != correct_group]

            for problematic_group in problematic_groups:

                # Find object names in the problematic group from the log
                problematic_names = {obj["id"].lower() for obj in log["objects"] if re.sub(r'\d+', '', obj["id"].lower()) in problematic_group}
                #print("problematic_names: ", problematic_names)

                # Screen attributes to find a matching name from other groups
                for obj in log["objects"]:
                    if obj["id"].lower() in problematic_names:
                        attributes = obj["attributes"]
                        for attr in attributes:
                            attr_name = attr["value"].lower()
                            if re.sub(r'\d+', '', attr_name) in correct_group:
                                #print("Possible replacement: ", attr_name)
                                original_object_id = obj["id"]
                                obj["id"] = attr_name
                                obj["attributes"] = [attr for attr in obj["attributes"] if attr["value"].lower() != attr_name]
                                # Check if the problematic name is unique
                                if len([o for o in log["objects"] if o["id"].lower() == original_object_id.lower()]) == 0 and original_object_id != "Object_instance_not_found":
                                    # Propagate changes to object-relationships and event-relationships
                                    for o in log["objects"]:
                                        relationships = o["relationships"]
                                        for rel in relationships:
                                            if rel["objectId"] == original_object_id:
                                                rel["objectId"] = attr_name
                                    for e in log["events"]:
                                        relationships = e["relationships"]
                                        for rel in relationships:
                                            if rel["objectId"] == original_object_id:
                                                rel["objectId"] = attr_name

                                break

    return log

def convert_objects_in_attributes_to_objects(log, similarity_groups):

    similarity_groups = {
        key: value
        for key, value in similarity_groups.items()
        if any(counter >= 5 for counter in value.values())
    }

    # Iterate over the objects in the log
    for obj in log["objects"]:
        # Extract attributes of the current object
        attributes = obj.get("attributes", [])
        for attr in attributes:
            # Remove numbers from the attribute value
            attr_value_cleaned = re.sub(r'\d+', '', attr["value"]).lower()

            # Check if the cleaned attribute value matches any similarity group
            matching_group = None
            for group in similarity_groups.keys():
                if attr_value_cleaned in group:
                    matching_group = group
                    break

            if matching_group:
                # Check if this attribute (with numbers) already exists as an object
                attr_value_original = attr["value"]
                existing_object = next((o for o in log["objects"] if o["id"].lower() == attr_value_original.lower()),
                                       None)

                if existing_object:
                    # If the object exists, remove the attribute
                    obj["attributes"] = [a for a in obj["attributes"] if a["value"].lower() != attr["value"].lower()]
                else:
                    # If the object doesn't exist, add it as a new object and remove the attribute
                    new_object = {
                        "id": attr_value_original,
                        "type": list(similarity_groups[matching_group].keys())[0],
                        # Use the type from similarity_groups
                        "attributes": []  # Start with no attributes, can add more if needed
                    }
                    log["objects"].append(new_object)
                    obj["attributes"] = [a for a in obj["attributes"] if a["value"].lower() != attr["value"].lower()]

    return log


def object_refiner(log):
    log = replace_object_types_if_subsets(log)
    log = assimilate_formatting_for_same_object_types(log)
    log, similarity_groups = adapt_object_types_based_on_similar_object_names(log)
    log = adapt_object_names_based_on_similarity_groups(log, similarity_groups)
    log = event_object_type_refiner(log)
    return log
