from fuzzywuzzy import fuzz
import re
import spacy
from nltk.stem import WordNetLemmatizer
from collections import Counter, defaultdict
import itertools

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load spaCy's English language model
nlp = spacy.load("en_core_web_md")


def calculate_similarity(event_name, other_name):
    doc1 = nlp(event_name)
    doc2 = nlp(other_name)
    semantic_similarity = doc1.similarity(doc2) * 100
    string_similarity = fuzz.partial_ratio(event_name, other_name)
    similarity_score = max(semantic_similarity, string_similarity)

    return similarity_score, semantic_similarity

def merge_attributes(keep, remove, log, removal_category, removal_list, readd_list, mapping):
    for attr in remove['attributes']:
        if attr not in keep['attributes']:
            keep['attributes'].append(attr)
    mapping[remove['name']] = keep['name']
    if remove in log[removal_category]:
        log[removal_category].remove(remove)
    removal_list.append(remove['name'])
    readd_list.append(keep)

    return removal_list,  mapping, readd_list


def process_similar_types_with_attribute_merging(log, similarity_threshold, main_category, adaption_category):

    iteration_count = 0  # Track number of iterations
    max_iterations = 5  # Maximum number of iterations allowed
    
    # Precompute entity type counts
    entity_type_count = Counter(ent['type'].lower() for ent in log[adaption_category])
    entity_type_count['object_type_not_identified'] = 0
    entity_type_count['dummy_activity'] = 0

    if main_category == 'eventTypes':
        for ent in entity_type_count:
            if len(set(ent.split())) == 1:
                entity_type_count[ent] = 1

    # Precompute sets for each entity
    entity_sets = {}
    for entity in log[main_category]:
        name = entity["name"]
        set_name = set([ent.lower() for ent in name.split()])
        adapted_set_name = set(
            [lemmatizer.lemmatize(ent.lower()) for ent in name.split() if ent.lower() not in ['a', 'an', 'the']])
        entity_sets[name] = (set_name, adapted_set_name)

    # Precompute similarity scores
    similarity_scores = {}
    for (entity1, entity2) in itertools.combinations(log[main_category], 2):
        name1 = entity1["name"]
        name2 = entity2["name"]
        if name1 != name2:
            similarity_score, semantic_similarity = calculate_similarity(name1, name2)
            similarity_scores[(name1, name2)] = (similarity_score, semantic_similarity)

    # Initialize
    change = True
    while change and iteration_count < max_iterations:  # Ensure maximum 5 iterations
        change = False
        iteration_count += 1  # Increment iteration count
        
        merged_entities = {}
        removed_entities = set()
        readd_entities = []

        # Track direct and exact merges
        potential_replacements = {ent["name"]: [] for ent in log[main_category]}
        name_to_entity = {}

        # First Pass: Exact Merging
        exact_duplicates = defaultdict(list)
        for entity in log[main_category]:
            name = entity["name"]
            if name not in name_to_entity:
                name_to_entity[name] = entity
            else:
                # Collect duplicates for exact merging
                exact_duplicates[name].append(entity)

        # Apply exact merges
        for name, duplicates in exact_duplicates.items():
            if len(duplicates) > 1:
                # Keep the first occurrence and remove others
                keep_entity = name_to_entity[name]
                for duplicate in duplicates[1:]:
                    if duplicate in log[main_category]:
                        log[main_category].remove(duplicate)
                    removed_entities.add(duplicate["name"])
                    merged_entities[duplicate["name"]] = name
                    readd_entities.append(keep_entity)

        # Remove exact duplicates from potential replacements
        potential_replacements = {name: [] for name in name_to_entity.keys()}

        # Second Pass: Direct Merge for Best Replacements
        for entity1, entity2 in itertools.combinations(log[main_category], 2):
            name1 = entity1["name"]
            name2 = entity2["name"]

            if name1 == name2:
                continue

            # Use precomputed sets
            set1, adapted_set1 = entity_sets[name1]
            set2, adapted_set2 = entity_sets[name2]

            # Use precomputed similarity scores
            similarity_score, semantic_similarity = similarity_scores.get((name1, name2), (0, 0))

            # Check for direct merge
            direct_merge = (name1.lower() == name2.lower() or
                            name1.lower() in name2.lower() or
                            name2.lower() in name1.lower() or
                            set1.issubset(set2) or set2.issubset(set1) or
                            adapted_set1.issubset(adapted_set2) or adapted_set2.issubset(adapted_set1) or
                            similarity_score > similarity_threshold or
                            (main_category == 'eventTypes' and (similarity_score > similarity_threshold-10 or
                             semantic_similarity > similarity_threshold - 15)))

            if direct_merge:
                if entity_type_count[name2] >= entity_type_count[name1]:
                    if name2 in potential_replacements:
                        if (name1, similarity_score, semantic_similarity) not in potential_replacements[name2]:
                            potential_replacements[name1].append((name2, similarity_score, semantic_similarity))
                else:
                    if name1 in potential_replacements:
                        if (name2, similarity_score, semantic_similarity) not in potential_replacements[name1]:
                            potential_replacements[name2].append((name1, similarity_score, semantic_similarity))

        # Determine the best replacement for each entity
        for entity_name, candidates in potential_replacements.items():
            if candidates:
                best_candidate = max(candidates, key=lambda x: (
                entity_type_count[x[0]], x[1]))  # Best based on type count and similarity score
                best_name = best_candidate[0]

                # Update merged_entities
                if entity_name != best_name:
                    removed_entities.add(entity_name)
                    merged_entities[entity_name] = best_name
                    readd_entities.append(next(ent for ent in log[main_category] if ent["name"] == best_name))
                    change = True

        # Update log after processing all replacements
        log[main_category] = [ent for ent in log[main_category] if ent["name"] not in removed_entities]
        for ent in readd_entities:
            if ent not in log[main_category]:
                log[main_category].append(ent)

        # Update adaption_category entries
        for entity in log[adaption_category]:
            if entity['type'] in merged_entities:
                entity['type'] = merged_entities[entity['type']]

        # Final cleanup: Remove remaining duplicates
    final_entities = {}
    for entity in log[main_category]:
        name = entity["name"]
        if name not in final_entities:
            final_entities[name] = entity

    log[main_category] = list(final_entities.values())

    return log


