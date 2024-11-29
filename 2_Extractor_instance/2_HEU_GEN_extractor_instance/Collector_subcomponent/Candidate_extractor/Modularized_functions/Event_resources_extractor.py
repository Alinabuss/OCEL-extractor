from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import extract_prefix_and_suffix
from Collector_subcomponent.Candidate_extractor.Modularized_functions.Helper_functions import remove_subsets


def event_resources_extractor(doc):
    event_resources_with_positions = {}

    # Scan the entire doc for tokens with the dependency 'agent'
    agent_tokens = [token for token in doc if token.dep_ == 'agent' or token.text == 'by']

    if agent_tokens:
        # Extract tokens with pos NOUN or PROPN following the agent token (skip DET)
        for agent in agent_tokens:
            extracted_tokens = []
            positions = []
            for token in agent.subtree:
                if token.pos_ == 'DET':
                    continue  # Skip DET token
                elif token.pos_ in ['NOUN', 'PROPN', 'SYM']:
                    extracted_tokens.append(token.text)
                    positions.append(token.i)
            if extracted_tokens:
                attribute = " ".join(extracted_tokens)
                if attribute not in event_resources_with_positions:
                    event_resources_with_positions[attribute] = []
                event_resources_with_positions[attribute].append(tuple(positions))

    # Search for 'nsubj' tokens with ent_type == ORG
    for token in doc:
        if token.dep_ == 'nsubj' and token.ent_type_ == 'ORG':

            refined_attribute, compound_prefix, positions = extract_prefix_and_suffix(doc, token)

            if refined_attribute not in event_resources_with_positions:
                event_resources_with_positions[refined_attribute] = []
            event_resources_with_positions[refined_attribute].append(tuple(positions))

    event_resources_with_positions = remove_subsets(event_resources_with_positions)

    return event_resources_with_positions




