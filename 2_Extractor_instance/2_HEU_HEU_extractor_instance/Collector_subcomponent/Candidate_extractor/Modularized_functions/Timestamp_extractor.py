from collections import defaultdict
from datetime import datetime
from dateutil.parser import parse as parse_date
from dateparser.search import search_dates


def timestamp_extractor(doc, text, DEFAULT_TIMESTAMP):
    # Initialize variables to hold extracted information
    ent_dates = []
    ent_times = []
    timestamps = []
    timestamps_to_text = {}
    timestamps_to_positions = {}
    timestamp_texts = []

    # Extract named entities and their positions
    for ent in doc.ents:
        if ent.label_ == "DATE":
            ent_dates.append((ent.text, list(range(ent.start, ent.end))))  # Append (text, position)
        elif ent.label_ == "TIME":
            ent_times.append((ent.text, list(range(ent.start, ent.end))))  # Append (text, position)

    # Add numeric values to ent_times
    for token in doc:
        if token.pos_ == 'NUM':
            ent_times.append((token.text, [token.i]))  # Append (text, position)

    # Get today's date in ISO format
    today_iso = datetime.today().strftime("%Y-%m-%d")
    default_date = DEFAULT_TIMESTAMP[:10]

    # Convert extracted DATEs into ISO-format with positions
    ent_iso_dates = []
    date_to_text = {}
    for date_str, pos in ent_dates:
        try:
            datetime_obj = parse_date(date_str)
            if isinstance(datetime_obj, tuple):
                datetime_obj = datetime_obj[0]
            iso_date_str = datetime_obj.strftime("%Y-%m-%d")

            # Ensure the date is not today's date
            if iso_date_str != today_iso and iso_date_str != default_date:
                date_to_text[iso_date_str] = date_str
                ent_iso_dates.append((iso_date_str, pos))  # Store date with position
        except ValueError:
            pass


    # Convert extracted TIMEs into ISO-format with positions
    ent_iso_times = []
    for time_str, pos in ent_times:
        try:
            datetime_obj = parse_date(time_str)
            if isinstance(datetime_obj, tuple):
                datetime_obj = datetime_obj[0]
            iso_time_str = datetime_obj.strftime("%H:%M:%S")

            # Ensure the time is not equal to "00:00:00"
            if iso_time_str != "00:00:00":
                ent_iso_times.append((iso_time_str, pos))  # Store time with position
        except ValueError:
            pass


    # Merging dates and times based on positions
    if len(ent_iso_dates) == 1:
        # Only one date: merge all times with this date
        date_str, date_positions = ent_iso_dates[0]
        for time_str, time_positions in ent_iso_times:
            # Get the TIME text and the previous token
            prev_token_pos = [time_positions[0] - 1] if time_positions[0] > 0 else []
            time_text = f"{doc[time_positions[0] - 1].text} {doc[time_positions[0]].text}" if time_positions[0] > 0 else \
            doc[time_positions[0]].text
            combined_text = f"{time_text}"  # Combine DATE and TIME text
            ent_timestamp = f"{date_str}T{time_str}Z"
            timestamps.append(ent_timestamp)
            timestamps_to_text[ent_timestamp] = combined_text
            timestamp_texts.extend(combined_text.split())

            # Store positions in timestamps_to_positions as tuples
            all_positions = list(set(prev_token_pos + time_positions))
            timestamps_to_positions[ent_timestamp] = [tuple(all_positions)]  # Store as a tuple in a list

    else:
        # Multiple dates: merge each time with the closest preceding date
        ent_iso_dates = sorted(ent_iso_dates, key=lambda x: x[1][0])  # Sort dates by first position
        ent_iso_times = sorted(ent_iso_times, key=lambda x: x[1][0])  # Sort times by first position

        for time_str, time_positions in ent_iso_times:
            # Find the closest preceding date or the closest overall if no preceding date
            closest_date = None
            closest_distance = float('inf')
            for date_str, date_positions in ent_iso_dates:
                if date_positions[0] <= time_positions[0] and (
                        time_positions[0] - date_positions[0]) < closest_distance:
                    closest_date = date_str
                    closest_distance = time_positions[0] - date_positions[0]
                elif date_positions[0] > time_positions[0] and (
                        date_positions[0] - time_positions[0]) < closest_distance:
                    closest_date = date_str
                    closest_distance = date_positions[0] - time_positions[0]

            if closest_date:
                # Get the TIME text and the previous token
                prev_token_pos = [time_positions[0] - 1] if time_positions[0] > 0 else []
                time_text = f"{doc[time_positions[0] - 1].text} {doc[time_positions[0]].text}" if time_positions[
                                                                                                      0] > 0 else doc[
                    time_positions[0]].text
                combined_text = f"{time_text}"  # Combine DATE and TIME text
                ent_timestamp = f"{closest_date}T{time_str}Z"
                timestamps.append(ent_timestamp)
                timestamps_to_text[ent_timestamp] = combined_text
                timestamp_texts.extend(combined_text.split())

                # Store positions in timestamps_to_positions as tuples
                all_positions = list(set(prev_token_pos + time_positions))
                timestamps_to_positions[ent_timestamp] = [tuple(all_positions)]  # Store as a tuple in a list

    # Run dateparser for results
    dateparser_results = search_dates(text)

    # Convert dateparser results to ISO-format timestamps
    dateparser_iso_timestamps = []
    if dateparser_results:
        for result in dateparser_results:
            dt = result[1]  # Extract the datetime object
            timestamp_texts.append(result[0])
            if isinstance(dt, datetime):
                # Convert to ISO format
                iso_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                dateparser_iso_timestamps.append(iso_timestamp)
                timestamps_to_text[iso_timestamp] = result[0]
                # Positions for these timestamps will be found in position extractor
                if iso_timestamp not in timestamps_to_positions:
                    timestamps_to_positions[iso_timestamp] = []

    # Filter dateparser_iso_timestamps by matching dates in ent_iso_dates
    corrected_timestamps = []
    for iso_timestamp in dateparser_iso_timestamps:
        timestamp_date = iso_timestamp.split('T')[0]
        timestamp_time = iso_timestamp.split('T')[1]
        if timestamp_date in [date[0] for date in ent_iso_dates]:
            corrected_timestamps.append(iso_timestamp)
        else:
            # Find the closest preceding DATE
            closest_date = None
            closest_distance = float('inf')
            for date_str, date_pos in ent_iso_dates:
                date_text = date_to_text[date_str]  # Correct DATE from ent_dates
                date_idx = text.find(date_text)
                if date_idx == -1:
                    continue

                if date_idx <= text.find(timestamp_time) and (
                        text.find(timestamp_time) - date_idx) < closest_distance:
                    closest_date = date_str
                    closest_distance = text.find(timestamp_time) - date_idx
                elif date_idx > text.find(timestamp_time) and (
                        date_idx - text.find(timestamp_time)) < closest_distance:
                    closest_date = date_str
                    closest_distance = date_idx - text.find(timestamp_time)

            if closest_date:
                corrected_timestamp = f"{closest_date}T{timestamp_time}"
                corrected_timestamps.append(corrected_timestamp)
                if iso_timestamp in timestamps_to_text:
                    timestamps_to_text[corrected_timestamp] = timestamps_to_text[iso_timestamp]
                    del timestamps_to_text[iso_timestamp]

    timestamps += corrected_timestamps

    # Add dates from ent_iso_dates that are not in dateparser_iso_timestamps with a dummy time
    if len(timestamps) == 0:
        dummy_time_str = "00:00:00Z"
        for date in ent_iso_dates:
            available_dates = [ts.split('T')[0] for ts, _ in timestamps_to_positions.items()]
            if str(date[0]) not in available_dates:
                dummy_timestamp = f"{date[0]}T{dummy_time_str}"
                timestamps.append(dummy_timestamp)
                timestamps_to_positions[dummy_timestamp] = []
                timestamps_to_text[dummy_timestamp] = ''

    # Grouping timestamps by date part
    grouped_timestamps = defaultdict(list)
    for ts in timestamps:
        date_part = ts.split('T')[0]
        grouped_timestamps[date_part].append(ts)

    # Remove timestamps with time = 00:00:00Z if another timestamp with a specific time exists for the same date
    final_timestamps = []
    for date, ts_list in grouped_timestamps.items():
        has_specific_time = any(ts.split('T')[1] != "00:00:00Z" for ts in ts_list)
        if has_specific_time:
            final_timestamps.extend(ts for ts in ts_list if ts.split('T')[1] != "00:00:00Z")
        else:
            final_timestamps.extend(ts_list)

    # Removing unwanted default or empty timestamps
    if DEFAULT_TIMESTAMP in final_timestamps:
        final_timestamps.remove(DEFAULT_TIMESTAMP)

    if '0001-01-01T00:00:00Z' in final_timestamps:
        final_timestamps.remove('0001-01-01T00:00:00Z')

    # Final mapping of timestamps to text
    final_timestamps_to_text = {}
    for timestamp in final_timestamps:
        if timestamp in timestamps_to_text:
            final_timestamps_to_text[timestamp] = timestamps_to_text[timestamp]
        else:
            reduced_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%SZ")
            reduced_mapping = {}
            for ts in timestamps_to_text.keys():
                reduced_ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%SZ")
                reduced_mapping[reduced_ts] = timestamps_to_text[ts]
            if reduced_timestamp in reduced_mapping and reduced_timestamp != '00:00:00Z':
                final_timestamps_to_text[timestamp] = reduced_mapping[reduced_timestamp]
            else:
                final_timestamps_to_text[timestamp] = ''

    final_timestamps_to_positions = {}
    for ts, positions in timestamps_to_positions.items():
        if ts in final_timestamps:
            if ts not in final_timestamps_to_positions:
                final_timestamps_to_positions[ts] = []
            for pos in positions:
                if pos not in final_timestamps_to_positions[ts]:
                    final_timestamps_to_positions[ts].append(pos)

    # Consolidate timestamp_texts to remove duplicates
    final_timestamp_texts = []
    for item in timestamp_texts:
        words = [word for word in item.split()]
        for word in words:
            word = word.rstrip(',.')
            if word not in final_timestamp_texts:
                final_timestamp_texts.append(word)

    # print(f"CHECK - NER results: Dates : {ent_dates},  Times: {ent_times}")
    # print(f"CHECK - ISO NER results: Dates : {ent_iso_dates},  Times: {ent_iso_times}")
    # print(f"CHECK - TIMESTAMPS - Dateparser-results: {dateparser_results}")
    # print(f"CHECK: final timestamps - {final_timestamps}")
    # print(f"CHECK: timestamps_to_text - {final_timestamps_to_text}")
    # print(f"CHECK: timestamp_texts - {final_timestamp_texts}")
    # print(f"CHECK: timestamps_to_positions - {final_timestamps_to_positions}")

    return final_timestamps, final_timestamps_to_text, final_timestamp_texts, final_timestamps_to_positions

