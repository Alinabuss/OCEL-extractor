import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Modularized_functions.Event_seperator import event_seperator
from Modularized_functions.Event_reducer import event_reducer
from Modularized_functions.Event_report_creator_with_openai import event_report_creator_with_openai
from config import OPENAI_KEY, AZURE_KEY, AZURE_ENDPOINT
from Modularized_functions.Grouped_report_creator_with_openai import grouped_report_creator_with_openai

# Specify folder-path to dataset
dataset_folder = "Data/Recruitment/Test_data/"

# Specify openai-api_key and openai-model OR azure-api_key, azure_endpoint, and azure_model
api_key = OPENAI_KEY
openai_model = "gpt-3.5-turbo"
azure_api_key = AZURE_KEY
azure_endpoint = AZURE_ENDPOINT
azure_model = "gpt-4o-mini-2024-07-18"


def generator_pipeline(dataset_folder, max_reports=None, api_type = "openai", openai_api_key = None, openai_model = "gpt-3.5-turbo", azure_api_key = None,  azure_endpoint = None, azure_model = None):
    event_reducer(dataset_folder)
    event_seperator(dataset_folder)
    event_report_creator_with_openai(dataset_folder, max_reports, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model)
    grouped_report_creator_with_openai(dataset_folder, api_type, openai_api_key, openai_model, azure_api_key, azure_endpoint, azure_model, level = 'Test_setup')

if __name__ == "__main__":
    #generator_pipeline(dataset_folder, max_reports = 100, api_type = "openai", openai_api_key = api_key, openai_model = openai_model)
    generator_pipeline(dataset_folder, max_reports=1000, api_type = "azure", azure_api_key = azure_api_key, azure_endpoint = azure_endpoint, azure_model = azure_model)

