import os
import json
from Refiner_subcomponent.Modularized_functions.OCEL_reader import OCEL_reader
from Refiner_subcomponent.Modularized_functions.OCEL_concatenator import OCEL_concatenator
from Refiner_subcomponent.Modularized_functions.OCEL_generative_refiner import OCEL_generative_refiner

def OCEL_generative_refiner_component(dataset_folder, api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model):

    extracted_event_log_path = os.path.join(dataset_folder, "Extracted_logs/GEN_subsets/")
    saving_folder = os.path.join(dataset_folder, "Extracted_logs/")

    OCEL_list = OCEL_reader(extracted_event_log_path)
    OCEL_concatenator(OCEL_list, saving_folder)
    #OCEL_generative_refiner(dataset_folder, api_type, openai_api_key, openai_model, azure_api_key,  azure_endpoint, azure_model)
    # Due to API-issues the generative refinement step is currently executed manually via the ChatGPT online version. Therefore, the concatenated file is uploaded and the following user-prompt is use: "You are a process mining expert. You will now receive a concatenated event log in ocel2.0 format over your knowledge base. Please refine this concatenated ocel2.0 log by for example cleaning the different names, merging similar entities and ensuring a correct correspondence between the different parts of the log. Don't merge any events that happened at different timestamps. Return ONLY the refined event log in OCEL2.0 format without any other text or information."


