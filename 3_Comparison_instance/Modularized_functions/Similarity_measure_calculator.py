import pm4py
from sklearn.metrics.pairwise import cosine_similarity
from nltk.metrics import edit_distance
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec
import pandas as pd

lemmatizer = WordNetLemmatizer()

extractors = {
    "object_type": lambda log, mapping: [obj_type['name'] for obj_type in log["objectTypes"] if obj_type['name'] != "Object_type_not_identified"],
    "object_instance": lambda log, mapping: [obj['id'] for obj in log['objects'] if obj['id']!='Object_instance_not_found'],
    "event_type": lambda log, mapping: [event_type['name'] for event_type in log['eventTypes'] if event_type['name']!="dummyactivity"],
    "event_instance": lambda log, mapping: [f"{event['time']}, {event['type']}" for event in log['events'] if event['type']!="dummyactivity"],
    "object_type_attribute_type": lambda log, mapping: [f"""{obj_type['name']}, {[attr["name"] for attr in obj_type.get('attributes', []) if attr["name"] != "attribute_type_not_identified"]}""" for obj_type in log["objectTypes"] if obj_type['name'] != "Object_type_not_identified"],
    "object_instance_object_type": lambda log, mapping: [f"{obj['id']} ,{obj['type']}" for obj in log["objects"] if obj['id']!='Object_instance_not_found' and obj['type']!="Object_type_not_identified"],
    "object_instance_attribute_type": lambda log, mapping: [f"""{obj['id']}, {[attr["name"] for attr in obj.get('attributes', []) if attr['name'] != 'attribute_type_not_identified']}""" for obj in log["objects"] if obj['id'] != 'Object_instance_not_found'],
    "object_instance_attribute_value": lambda log, mapping: [f"{obj['id']}, {[attr['value'] for attr in obj.get('attributes', [])]}" for obj in log["objects"] if obj['id']!='Object_instance_not_found'],
    "object_to_object": lambda log, mapping: [f"{obj['id']}, {[rel['objectId'] for rel in obj.get('relationships', [])]}" for obj in log["objects"] if obj['id']!='Object_instance_not_found'],
    "event_type_attribute_type": lambda log, mapping: [f"""{event_type["name"]}, {[attr['name'] for attr in event_type['attributes']]}""" for event_type in log['eventTypes'] if event_type['name'] != "dummyactivity"],
    "event_instance_attribute_type": lambda log, mapping: [f"""{event["time"]}, {event["type"]}, {[attr['name'] for attr in event.get('attributes', []) if attr['name'] != 'attribute_type_not_identified']}""" for event in log['events'] if event['type'] != "dummyactivity"],
    "event_instance_attribute_value": lambda log, mapping: [f"""{event["time"]}, {event["type"]}, {[attr['value'] for attr in event.get('attributes', [])]}""" for event in log['events'] if event['type'] != "dummyactivity"],
    "event_to_object": lambda log, mapping: [f"""{event["time"]},{event["type"]},{[rel['objectId'] for rel in event['relationships']]}""" for event in log['events'] if event['type']!="dummyactivity"],
    "object_type_attribute_type_rel": lambda log, mapping: [f"""{obj_type['name']}, {[attr["name"] for attr in obj_type.get('attributes', []) if attr["name"] != "attribute_type_not_identified"]}""" for obj_type in log["objectTypes"] if obj_type['name'] in mapping.keys() or obj_type['name'] in mapping.values()],
    "object_instance_object_type_rel": lambda log, mapping: [f"{obj['id']} ,{obj['type']}" for obj in log["objects"] if obj['id']!='Object_instance_not_found' and obj['type']!="Object_type_not_identified" and (obj['id'] in mapping.keys() or obj['id'] in mapping.values())],
    "object_instance_attribute_type_rel": lambda log, mapping: [f"{obj['id']}, {[attr['name'] for attr in obj.get('attributes', []) if attr['name'] != 'attribute_type_not_identified']}" for obj in log["objects"] if obj['id'] in mapping.keys() or obj['id'] in mapping.values()],
    "object_instance_attribute_value_rel": lambda log, mapping: [f"{obj['id']}, {[attr['value'] for attr in obj.get('attributes', [])]}" for obj in log["objects"] if obj['id'] in mapping.keys() or obj['id'] in mapping.values()],
    "object_to_object_rel": lambda log, mapping: [f"{obj['id']}, {[rel['objectId'] for rel in obj.get('relationships', [])]}" for obj in log["objects"] if obj['id'] in mapping.keys() or obj['id'] in mapping.values()],
    "event_type_attribute_type_rel": lambda log, mapping: [f"""{event_type["name"]}, {[attr['name'] for attr in event_type['attributes'] if attr['name'] != 'attribute_type_not_identified']}""" for event_type in log['eventTypes'] if event_type['name'] in mapping.keys() or event_type['name'] in mapping.values()],
    "event_instance_attribute_type_rel": lambda log, mapping: [f"""{event["time"]}, {event["type"]}, {[attr['name'] for attr in event.get('attributes', []) if attr['name'] != 'attribute_type_not_identified']}""" for event in log['events'] if(event['time'], event['type']) in mapping.keys() or (event['time'], event['type']) in mapping.values()],
    "event_instance_attribute_value_rel": lambda log, mapping: [f"""{event["time"]}, {event["type"]}, {[attr['value'] for attr in event.get('attributes', [])]}""" for event in log['events'] if (event['time'], event['type']) in mapping.keys() or (event['time'], event['type']) in mapping.values()],
    "event_to_object_rel": lambda log, mapping: [f"""{event["time"]},{event["type"]},{[rel['objectId'] for rel in event['relationships']]}""" for event in log['events'] if (event['time'], event['type']) in mapping.keys() or (event['time'], event['type']) in mapping.values()]
}


