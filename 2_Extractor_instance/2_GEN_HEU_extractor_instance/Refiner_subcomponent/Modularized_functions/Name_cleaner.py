from nltk.stem import WordNetLemmatizer
import spacy
from word2number import w2n

# Load the English model for spaCy
nlp = spacy.load("en_core_web_md")
lemmatizer = WordNetLemmatizer()


def clean_all_names(log):

    for object_type in log['objectTypes']:
        if object_type['name'] in ['Object_type_not_identified', 'object_type_not_identified']:
            object_type['name'] = 'object_type_not_identified'
        else:
            doc = nlp(object_type['name'].lower())
            nouns_only = [token.text.lower() for token in doc if token.pos_ not in ['ADP', 'DET', 'ADJ']]
            if nouns_only:
                object_type['name'] = ' '.join(nouns_only)
            else:
                object_type['name'] = 'object_type_not_identified'
        object_type['name'] = object_type['name'].lower()
        for attr in object_type['attributes']:
            attr['name'] = lemmatizer.lemmatize(attr['name']).lower()

    for event_type in log['eventTypes']:
        event_type['name'] = lemmatizer.lemmatize(event_type['name']).lower()
        for attr in event_type['attributes']:
            attr['name'] = lemmatizer.lemmatize(attr['name']).lower()

    for object in log['objects'].copy():
        object['id'] = lemmatizer.lemmatize(object['id']).lower()
        if object['type'] in ['Object_type_not_identified', 'object_type_not_identified']:
            object['type'] = 'object_type_not_identified'
        else:
            doc = nlp(object['type'].lower())
            nouns_only = [token.text.lower() for token in doc if token.pos_ not in ['ADP', 'DET', 'ADJ']]
            if nouns_only:
                object['type'] = ' '.join(nouns_only)
            else:
                object['type'] = 'object_type_not_identified'
        object['type'] = object['type'].lower()
        for attr in object_type['attributes']:
            attr['name'] = lemmatizer.lemmatize(attr['name']).lower()
        if 'attributes' in object:
            for attr in object['attributes']:
                attr['name'] = lemmatizer.lemmatize(attr['name']).lower()
                doc = nlp(attr['value'])
                for token in doc:
                    # Check if the token is a CARDINAL entity and does not contain digits
                    if token.ent_type_ == "CARDINAL" and not any(char.isdigit() for char in token.text):
                        try:
                            # Convert the word-based number to an integer and then to a float
                            attr['value'] = str(w2n.word_to_num(token.text))
                        except:
                            attr['value'] = lemmatizer.lemmatize(attr['value']).lower()
                    else:
                        attr['value'] = lemmatizer.lemmatize(attr['value']).lower()



        if 'relationships' in object:
            for rel in object['relationships'].copy():
                rel['objectId'] = lemmatizer.lemmatize(rel['objectId']).lower()

    for event in log['events']:
        event['type'] = lemmatizer.lemmatize(event['type']).lower()
        if 'attributes' in event:
            for attr in event['attributes']:
                attr['name'] = lemmatizer.lemmatize(attr['name']).lower()
                doc = nlp(attr['value'])
                for token in doc:
                    # Check if the token is a CARDINAL entity and does not contain digits
                    if token.ent_type_ == "CARDINAL" and not any(char.isdigit() for char in token.text):
                        try:
                            # Convert the word-based number to an integer and then to a float
                            attr['value'] = str(w2n.word_to_num(token.text))
                        except:
                            attr['value'] = lemmatizer.lemmatize(attr['value']).lower()
                    else:
                        attr['value'] = lemmatizer.lemmatize(attr['value']).lower()

        for rel in event['relationships'].copy():
            rel['objectId'] = lemmatizer.lemmatize(rel['objectId']).lower()
    return log