def process_object_instances(log):
    change = True
    iteration_count = 0  # Track number of iterations
    max_iterations = 5  # Maximum number of iterations allowed

    # Precompute object type counts and object label counts
    object_type_count = Counter(obj['type'] for obj in log['objects'])
    object_type_count['object_type_not_identified'] = 0

    object_label_count = Counter(
        rel['objectId'] for event in log['events'] for rel in event.get('relationships', [])
    )

    # Precompute adapted and normalized sets for object IDs
    entity_sets = {}
    
    for obj in log['objects']:
        obj_id = obj["id"]
        adapted_norm_set = set(lemmatizer.lemmatize(word) for word in re.sub(r'[^\w\s]+', '', obj_id).split())
        norm_set = set(re.sub(r'[^\w]+', ' ', obj_id).split())
        numerics = [int(num) for num in re.findall(r'\d+', obj_id)]
        entity_sets[obj_id] = (adapted_norm_set, norm_set, numerics)

    while change and iteration_count < max_iterations:  # Ensure maximum 5 iterations
        change = False
        iteration_count += 1  # Increment iteration count
        
        merged_objects = {}
        removed_objects = set()
        readd_objects = []

        # Track direct and exact merges
        potential_replacements = {obj["id"]: [] for obj in log['objects']}
        id_to_object = {}

        # First Pass: Exact Merging
        exact_duplicates = defaultdict(list)
        for obj in log['objects']:
            obj_id = obj["id"]
            if obj_id not in id_to_object:
                id_to_object[obj_id] = obj
            else:
                # Collect duplicates for exact merging
                exact_duplicates[obj_id].append(obj)

        # Apply exact merges
        for obj_id, duplicates in exact_duplicates.items():
            if len(duplicates) > 1:
                # Keep the first occurrence and remove others
                keep_object = id_to_object[obj_id]
                for duplicate in duplicates[1:]:
                    if duplicate in log['objects']:
                        log['objects'].remove(duplicate)
                    removed_objects.add(duplicate["id"])
                    merged_objects[duplicate["id"]] = obj_id
                    readd_objects.append(keep_object)

        # Remove exact duplicates from potential replacements
        potential_replacements = {obj_id: [] for obj_id in id_to_object.keys()}

        # Second Pass: Direct Merge for Best Replacements
        for obj1, obj2 in itertools.combinations(log['objects'], 2):
            id1 = obj1["id"]
            id2 = obj2["id"]

            if id1 == id2:
                continue

            # Use precomputed sets
            adapted_norm_set1, norm_set1, numerics1 = entity_sets[id1]
            adapted_norm_set2, norm_set2, numerics2 = entity_sets[id2]

            # Direct merge condition with numerics check
            direct_merge = (
                id1 in id2 or id2 in id1 or
                norm_set1.issubset(norm_set2) or norm_set2.issubset(norm_set1) or
                adapted_norm_set1.issubset(adapted_norm_set2) or adapted_norm_set2.issubset(adapted_norm_set1)
            )

            # Check for numerics equality before proceeding
            if direct_merge and numerics1 == numerics2:
                if object_label_count[id2] >= object_label_count[id1]:
                    potential_replacements[id1].append(id2)
                else:
                    potential_replacements[id2].append(id1)

        # Determine the best replacement for each object
        for obj_id, candidates in potential_replacements.items():
            if candidates:
                best_id = max(candidates, key=lambda x: object_label_count[x])

                # Update merged_objects
                if obj_id != best_id:
                    removed_objects.add(obj_id)
                    merged_objects[obj_id] = best_id
                    readd_objects.append(next(obj for obj in log['objects'] if obj["id"] == best_id))
                    change = True

        # Update log after processing all replacements
        log['objects'] = [obj for obj in log['objects'] if obj["id"] not in removed_objects]
        for obj in readd_objects:
            if obj not in log['objects']:
                log['objects'].append(obj)

        # Update relationships in the objects list
        for obj in log['objects']:
            if 'relationships' in obj:
                for rel in obj['relationships']:
                    if rel['objectId'] in merged_objects:
                        rel['objectId'] = merged_objects[rel['objectId']]

        # Update relationships in the events list
        for event in log['events']:
            for rel in event.get('relationships', []):
                if rel['objectId'] in merged_objects:
                    rel['objectId'] = merged_objects[rel['objectId']]

    # Final cleanup: Remove remaining duplicates
    final_objects = {}
    for obj in log['objects']:
        obj_id = obj["id"]
        if obj_id not in final_objects:
            final_objects[obj_id] = obj

    log['objects'] = list(final_objects.values())

    return log




