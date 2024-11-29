def quality_measure_calculator(confusion_matrix):

    # Extract values from confusion_matrix
    tp = confusion_matrix.get("TP")
    fp = confusion_matrix.get("FP")
    fn = confusion_matrix.get("FN")
    tn = confusion_matrix.get("TN")
    oc = confusion_matrix.get("OC")
    nc = confusion_matrix.get("NC")

    # Calculate Quality Measures
    Completeness = nc / oc if oc != 0 else 0 # Count new log/Count original log
    Accuracy = (tp+tn) / (tp + tn + fp + fn) if tp + fp + fn != 0 else 0
    Precision = tp / (tp + fp) if tp + fp != 0 else 0
    Recall = tp / (tp + fn) if tp + fn != 0 else 0
    F1_Score = (2 * Precision * Recall) / (Precision + Recall) if Precision + Recall != 0 else 0

    Quality_metrics_dictionary = {
        "Completeness": round(Completeness, 2),
        "Accuracy": round(Accuracy, 2),
        "Precision": round(Precision, 2),
        "Recall": round(Recall, 2),
        "F1_Score": round(F1_Score, 2)
    }

    return Quality_metrics_dictionary

