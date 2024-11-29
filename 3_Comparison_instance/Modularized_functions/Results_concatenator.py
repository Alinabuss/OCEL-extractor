import pandas as pd

def results_concatenator(confusion_matrix_list, quality_metrics_list, similarity_metrics_list=None):
    # Create DataFrames
    confusion_matrices_df = pd.DataFrame.from_records([
        {"Metric": "Object_type", **confusion_matrix_list[0]},
        #{"Metric": "Object_type_attribute_type (Abs)", **confusion_matrix_list[1]},
        #{"Metric": "Object_type_attribute_type (Rel)", ** confusion_matrix_list[2]},
        {"Metric": "Object_instance", **confusion_matrix_list[3]},
        {"Metric": "Object_to_type (Abs)", **confusion_matrix_list[4]},
        {"Metric": "Object_to_type (Rel)", **confusion_matrix_list[5]},
        {"Metric": "Object_instance_attribute_type (Abs)", **confusion_matrix_list[6]},
        {"Metric": "Object_instance_attribute_type (Rel)", **confusion_matrix_list[7]},
        {"Metric": "Object_instance_attribute_value (Abs)", **confusion_matrix_list[8]},
        {"Metric": "Object_instance_attribute_value (Rel)", **confusion_matrix_list[9]},
        {"Metric": "Object_to_object (Abs)", **confusion_matrix_list[10]},
        {"Metric": "Object_to_object (Rel)", **confusion_matrix_list[11]},
        {"Metric": "Event_type", **confusion_matrix_list[12]},
        #{"Metric": "Event_type_attribute_type (Abs)", **confusion_matrix_list[13]},
        #{"Metric": "Event_type_attribute_type (Rel)", **confusion_matrix_list[14]},
        {"Metric": "Event_instance", **confusion_matrix_list[15]},
        {"Metric": "Event_instance_attribute_type (Abs)", **confusion_matrix_list[16]},
        {"Metric": "Event_instance_attribute_type (Rel)", **confusion_matrix_list[17]},
        {"Metric": "Event_instance_attribute_value (Abs)", **confusion_matrix_list[18]},
        {"Metric": "Event_instance_attribute_value (Rel)", **confusion_matrix_list[19]},
        {"Metric": "Event_to_object (Abs)", **confusion_matrix_list[20]},
        {"Metric": "Event_to_object (Rel)", **confusion_matrix_list[21]}
    ])

    if similarity_metrics_list:
        quality_metrics_df = pd.DataFrame.from_records([
            {"Metric": "Object_type", **quality_metrics_list[0], **similarity_metrics_list[0]},
            #{"Metric": "Object_type_attribute_type (Abs)", **quality_metrics_list[1], **similarity_metrics_list[1]},
            #{"Metric": "Object_type_attribute_type (Rel)", **quality_metrics_list[2], **similarity_metrics_list[2]},
            {"Metric": "Object_instance", **quality_metrics_list[3], **similarity_metrics_list[3]},
            {"Metric": "Object_to_type (Abs)", **quality_metrics_list[4], **similarity_metrics_list[4]},
            {"Metric": "Object_to_type (Rel)", **quality_metrics_list[5], **similarity_metrics_list[5]},
            {"Metric": "Object_instance_attribute_type (Abs)", **quality_metrics_list[6], **similarity_metrics_list[6]},
            {"Metric": "Object_instance_attribute_type (Rel)", **quality_metrics_list[7], **similarity_metrics_list[7]},
            {"Metric": "Object_instance_attribute_value (Abs)", **quality_metrics_list[8], **similarity_metrics_list[8]},
            {"Metric": "Object_instance_attribute_value (Rel)", **quality_metrics_list[9], **similarity_metrics_list[9]},
            {"Metric": "Object_to_object (Abs)", **quality_metrics_list[10], **similarity_metrics_list[10]},
            {"Metric": "Object_to_object (Rel)", **quality_metrics_list[11], **similarity_metrics_list[11]},
            {"Metric": "Event_type", **quality_metrics_list[12], **similarity_metrics_list[12]},
            #{"Metric": "Event_type_attribute_type (Abs)", **quality_metrics_list[13], **similarity_metrics_list[13]},
            #{"Metric": "Event_type_attribute_type (Rel)", **quality_metrics_list[14], **similarity_metrics_list[14]},
            {"Metric": "Event_instance", **quality_metrics_list[15], **similarity_metrics_list[15]},
            {"Metric": "Event_instance_attribute_type (Abs)", **quality_metrics_list[16], **similarity_metrics_list[16]},
            {"Metric": "Event_instance_attribute_type (Rel)", **quality_metrics_list[17], **similarity_metrics_list[17]},
            {"Metric": "Event_instance_attribute_value (Abs)", **quality_metrics_list[18], **similarity_metrics_list[18]},
            {"Metric": "Event_instance_attribute_value (Rel)", **quality_metrics_list[19], **similarity_metrics_list[19]},
            {"Metric": "Event_to_object (Abs)", **quality_metrics_list[20], **similarity_metrics_list[20]},
            {"Metric": "Event_to_object (Rel)", **quality_metrics_list[21], **similarity_metrics_list[21]}
        ])
    else:
        quality_metrics_df = pd.DataFrame.from_records([
            {"Metric": "Object_type", **quality_metrics_list[0]},
            #{"Metric": "Object_type_attribute_type (Abs)", **quality_metrics_list[1]},
            #{"Metric": "Object_type_attribute_type (Rel)", **quality_metrics_list[2]},
            {"Metric": "Object_instance", **quality_metrics_list[3]},
            {"Metric": "Object_to_type (Abs)", **quality_metrics_list[4]},
            {"Metric": "Object_to_type (Rel)", **quality_metrics_list[5]},
            {"Metric": "Object_instance_attribute_type (Abs)", **quality_metrics_list[6]},
            {"Metric": "Object_instance_attribute_type (Rel)", **quality_metrics_list[7]},
            {"Metric": "Object_instance_attribute_value (Abs)", **quality_metrics_list[8]},
            {"Metric": "Object_instance_attribute_value (Rel)", **quality_metrics_list[9]},
            {"Metric": "Object_to_object (Abs)", **quality_metrics_list[10]},
            {"Metric": "Object_to_object (Rel)", **quality_metrics_list[11]},
            {"Metric": "Event_type", **quality_metrics_list[12]},
            #{"Metric": "Event_type_attribute_type (Abs)", **quality_metrics_list[13]},
            #{"Metric": "Event_type_attribute_type (Rel)", **quality_metrics_list[14]},
            {"Metric": "Event_instance", **quality_metrics_list[15]},
            {"Metric": "Event_instance_attribute_type (Abs)", **quality_metrics_list[16]},
            {"Metric": "Event_instance_attribute_type (Rel)", **quality_metrics_list[17]},
            {"Metric": "Event_instance_attribute_value (Abs)", **quality_metrics_list[18]},
            {"Metric": "Event_instance_attribute_value (Rel)", **quality_metrics_list[19]},
            {"Metric": "Event_to_object (Abs)", **quality_metrics_list[20]},
            {"Metric": "Event_to_object (Rel)", **quality_metrics_list[21]}
        ])

    # Filter out the relative metrics before calculating the mean
    non_relative_df = quality_metrics_df[~quality_metrics_df["Metric"].str.contains(r'\(Rel\)', regex=True)]

    # Calculate the mean for each column, excluding the 'Metric' column
    means = non_relative_df.iloc[:, 1:].select_dtypes(include='number').mean().round(2)

    # Create a dictionary for the 'Overall_event_log' metric
    overall_event_log = {"Metric": "Overall_event_log"}
    overall_event_log.update(means)

    # Create a new DataFrame for the 'Overall_event_log' row
    overall_event_log_df = pd.DataFrame([overall_event_log])

    # Concatenate the new row to the original DataFrame
    quality_metrics_df = pd.concat([quality_metrics_df, overall_event_log_df], ignore_index=True)

    # Round the entire DataFrame to 2 decimal places if float
    confusion_matrices_df = confusion_matrices_df.applymap(lambda x: int(x) if isinstance(x, int) else round(x, 2) if isinstance(x, float) else x)
    quality_metrics_df = quality_metrics_df.applymap(lambda x: int(x) if isinstance(x, int) else round(x, 2) if isinstance(x, float) else x)

    # Print DataFrames
    print("Confusion Matrices:")
    print(confusion_matrices_df.to_string(index=False))

    print("\nQuality and Similarity Metrics:")
    print(quality_metrics_df.to_string(index=False))