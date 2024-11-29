def extract_related_token(doc, list1):
    token_mapping = {}

    for entity in list1:
        if not isinstance(entity, str):
            related_tokens = []
            entity_positions = entity[1]

            for pos in entity_positions:
                token = doc[int(pos)]
                # Collect related tokens: children and ancestors
                related_tokens.extend([t.i for t in token.children])
                related_tokens.extend([t.i for t in token.ancestors])

            token_mapping[entity] = list(set(related_tokens))

    return token_mapping

def direct_matching_over_position(doc, mapping_with_positions, list1, list2, case = None, level = None):

    # Search related tokens of second list for tokens of first list
    list1_token_mapping = extract_related_token(doc, list1)
    list2_token_mapping = extract_related_token(doc, list2)

    for entity1, related_tokens1 in list1_token_mapping.items():
        max_intersections = 0
        for entity2 in list2:
            #print(f"Compare related tokens of '{entity1}' - {related_tokens1} to '{entity2}")
            intersection_size = len(set(related_tokens1) & set(entity2[1]))

            if case == 'strict':
                intersection = len(set(entity1[1]) & set(entity2[1]))
                if intersection or entity1[0] in entity2[0] or entity2[0] in entity1[0]:
                    print("CHECK: Break matching for ", entity1, " to ", entity2)
                    break

            if intersection_size > 0:
                #print("MATCH")
                if level == 'best_match':
                    if intersection_size > max_intersections:
                        max_intersections = intersection_size
                        mapping_with_positions[entity2[0]] = entity1[0]

                else:
                    if entity2[0] not in mapping_with_positions.keys():
                        mapping_with_positions[entity2[0]] = []
                    if case == 'with_position':
                        if entity1 not in mapping_with_positions[entity2[0]]:
                            mapping_with_positions[entity2[0]].append(entity1)
                    else:
                        if entity1[0] not in mapping_with_positions[entity2[0]]:
                            mapping_with_positions[entity2[0]].append(entity1[0])

    for entity2, related_tokens2 in list2_token_mapping.items():
        max_intersections = 0
        for entity1 in list1:
            #print(f"Compare related tokens of '{entity2}' - {related_tokens2} to '{entity1}")
            intersection_size = len(set(related_tokens2) & set(entity1[1]))

            if intersection_size > 0:
                #print("MATCH")
                if level == 'best_match':
                    if intersection_size > max_intersections:
                        max_intersections = intersection_size
                        mapping_with_positions[entity2[0]] = entity1[0]
                else:
                    if entity2[0] not in mapping_with_positions.keys():
                        mapping_with_positions[entity2[0]] = []
                    if case == 'with_position':
                        if entity1 not in mapping_with_positions[entity2[0]]:
                            mapping_with_positions[entity2[0]].append(entity1)
                    else:
                        if entity1[0] not in mapping_with_positions[entity2[0]]:
                            mapping_with_positions[entity2[0]].append(entity1[0])


    return mapping_with_positions

def indirect_matching_over_position(doc, mapping_with_positions, list1, list2, case=None, level=None):
    # Search related tokens of second list for tokens of first list
    list1_token_mapping = extract_related_token(doc, list1)
    list2_token_mapping = extract_related_token(doc, list2)

    for entity1, related_tokens1 in list1_token_mapping.items():
        max_intersections = 0
        best_match_entity = None
        for entity2, related_tokens2 in list2_token_mapping.items():
            # Find intersection between related tokens of both entities
            intersection_size = len(set(related_tokens1) & set(related_tokens2))
            #print(f"Compare related tokens of '{entity2}' - {related_tokens2} to '{entity1} - {related_tokens1}")

            if intersection_size > 0:
                # There is an indirect match through related tokens
                #print(f"Indirect MATCH: '{entity1}' with '{entity2}'")
                if level == 'best_match':
                    if intersection_size > max_intersections:
                        max_intersections = intersection_size
                        best_match_entity = entity2[0]
                else:
                    if entity2[0] not in mapping_with_positions.keys():
                        mapping_with_positions[entity2[0]] = []
                    if case == 'with_position':
                        if entity1 not in mapping_with_positions[entity2[0]]:
                            mapping_with_positions[entity2[0]].append(entity1)
                    else:
                        if entity1[0] not in mapping_with_positions[entity2[0]]:
                            mapping_with_positions[entity2[0]].append(entity1[0])

        if level == 'best_match' and best_match_entity is not None:
            mapping_with_positions[best_match_entity] = entity1[0]

    return mapping_with_positions




