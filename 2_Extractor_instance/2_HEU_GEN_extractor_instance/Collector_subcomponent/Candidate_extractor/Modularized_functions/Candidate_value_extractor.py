import re
from word2number import w2n
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import remove_subsets
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import merge_adjacent_values


def test_punctual_prefix_and_suffix(doc, value, positions):
    # Save the original value and positions for resetting if necessary
    original_value = value
    original_positions = positions.copy()

    # Initialize the first and last positions in the positions list
    first_position = positions[0]
    last_position = positions[-1]

    # Check for punct and noun/proper noun before the value
    if first_position > 0 and doc[first_position - 1].pos_ == 'PUNCT' and doc[first_position - 1].text not in ['.',
                                                                                                               ',']:
        first_position -= 1
        while first_position > 0:
            previous_token = doc[first_position]
            if previous_token.pos_ == 'PUNCT' and previous_token.text not in ['.', ',']:
                value = previous_token.text + value  # Prepend the PUNCT token
                positions.insert(0, first_position)  # Update the positions
                first_position -= 1  # Move the position index back to the punctuation
            elif previous_token.pos_ in ['NOUN', 'PROPN']:
                value = previous_token.text + ' ' + value  # Prepend the noun/proper noun
                positions.insert(0, first_position)  # Update the positions
                first_position -= 1  # Move the position index back to the noun/proper noun
                break
            else:
                # Reset if a token is not PUNCT or NOUN/PROPN
                value = original_value
                positions = original_positions
                break

    # Check for punct and noun/proper noun after the value
    if last_position < len(doc) - 1 and doc[last_position + 1].pos_ == 'PUNCT' and doc[last_position + 1].text not in [
        '.', ',']:
        last_position += 1
        while last_position < len(doc) - 1:
            next_token = doc[last_position]
            if next_token.pos_ == 'PUNCT' and next_token.text not in ['.', ',', '*']:
                value = value + next_token.text  # Append the PUNCT token
                positions.append(last_position)  # Update the positions
                last_position += 1  # Move the position index forward to the punctuation
            elif next_token.pos_ in ['NOUN', 'PROPN']:
                value = value + ' ' + next_token.text  # Append the noun/proper noun
                positions.append(last_position)  # Update the positions
                last_position += 1  # Move the position index forward to the noun/proper noun
                break
            else:
                # Reset if a token is not PUNCT or NOUN/PROPN
                value = original_value
                positions = original_positions
                break

    return value, positions


def candidate_value_extractor(doc, text):
    attribute_values_with_positions = {}

    quotated_elements = set()

    # Regular expression pattern to match text
    pattern_double_quotation_marks = r'\"(.*?)\"'
    pattern_single_quotation_marks = r'\'(.*?)\''
    pattern_round_brackets = r'\((.*?)\)'
    pattern_square_brackets = r'\[(.*?)\]'

    # Use regular expressions to find text within round brackets
    quotated_elements.update(match.group(1) for match in re.finditer(pattern_double_quotation_marks, text))
    quotated_elements.update(match.group(1) for match in re.finditer(pattern_single_quotation_marks, text))
    quotated_elements.update(match.group(1) for match in re.finditer(pattern_round_brackets, text))
    quotated_elements.update(match.group(1) for match in re.finditer(pattern_square_brackets, text))

    # Correction step: Remove periods at the end of object labels
    quotated_elements = list({element.rstrip('.') for element in quotated_elements})

    # Append quotated elements if they correspond to tuple
    for i, token in enumerate(doc):
        for quotated_element in quotated_elements:
            quotated_tokens = quotated_element.split()
            if token.text == quotated_tokens[0]:  # If the current token matches the start of a quoted element
                match = True
                match_indices = [token.i]
                for j in range(1, len(quotated_tokens)):
                    if i + j < len(doc) and doc[i + j].text == quotated_tokens[j]:
                        match_indices.append(doc[i + j].i)
                    else:
                        match = False
                        continue
                if match:
                    # Join the tokens to form the full quoted element
                    full_quotated_element = ' '.join(quotated_tokens)
                    if full_quotated_element not in attribute_values_with_positions:
                        attribute_values_with_positions[full_quotated_element] = []
                    attribute_values_with_positions[full_quotated_element].append(tuple(match_indices))


    # Append more types of attribute values
    for token in doc:
        if token.pos_ in ['NUM'] or (re.search(r'[A-Za-z]', token.text) and re.search(r'\d', token.text)) or (token.ent_type_ and token.ent_type_ not in ['DATE', 'TIME', 'ORDINAL'] and token.pos_ not in ['DET', 'X']) or token.text in quotated_elements or (token.pos_ in ['ADJ'] and token.dep_ in ['pobj']):

            if token.ent_type_ == 'CARDINAL' and token.i + 1 < len(doc) and doc[token.i + 1].pos_ == 'PUNCT' and doc[token.i + 1].text not in ['.', ',']:
                continue
            # Initialize positions list and value
            positions = [token.i]
            value = token.text

            if token.ent_type_ == "CARDINAL" and not any(char.isdigit() for char in token.text):
                try:
                    # Convert the word-based number to an integer and then to a float
                    value = str(w2n.word_to_num(token.text))
                except:
                    pass

            # Scan previous tokens for 'compound' or 'appos' dependencies
            previous_token = token.i - 1
            while previous_token >= 0 and doc[previous_token].dep_ in ['compound', 'appos', 'pobj'] and doc[previous_token].pos_ in ['NOUN', 'PROPN']:
                # Prepend the previous token's text and append its position
                value = doc[previous_token].text + ' ' + value
                positions.insert(0, previous_token)
                previous_token -= 1

            value, positions = test_punctual_prefix_and_suffix(doc, value, positions)

            # Add the value and positions to the dictionary
            if value not in attribute_values_with_positions:
                attribute_values_with_positions[value] = []
            attribute_values_with_positions[value].append(tuple(positions))

    attribute_values_with_positions = remove_subsets(attribute_values_with_positions)
    attribute_values_with_positions = merge_adjacent_values(doc, attribute_values_with_positions)

    return attribute_values_with_positions



