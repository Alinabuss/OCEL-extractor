from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import indirect_matching_over_position
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

def attribute_value_mapper(doc, token_position_mapping):
    attribute_value_mapping = {}


    attribute_values_with_positions = []
    for attr_val in token_position_mapping['attribute_values_positions'].keys():
        for positions in token_position_mapping['attribute_values_positions'][attr_val]:
            if tuple([attr_val, positions]) not in attribute_values_with_positions:
                attribute_values_with_positions.append(tuple([attr_val, positions]))

    undefined_values_with_positions = []
    for attr_val in token_position_mapping['remaining_values_positions'].keys():
        for positions in token_position_mapping['remaining_values_positions'][attr_val]:
            if tuple([attr_val, positions]) not in undefined_values_with_positions:
                undefined_values_with_positions.append(tuple([attr_val, positions]))

    attribute_values_with_positions += undefined_values_with_positions

    attributes_with_positions = []
    for attr_val in token_position_mapping['attributes_positions'].keys():
        for positions in token_position_mapping['attributes_positions'][attr_val]:
            if tuple([attr_val, positions]) not in attributes_with_positions:
                attributes_with_positions.append(tuple([attr_val, positions]))

    resources_with_positions = [
        (matching, tuple(sum(token_position_mapping["event_resources_positions"][matching], ()))) for matching in
        token_position_mapping['event_resources_positions'].keys()]

    lifecycle_status_with_positions = [
        (matching, tuple(sum(token_position_mapping["event_lifecylce_positions"][matching], ()))) for matching in
        token_position_mapping['event_lifecylce_positions'].keys()]

    timestamps_with_positions = [
        (matching, tuple(sum(token_position_mapping["timestamp_positions"][matching], ()))) for matching in
        token_position_mapping['timestamp_positions'].keys()]

    # Store unmatched attributes and attribute values
    resources = [resource[0] for resource in resources_with_positions]
    lifecycle_status = [status[0] for status in lifecycle_status_with_positions]


    #### Try to match over position of tokens in text if value and attribute type in direct neighborhood
    if len(attribute_values_with_positions)>0:
        for attr_value, attr_value_positions in attribute_values_with_positions:
            if attr_value not in attribute_value_mapping:
                for attr_type, attr_positions in attributes_with_positions:
                    if attr_positions != () and attr_value_positions != ():
                        distance = abs(min(attr_value_positions) - max(attr_positions))
                        if distance < 3:
                            attribute_value_mapping[attr_value] = attr_type
                            continue

                tokens = list(doc)
                preceding_tokens = tokens[max(0, min(attr_value_positions) - 3):min(attr_value_positions)]
                for token in preceding_tokens:
                    if token.pos_ == "VERB":  # Check if token is a verb
                        lemmatized_token = token.lemma_  # Get the lemmatized version of the verb
                        for attr_type, _ in attributes_with_positions:
                            if lemmatized_token in attr_type:  # Check if the lemma is a substring of an attribute type
                                attribute_value_mapping[attr_value] = attr_type
                                continue

    for value in attribute_values_with_positions.copy():
        if value[0] in attribute_value_mapping.keys():
            attribute_values_with_positions.remove(value)

    #### Try direct matching
    if len(attribute_values_with_positions) > 0:
        # Check if attribute value is in the related tokens of attribute type
        attribute_value_mapping = direct_matching_over_position(doc, attribute_value_mapping, attributes_with_positions, attribute_values_with_positions, level = 'best_match')
        for value in attribute_values_with_positions.copy():
            if value[0] in attribute_value_mapping.keys():
                attribute_values_with_positions.remove(value)

    #### Try indirect matching
    if len(attribute_values_with_positions)>0:
        attribute_value_mapping = indirect_matching_over_position(doc, attribute_value_mapping, attributes_with_positions,
                                                                attribute_values_with_positions, level='best_match')

        for value in attribute_values_with_positions.copy():
            if value[0] in attribute_value_mapping.keys():
                attribute_values_with_positions.remove(value)

    #### Add mapping for event lifecycle and event resource attributes
    for status in lifecycle_status:
        attribute_value_mapping[status] = 'lifecycle'

    for resource in resources:
        attribute_value_mapping[resource] = 'resource'


    #### Handle exception case when a timestamp can be an attribute value
    date_time_indicator = ['date', 'time', 'timestamp', 'year', 'month', 'day', 'hour', 'minute', 'second']
    exception_case = False
    exception_attributes = []
    for indicator in date_time_indicator:
        for attr in attributes_with_positions:
            if indicator in lemmatizer.lemmatize(attr[0]).lower() and indicator != lemmatizer.lemmatize(attr[0]).lower():
                exception_case = True
                if attr not in exception_attributes:
                    exception_attributes.append(attr)

    if exception_case == True:
        attribute_value_mapping = direct_matching_over_position(doc, attribute_value_mapping, exception_attributes,
                                                                timestamps_with_positions, level='best_match')

        intermediate_list = list(token_position_mapping["timestamp_positions"].keys())
        for value in intermediate_list:
            if value in attribute_value_mapping.keys():
                del token_position_mapping["timestamp_positions"][value]
                for ts in timestamps_with_positions:
                    if ts[0] == value:
                        positions = ts[1]
                token_position_mapping["attribute_values_positions"][value] = [positions]

    #### Remaining clear attribute values are mapped to Attribute_type_not_identified
    for attr in attribute_values_with_positions.copy():
        if attr in undefined_values_with_positions:
            attribute_values_with_positions.remove(attr)

    for attr in attribute_values_with_positions:
        if attr[0] not in attribute_value_mapping.keys():
            attribute_value_mapping[attr[0]] = "Attribute_type_not_identified"

    #### Update token_position_mapping --> remove attribute values that have not been used
    intermediate_list = list(token_position_mapping["remaining_values_positions"].keys())
    for value in intermediate_list:
        if value not in attribute_value_mapping.keys():
            del token_position_mapping["remaining_values_positions"][value]

    return attribute_value_mapping, token_position_mapping
