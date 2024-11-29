import re

def value_differentiator(doc, candidate_values_with_positions):
    object_labels_with_positions = {}
    clear_attribute_values_with_positions = {}
    remaining_values_with_positions = {}

    for value, position_list in candidate_values_with_positions.items():

        product = False
        attr_val = False
        for positions in position_list:
            for position in positions:
                if (doc[position].ent_type_ in ['CARDINAL', 'QUANTITY'] and re.search(r'\d', value)) or (doc[position].pos_ in ['ADJ', 'VERB'] and doc[position].ent_type not in ['ORDINAL']):
                    attr_val = True
                elif doc[position].ent_type_ in ['PRODUCT'] or (
                        re.search(r'[A-Za-z]', doc[position].text) and re.search(r'\d', doc[position].text)):
                    product = True

        if product == True:
            object_labels_with_positions[value] = position_list

        elif attr_val == True:
            clear_attribute_values_with_positions[value] = position_list

        else:
            remaining_values_with_positions[value] = position_list

    return object_labels_with_positions, clear_attribute_values_with_positions, remaining_values_with_positions



