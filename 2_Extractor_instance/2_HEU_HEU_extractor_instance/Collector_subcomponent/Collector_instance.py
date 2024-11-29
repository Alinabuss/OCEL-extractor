import os
from tqdm import tqdm
from Collector_subcomponent.Candidate_extractor.Candidate_extractor import candidate_extractor
from Collector_subcomponent.NLP_preprocessor.NLP_preprocessor import NLP_preprocessor
from Collector_subcomponent.Candidate_mapper.Candidate_mapper import candidate_mapper
from Collector_subcomponent.OCEL_constructor.OCEL_constructor import OCEL_constructor


def OCEL_heuristic_collector_component(dataset_folder, level):

    DEFAULT_TIMESTAMP = '1970-01-01T00:00:00Z'

    if level == 'event':
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Event_reports/")

    elif level == 'disjunct_event_groups':
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Disjunct_grouped_reports/")

    elif level == "intersecting_event_groups":
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Intersecting_grouped_reports/")

    elif level == "Test_setup":
        report_folder = os.path.join(dataset_folder, "Textual_descriptions/Test_reports/")

    saving_folder = os.path.join(dataset_folder, "Extracted_logs/HEU_subsets/")


    for filename in tqdm(os.listdir(report_folder), desc="Collect information from textual descriptions", unit="file"):
    #for filename in os.listdir(report_folder):
          if filename.endswith(".txt"):  # Process only text files
              try:
                  doc, text, filepath = NLP_preprocessor(report_folder, filename, printing = False)
                  token_position_mapping = candidate_extractor(doc, text, DEFAULT_TIMESTAMP, printing = False)
                  mapping = candidate_mapper(doc, token_position_mapping, DEFAULT_TIMESTAMP, printing = False)
                  OCEL_constructor(mapping, filepath, saving_folder, level,printing = False)
              except:
                  pass


