# app.py

import random
from flask import Flask, request, jsonify
from chatbot import wit_ai
import json

app = Flask(__name__)

# Load dataset
with open('static/data.json', 'r') as file:
    data = json.load(file)
    intents = {intent['tag']: intent for intent in data['intents']}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json['message']

    # Process user message with Wit.ai for intent detection
    intent, entities = wit_ai.process_message(user_message)

    # Check if intent is detected
    if intent:
        # Print detected intent and entities
        print("Intent:", intent)
        print("Entities:", entities)

        # Check if the intent exists in the dataset (case-insensitive comparison)
        if intent.lower() in intents:
            # Retrieve responses for the detected intent
            responses = intents[intent.lower()]['responses']
            # Select a random response
            bot_response = random.choice(responses)
        else:
            bot_response = "Sorry, I don't have a response for that intent."
    else:
        bot_response = "Sorry, I didn't understand. Can you please rephrase your question?"

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
