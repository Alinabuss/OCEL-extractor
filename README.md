# OCEL Extractor

This GitHub repository accompanies the paper titled "From Text to Event Log: A Hybrid NLP Approach for Object-Centric Event Log Extraction". In this study, four distinct extractor variants were developed and evaluated for the unsupervised construction of object-centric event logs in the OCEL 2.0 format within an artificial development and evaluation framework. This repository contains the comprehensive framework, including the four extractor variants, results, and detailed documentation of the development and evaluation processes.

## Initial setup

To utilize the development and evaluation framework or the four extractor variants, please follow the setup guide provided. The framework and extractors incorporate the OpenAI API for various generative subcomponents. If you prefer not to use these components, you may skip Step 3. Otherwise, please enter your personal access tokens as described in Step 3.

This study employs an intermediate Azure endpoint for accessing the OpenAI APIs; however, you are welcome to use your OpenAI tokens directly. Ensure that you update the necessary information in the config.py file and the corresponding scripts accordingly.

1. Clone repositiory: `git clone https://github.com/Alinabuss/OCEL-extractor.git`
2. Install requirements: `pip install -r requirements.txt`
3. Add personal OpenAI-configuration to `config.py`.
    - Copy `config_sample.py` file to `config.py`: `cp config_sample.py config.py`
    - Add your OpenAI key or your Azure key and Azure endpoint to `config.py`.

## Data

Six object-centric event logs — Recruitment, Logistics, P2P, Order Management, Production, and Age of Empire — were used during the development and evaluation of the four extractor variants. The original event logs, along with their extracted counterparts, are provided in the respective subfolders within the 'Data' folder. You are welcome to use these logs for testing. Alternatively, if you wish to use a new event log, simply create a new subfolder within the 'Data' folder and store your logs there.

The provided event logs are pre-separated into training, validation, and test subsets, with corresponding sample sizes of 100, 100, and 1000 events per log sample. This separation was generated using the script Train_Validation_Test_Split_creator.py, located in the 0_Train_Validation_Test_Split_creator folder. If you wish to use this script for your own event logs, ensure that you adjust the path to your target Data folder accordingly within the script.

## Development and evaluation framework

The development and evaluation framework consists of three components: a generator instance (1_Generator_instance), an extractor instance (2_Extractor_instance), and a comparison instance (3_Comparison_instance). The generator instance receives an event log in OCEL2.0 format and utilizes LLM capabilities to convert it into corresponding textual descriptions. The extractor instance then analyzes these textual descriptions to re-engineer the original event log. Within the folder 2_Extractor_instance you can find the four extractor variants developed for this task. Finally, the extracted and original event logs are compared to each other within the comparison instance. Thereby, various performance metrics are computed across different components of the event logs to assess the similarity between the extracted log and the original log.

![Reverse_Engineering_Framework](https://github.com/user-attachments/assets/6051acf1-4fd9-4856-9c4e-03cbd5949d86)


### Generator instance
To use the generator instance of the reverse engineering framework, execute the Generator-pipeline file in the 1_Generator_instance folder after adapting it to your requirements. The following modifications can/must be made:

1. Specify the Data Path: Set the path to the data folder you wish to use with the generator (line 14).
2. OpenAI API Setup: As the generator instance utilizes the OpenAI API, ensure that you have correctly configured the config.py file with your personal access tokens. Alternatively, you may provide the access tokens directly within the script (lines 17-21):
    - Using Direct OpenAI Access Tokens:
        - Add your OpenAI token in the script or on line 17.
        - Specify the model you want to use for generation in line 18.
        - Ensure that you execute line 31 with the API mode set to 'openai' (comment out line 32).
    - Using the OpenAI API via Azure:
        - Modify either the config.py file or lines 19 and 20 in the script to set up Azure API access.
        - Specify the model you want to use in line 21.
        - Ensure that you execute line 32 with the API mode set to 'azure' (comment out line 31).
          
3. Further Adaptations:
    - In lines 31 and 32, you can specify the maximum number of reports to be generated.
    - In lines 25-28, you can configure which specific parts of the generator should be executed. Detailed descriptions of these components are available in the documentation.
       
The resulting textual descriptions will be automatically saved to the corresponding subfolders within the Data directory.
   
### Extractor instance
Within the 2_Extractor_instance folder, you will find the four extractor variants developed in the paper. Each extractor variant consists of two primary components: a collector and a refiner. Both components have been developed in heuristic and generative forms. The combination of these subcomponent variants results in the following four extractor types:

- HEU-HEU Extractor: Comprising a heuristic collector and a heuristic refiner.
- GEN-GEN Extractor: Comprising a generative collector and a generative refiner.
- HEU-GEN Extractor: Utilizing a heuristic collector and a generative refiner.
- GEN-HEU Extractor: Utilizing a generative collector and a heuristic refiner.

![Extractor_variants](https://github.com/user-attachments/assets/5fbbe182-5b03-46f8-abff-86a954035077)

  
To test the respective extractors, execute the corresponding Python file in the subfolder after adapting the path to the data folder and your OpenAI access credentials, if necessary. The extracted logs will be automatically saved to the same folder.

### Comparison instance
The comparison instance is used to compare the extracted logs to their original counterparts across various categories. To use this component, update the data path within the script and then execute the Comparison_pipeline.py file located in the 3_Comparison_instance folder. A detailed evaluation matrix containing confusion-matrix and similarity-based measures across different categories will be printed in the terminal upon completion. Please note that depending on the size of your comparison logs, this step may take some time.

![image](https://github.com/user-attachments/assets/3fb0fcab-aac0-4328-a379-0edb57fb8c1a)


## Results
The results of our evaluation against the six provided test event logs are available in the Results folder as .xlsx files. In conclusion, we recommend using the GEN-HEU extractor variant as it combines the strengths of the generative collector and heuristic refiner. This hybrid approach consistently achieves the best overall performance, delivering satisfactory precision and F1-scores while maintaining strong recall and robust generalization capabilities. 

# Citation
We encourage everyone to use our framework, extractors, or results for future research. However, if any part of our code is utilized, please ensure that the associated paper is cited accordingly.

