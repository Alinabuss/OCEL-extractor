import spacy
import os
import re

def NLP_preprocessor(report_folder, filename, printing = False):
    # NLP preprocessing
    filepath = os.path.join(report_folder, filename)
    filepath = os.path.abspath(filepath)

    # Read filepath
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()

    text = re.sub(r'\*', '', text)

    # Construct and execute NLP-Pipeline for general english library
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    if printing:
        print(f"Processing {filename}")
        print("Text: ", text)
        for token in doc:
            print("ID: ", token.i , " Token: ", token.text, " Token-Dependency: ", token.dep_, " Token-PoS: ", token.pos_, " Token-enttype: ",
                  token.ent_type_, "Token-children: ", [child for child in token.children], "Token-ancestor: ",
                  [anc for anc in token.ancestors])
        print()

    return doc, text, filepath