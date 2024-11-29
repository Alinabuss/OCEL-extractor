def attribute_object_type_mapper(object_type_mapping, object_to_attribute_value_mapping, attribute_value_mapping):

    # Define a mapping from type abbreviations to full type names
    type_name_mapping = {
        'str': 'string',
        'int': 'integer',
        'float': 'float',
        'bool': 'boolean',
        # Add other types as needed
    }
    object_type_to_attribute_type = {}

    # Initialize attribute_object_type_dict with object types as keys
    for obj_type in set(object_type_mapping.values()):
        object_type_to_attribute_type[obj_type] = []

    # Iterate over attribute_value_object_mapping to map object instances to attributes
    for obj_instance, attr_values in object_to_attribute_value_mapping.items():
        for attr_value in attr_values:
            if obj_instance in object_type_mapping.keys():
                obj_type = object_type_mapping[obj_instance]

                # Ensure that the obj_type is in the attribute_object_type_dict
                if obj_type not in object_type_to_attribute_type:
                    object_type_to_attribute_type[obj_type] = []

                if attr_value in attribute_value_mapping:
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

                    # Add a new sub-dict with the attribute name and full type
                    object_type_to_attribute_type[obj_type].append({attr: attr_type})

    return object_type_to_attribute_type