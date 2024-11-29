import spacy
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import indirect_matching_over_position
from datetime import datetime

# Load spaCy model for lemmatization
nlp = spacy.load("en_core_web_sm")

def timestamp_activty_attribute_mapper(doc, token_position_mapping, DEFAULT_TIMESTAMP):
    timestamp_activity_mapping = {}
    attribute_timestamp_mapping = {}

    attributes_with_positions = [
        (matching, tuple(sum(token_position_mapping["attributes_positions"][matching], ()))) for matching in
        token_position_mapping['attributes_positions'].keys()]

    unmatched_attribute_values_with_positions = [
        (matching, tuple(sum(token_position_mapping["attribute_values_positions"][matching], ()))) for matching in
        token_position_mapping['attribute_values_positions'].keys()]

    undefined_values_with_positions = [
        (matching, tuple(sum(token_position_mapping["remaining_values_positions"][matching], ()))) for matching in
        token_position_mapping['remaining_values_positions'].keys()]

    unmatched_attribute_values_with_positions += undefined_values_with_positions

    unmatched_activities_with_positions = []
    for activity in token_position_mapping['activity_positions'].keys():
        for positions in token_position_mapping['activity_positions'][activity]:
            if tuple([activity, positions]) not in unmatched_activities_with_positions:
                unmatched_activities_with_positions.append(tuple([activity, positions]))

    potential_timestamps_with_positions = []
    for ts in token_position_mapping['timestamp_positions'].keys():
        for positions in token_position_mapping['timestamp_positions'][ts]:
            if tuple([ts, positions]) not in potential_timestamps_with_positions:
                potential_timestamps_with_positions.append(tuple([ts, positions]))


    #### Try to map timestamps to attributes
    # Try direct matchings
    if len(unmatched_attribute_values_with_positions) > 0:
        # Search for timestamp in related token of attribute value
        attribute_timestamp_mapping = direct_matching_over_position(doc, attribute_timestamp_mapping, potential_timestamps_with_positions, unmatched_attribute_values_with_positions, level = 'best_match')
        for value in unmatched_attribute_values_with_positions.copy():
             if value[0] in attribute_timestamp_mapping.keys():
                 unmatched_attribute_values_with_positions.remove(value)


    # If direct matching wasn't successful, a default timestamp is assigned to every attribute value
    if len(unmatched_attribute_values_with_positions) > 0:
        for attr_val in unmatched_attribute_values_with_positions:
            attribute_timestamp_mapping[attr_val[0]] = DEFAULT_TIMESTAMP


    #### Try direct matching for activity timestamp mapping
    if len(unmatched_activities_with_positions)>0:
        timestamp_activity_mapping = direct_matching_over_position(doc, timestamp_activity_mapping,unmatched_activities_with_positions, potential_timestamps_with_positions, case = 'with_position')

        for timestamp, activities_with_positions in timestamp_activity_mapping.items():
            for ts_with_position in potential_timestamps_with_positions.copy():
                if timestamp == ts_with_position[0]:
                    if ts_with_position in potential_timestamps_with_positions:
                        potential_timestamps_with_positions.remove(ts_with_position)
            for activity_with_positions in activities_with_positions:
                if activity_with_positions in unmatched_activities_with_positions:
                    unmatched_activities_with_positions.remove(activity_with_positions)

    # Try indirect matching
    if len(unmatched_activities_with_positions)>0:
        timestamp_activity_mapping = indirect_matching_over_position(doc, timestamp_activity_mapping,unmatched_activities_with_positions, potential_timestamps_with_positions, case = 'with_position')

        for timestamp, activities_with_positions in timestamp_activity_mapping.items():
            for ts_with_position in potential_timestamps_with_positions.copy():
                if timestamp == ts_with_position[0]:
                    if ts_with_position in potential_timestamps_with_positions:
                        potential_timestamps_with_positions.remove(ts_with_position)
            for activity_with_positions in activities_with_positions:
                if activity_with_positions in unmatched_activities_with_positions:
                    unmatched_activities_with_positions.remove(activity_with_positions)


    # Refine attribute-timestamp-mapping --> If a timestamp is assigned to an activity, it cannot be assigned to an attribute
    for attr, ts in attribute_timestamp_mapping.items():
        if ts in timestamp_activity_mapping.keys():
            attribute_timestamp_mapping[attr] == DEFAULT_TIMESTAMP
        else:
            for ts_with_position in potential_timestamps_with_positions.copy():
                if ts == ts_with_position[0]:
                    if ts_with_position in potential_timestamps_with_positions:
                        potential_timestamps_with_positions.remove(ts_with_position)

    #### Try more desperate mapping of activities to timestamps if timestamp_activity_mapping is still empty

    potential_timestamps = [ts[0] for ts in potential_timestamps_with_positions]
    if len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) == 0 and len(potential_timestamps) == 0:
        dummy_timestamp = None
        dummy_activity = 'dummy_activity'
        timestamp_activity_mapping[dummy_timestamp] = [dummy_activity]

    elif len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) > 0 and len(potential_timestamps) == 0:
        for activity in unmatched_activities_with_positions.copy():
            dummy_timestamp = None
            if dummy_timestamp not in timestamp_activity_mapping.keys():
                timestamp_activity_mapping[dummy_timestamp] = []
            timestamp_activity_mapping[dummy_timestamp].append(activity)
            unmatched_activities_with_positions.remove(activity)

    elif len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) == 0 and len(potential_timestamps) == 1:
        dummy_activity = 'dummy_activity'
        timestamp_activity_mapping[potential_timestamps[0]] = [dummy_activity]
        potential_timestamps.remove(potential_timestamps[0])

    elif len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) == 1 and len(potential_timestamps) == 1:
        timestamp_activity_mapping[potential_timestamps[0]] = unmatched_activities_with_positions
        unmatched_activities_with_positions.remove(unmatched_activities_with_positions[0])
        potential_timestamps.remove(potential_timestamps[0])


    # Calculate most detailed timestamp
    if len(timestamp_activity_mapping) == 0 and len(potential_timestamps) > 1:

        most_detailed_timestamp = None
        highest_detail_level = -1

        for timestamp in potential_timestamps.copy():
            # Parse the timestamp
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue  # Skip invalid timestamps

            # Determine the detail level
            detail_level = 0
            if dt.second > 0:
                detail_level += 1  # Has seconds detail
            if dt.minute > 0:
                detail_level += 1  # Has minutes detail
            if dt.hour > 0:
                detail_level += 1  # Has hours detail
            if dt.day > 0:
                detail_level += 1  # Has day detail
            if dt.month > 0:
                detail_level += 1  # Has month detail
            if dt.year > 0:
                detail_level += 1  # Has year detail

            # Update the most detailed timestamp if this one is more detailed
            if detail_level > highest_detail_level:
                highest_detail_level = detail_level
                most_detailed_timestamp = timestamp

        if len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) == 0 and len(potential_timestamps) > 1 and most_detailed_timestamp:
            dummy_activity = 'dummy_activity'
            timestamp_activity_mapping[most_detailed_timestamp] = [dummy_activity]
            potential_timestamps.remove(most_detailed_timestamp)

        elif len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) == 1  and len(potential_timestamps) > 1 and most_detailed_timestamp:

            # Assign the most detailed timestamp to the unmatched activity
            for activity in unmatched_activities_with_positions:
                if most_detailed_timestamp not in timestamp_activity_mapping.keys():
                    timestamp_activity_mapping[most_detailed_timestamp] = []
                timestamp_activity_mapping[most_detailed_timestamp].append(activity)
                unmatched_activities_with_positions.remove(activity)
                potential_timestamps.remove(most_detailed_timestamp)


        elif len(timestamp_activity_mapping) == 0 and len(unmatched_activities_with_positions) > 1  and len(potential_timestamps) > 1 and most_detailed_timestamp:
            timestamp_activity_mapping[most_detailed_timestamp] = [unmatched_activities_with_positions[0]]
            unmatched_activities_with_positions.remove(unmatched_activities_with_positions[0])


    #### Last solution if nothing worked
    if len(timestamp_activity_mapping) == 0:
        dummy_timestamp = None
        dummy_activity = 'dummy_activity'
        timestamp_activity_mapping[dummy_timestamp] = [dummy_activity]

    # Refine attribute-timestamp-mapping --> If a timestamp is assigned to an activity, it cannot be assigned to an attribute
    for attr, ts in attribute_timestamp_mapping.items():
        if ts in timestamp_activity_mapping.keys():
            attribute_timestamp_mapping[attr] == DEFAULT_TIMESTAMP
        else:
            if ts in potential_timestamps:
                potential_timestamps.remove(ts)

    # Update related_token_mapping --> remove timestamps that have never been used
    for ts in potential_timestamps:
        if ts in token_position_mapping['timestamp_positions'].keys():
            del token_position_mapping["timestamp_positions"][ts]

    #print(f"CHECK: unmatched activities - ", unmatched_activities_with_positions)
    #print(f"CHECK: potential timestamps - ", potential_timestamps)

    return timestamp_activity_mapping, attribute_timestamp_mapping