def process_attribute_types(log, similarity_threshold, type_category, instance_category):

    attribute_type_count = Counter(attr['name'] for obj in log[instance_category] for attr in obj.get('attributes', []))
    attribute_type_count['attribute_type_not_identified'] = 0

    change = True
    while change:
        change = False
        merged_attr = {}
        removed_attr = []
        readd_attr = {}

        for object_type in log[type_category]:
            attributes_copy = object_type['attributes'].copy()

            for i, attr1 in enumerate(attributes_copy):
                for j in range(i + 1, len(attributes_copy)):
                    attr2 = attributes_copy[j]
                    key1 = (object_type['name'], attr1['name'])
                    key2 = (object_type['name'], attr2['name'])
                    if attr1 == attr2:
                        if attr2 in object_type['attributes']:
                            object_type['attributes'].remove(attr2)
                        if key2 not in removed_attr:
                            removed_attr.append(key2)
                        merged_attr[key1] = key2
                        readd_attr[object_type['name']] = attr1
                        change = True
                        continue

                    if attr1['name'] == attr2['name']:
                        types = []
                        attributes = [attr1['type'], attr2['type']]
                        types.extend(t for attr in attributes for t in attr.split('/'))
                        merged_type = "/".join(sorted(set(types)))
                        attr1['type'] = merged_type
                        if attr2 in object_type['attributes']:
                            object_type['attributes'].remove(attr2)
                        if key2 not in removed_attr:
                            removed_attr.append(key2)
                        merged_attr[key1] = key2
                        readd_attr[object_type['name']] = attr1
                        change = True
                        continue

                    direct_merge = False
                    set1 = set(attr1["name"].split())
                    set2 = set(attr2['name'].split())
                    adapted_set1 = set([lemmatizer.lemmatize(entity.lower()) for entity in attr1["name"].split()])
                    adapted_set2 = set([lemmatizer.lemmatize(entity.lower()) for entity in attr2["name"].split()])
                    similarity_score, semantic_similarity = calculate_similarity(attr1["name"], attr2["name"])
                    if attr1["name"] == attr2["name"] or attr1["name"] in attr2["name"] or attr1["name"] in attr2["name"]:
                        direct_merge = True
                    elif (set1.issubset(set2) or set2.issubset(set1) or adapted_set1.issubset(
                            adapted_set2) or adapted_set2.issubset(adapted_set1)) and abs(len(set1) - len(set2)) < 2:
                        direct_merge = True

                    elif similarity_score > similarity_threshold or semantic_similarity > similarity_threshold - 5:
                        direct_merge = True

                    if direct_merge == True:
                        keep, remove = (attr1, attr2) if attribute_type_count[attr1["name"]] >= attribute_type_count[attr2["name"]] else (attr2, attr1)
                        key_keep = (object_type['name'], keep['name'])
                        key_remove = (object_type['name'], remove['name'])
                        if keep['type'] != remove['type']:
                            types = []
                            attributes = [keep['type'], remove['type']]
                            types.extend(t for attr in attributes for t in attr.split('/'))
                            merged_type = "/".join(sorted(set(types)))
                            keep['type'] = merged_type
                        if remove in object_type['attributes']:
                            object_type['attributes'].remove(remove)
                        if key_remove not in removed_attr:
                            removed_attr.append(key_remove)
                        merged_attr[key_keep] = key_remove
                        readd_attr[object_type['name']] = keep
                        change = True

        for object_type in log[type_category]:
            if object_type['name'] in readd_attr.keys():
                if readd_attr[object_type['name']] not in object_type['attributes']:
                    object_type['attributes'].append(readd_attr[object_type['name']])

        for object in log[instance_category]:
            for original, replacement in merged_attr.items():
                if object['type'] == original[0]:
                    if 'attributes' in object:
                        for attr in object['attributes']:
                            if attr['name'] in original[1]:
                                attr['name'] = replacement[1]


    return log

