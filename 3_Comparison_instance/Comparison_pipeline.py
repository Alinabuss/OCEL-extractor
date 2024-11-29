from Modularized_functions.Comparison_sets_creator import comparison_sets_creator
from Modularized_functions.Confusion_matrix_creator import confusion_matrix_creator
from Modularized_functions.Quality_measure_calculator import quality_measure_calculator
from Modularized_functions.Results_concatenator import results_concatenator
from Modularized_functions.Similarity_measure_calculator import similarity_measure_calculator

dataset_folder = "Data/Age_of_empire/Test_data/"
nltk.download('wordnet')

def  OCEL_comparison(dataset_folder):

    # Create and read original and extracted comparison sets
    original_ocel_json, extracted_ocel_json = comparison_sets_creator(dataset_folder)

    # Create confusion-matrices for different levels
    object_type_confusion_matrix, object_type_mapping = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_type")
    object_type_attribute_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_type_attribute_type", mapping = object_type_mapping)
    object_type_attribute_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_type_attribute_type_rel", mapping = object_type_mapping)
    object_instance_confusion_matrix, object_instance_mapping = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_instance")
    object_instance_type_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_instance_object_type", mapping=object_instance_mapping)
    object_instance_type_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_instance_object_type_rel", mapping=object_instance_mapping)
    object_instance_attribute_type_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="object_instance_attribute_type",mapping=object_instance_mapping)
    object_instance_attribute_type_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="object_instance_attribute_type_rel",mapping=object_instance_mapping)
    object_instance_attribute_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_instance_attribute_value", mapping=object_instance_mapping)
    object_instance_attribute_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_instance_attribute_value_rel", mapping=object_instance_mapping)
    object_to_object_relationship_confusion_matrix= confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_to_object", mapping=object_instance_mapping)
    object_to_object_relationship_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "object_to_object_rel", mapping=object_instance_mapping)
    event_type_confusion_matrix, event_type_mapping = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level = "event_type")
    event_type_attribute_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level="event_type_attribute_type",mapping=event_type_mapping)
    event_type_attribute_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="event_type_attribute_type_rel", mapping=event_type_mapping)
    event_instance_confusion_matrix, event_instance_mapping = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level="event_instance")
    event_instance_attribute_type_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="event_instance_attribute_type", mapping=event_instance_mapping)
    event_instance_attribute_type_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="event_instance_attribute_type_rel", mapping=event_instance_mapping)
    event_instance_attribute_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="event_instance_attribute_value",mapping=event_instance_mapping)
    event_instance_attribute_rel_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json,level="event_instance_attribute_value_rel",mapping=event_instance_mapping)
    event_to_object_relationship_confusion_matrix = confusion_matrix_creator(original_ocel_json, extracted_ocel_json, level="event_to_object", mapping=event_instance_mapping)
    event_to_object_relationship_rel_confusion_matrix= confusion_matrix_creator(original_ocel_json,extracted_ocel_json,level="event_to_object_rel", mapping=event_instance_mapping)
    confusion_matrix_list = [object_type_confusion_matrix, object_type_attribute_confusion_matrix, object_type_attribute_rel_confusion_matrix,
                             object_instance_confusion_matrix, object_instance_type_confusion_matrix, object_instance_type_rel_confusion_matrix,
                             object_instance_attribute_type_confusion_matrix, object_instance_attribute_type_rel_confusion_matrix,
                             object_instance_attribute_confusion_matrix, object_instance_attribute_rel_confusion_matrix,
                             object_to_object_relationship_confusion_matrix, object_to_object_relationship_rel_confusion_matrix,
                             event_type_confusion_matrix, event_type_attribute_confusion_matrix, event_type_attribute_rel_confusion_matrix,
                             event_instance_confusion_matrix, event_instance_attribute_type_confusion_matrix, event_instance_attribute_type_rel_confusion_matrix,
                             event_instance_attribute_confusion_matrix, event_instance_attribute_rel_confusion_matrix,
                             event_to_object_relationship_confusion_matrix, event_to_object_relationship_rel_confusion_matrix]

    # Calculate quality measures based on confusion-matrices for different levels
    object_type_quality_metrics = quality_measure_calculator(object_type_confusion_matrix)
    object_type_attribute_quality_metrics = quality_measure_calculator(object_type_attribute_confusion_matrix)
    object_type_attribute_rel_quality_metrics = quality_measure_calculator(object_type_attribute_rel_confusion_matrix)
    object_instance_quality_metrics = quality_measure_calculator(object_instance_confusion_matrix)
    object_instance_type_quality_metrics = quality_measure_calculator(object_instance_type_confusion_matrix)
    object_instance_type_rel_quality_metrics = quality_measure_calculator(object_instance_type_rel_confusion_matrix)
    object_instance_attribute__type_quality_metrics = quality_measure_calculator(object_instance_attribute_type_confusion_matrix)
    object_instance_attribute_type_rel_quality_metrics = quality_measure_calculator(object_instance_attribute_type_rel_confusion_matrix)
    object_instance_attribute_quality_metrics = quality_measure_calculator(object_instance_attribute_confusion_matrix)
    object_instance_attribute_rel_quality_metrics = quality_measure_calculator(object_instance_attribute_rel_confusion_matrix)
    object_to_object_relationship_quality_metrics = quality_measure_calculator(object_to_object_relationship_confusion_matrix)
    object_to_object_relationship_rel_quality_metrics = quality_measure_calculator(object_to_object_relationship_rel_confusion_matrix)
    event_type_quality_metrics = quality_measure_calculator(event_type_confusion_matrix)
    event_type_attribute_quality_metrics = quality_measure_calculator(event_type_attribute_confusion_matrix)
    event_type_attribute_rel_quality_metrics = quality_measure_calculator(event_type_attribute_rel_confusion_matrix)
    event_instance_quality_metrics = quality_measure_calculator(event_instance_confusion_matrix)
    event_instance_attribute_type_quality_metrics = quality_measure_calculator(event_instance_attribute_type_confusion_matrix)
    event_instance_attribute_type_rel_quality_metrics = quality_measure_calculator(event_instance_attribute_type_rel_confusion_matrix)
    event_instance_attribute_quality_metrics = quality_measure_calculator(event_instance_attribute_confusion_matrix)
    event_instance_attribute_rel_quality_metrics = quality_measure_calculator(event_instance_attribute_rel_confusion_matrix)
    event_to_object_relationship_quality_metrics = quality_measure_calculator(event_to_object_relationship_confusion_matrix)
    event_to_object_relationship_rel_quality_metrics = quality_measure_calculator(event_to_object_relationship_rel_confusion_matrix)
    quality_metrics_list = [object_type_quality_metrics, object_type_attribute_quality_metrics, object_type_attribute_rel_quality_metrics,
                            object_instance_quality_metrics, object_instance_type_quality_metrics, object_instance_type_rel_quality_metrics,
                            object_instance_attribute__type_quality_metrics, object_instance_attribute_type_rel_quality_metrics,
                            object_instance_attribute_quality_metrics, object_instance_attribute_rel_quality_metrics,
                            object_to_object_relationship_quality_metrics, object_to_object_relationship_rel_quality_metrics,
                            event_type_quality_metrics, event_type_attribute_quality_metrics, event_type_attribute_rel_quality_metrics,
                            event_instance_quality_metrics, event_instance_attribute_type_quality_metrics, event_instance_attribute_type_rel_quality_metrics,
                            event_instance_attribute_quality_metrics, event_instance_attribute_rel_quality_metrics,
                            event_to_object_relationship_quality_metrics, event_to_object_relationship_rel_quality_metrics]

    results_concatenator(confusion_matrix_list, quality_metrics_list)

    # Calculate similarity measures for different levels
    object_type_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="object_type")
    object_type_attribute_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="object_type_attribute_type", mapping = object_type_mapping)
    object_type_attribute_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="object_type_attribute_type_rel", mapping = object_type_mapping)
    object_instance_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="object_instance")
    object_instance_type_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="object_instance_object_type")
    object_instance_type_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="object_instance_object_type_rel", mapping = object_instance_mapping)
    object_instance_attribute_type_similarity_metrics = similarity_measure_calculator(original_ocel_json,extracted_ocel_json,level="object_instance_attribute_type")
    object_instance_attribute_type_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json,extracted_ocel_json,level="object_instance_attribute_type_rel",mapping=object_instance_mapping)
    object_instance_attribute_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="object_instance_attribute_value")
    object_instance_attribute_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="object_instance_attribute_value_rel", mapping = object_instance_mapping)
    object_to_object_relationship_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="object_to_object")
    object_to_object_relationship_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="object_to_object_rel", mapping = object_instance_mapping)
    event_type_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="event_type")
    event_type_attribute_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="event_type_attribute_type", mapping = event_type_mapping)
    event_type_attribute_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="event_type_attribute_type_rel", mapping = event_type_mapping)
    event_instance_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="event_instance")
    event_instance_attribute_type_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="event_instance_attribute_type")
    event_instance_attribute_type_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json,extracted_ocel_json,level="event_instance_attribute_type_rel",mapping=event_instance_mapping)
    event_instance_attribute_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="event_instance_attribute_value")
    event_instance_attribute_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="event_instance_attribute_value_rel", mapping = event_instance_mapping)
    event_to_object_relationship_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json,level="event_to_object")
    event_to_object_relationship_rel_similarity_metrics = similarity_measure_calculator(original_ocel_json, extracted_ocel_json, level="event_to_object_rel", mapping=event_instance_mapping)
    similarity_metrics_list = [object_type_similarity_metrics, object_instance_similarity_metrics, object_instance_type_similarity_metrics,
                               object_type_attribute_similarity_metrics, object_type_attribute_rel_similarity_metrics,
                               object_instance_type_rel_similarity_metrics,  object_instance_attribute_type_similarity_metrics,
                               object_instance_attribute_type_rel_similarity_metrics, object_instance_attribute_similarity_metrics,
                               object_instance_attribute_rel_similarity_metrics, object_to_object_relationship_similarity_metrics,
                               object_to_object_relationship_rel_similarity_metrics, event_type_similarity_metrics,
                               event_type_attribute_similarity_metrics, event_type_attribute_rel_similarity_metrics,
                               event_instance_similarity_metrics,event_instance_attribute_type_similarity_metrics, event_instance_attribute_type_rel_similarity_metrics,
                               event_instance_attribute_similarity_metrics, event_instance_attribute_rel_similarity_metrics,
                               event_to_object_relationship_similarity_metrics, event_to_object_relationship_rel_similarity_metrics]


    # Concatenate and print results for different confusion matrices and different quality measures
    #results_concatenator(confusion_matrix_list, quality_metrics_list)
    results_concatenator(confusion_matrix_list, quality_metrics_list, similarity_metrics_list)

if __name__ == "__main__":
    OCEL_comparison(dataset_folder)