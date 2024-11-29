def attribute_event_type_mapper(timestamp_activity_mapping, refined_attribute_value_event_mapping, attribute_value_mapping):
    event_type_to_attribute_type_mapping = {}

    # Define a mapping from type abbreviations to full type names
    type_name_mapping = {
        'str': 'string',
        'int': 'integer',
        'float': 'float',
        'bool': 'boolean',
        # Add other types as needed
    }

    for event, attr_values in refined_attribute_value_event_mapping.items():
        for attr_value in attr_values:
            if event not in event_type_to_attribute_type_mapping.keys():
                event_type_to_attribute_type_mapping[event] = []
            if attr_value in attribute_value_mapping.keys():
                attr = attribute_value_mapping[attr_value]

                # Convert attr_value to a type for accurate detection
                try:
                    if isinstance(attr_value, str):
                        # Check if the string represents a number
                        if attr_value.strip().replace('.', '', 1).isdigit() or (
                                '.' in attr_value and attr_value.replace('.', '', 1).isdigit()):
                            # Convert to float
                            attr_value_adapted = float(attr_value)
                        else:
                            attr_value_adapted = attr_value

                    else:
                        attr_value_adapted = attr_value
                except ValueError:
                    attr_value_adapted = attr_value

                # Determine the full type name
                attr_type_abr = type(attr_value_adapted).__name__
                attr_type = 'int' if isinstance(attr_value_adapted, int) else \
                    'float' if isinstance(attr_value_adapted, float) else \
                        'string' if isinstance(attr_value_adapted, str) else \
                            type_name_mapping.get(attr_type_abr, attr_type_abr)

                event_type_to_attribute_type_mapping[event].append({attr: attr_type})

    for timestamp, activities in timestamp_activity_mapping.items():
        for activity in activities:
            if activity not in event_type_to_attribute_type_mapping.keys():
                event_type_to_attribute_type_mapping[activity] = []

    return event_type_to_attribute_type_mapping
