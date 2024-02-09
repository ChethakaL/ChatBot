# chatbot/wit_ai.py

from wit import Wit
from .spacy_nlp import extract_entities  # Import extract_entities function from spacy_nlp module

# Initialize Wit.ai client with your access token
wit_client = Wit(access_token='C7V3EG5IU77M7UYJMWGIJT6UHVYY4JXS')

def process_message(message):
    # Send user message to Wit.ai for processing
    response = wit_client.message(message)
    intent = response['intents'][0]['name'] if response['intents'] else None
    wit_entities = response['entities']

    # Extract entities using spaCy
    spacy_entities = extract_entities(message)

    # Merge entities from Wit.ai and spaCy
    entities = {**wit_entities, **spacy_entities}

    print("Intent detected: ", intent)
    print("Entities: ", entities)

    return intent, entities
