def event_lifecycle_status_extractor(doc, candidate_activities_with_positions):
    candidate_lifecycle_status_with_positions = {}
    activity_indicators = ["event", "activity", "action"]
    activities = activity_indicators + [token for token in candidate_activities_with_positions.keys()]
    potential_lifecycle_stages = ['schedule', 'assign', 'withdraw', 'reassign', 'suspend', 'resume', 'pi_abort',
                                  'ate_abort', 'complete', 'autoskip', 'manualskip', 'unknown']

    # Convert potential lifecycle stages to a set for efficient lookup
    potential_lifecycle_stages_set = set(potential_lifecycle_stages)

    for activity in activities:
        activity_words = set(word.lower() for word in activity.split())  # Convert activity words to lowercase

        for sent_idx, sent in enumerate(doc.sents):
            # Convert sentence tokens to lowercase
            sentence_tokens_text = set(token.text.lower() for token in sent)
            sentence_tokens_lemma = set(token.lemma_.lower() for token in sent)

            if activity_words.issubset(sentence_tokens_lemma) or activity_words.issubset(sentence_tokens_text):
                # Check the lemmatized tokens for potential lifecycle stages
                for word in sent:
                    if word.lemma_.lower() in potential_lifecycle_stages_set:
                        if word.lemma_.lower() not in candidate_lifecycle_status_with_positions:
                            candidate_lifecycle_status_with_positions[word.lemma_.lower()] = []
                        candidate_lifecycle_status_with_positions[word.lemma_.lower()].append(tuple([word.i]))
                        break


    return candidate_lifecycle_status_with_positions