def similarity_measure_calculator(original_log, extracted_log, level, mapping = None):

    original_list = extractors[level](original_log, mapping)
    extracted_list = extractors[level](extracted_log, mapping)

    # Convert all words to lowercase and lemmatize
    original_list = [lemmatizer.lemmatize(word.lower()) for word in original_list]
    extracted_list = [lemmatizer.lemmatize(word.lower()) for word in extracted_list]

    #print(f"Level: {level}")
    #print(original_list)
    #print(extracted_list)
    #print()

    # Check if either list is empty and handle it accordingly
    if not original_list or not extracted_list:
        # Create the similarity dictionary
        similarity_dict = {
            "avg_cosine_sim": '/',
            "avg_lev_dist": '/'
        }
        # Return a default similarity dictionary
        return similarity_dict

    #### Calculate cosine similarity

    # Train a Word2Vec model on the concatenated lists
    word2vec_model = Word2Vec(sentences=[original_list, extracted_list], vector_size=100, window=5, min_count=1,
                              workers=4)

    # Calculate cosine similarity
    total_cosine_similarities = []

    for extracted_word in extracted_list:
        if extracted_word in word2vec_model.wv:
            cosine_similarities = []
            for original_word in original_list:
                if original_word in word2vec_model.wv:
                    cosine_similarity_score = cosine_similarity(
                        word2vec_model.wv[extracted_word].reshape(1, -1),
                        word2vec_model.wv[original_word].reshape(1, -1)
                    )[0][0]
                    cosine_similarities.append(cosine_similarity_score)
            if cosine_similarities:
                max_cosine_similarity = max(cosine_similarities)
                total_cosine_similarities.append(max_cosine_similarity)

    if total_cosine_similarities:
        average_max_cosine_similarity = sum(total_cosine_similarities) / len(total_cosine_similarities)
    else:
        average_max_cosine_similarity = 0.0  # Handle case where no valid similarities found

    #print(f"Cosine Similarity calculation finalized for {level} level")


    #### Calculate Levenshtein distance and similarity
    total_lev_distances = []

    # Calculate total Levenshtein distances
    for extracted_word in extracted_list:
        min_distance = min(edit_distance(extracted_word, original_word) for original_word in original_list)
        total_lev_distances.append(min_distance)

    # Calculate averages
    if len(total_lev_distances) > 0:
        average_lev_distance = sum(total_lev_distances) / len(total_lev_distances)
    else:
        average_lev_distance = 0.0  # Handle case where no valid distances found

    #print(f"Levenshtein distance calculation finalized for {level} level")

    # Create the similarity dictionary
    similarity_dict = {
        "avg_cosine_sim": round(average_max_cosine_similarity, 2),
        "avg_lev_dist": round(average_lev_distance, 2)
    }

    return similarity_dict