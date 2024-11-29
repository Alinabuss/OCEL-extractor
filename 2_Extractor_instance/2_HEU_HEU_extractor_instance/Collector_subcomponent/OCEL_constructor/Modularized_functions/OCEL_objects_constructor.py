def OCEL_objects_constructor(mapping):
    objects = []

    # Create initial objects that consists of only object id and object type
    for label in mapping["object_type_mapping"].keys():
        objects.append({"id": label,
                        "type":  mapping["object_type_mapping"][label],
                        "attributes": [],
                        "relationships": []})

    # Add object attributes to objects
    for mapped_obj, attr_values in mapping['object_to_attribute_value_mapping'].items():
        for attr_val in attr_values:
            for obj in objects:
                if obj['id'] == mapped_obj:
                    attribute = {
                        "name": mapping["attribute_value_mapping"][attr_val],
                        "time": mapping["attribute_timestamp_mapping"][attr_val],
                        "value": attr_val
                    }

                    obj['attributes'].append(attribute)

    # Add O2O-relationships to objects
    for key, relationships in mapping["o2o_relationship_mapping"].items():
        for obj in objects:
            if obj["id"] == key:
                # Append relationships to the matching object
                obj["relationships"].extend(relationships)


    return objects
