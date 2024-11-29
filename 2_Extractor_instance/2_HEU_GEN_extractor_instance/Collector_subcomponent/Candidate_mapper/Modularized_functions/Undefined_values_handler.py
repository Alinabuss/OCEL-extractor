from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Mutual_exclusion_step import filter_unacceptable_words
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Mutual_exclusion_step import remove_unnecessary_prepositions_punctuals_and_adjectives

def undefined_values_handler(doc, token_position_mapping):
    undefined_values = token_position_mapping['remaining_values_positions']
    value_event_mapping = {}

    unmatched_activities_with_positions = []
    for activity in token_position_mapping['activity_positions'].keys():
        for positions in token_position_mapping['activity_positions'][activity]:
            if tuple([activity, positions]) not in unmatched_activities_with_positions:
                unmatched_activities_with_positions.append(tuple([activity, positions]))

    # Try to identify object labels in undefined values (values that are NOUN/PROPN/NUM and can be matched to an activity)
    label_search = undefined_values.copy()
    for word, positions in label_search.items():
        all_positions_valid  = True
        for position in positions:
            for pos in position:
                if doc[pos] not in ['NOUN', 'PROPN']:
                    all_positions_valid = False

        if all_positions_valid:
            undefined_value_with_position = [
                (word, tuple(sum(token_position_mapping["remaining_values_positions"][word], ())))]

            # Use direct_matching_over_position to match the word
            value_event_mapping = direct_matching_over_position(
                doc,
                value_event_mapping,
                unmatched_activities_with_positions,
                undefined_value_with_position,
                level='best_match'
            )

            # If matched, update the token_position_mapping
            if word in value_event_mapping.keys():
                token_position_mapping['object_labels_positions'][word] = positions

    # Remove matched values from undefined_values
    for value in list(undefined_values.keys()):  # Use list to create a static copy for safe iteration
        if value in token_position_mapping['object_labels_positions']:
            del undefined_values[value]

    #### Cleaning of token position mapping for new object labels
    token_position_mapping['event_resources_positions'] = filter_unacceptable_words(doc, token_position_mapping['event_resources_positions'],[token_position_mapping['object_labels_positions']])
    token_position_mapping['activity_positions'] = filter_unacceptable_words(doc, token_position_mapping['activity_positions'], [token_position_mapping['object_labels_positions']], case='activity')
    token_position_mapping['attributes_positions'] = filter_unacceptable_words(doc, token_position_mapping['attributes_positions'], [token_position_mapping['object_labels_positions']])
    token_position_mapping['object_type_positions'] = filter_unacceptable_words(doc, token_position_mapping['object_type_positions'], [token_position_mapping['object_labels_positions']])

    token_position_mapping['event_resources_positions'] = remove_unnecessary_prepositions_punctuals_and_adjectives(doc, token_position_mapping['event_resources_positions'])
    token_position_mapping['activity_positions'] = remove_unnecessary_prepositions_punctuals_and_adjectives(doc,token_position_mapping['activity_positions'])
    token_position_mapping['attributes_positions'] = remove_unnecessary_prepositions_punctuals_and_adjectives(doc,token_position_mapping['attributes_positions'])
    token_position_mapping['object_type_positions'] = remove_unnecessary_prepositions_punctuals_and_adjectives(doc,token_position_mapping['object_type_positions'])

    return token_position_mapping






