import json
from utils import get_function_and_args, setup_client

# Set up the OpenAI client, get the deployment name
client, DEPLOYMENT_NAME = setup_client()

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
                Determine a reasonable Unit of Measurement (Celsius or Fahrenheit) for the temperature based on the location.
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
                        "unit": {
                            "type": "string", 
                            "description": "Unit of Measurement (Celsius or Fahrenheit) for the temperature based on the location",
                            "enum": ["celsius", "fahrenheit"]
                        },
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
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

            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            function_name = tool_call.function.name

            # get the function and arguments
            function_to_call, function_args = get_function_and_args(tool_call, available_functions)
            
            # call the function
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
            model=DEPLOYMENT_NAME,
            messages=messages,
            temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
        )  # get a new response from the model where it can see the function response
        return second_response
    

result = run_conversation()

message_content = result.choices[0].message.content
print(message_content)

