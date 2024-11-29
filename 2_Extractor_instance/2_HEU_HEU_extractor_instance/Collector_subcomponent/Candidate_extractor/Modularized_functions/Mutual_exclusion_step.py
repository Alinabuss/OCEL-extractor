from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import re
import spacy

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Now you can pass this `nlp` model to your function


def remove_non_letters(items_with_positions):
    cleaned_items_with_positions = {}

    for i in items_with_positions:
        cleaned_items_with_positions[re.sub(r'[^a-zA-Z\s]', '', i)] = items_with_positions[i]

    return cleaned_items_with_positions

def remove_invalid_elements(items_with_positions):
    valid_items_with_positions = {}

    for element in items_with_positions:
        tokens = element.split()
        for token in tokens:
            # If the element does not match the invalid pattern, keep it
            if re.search(r'[A-Za-z]', token) and re.search(r'\d', token):
                pass
            else:
                valid_items_with_positions[element] = items_with_positions[element]

    return valid_items_with_positions


def filter_unacceptable_words(doc, items_with_positions, unacceptable_dicts, case = None):
    filtered_items_with_positions = {}

    # Flatten the unacceptable dicts for easy comparison
    unacceptable_positions = []
    unacceptable_words = []
    for d in unacceptable_dicts:
        for key, pos_lists in d.items():
            if key not in unacceptable_words:
                unacceptable_words.append(key)
            for pos_list in pos_lists:
                for pos in pos_list:
                    if doc[pos].dep_ not in ['prep', 'det']:
                        unacceptable_positions.append(pos)

    for item, position_lists in items_with_positions.items():
        final_position_list = []
        for position_list in position_lists:
            final_positions = []
            for position in position_list:
                if position not in unacceptable_positions:
                    if position not in final_positions:
                        final_positions.append(position)
            final_position_list.append(tuple(final_positions))

        new_name = ''
        if final_position_list != []:
            for pos in final_position_list[0]:
                if doc[pos].pos_ == 'VERB' and case == 'activity':
                    new_name += ' ' + doc[pos].lemma_
                else:
                    new_name += ' ' + doc[pos].text

        new_name = new_name.strip()
        if new_name != '' and new_name not in unacceptable_words:
            if new_name not in filtered_items_with_positions:
                filtered_items_with_positions[new_name] = []
            filtered_items_with_positions[new_name] += final_position_list

    return filtered_items_with_positions

def remove_unnecessary_prepositions_punctuals_and_adjectives(doc, items_with_positions, case = None):
    filtered_items_with_positions = {}
    unacceptable_list = ['prep', 'det', 'punct']
    unacceptable_pos = ['ADP', 'DET', 'PUNCT']


    for item, position_lists in items_with_positions.items():
        final_position_list = []
        for position_list in position_lists:
            final_positions = list(position_list)  # Convert tuple to list to allow modifications

            if case == "with_verbs":
                # Remove prepositions and determiners from the edges
                while final_positions and (doc[final_positions[0]].dep_ in unacceptable_list or doc[final_positions[0]].pos_ in unacceptable_pos or doc[final_positions[0]].pos_ == 'VERB'):
                    final_positions.pop(0)
                while final_positions and (doc[final_positions[-1]].dep_ in unacceptable_list or doc[final_positions[-1]].pos_ in unacceptable_pos or doc[final_positions[-1]].pos_ == 'VERB'):
                    final_positions.pop()

            else:
                # Remove prepositions and determiners from the edges
                while final_positions and (doc[final_positions[0]].dep_ in unacceptable_list or doc[final_positions[0]].pos_ in unacceptable_pos):
                    final_positions.pop(0)
                while final_positions and (doc[final_positions[-1]].dep_ in unacceptable_list or doc[final_positions[-1]].pos_ in unacceptable_pos):
                    final_positions.pop()

            if final_positions:  # If there are any positions left
                final_position_list.append(tuple(final_positions))

        new_name = ''
        if final_position_list != []:
            for pos in final_position_list[0]:
                if doc[pos].pos_ == 'VERB':
                    new_name += ' ' + doc[pos].lemma_
                else:
                    new_name += ' ' + doc[pos].text

        new_name = new_name.strip()
        # Re-parse the constructed text using the external NLP pipeline to exclude adjectives
        if new_name:
            parsed_new_name = nlp(new_name)  # Parse the newly constructed name
            filtered_new_name = ''
            for token in parsed_new_name:
                if token.pos_ != 'ADJ':  # Exclude adjectives
                    filtered_new_name += ' ' + token.text

            new_name = filtered_new_name.strip()

        # Add the filtered name and positions to the final dictionary
        if new_name != '':
            if new_name not in filtered_items_with_positions:
                filtered_items_with_positions[new_name] = []
            filtered_items_with_positions[new_name] += final_position_list
    return filtered_items_with_positions



