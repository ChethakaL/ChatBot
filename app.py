import random
from flask import Flask, request, jsonify, session
from chatbot import wit_ai  # Ensure this is correctly implemented
import json
import os
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.urandom(
    24)  # It's better to use a fixed secret key for session consistency across restarts during development

# Connect to MongoDB
client = MongoClient("mongodb+srv://chethakasl:03dDAhSzTu7Um91D@cluster0.9jcbhec.mongodb.net/")
db = client['test']
collection = db['shops']

# Load intents dataset
with open('static/data.json', 'r') as file:
    data = json.load(file)
    intents = {intent['tag']: intent for intent in data['intents']}


@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json['message']
    print(f"User message: {user_message}")  # Log user message

    # Initialize session if not already exists
    if 'conversation_state' not in session:
        session['conversation_state'] = {'intent': None, 'product_name': None}

    # Initialize bot_response with a default value
    bot_response = "Sorry, I didn't understand. Can you please rephrase your question?"

    # Process user message with wit.ai for intent detection
    intent, entities = wit_ai.process_message(user_message)
    print(f"Detected intent: {intent}, entities: {entities}")  # Log intent and entities

    # Retrieve previous conversation state
    prev_intent = session['conversation_state']['intent']
    product_name = session['conversation_state']['product_name']
    print(f"Previous intent: {prev_intent}, product name: {product_name}")  # Log previous state

    # Check if intent is detected
    if intent:
        if intent.lower() == 'product_inquiry':
            product_entity = entities.get('product:product')
            if product_entity:
                product_name = product_entity[0]['value']
                # Update the conversation state with the new product
                session['conversation_state'] = {'intent': intent.lower(), 'product_name': product_name}

                # Query MongoDB for the product
                product_in_db = collection.find_one({"name": {"$regex": product_name, "$options": "i"}})
                if product_in_db:
                    # If product is found in the database, generate a positive response
                    bot_response = f"Yes, we have {product_name}. What would you like to know about it?"
                else:
                    # If product is not found, inform the user
                    bot_response = f"Sorry, we don't have {product_name} in our inventory."

        elif intent.lower() == 'colors' and product_name:
            result = collection.find_one({"name": {"$regex": product_name, "$options": "i"}})
            if result:
                colors = result.get('colours', [])
                if colors:
                    bot_response = f"Available colors for {product_name}: {', '.join(colors)}."
                else:
                    bot_response = f"Sorry, we do not have information about colors for {product_name}."
            else:
                bot_response = "Please inquire about a product before asking about its colors."
        elif intent.lower() == 'sizes' and product_name:
            # New block to handle size inquiries
            result = collection.find_one({"name": {"$regex": product_name, "$options": "i"}})
            if result:
                sizes = result.get('size', [])  # Assuming 'sizes' is a field in your MongoDB documents
                if sizes:
                    bot_response = f"Available sizes for {product_name}: {', '.join(sizes)}."
                else:
                    bot_response = f"Sorry, we do not have information about sizes for {product_name}."
            else:
                bot_response = "Please inquire about a product before asking about its sizes."
        else:
            matching_intents = [i for i in intents.values() if i['tag'] == intent.lower()]
            if matching_intents:
                responses = matching_intents[0]['responses']
                bot_response = random.choice(responses)
            else:
                bot_response = "I'm not sure how to respond to that."
    else:
        bot_response = "Sorry, I didn't understand. Can you please rephrase your question?"

    print(f"Bot response: {bot_response}")  # Log the final bot response
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
