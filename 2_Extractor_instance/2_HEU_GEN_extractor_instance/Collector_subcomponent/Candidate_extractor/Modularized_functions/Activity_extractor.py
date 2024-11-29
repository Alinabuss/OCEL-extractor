from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import extract_prefix_and_suffix
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import remove_subsets
import spacy

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')

def test_adv_and_preps(doc, last_i, activity, positions):
    if doc[last_i + 1].dep_ == 'prep':
        potential_positions = []
        compound_suffix = []
        compound_suffix.append(doc[last_i + 1].text)
        found_noun = False
        potential_positions.append(last_i+1)
        for j in range(1, len(doc)):
            if doc[last_i + 1 + j].pos_ in ['DET', 'NOUN', 'ADJ']:
                compound_suffix.append(doc[last_i + 1 + j].text)
                potential_positions.append(last_i + 1 + j)
                if doc[last_i + 1 + j].pos_ in ['NOUN']:
                    found_noun = True
            else:
                break

        if found_noun:
            # Combine the components to form the refined object type
            refined_child_text = ' '.join(compound_suffix)
            activity += " " + refined_child_text
            positions += potential_positions


    elif doc[last_i + 1].dep_ == 'advmod':
        activity += " " + doc[last_i + 1].text
        positions.append(last_i + 1)

    return activity, positions

def candidate_activity_extractor(doc):
    activities = []
    activity_position_mapping = {}
    be_have_verbs = {"be", "have", "relate", "associate", "link"}

    for i, token in enumerate(doc):
        if token.dep_ in ["ROOT", "relcl", 'ccomp', 'advcl', 'conj'] and token.pos_ == 'VERB':
            positions = []
            activity = token.lemma_
            positions.append(token.i)

            last_i = i
            if doc[i+1].dep_ == 'xcomp':
                last_i = i+1
                activity += " " + doc[i+1].text
                positions.append(i+1)

            # Check for direct objects of the verb (if any)
            related_tokens = list(doc[last_i].children) + list(doc[last_i].ancestors)

            for child in related_tokens:
                if child.dep_ in ["dobj", "nsubjpass", "attr"]:
                    refined_child_text, compound_prefix, further_positions = extract_prefix_and_suffix(doc, child)
                    activity += " " + refined_child_text
                    for j in further_positions:
                        if j not in positions:
                            positions.append(j)
                            last_i = j

            activity, positions = test_adv_and_preps(doc, i, activity, positions)
            activity, positions = test_adv_and_preps(doc, last_i, activity, positions)

            # Add the activity to the list of candidate activities
            if not any(verb in activity.lower() for verb in be_have_verbs):
                activities.append(activity)
                if activity not in activity_position_mapping.keys():
                    activity_position_mapping[activity] = []
                activity_position_mapping[activity].append(tuple(positions))

    activity_position_mapping = remove_subsets(activity_position_mapping)

    return activity_position_mapping