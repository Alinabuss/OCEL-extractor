import json

filepath = "final_event_log.json"
filter_obj = "forensic_report_june_2018"

with open(filepath, 'r') as file:
    ocel = json.load(file)

correct_events = []

for event in ocel['events']:
    for rel in event['relationships']:
        if rel['objectId'] == filter_obj:
            correct_events.append(event)

ocel['events'] = correct_events

# Save the filtered OCEL log
filtered_file_path = "filtered_event_log.json"

with open(filtered_file_path, "w") as f:
    json.dump(ocel, f, indent=4)

print(f"Filtered OCEL log saved to {filtered_file_path}")


