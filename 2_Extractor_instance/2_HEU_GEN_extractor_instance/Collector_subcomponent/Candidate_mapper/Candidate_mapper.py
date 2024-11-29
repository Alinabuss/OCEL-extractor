from Collector_subcomponent.Candidate_mapper.Modularized_functions.Attribute_value_mapper import attribute_value_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Attribute_value_object_event_mapper import attribute_value_object_event_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Attribute_object_type_mapper import attribute_object_type_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Timestamp_to_activity_and_attribute_mapper import timestamp_activty_attribute_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.O2O_Relationship_mapper import o2o_relationship_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.E2O_Relationship_mapper import e2o_relationship_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Attribute_event_type_mapper import attribute_event_type_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Object_label_type_mapper import object_label_type_mapper
from Collector_subcomponent.Candidate_mapper.Modularized_functions.Undefined_values_handler import undefined_values_handler

def candidate_mapper(doc, token_position_mapping, DEFAULT_TIMESTAMP, printing = False):
    token_position_mapping = undefined_values_handler(doc, token_position_mapping)
    object_type_mapping, token_position_mapping = object_label_type_mapper(doc, token_position_mapping)
    attribute_value_mapping, token_position_mapping = attribute_value_mapper(doc, token_position_mapping)
    o2o_relationship_mapping = o2o_relationship_mapper(doc,object_type_mapping, token_position_mapping)
    timestamp_activity_mapping, attribute_timestamp_mapping = timestamp_activty_attribute_mapper(doc, token_position_mapping, DEFAULT_TIMESTAMP)
    e2o_relationship_mapping, timestamp_activity_mapping = e2o_relationship_mapper(doc, timestamp_activity_mapping, token_position_mapping)
    object_to_attribute_value_mapping, event_to_attribute_value_mapping = attribute_value_object_event_mapper(doc, token_position_mapping, object_type_mapping,timestamp_activity_mapping)
    object_type_to_attribute_type = attribute_object_type_mapper(object_type_mapping, object_to_attribute_value_mapping,attribute_value_mapping)
    event_type_to_attribute_type_mapping = attribute_event_type_mapper(timestamp_activity_mapping, event_to_attribute_value_mapping, attribute_value_mapping)

    mapping = {
        "timestamp_activity_mapping" : timestamp_activity_mapping,
        "e2o_relationship_mapping" : e2o_relationship_mapping,
        "object_type_mapping" : object_type_mapping,
        "object_type_to_attribute_type" : object_type_to_attribute_type,
        "object_to_attribute_value_mapping" : object_to_attribute_value_mapping,
        "attribute_value_mapping" : attribute_value_mapping,
        "attribute_timestamp_mapping" : attribute_timestamp_mapping,
        "o2o_relationship_mapping": o2o_relationship_mapping,
        "event_to_attribute_value_mapping": event_to_attribute_value_mapping,
        "event_type_to_attribute_type_mapping" : event_type_to_attribute_type_mapping
    }

    if printing:
         for key, value in mapping.items():
            print(f"{key} : {value}")

         print()

    return mapping
