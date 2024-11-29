from Collector_subcomponent.Candidate_mapper.Modularized_functions.Helper_functions import direct_matching_over_position


def e2o_relationship_mapper(doc, timestamp_activity_mapping, token_position_mapping):
    e2o_relationship_mappings = {}
    o2e_relationship_mappings = {}

    potential_activities_with_positions = []
    activity_timestamp_mapping = {}
    for ts, activities in timestamp_activity_mapping.items():
        for activity in activities:
            activity_timestamp_mapping[activity] = ts
            if activity not in potential_activities_with_positions and activity != "dummy_activity":
                potential_activities_with_positions.append(activity)

    unmatched_objects_with_positions = [(matching, tuple(sum(token_position_mapping["object_labels_positions"][matching], ()))) for matching in token_position_mapping['object_labels_positions'].keys()]

    #### Try direct matching
    if len(unmatched_objects_with_positions)>0:
        o2e_relationship_mappings = direct_matching_over_position(doc, o2e_relationship_mappings, potential_activities_with_positions, unmatched_objects_with_positions, case = 'with_position')

        for object, activities in o2e_relationship_mappings.items():
            for obj_with_positions in unmatched_objects_with_positions.copy():
                if obj_with_positions[0] == object:
                    if obj_with_positions in unmatched_objects_with_positions:
                        unmatched_objects_with_positions.remove(obj_with_positions)

    #### Match objects by position if not still part of undefined values
    for obj in unmatched_objects_with_positions.copy():
        if obj[0] in token_position_mapping['remaining_values_positions'].keys():
            unmatched_objects_with_positions.remove(obj)

    if unmatched_objects_with_positions and potential_activities_with_positions:

        for obj, obj_positions in unmatched_objects_with_positions:
            last_activity = None
            min_activity_distance = float('inf')

            # Find the closest object before the attribute
            for activity, positions in potential_activities_with_positions:
                if max(positions) < min(obj_positions):
                    distance = min(obj_positions) - max(positions)
                    if distance < min_activity_distance:
                        min_activity_distance = distance
                        last_activity = activity
                        last_activity_positions = positions


            # Map the attribute to the closest acceptable object
            if last_activity:
                if (last_activity, last_activity_positions) not in e2o_relationship_mappings:
                    e2o_relationship_mappings[(last_activity, last_activity_positions)] = []
                e2o_relationship_mappings[(last_activity, last_activity_positions)].append(obj)

    for object, activities in o2e_relationship_mappings.items():
        for activity in activities:
            if activity not in e2o_relationship_mappings:
                e2o_relationship_mappings[activity] = []
            e2o_relationship_mappings[activity].append(object)

    return e2o_relationship_mappings, timestamp_activity_mapping