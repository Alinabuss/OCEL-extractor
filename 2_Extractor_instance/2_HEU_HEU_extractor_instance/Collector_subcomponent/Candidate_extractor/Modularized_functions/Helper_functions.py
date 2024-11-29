def extract_prefix_and_suffix(doc, token):
    compound_prefix = []
    compound_suffix = []
    positions = []

    # Combine token children and ancestors for analysis
    related_tokens = list(token.children) + list(token.ancestors)

    positions.append(token.i)
    # Check related tokens for 'compound' or 'pcomp' dependency
    for related_token in related_tokens:
        if related_token.dep_ in ['compound', 'pcomp', 'amod']:
            if related_token.i < token.i:
                compound_prefix.insert(0,related_token.text)
                positions.insert(0,related_token.i)
                # Expand prefix collection from related_token
                prev_token = related_token
                while prev_token.i > 0:
                    prev_token = doc[prev_token.i - 1]
                    if prev_token.dep_ in ['compound', 'pcomp', 'amod']:
                        compound_prefix.insert(0, prev_token.text)
                        positions.insert(0, prev_token.i)
                    else:
                        break

            elif related_token.i > token.i:
                compound_suffix.append(related_token.text)
                positions.append(related_token.i)
                # Expand suffix collection from related_token
                next_token = related_token
                while next_token.i < len(doc) - 1:
                    next_token = doc[next_token.i + 1]
                    if next_token.dep_ in ['compound', 'pcomp'] and next_token.text not in compound_suffix:
                        compound_suffix.append(next_token.text)
                        positions.append(next_token.i)
                    else:
                        break



    # Combine the components to form the refined attribute
    refined_attribute = ' '.join(compound_prefix + [token.text] + compound_suffix)

    #### Check for numeric prefix
    numeric_prefix = []
    if min(positions) > 1:  # Ensure there are at least two tokens before the prefix
        num_token = doc[min(positions) - 2]
        punct_token = doc[min(positions) - 1]

        if num_token.pos_ == 'NUM' and punct_token.pos_ == 'PUNCT' and punct_token.text not in ['.', ',']:
            numeric_prefix.insert(0, punct_token.text)  # Prepend PUNCT token
            numeric_prefix.insert(0, num_token.text)  # Prepend NUM token
            positions.insert(0, punct_token.i)
            positions.insert(0, num_token.i)

    refined_attribute = ' '.join(numeric_prefix + [refined_attribute])

    #### Check for noun/propn prefix
    noun_prefix = []
    if min(positions) > 1:  # Ensure there are at least two tokens before the prefix
        pre_token = doc[min(positions) - 1]

        if pre_token.pos_ == 'NUM' in ['NOUN', 'PROPN'] and pre_token.i not in positions:
            noun_prefix.insert(0, pre_token.text)  # Prepend PUNCT token
            positions.insert(0, pre_token.i)

    refined_attribute = ' '.join(noun_prefix + [refined_attribute])


    return refined_attribute, compound_prefix, positions

def extract_prepositional_prefix(doc, current_attribute, positions):
    first_token_pos = min(positions)

    # Combine token children and ancestors for analysis
    related_tokens = list(doc[first_token_pos].children) + list(doc[first_token_pos].ancestors)
    refined_attribute = current_attribute

    # Check related tokens for 'compound' or 'pcomp' dependency
    for related_token in related_tokens:
        if related_token.dep_ in ['prep'] and doc[related_token.i - 1].pos_ in ['NOUN', 'PROPN'] and related_token.i < first_token_pos:
            refined_attribute = f"{doc[related_token.i - 1].text} {doc[related_token.i].text} {current_attribute}"
            positions.insert(0, related_token.i)
            positions.insert(0, related_token.i - 1)


    return refined_attribute, positions


def remove_subsets(mapping):
    # Remove subsets of values based on their positions
    filtered_values = {}
    for value, pos_list in mapping.items():
        is_subset = False
        for other_value, other_pos_list in mapping.items():
            # Skip comparing the same item
            if value == other_value:
                continue
            # Check if the current value's positions are a subset of another value's positions
            if pos_list and other_pos_list:
                if all(pos in other_pos_list[0] for pos in pos_list[0]):
                    is_subset = True
                    break

        # If it's not a subset, add it to the filtered list
        if not is_subset:
            filtered_values[value] = pos_list

    copy = filtered_values.copy()

    # Dictionary to keep track of merged positions
    merged_values = {}

    # Iterate through the values and positions
    for value, pos_list in copy.items():
        merged = False  # Track if the value has been merged
        for other_value, other_pos_list in copy.items():
            if value == other_value:
                continue

            # Check if 'value' is a substring of 'other_value'
            if value in other_value:
                # Merge positions into the larger word (other_value)
                if other_value not in merged_values:
                    merged_values[other_value] = list(filtered_values[other_value])  # Start with its original positions
                merged_values[other_value].extend(pos_list)
                merged = True
                break  # Stop further processing for this value if it's merged

        # If the value hasn't been merged, retain it as-is
        if not merged:
            if value not in merged_values:
                merged_values[value] = pos_list

    # Handle transitive merging: deduplicate positions in merged_values
    for key in merged_values:
        merged_values[key] = list(set(merged_values[key]))  # Remove duplicates if needed

    return merged_values


def merge_adjacent_values(doc, attribute_values_with_positions):
    merged_values_with_positions = {}

    # Sort entries by their first position to ensure processing in the correct order
    sorted_entries = sorted(attribute_values_with_positions.items(), key=lambda x: x[1][0][0])

    current_value = ""
    current_positions = []

    for value, positions_list in sorted_entries:
        if not current_value:  # Start a new entry
            current_value = value
            current_positions = list(positions_list[0])  # Convert tuple to list
        else:
            # Check if the last position of the current entity is directly followed by the next position
            # or separated by a PUNCT token (but not '.' or ',')
            last_position = current_positions[-1]
            next_position = positions_list[0][0]

            # Create a variable to track punctuations
            punct_text = ""
            punct_positions = []
            is_mergeable = True

            # Check if there are PUNCT tokens between the current and next position
            for pos in range(last_position + 1, next_position):
                token = doc[pos]
                if token.pos_ == 'PUNCT' and token.text not in ['.', ',']:
                    punct_text += token.text
                    punct_positions.append(pos)
                else:
                    # If there is a non-PUNCT token (other than space) between, stop the merge
                    is_mergeable = False
                    break

            # Merge if the values are directly adjacent or separated by punctuations
            if is_mergeable:
                current_value += punct_text + value  # Merge with punctuations (no space)
                current_positions.extend(punct_positions)  # Add punct positions
                current_positions.extend(list(positions_list[0]))  # Merge the positions
            else:
                # Finalize the current entity
                if current_value not in merged_values_with_positions:
                    merged_values_with_positions[current_value] = []
                merged_values_with_positions[current_value].append(tuple(current_positions))

                # Start a new entry
                current_value = value
                current_positions = list(positions_list[0])

    # Finalize the last entity
    if current_value:
        if current_value not in merged_values_with_positions:
            merged_values_with_positions[current_value] = []
        merged_values_with_positions[current_value].append(tuple(current_positions))

    return merged_values_with_positions

