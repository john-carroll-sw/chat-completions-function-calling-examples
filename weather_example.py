import os
from openai import AzureOpenAI
import json

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)


# Example function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "72", "unit": unit}
        )
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
        { 
            "role": "system", 
            "content": """
                You are a helpful assistant.
                You have access to a function that can get the current weather in a given location.
            """
        },
        {
            "role": "user",
            "content": "What's the weather like in San Francisco, Tokyo, and Paris?",
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": """
                    Get the current weather in a given location. 
                    Note: any US cities have temperatures in Fahrenheit
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: check if the model wanted to call a function
    if tool_calls:

        messages.append(response_message)  # extend conversation with assistant's reply
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        
        for tool_call in tool_calls:

            # Note: the JSON response may not always be valid; be sure to handle errors
            function_name = tool_call.function.name
            if function_name not in available_functions:
                return "Function " + function_name + " does not exist"
        
            # Step 3: call the function with arguments if any
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            # Step 4: send the info for each function call and function response to the model
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response

        second_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
    

# print(run_conversation())
result = run_conversation()

# from pprint import pprint
# pprint(vars(result))

message_content = result.choices[0].message.content
print(message_content)

