def OCEL_object_types_constructor(mapping):

    # Define object types with attributes
    object_types = []
    for obj_type, attributes in mapping["object_type_to_attribute_type"].items():
        formatted_attributes = [
            {
                "name": attr_name,
                "type": attr_type
            }
            for attr_dict in attributes
            for attr_name, attr_type in attr_dict.items()
        ]
        object_types.append({
            "name": obj_type,
            "attributes": formatted_attributes
        })

    return object_types