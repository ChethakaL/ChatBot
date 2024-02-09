# chatbot/spacy_nlp.py

import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    # Process the text using spaCy
    doc = nlp(text)

    # Extract named entities
    entities = {ent.label_: ent.text for ent in doc.ents}

    return entities