def process_relationships(log, instance_category):

    removed_rel = []
    merged_rel = {}
    readd_rel = {}

    for obj in log[instance_category]:
        if 'relationships' in obj:
            relationships_copy = obj['relationships'].copy()

            for i, rel1 in enumerate(relationships_copy):
                for j in range(i + 1, len(relationships_copy)):
                    rel2 = relationships_copy[j]
                    key1 = (obj['id'], rel1['objectId'])
                    key2 = (obj['id'], rel2['objectId'])
                    if rel1 == rel2:
                        if rel2 in obj['relationships']:
                            obj['relationships'].remove(rel2)

                        removed_rel.append(key2)
                        merged_rel[key1] = key2
                        readd_rel[obj['id']] = rel1
                        continue

                    if rel1["objectId"] == rel2["objectId"]:
                        if not rel1['qualifier']:
                            rel1['qualifier'] = rel2['qualifier']

                        if rel2 in obj['relationships']:
                            obj['relationships'].remove(rel2)

                        removed_rel.append(key2)
                        merged_rel[key1] = key2
                        readd_rel[obj['id']] = rel1
                        continue

    for object in log[instance_category]:
        if object['id'] in readd_rel.keys():
            if readd_rel[object['id']] not in object['relationships']:
                object['relationships'].append(readd_rel[object['id']])



    return log


def extract_numerical_value(value_str):
    """Try to convert a string to a numerical value. If it fails, extract standalone numbers."""
    try:
        return float(value_str)
    except ValueError:
        # Extract numerical parts if conversion fails
        numbers = []
        parts = value_str.split()
        for part in parts:
            try:
                num = float(part)
                numbers.append(num)
            except ValueError:
                continue
        # Return None if no numbers are found
        return numbers[0] if numbers else None


