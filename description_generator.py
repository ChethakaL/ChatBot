import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, GPT2Tokenizer, GPT2LMHeadModel


class DescriptionGenerator:
    def __init__(self):
        # Load CLIP for image understanding
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Load GPT-2 for text generation
        self.gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Define a set of predefined marketing phrases
        self.marketing_phrases = [
            "a cozy and warm hoodie perfect for chilly evenings",
            "a stylish and trendy t-shirt for your everyday look",
            "an elegant and comfortable dress for special occasions",
            "a versatile and durable jacket for adventure seekers",
            # Add more phrases as needed
        ]

    def generate(self, image_stream, productName, productType, productPrice, sizesAvailable, colorsAvailable):
        try:
            image_description = self.analyze_image(image_stream)

            # Formulate a new prompt that's concise and specific
            prompt = f"Write a catchy and compelling product description for a {productType.lower()} named '{productName}'. Priced at ${productPrice}, it comes in sizes {sizesAvailable} and colors {colorsAvailable}."

            # Generate the description using the prompt
            generated_description = self.generate_description_with_gpt2(prompt, image_description)

            # Return the generated description
            return generated_description

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An eye-catching product is waiting for you!"

    def generate_description_with_gpt2(self, prompt, image_description):
        input_ids = self.gpt_tokenizer(prompt, return_tensors="pt").input_ids

        # Set an appropriate max_length for generation if needed
        output_sequences = self.gpt_model.generate(
            input_ids=input_ids,
            max_length=200,  # Increased max_length for a complete sentence
            temperature=0.9,  # Slightly higher temperature for creativity
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            top_k=50,
            top_p=0.95,
            pad_token_id=self.gpt_tokenizer.eos_token_id,
            eos_token_id=self.gpt_tokenizer.eos_token_id
        )

        generated_text = self.gpt_tokenizer.decode(output_sequences[0], skip_special_tokens=True)

        # Remove the prompt from the generated text
        generated_text = generated_text[len(prompt):].strip()

        # Post-process to ensure the text ends in a complete sentence.
        return f"{generated_text.capitalize()}. {image_description}"

    def analyze_image(self, image_stream):
        image = Image.open(image_stream).convert("RGB")
        inputs = self.clip_processor(images=image, return_tensors="pt")

        # Generate image features using CLIP
        image_features = self.clip_model.get_image_features(**inputs)

        # Now, compare the image features with the embeddings of the marketing phrases
        text_inputs = self.clip_processor(text=self.marketing_phrases, return_tensors="pt", padding=True)
        text_features = self.clip_model.get_text_features(**text_inputs)

        # Calculate similarities between image and text features
        similarities = (text_features @ image_features.T).softmax(dim=0)

        # Find the best matching marketing phrase
        best_match_index = similarities.argmax().item()
        best_phrase = self.marketing_phrases[best_match_index]

        return best_phrase


# Instantiate the DescriptionGenerator class
generator = DescriptionGenerator()

# Example usage
image_stream = "path_to_your_image.jpg"
productName = "Stylish Hoodie"
productType = "Hoodie"
productPrice = 49.99
sizesAvailable = "S, M, L, XL"
colorsAvailable = "Black, Gray, Navy"

# Generate the description
description = generator.generate(image_stream, productName, productType, productPrice, sizesAvailable, colorsAvailable)
print(description)
