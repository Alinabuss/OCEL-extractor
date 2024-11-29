from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import extract_prefix_and_suffix
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import remove_subsets
import re

def candidate_object_type_extractor(doc, text):
    object_types_with_positions = {}
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

    # Iterate through the tokens in the text
    for i, token in enumerate(doc):
        # Check if the token is a noun and not a stop word
        if token.pos_ in ['NOUN', 'PROPN']:
            # Check the dependency of the token
            if token.dep_ in ['nsubj', 'attr', 'dobj', 'pobj', 'nsubjpass', 'conj', 'appos'] or token.ent_type_ in ['ORG']:

                refined_attribute, compound_prefix, positions = extract_prefix_and_suffix(doc, token)

                if refined_attribute not in object_types_with_positions:
                    object_types_with_positions[refined_attribute] = []
                object_types_with_positions[refined_attribute].append(tuple(positions))

    object_types_with_positions = remove_subsets(object_types_with_positions)
    for obj in object_types_with_positions.copy():
        if any(obj in entity for entity in quotated_elements):
            del object_types_with_positions[obj]


    return object_types_with_positions