def process_attribute_values(log, similarity_threshold, instance_category):
    attr_val_counter = {}

    # Iterate over each object in the specified instance category of the log
    for obj in log[instance_category]:
        if 'attributes' in obj:  # Check if the object has attributes
            for attr in obj['attributes']:
                attr_value = attr['value']
                attr_name = attr['name']

                # Initialize the dictionary for the attribute value if not already present
                if attr_value not in attr_val_counter:
                    attr_val_counter[attr_value] = {}

                # Initialize the counter for the attribute name if not already present
                if attr_name not in attr_val_counter[attr_value]:
                    attr_val_counter[attr_value][attr_name] = 0

                # Increment the counter for the attribute name
                if attr_name != "attribute_type_not_identified":
                    attr_val_counter[attr_value][attr_name] += 1

    # Second pass: Replace attribute names with the most common one
    for obj in log[instance_category]:
        if 'attributes' in obj:  # Check if the object has attributes
            for attr in obj['attributes']:
                attr_value = attr['value']

                # Find the most common attribute name for this value
                if attr_value in attr_val_counter:
                    most_common_name = max(attr_val_counter[attr_value], key=attr_val_counter[attr_value].get)

                    # Replace the attribute name with the most common one
                    attr['name'] = most_common_name


    removed_attr_val = []
    merged_attr_val = {}
    readd_attr_val = {}

    attribute_type_count = Counter(attr['name'] for obj in log[instance_category] for attr in obj.get('attributes', []))
    attribute_type_count['attribute_type_not_identified'] = 0
    attribute_value_count = Counter(attr['value'] for obj in log[instance_category] for attr in obj.get('attributes', []))

    for obj in log[instance_category]:
        if 'attributes' in obj:
            attributes_copy = obj['attributes'].copy()

            if obj['id'] not in readd_attr_val:
                readd_attr_val[obj['id']] = []

            for i, attr1 in enumerate(attributes_copy):
                for j in range(i + 1, len(attributes_copy)):
                    attr2 = attributes_copy[j]
                    key1 = (obj['id'], attr1['value'])
                    key2 = (obj['id'], attr2['value'])
                    if attr1 == attr2:
                        if attr2 in obj['attributes']:
                            obj['attributes'].remove(attr2)

                        removed_attr_val.append(key2)
                        merged_attr_val[key1] = key2
                        if attr1 not in readd_attr_val[obj['id']]:
                            readd_attr_val[obj['id']].append(attr1)
                        continue

                    if attr1['value'] == attr2['value']:
                        if attr1['name'] != attr2["name"]:
                            if attribute_type_count[attr1['name']] < attribute_type_count[attr2['name']]:
                                attr1['name'] = attr2['name']
                        if 'time' in attr1 and 'time' in attr2:
                            if attr1['time'] != attr2['time']:
                                if attr1['time'] == None:
                                    attr1['time'] == attr2['time']

                        if attr2 in obj['attributes']:
                            obj['attributes'].remove(attr2)

                        removed_attr_val.append(key2)
                        merged_attr_val[key1] = key2
                        if attr1 not in readd_attr_val[obj['id']]:
                            readd_attr_val[obj['id']].append(attr1)
                        continue

                    numerical_value1 = extract_numerical_value(attr1['value'])
                    numerical_value2 = extract_numerical_value(attr2['value'])

                    if numerical_value1 is not None and numerical_value1 == numerical_value2:
                        attr1['value'] = str(numerical_value1)
                        if attr1['name'] != attr2["name"]:
                            if attribute_type_count[attr1['name']] < attribute_type_count[attr2['name']]:
                                attr1['name'] = attr2['name']
                        if 'time' in attr1 and 'time' in attr2:
                            if attr1['time'] != attr2['time']:
                                if attr1['time'] == None:
                                    attr1['time'] == attr2['time']

                        if attr2 in obj['attributes']:
                            obj['attributes'].remove(attr2)

                        removed_attr_val.append(key2)
                        merged_attr_val[key1] = key2
                        if attr1 not in readd_attr_val[obj['id']]:
                            readd_attr_val[obj['id']].append(attr1)
                        continue

                    if numerical_value1 is None and numerical_value2 is None and (
                            attr1['value'] in attr2['value']
                            or attr2['value'] in attr1['value']
                            or fuzz.partial_ratio(attr1["value"], attr2["value"]) > similarity_threshold):
                        if attribute_value_count[attr1["value"]] < attribute_value_count[attr2["value"]]:
                            attr1["value"] = attr2["value"]
                        if attr1['name'] != attr2["name"]:
                            if attribute_type_count[attr1['name']] < attribute_type_count[attr2['name']]:
                                attr1['name'] = attr2['name']
                        if 'time' in attr1 and 'time' in attr2:
                            if attr1['time'] != attr2['time']:
                                if attr1['time'] == None:
                                    attr1['time'] == attr2['time']

                        if attr2 in obj['attributes']:
                            obj['attributes'].remove(attr2)

                        removed_attr_val.append(key2)
                        merged_attr_val[key1] = key2
                        if attr1 not in readd_attr_val[obj['id']]:
                            readd_attr_val[obj['id']].append(attr1)
                        continue


    for object in log[instance_category]:
        if object['id'] in readd_attr_val.keys() and readd_attr_val[object['id']]!=[]:
            for val in readd_attr_val[object['id']]:
                if val not in object['attributes']:
                    object['attributes'].append(val)

    return log

