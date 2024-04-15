import random
from flask import Flask, request, jsonify
from chatbot import wit_ai
import json
import os
from pymongo import MongoClient
from description_generator import DescriptionGenerator

app = Flask(__name__)
generator = DescriptionGenerator()
app.secret_key = os.urandom(
    24)  # It's better to use a fixed secret key for session consistency across restarts during development
user_sessions = {}
# Connect to MongoDB
client = MongoClient("mongodb+srv://chethakasl:03dDAhSzTu7Um91D@cluster0.9jcbhec.mongodb.net/")
db = client['test']
collection = db['shops']

# Load intents dataset
with open('static/data.json', 'r') as file:
    data = json.load(file)
    intents = {intent['tag']: intent for intent in data['intents']}


@app.route('/ai', methods=['GET'])
def home():
    return "AI is running"


@app.route('/ai/generate-description', methods=['POST'])
def generate_description():
    # Check if the image file is in the request
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    # Extract product attributes from the form data
    image = request.files['image']
    productName = request.form.get('productName')
    productType = request.form.get('productType')
    productPrice = request.form.get('productPrice')
    sizesAvailable = request.form.get('sizesAvailable')
    colorsAvailable = request.form.get('colorsAvailable')

    # Check for missing product attributes
    if not all([productName, productType, productPrice, sizesAvailable, colorsAvailable]):
        return jsonify({"error": "Missing product attributes"}), 400

    # Use the generator to create a description based on the product attributes and the image
    description = generator.generate(image, productName, productType, productPrice, sizesAvailable, colorsAvailable)
    return jsonify({"description": description})



@app.route('/ai/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data['message']
    user_id = data['user_id']
    print(f"User message: {user_message,user_id}")

    #TODO  Previous code
    # if 'conversation_state' not in session:
    #     session['conversation_state'] = {'intent': None, 'product_name': None}

    # Initialize or retrieve user session
    if user_id not in user_sessions:
        user_sessions[user_id] = {'intent': None, 'product_name': None}
    session = user_sessions[user_id]

    # Initialize bot_response with a default value
    bot_response = "Sorry, I didn't understand. Can you please rephrase your question?"

    # Process user message with wit.ai for intent detection
    intent, entities = wit_ai.process_message(user_message)
    print(f"Detected intent: {intent}, entities: {entities}")  # Log intent and entities

    # Retrieve previous conversation state
    prev_intent = session['intent']
    product_name = session['product_name']
    print(f"Previous intent: {prev_intent}, product name: {product_name}")  # Log previous state

    # Check if intent is detected
    if intent:
        if intent.lower() == 'product_inquiry':
            product_entity = entities.get('product:product')
            if product_entity:
                product_name = product_entity[0]['value']
                # Update the conversation state with the new product
                session['intent'] = intent.lower()
                session['product_name'] = product_name

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
            if result and 'stocks' in result:
                colors = [stock['color'] for stock in result['stocks'] if 'color' in stock]
                if colors:
                    bot_response = f"Available colors for {product_name}: {', '.join(set(colors))}."
                else:
                    bot_response = f"Sorry, we do not have information about colors for {product_name}."
            else:
                bot_response = "Please inquire about a product before asking about its colors."
        elif intent.lower() == 'sizes' and product_name:
            result = collection.find_one({"name": {"$regex": product_name, "$options": "i"}})
            if result and 'stocks' in result:
                sizes = [stock['size'] for stock in result['stocks'] if 'size' in stock]
                if sizes:
                    bot_response = f"Available sizes for {product_name}: {', '.join(set(sizes))}."
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
    user_sessions[user_id] = session

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
