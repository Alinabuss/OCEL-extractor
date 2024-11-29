from Collector_subcomponent.Candidate_extractor.Modularized_functions.Timestamp_extractor import timestamp_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Activity_extractor import candidate_activity_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Candidate_value_extractor import candidate_value_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Candidate_attributes_extractor import candidate_attributes_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Candidate_object_type_extractor import candidate_object_type_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Event_resources_extractor import event_resources_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Event_lifecycle_status_extractor import event_lifecycle_status_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Mutual_exclusion_step import mutual_exclusion_step
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Token_position_extractor import token_position_extractor
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Value_differentiator import value_differentiator

def candidate_extractor(doc, text, DEFAULT_TIMESTAMP, printing = False):

    # Extract different components of OCEL2.0 log
    timestamps, timestamps_to_text, timestamp_texts, timestamps_to_positions = timestamp_extractor(doc, text, DEFAULT_TIMESTAMP)
    candidate_activities_with_positions = candidate_activity_extractor(doc)
    candidate_object_types_with_positions = candidate_object_type_extractor(doc, text)
    candidate_attributes_with_positions = candidate_attributes_extractor(doc, text)
    candidate_values_with_positions = candidate_value_extractor(doc, text)
    event_resources_with_positions = event_resources_extractor(doc)
    event_lifecylce_status_with_positions = event_lifecycle_status_extractor(doc, candidate_activities_with_positions)
    object_labels_with_positions, clear_attribute_values_with_positions, remaining_values_with_positions = value_differentiator(doc, candidate_values_with_positions)


    if printing:
        print("Extracted values: ")
        print("Extracted timestamps: ", timestamps_to_positions)
        print("Timestamp_texts: ", timestamp_texts)
        print("Extracted candidate activities: ", candidate_activities_with_positions)
        print("Extracted candidate object types: ", candidate_object_types_with_positions)
        print("Extracted candidate attributes: ", candidate_attributes_with_positions)
        print("Extracted candidate attribute values: ", candidate_values_with_positions)
        print("Extracted event resources: ", event_resources_with_positions)
        print("Extracted lifecycle status: ", event_lifecylce_status_with_positions)
        print("Differentiation of values")
        print("Object labels: ", object_labels_with_positions)
        print("Attribute values: ", clear_attribute_values_with_positions)
        print("Undefined values: ", remaining_values_with_positions)
        print()

    # Adapt extracted values and refine their position mapping
    object_labels_with_positions, event_resources_with_positions, candidate_activities_with_positions, candidate_object_types_with_positions, candidate_attributes_with_positions, clear_attribute_values_with_positions, remaining_values_with_positions = mutual_exclusion_step(
            doc, timestamp_texts, object_labels_with_positions, candidate_activities_with_positions,
            candidate_object_types_with_positions, candidate_attributes_with_positions,
            clear_attribute_values_with_positions, event_resources_with_positions,
            event_lifecylce_status_with_positions, remaining_values_with_positions)
    token_position_mapping = token_position_extractor(doc, timestamps_to_text, timestamps_to_positions,
                                                          event_resources_with_positions, object_labels_with_positions,
                                                          candidate_activities_with_positions,
                                                          candidate_object_types_with_positions,
                                                          candidate_attributes_with_positions,
                                                          clear_attribute_values_with_positions,
                                                          event_lifecylce_status_with_positions,
                                                          remaining_values_with_positions)

    if printing:
        print("Adapted values: ")
        print("Timestamps: ", timestamps_to_positions)
        print("Adapted activities: ", candidate_activities_with_positions)
        print("Adapted object types: ", candidate_object_types_with_positions)
        print("Object labels: ", object_labels_with_positions)
        print("Adapted attributes: ", candidate_attributes_with_positions)
        print("Clear attribute values: ", clear_attribute_values_with_positions)
        print("Adapted resources: ", event_resources_with_positions)
        print("Lifecycle status: ", event_lifecylce_status_with_positions)
        print("Undefined values: ", remaining_values_with_positions)
        print("Token position mapping: ", token_position_mapping)
        print()

    return token_position_mapping