def process_events(log):
    merged_events = {}

    for event in log['events']:
        # Create a unique key based on time and type
        key = (event['time'], event['type'])

        if key not in merged_events:
            # If the key is not in the dictionary, add the event as is
            merged_events[key] = {
                "id": event['id'],
                "type": event['type'],
                "time": event['time'],
                "attributes": event['attributes'][:],  # Copy the list to avoid reference issues
                "relationships": event['relationships'][:]
            }
        else:
            # Merge attributes and relationships
            existing_event = merged_events[key]

            # Merge attributes
            attribute_names = {attr['name'] for attr in existing_event['attributes']}
            for attr in event['attributes']:
                if attr['name'] not in attribute_names:
                    existing_event['attributes'].append(attr)
                    attribute_names.add(attr['name'])

            # Merge relationships
            existing_relationships = {rel['objectId'] for rel in existing_event['relationships']}
            for rel in event['relationships']:
                if rel['objectId'] not in existing_relationships:
                    existing_event['relationships'].append(rel)
                    existing_relationships.add(rel['objectId'])

    # Convert merged_events dictionary back to a list
    merged_events_list = list(merged_events.values())

    # Update log with merged events
    log['events'] = merged_events_list

    return log


def remove_very_similar_entities_over_all_categories(log, similarity_threshold=95):

    #### Remove duplicates, substrings and very similar object/event types, while merging the attributes and propagating the changes to the objects/events-list
    print("Start removing similar entities")
    log = process_similar_types_with_attribute_merging(log, similarity_threshold, 'objectTypes', 'objects')
    print("Object types merged")
    log = process_similar_types_with_attribute_merging(log, similarity_threshold, 'eventTypes', 'events')
    print("Event types merged")
          
    #### Remove duplicates and substrings from objects, while merging the object_types, attributes and object-to-object-relationships
    log = process_object_instances(log)
    print("Object instances merged")
          
    #### Remove duplicates, substrings and very similar object/event attribute types
    log = process_attribute_types(log, similarity_threshold, 'objectTypes', 'objects')
    log = process_attribute_types(log, similarity_threshold, 'eventTypes', 'events')

    #### Remove duplicates, substrings (without numbers) and numerically identical object/event attribute values
    log = process_attribute_values(log, similarity_threshold, 'objects')
    log = process_attribute_values(log, similarity_threshold, 'events')

    #### Remove duplicates in object-to-object and event-to-object-relationships
    log = process_relationships(log, 'objects')
    log = process_relationships(log, 'events')

    #### Remove duplicates from events
    log = process_events(log)

    return log

