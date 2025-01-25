import openai
from pydantic import BaseModel
from typing import List
from utils import setup_client

# Set up the OpenAI client, get the deployment name
client, DEPLOYMENT_NAME = setup_client()

class CoffeeMenuItem(BaseModel):
    category: str
    item: str
    description: str
    price: str = None

class CoffeeMenu(BaseModel):
    items: List[CoffeeMenuItem]

def print_parsed_menu(parsed_menu):
    # Print the parsed menu in a formatted way
    if parsed_menu:
        for item in parsed_menu.items:
            print(f"Category: {item.category}")
            print(f"Item: {item.item}")
            print(f"Description: {item.description}")
            print(f"Price: {item.price}")
            print()  # Add a blank line between items

def parse_menu_with_gpt4o(raw_text, model_deployment_name):
    """Parse the raw text into structured JSON using GPT-4o."""
    prompt = f"""
    You are a menu parser. Convert the following raw text from a coffee menu into structured JSON with the fields:
    - category
    - item
    - description
    - price (if available)

    Here is the coffee menu text:
    ---
    {raw_text}
    ---
    """
    try:
        response = client.beta.chat.completions.parse(
            model=model_deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format=CoffeeMenu
        )

        parsed_output = response.choices[0].message.parsed
        return parsed_output

    except openai.ContentFilterFinishReasonError as e:
        print(f"Content filter error: {e}")
        print(f"Problematic prompt: {prompt}")
        return None

# Example usage
sample_raw_text = """
Espresso Drinks
- Espresso: A strong coffee brewed by forcing hot water under pressure through finely ground coffee beans. $2.99
- Cappuccino: Espresso with steamed milk and a layer of foam. $3.99

Cold Brews
- Cold Brew: Coffee brewed cold for a smooth, rich flavor. $4.99
- Nitro Cold Brew: Cold brew infused with nitrogen for a creamy texture. $5.99
"""

# Print the Pydantic classes
print("Pydantic classes used in the script:")

print("\nclass CoffeeMenuItem(BaseModel):")
print("    category: str")
print("    item: str")
print("    description: str")
print("    price: str = None")

print("\nclass CoffeeMenu(BaseModel):")
print("    items: List[CoffeeMenuItem]")

print("\nParsing the following raw text:")
print(sample_raw_text)


parsed_menu = parse_menu_with_gpt4o(sample_raw_text, DEPLOYMENT_NAME)

print("\nParsed menu in structured JSON based on the pydantic classes:")
print_parsed_menu(parsed_menu)