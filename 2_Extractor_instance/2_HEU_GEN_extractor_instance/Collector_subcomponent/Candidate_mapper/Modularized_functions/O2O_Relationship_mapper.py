import spacy
from nltk.stem import WordNetLemmatizer
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load English tokenizer, POS tagger, lemmatizer, and NER
nlp = spacy.load("en_core_web_sm")

def o2o_relationship_mapper(doc, object_type_mapping, token_position_mapping):
    complete_relationship_mapping = {}
    o2o_relations = {}

    objects_with_positions = [
        (matching, tuple(sum(token_position_mapping["object_labels_positions"][matching], ()))) for matching in
        token_position_mapping['object_labels_positions'].keys()]

    object_types_with_positions = [
        (matching, tuple(sum(token_position_mapping["object_type_positions"][matching], ()))) for matching in
        token_position_mapping['object_type_positions'].keys()]

    for obj in objects_with_positions:
        complete_relationship_mapping[obj[0]] = []

    # Try direct matching between objects:
    # if len(objects_with_positions)>1:
    #     o2o_relations = direct_matching_over_position(doc, o2o_relations, objects_with_positions, objects_with_positions, case = 'strict')
    #     for first_object, second_objects in o2o_relations.items():
    #         for second_object in second_objects:
    #             if first_object != second_object:
    #                 complete_relationship_mapping[first_object].append({
    #                     "objectId": second_object,
    #                     "qualifier": None
    #                 })


    indicator_words = ['relationship', 'related', 'relation', 'associated', 'linked', 'connected']

    for token in doc:
        if token.text in indicator_words:
            token_pos = token.i  # Get the position of the indicator word

            # Initialize variables to store the closest objects and object types
            closest_before = None
            closest_after = None
            closest_type_before = None
            closest_type_after = None

            min_distance_before = float('inf')
            min_distance_after = float('inf')
            min_type_distance_before = float('inf')
            min_type_distance_after = float('inf')

            # Step 1: Search for the closest object (before and after the indicator word)
            for obj, positions in objects_with_positions:
                for pos in positions:
                    # Find the closest object before the indicator word
                    if pos < token_pos and (token_pos - pos) < min_distance_before:
                        min_distance_before = token_pos - pos
                        closest_before = obj

                    # Find the closest object after the indicator word
                    elif pos > token_pos and (pos - token_pos) < min_distance_after:
                        min_distance_after = pos - token_pos
                        closest_after = obj

            # Step 2: Search for the closest object type (before and after the indicator word)
            for obj_type, obj_type_positions in object_types_with_positions:
                for pos in obj_type_positions:
                    # Find the closest object type before the indicator word
                    if pos < token_pos and (token_pos - pos) < min_type_distance_before:
                        min_type_distance_before = token_pos - pos
                        closest_type_before = obj_type

                    # Find the closest object type after the indicator word
                    elif pos > token_pos and (pos - token_pos) < min_type_distance_after:
                        min_type_distance_after = pos - token_pos
                        closest_type_after = obj_type

            #print(f"intermediate: closest_before: {closest_before}; {closest_type_before}, closest_after: {closest_after}, {closest_type_after}")

            # Step 3: Compare distances and proceed accordingly
            if min_distance_before <= min_type_distance_before:
                # Closest object is before the indicator word, use it directly
                final_closest_before = closest_before
            else:
                # Closest object type is before the indicator word, find the closest acceptable object
                acceptable_objects_before = [obj for obj, obj_type in object_type_mapping.items() if
                                             obj_type == closest_type_before]
                if acceptable_objects_before != []:
                    final_closest_before = None
                    min_distance = float('inf')
                    for obj, positions in objects_with_positions:
                        if obj in acceptable_objects_before:
                            for pos in positions:
                                if pos < token_pos and (token_pos - pos) < min_distance:
                                    min_distance = token_pos - pos
                                    final_closest_before = obj
                else:
                    final_closest_before = closest_before

            if min_distance_after <= min_type_distance_after:
                # Closest object is after the indicator word, use it directly
                final_closest_after = closest_after
            else:
                # Closest object type is after the indicator word, find the closest acceptable object
                acceptable_objects_after = [obj for obj, obj_type in object_type_mapping.items() if
                                            obj_type == closest_type_after]
                if acceptable_objects_after != []:
                    final_closest_after = None
                    min_distance = float('inf')
                    for obj, positions in objects_with_positions:
                        if obj in acceptable_objects_after:
                            for pos in positions:
                                if pos > token_pos and (pos - token_pos) < min_distance:
                                    min_distance = pos - token_pos
                                    final_closest_after = obj
                else:
                    final_closest_after = closest_after

            # Step 4: If both closest objects (before and after) are found, map them
            #print(f"final_closest_before: {final_closest_before}, final_closest_after: {final_closest_after}")
            if final_closest_before and final_closest_after:
                complete_relationship_mapping[final_closest_before].append(
                    {"objectId": final_closest_after, "qualifier": None})


    #print("CHECK: complete_relationship_mapping - ", complete_relationship_mapping)

    final_relationship_mapping = {}
    for obj in complete_relationship_mapping.keys():
        if complete_relationship_mapping[obj]!=[]:
            if len(complete_relationship_mapping[obj])>1:
                related_objects = []
                for rel in complete_relationship_mapping[obj]:
                    if rel['objectId'] not in related_objects:
                        related_objects.append(rel['objectId'])
                        if obj not in final_relationship_mapping.keys():
                            final_relationship_mapping[obj]=[]
                        final_relationship_mapping[obj].append(rel)

            else:
                final_relationship_mapping[obj] = complete_relationship_mapping[obj]

    #print("CHECK: final_relationship_mapping - ", final_relationship_mapping)


    return final_relationship_mapping