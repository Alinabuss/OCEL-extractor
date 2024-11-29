import os
from tqdm import tqdm
from Collector_subcomponent.Modularized_functions.Generative_extractor_setup import generative_extractor_setup
from Collector_subcomponent.Modularized_functions.OCEL_collection_using_LLM import OCEL_collector_using_LLM

def OCEL_generative_collector_component(dataset_folder, level, api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model):
    if level == 'event':
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Event_reports/")

    elif level == 'disjunct_event_groups':
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Disjunct_grouped_reports/")

    elif level == "intersecting_event_groups":
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Intersecting_grouped_reports/")

    elif level == "Test_setup":
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Test_reports/")

    saving_folder = os.path.join(dataset_folder, "Extracted_logs/GEN_subsets/")

    os.makedirs(saving_folder, exist_ok=True)

    client, assistant = generative_extractor_setup(api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model)

    for filename in tqdm(os.listdir(report_folder), desc="Collect information from textual descriptions", unit="file"):
        if filename.endswith(".txt"):  # Process only text files
            OCEL_collector_using_LLM(report_folder, filename,  saving_folder, level, client, assistant)


