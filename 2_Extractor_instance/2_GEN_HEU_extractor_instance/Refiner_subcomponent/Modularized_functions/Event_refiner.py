from collections import defaultdict, Counter
from datetime import datetime

def remove_dummy_events(log):

    correct_events = []
    for event in log['events']:
        if event['type'] != 'dummy_activity':
            correct_events.append(event)

    log['events'] = correct_events

    return log

def remove_events_without_timestamp(log):

    correct_events = []

    for event in log['events']:
        try:
            # Try to parse the timestamp and check if it's in the correct format
            datetime.strptime(event['time'], '%Y-%m-%dT%H:%M:%SZ')
            correct_events.append(event)
        except (ValueError, KeyError):
            # If parsing fails or 'time' is not present, skip the event
            continue

    log['events'] = correct_events
    return log

def remove_non_found_object_instances_from_relations(log):
    # Iterate over each event in the log
    for event in log['events']:
        # Extract relationships from the event
        relationships = event.get('relationships', [])

        # Filter out relationships where objectId is 'Object_instance_not_found'
        event['relationships'] = [rel for rel in relationships if rel.get('objectId') != 'object_instance_not_found']

    return log

def remove_events_without_relationships(log):

    correct_events = []
    for event in log['events']:
        relationships = event.get('relationships', [])
        if relationships == []:
            pass
        else:
            correct_events.append(event)

    log['events']= correct_events

    return log

def remove_event_without_timestamp(log):

    correct_events = []
    for event in log['events']:
        if event['time'] != None:
            correct_events.append(event)

    log['events'] = correct_events



    return log

def remove_event_attributes_that_only_appear_once(log):
    attribute_counter = Counter()

    # First pass: Count occurrences of each attribute name
    for event in log['events']:
        if 'attributes' in event:
            for attr in event['attributes']:
                attribute_counter[attr['name']] += 1

    # Second pass: Remove attributes that only appear once and replace them
    for event in log['events']:
        if 'attributes' in event:
            # Filter attributes to keep only those that appear more than once
            event['attributes'] = [
                attr if attribute_counter[attr['name']] > 1 else {'name': 'attribute_type_not_identified',
                                                                  'value': attr['value']}
                for attr in event['attributes']
            ]

    # Update object types to reflect changes
    for event_type in log['eventTypes']:
        if 'attributes' in event_type:
            event_type['attributes'] = [
                attr for attr in event_type['attributes'] if attribute_counter[attr['name']] > 1
            ]

    # Return the refined log
    return log

def fix_lifecycle_and_resources_attributes(log):
    lifecycle_count_per_event_type = defaultdict(Counter)
    resource_count_per_event_type = defaultdict(Counter)

    for event in log['events']:
        event_type = event["type"]

        # Filter for attributes with the name 'lifecycle' and 'resource'
        lifecycle_values = [attr["value"] for attr in event.get("attributes", []) if attr["name"] == "lifecycle"]
        resource_values = [attr["value"] for attr in event.get("attributes", []) if attr["name"] == "resource"]

        for lifecycle_value in lifecycle_values:
            lifecycle_count_per_event_type[event_type][lifecycle_value] += 1

        for resource_value in resource_values:
            resource_count_per_event_type[event_type][resource_value] += 1

    for event in log['events']:
        event_type = event["type"]
        resources = []
        lifecycle_status = []

        if 'attributes' in event:
            resource_values = []
            lifecycle_values = []
            other_attributes = []

            for attr in event['attributes']:
                if attr['name'] == 'resource':
                    resource_values.append(attr['value'])
                elif attr['name'] == 'lifecycle':
                    lifecycle_values.append(attr['value'])
                else:
                    other_attributes.append(attr)

            # Determine the most popular lifecycle value for the event type
            if lifecycle_values:
                most_popular_lifecycle = max(
                    lifecycle_values,
                    key=lambda val: lifecycle_count_per_event_type[event_type][val]
                )
                lifecycle_status = [most_popular_lifecycle]

            # Determine the most popular resource value for the event type
            if resource_values:
                most_popular_resource = max(
                    resource_values,
                    key=lambda val: resource_count_per_event_type[event_type][val]
                )
                resources = [most_popular_resource]

        event['attributes'] = other_attributes
        event['attributes'].extend([
            {'name': 'lifecycle', 'value': val} for val in lifecycle_status
        ])
        event['attributes'].extend([
            {'name': 'resource', 'value': val} for val in resources
        ])

    return log



def merge_events_at_same_timestamp(log):
    # Dictionary to group events by their timestamp
    events_by_timestamp = defaultdict(list)

    # Group events by their timestamp
    for event in log['events']:
        events_by_timestamp[event['time']].append(event)

    # Calculate the frequency of each type across the whole log
    type_counter = Counter(event['type'] for event in log['events'])

    merged_events = []

    for timestamp, events in events_by_timestamp.items():
        # Case 1: If time and type are identical, merge attributes and relationships
        unique_events = {}
        for event in events:
            key = (event['type'], tuple(sorted([rel['objectId'] for rel in event['relationships']])))
            if key not in unique_events:
                unique_events[key] = event
            else:
                # Merge attributes and relationships
                unique_events[key]['attributes'].extend(event['attributes'])
                unique_events[key]['relationships'].extend(event['relationships'])

        # Case 2: If time equal, relationships equal, but type different
        grouped_by_relationships = defaultdict(list)
        for event in unique_events.values():
            rel_key = tuple(sorted([rel['objectId'] for rel in event['relationships']]))
            grouped_by_relationships[rel_key].append(event)

        for rel_key, grouped_events in grouped_by_relationships.items():
            if len(grouped_events) > 1:
                # Find the most popular type in the group
                most_popular_event = max(grouped_events, key=lambda e: type_counter[e['type']])

                # Merge attributes from all events in the group to the most popular one
                for event in grouped_events:
                    if event != most_popular_event:
                        most_popular_event['attributes'].extend(event['attributes'])

                merged_events.append(most_popular_event)
            else:
                merged_events.append(grouped_events[0])

    # Update the log with merged events
    log['events'] = merged_events

    return log


def event_refiner(log):

    log = remove_dummy_events(log)
    log = remove_events_without_timestamp(log)
    log = remove_non_found_object_instances_from_relations(log)
    log = remove_events_without_relationships(log)
    log = remove_event_without_timestamp(log)
    log = fix_lifecycle_and_resources_attributes(log)
    log = merge_events_at_same_timestamp(log)

    return log