def mutual_exclusion_step(doc, timestamp_texts, object_labels_with_positions, candidate_activities_with_positions, candidate_object_types_with_positions, candidate_attributes_with_positions, clear_attribute_values_with_positions, event_resources_with_positions, event_lifecylce_status_with_positions, remaining_values_with_positions):

    forbidden_words = ['event', 'action', 'activity', 'attribute', 'value', 'id', 'code', 'resource', 'lifecycle', 'object', 'process']
    forbidden_words += timestamp_texts
    forbidden_dict = {}

    for token in doc:
        if (lemmatizer.lemmatize(token.text).lower() in forbidden_words or token.text in forbidden_words) and token.dep_ not in ['prep', 'det']:
            if token.text not in forbidden_dict:
                forbidden_dict[token.text] = []
            forbidden_dict[token.text].append(tuple([token.i]))

    # Adapt object labels --> remove forbidden words and timestamps
    object_labels_with_positions = filter_unacceptable_words(doc, object_labels_with_positions, [forbidden_dict])

    # Adapt resources --> remove resource if it is timestamp, attribute, activity or object label
    event_resources_with_positions = filter_unacceptable_words(doc, event_resources_with_positions, [forbidden_dict, object_labels_with_positions, clear_attribute_values_with_positions])
    event_resources_with_positions = remove_unnecessary_prepositions_punctuals_and_adjectives(doc, event_resources_with_positions)

    # Adapt activities --> remove words from the activity that are object labels or timestamp indicators
    candidate_activities_with_positions = filter_unacceptable_words(doc, candidate_activities_with_positions, [forbidden_dict, object_labels_with_positions, clear_attribute_values_with_positions], case = 'activity')
    candidate_activities_with_positions = remove_non_letters(candidate_activities_with_positions)
    candidate_activities_with_positions = remove_unnecessary_prepositions_punctuals_and_adjectives(doc, candidate_activities_with_positions)

    # Adapt attributes --> remove attributes that are object labels, resources, activities or timestamp indicators
    candidate_attributes_with_positions = filter_unacceptable_words(doc, candidate_attributes_with_positions, [forbidden_dict, object_labels_with_positions, event_resources_with_positions, clear_attribute_values_with_positions])
    candidate_attributes_with_positions = remove_invalid_elements(candidate_attributes_with_positions)
    candidate_attributes_with_positions = remove_non_letters(candidate_attributes_with_positions)
    candidate_attributes_with_positions = remove_unnecessary_prepositions_punctuals_and_adjectives(doc, candidate_attributes_with_positions)

    # Adapt object types --> remove attributes that are object labels, resources, activities or timestamp indicators
    candidate_object_types_with_positions = filter_unacceptable_words(doc, candidate_object_types_with_positions,[forbidden_dict, object_labels_with_positions, event_resources_with_positions, clear_attribute_values_with_positions])
    candidate_object_types_with_positions = remove_invalid_elements(candidate_object_types_with_positions)
    candidate_object_types_with_positions = remove_non_letters(candidate_object_types_with_positions)
    candidate_object_types_with_positions = remove_unnecessary_prepositions_punctuals_and_adjectives(doc, candidate_object_types_with_positions)

    # Adapt clear attribute values
    clear_attribute_values_with_positions = filter_unacceptable_words(doc, clear_attribute_values_with_positions, [forbidden_dict, event_lifecylce_status_with_positions, event_resources_with_positions])
    clear_attribute_values_with_positions = remove_invalid_elements(clear_attribute_values_with_positions)

    # Adapt remaining values
    remaining_values_with_positions = filter_unacceptable_words(doc, remaining_values_with_positions, [forbidden_dict, event_lifecylce_status_with_positions, event_resources_with_positions])
    remaining_values_with_positions = remove_invalid_elements(remaining_values_with_positions)

    return object_labels_with_positions, event_resources_with_positions, candidate_activities_with_positions, candidate_object_types_with_positions, candidate_attributes_with_positions, clear_attribute_values_with_positions, remaining_values_with_positions