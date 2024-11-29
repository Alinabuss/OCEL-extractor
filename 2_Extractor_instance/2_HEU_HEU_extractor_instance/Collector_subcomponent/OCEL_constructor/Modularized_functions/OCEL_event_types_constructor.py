def OCEL_event_types_constructor(mapping):
    # Define event types with event attribute types
    event_types = []

    for event_type, attributes in mapping["event_type_to_attribute_type_mapping"].items():
        if attributes != []:
            formatted_attributes = [
                {
                    "name": attr_name,
                    "type": attr_type
                }
                for attr_dict in attributes
                for attr_name, attr_type in attr_dict.items()
            ]
            event_types.append({
                "name": event_type[0],
                "attributes": formatted_attributes
            })
        else:
            event_types.append({
                "name": event_type[0],
                "attributes": []
            })

    return event_types