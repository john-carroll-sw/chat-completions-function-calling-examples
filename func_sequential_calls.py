import json
import math
import pandas as pd
import pytz
from datetime import datetime
from utils import check_args, setup_client

# Set up the OpenAI client, get the deployment name
client, DEPLOYMENT_NAME = setup_client()

def get_current_time(location):
    try:
        # Get the timezone for the city
        timezone = pytz.timezone(location)

        # Get the current time in the timezone
        now = datetime.now(timezone)
        current_time = now.strftime("%I:%M:%S %p")

        return current_time
    except:
        return "Sorry, I couldn't find the timezone for that location."

def get_stock_market_data(index):
    available_indices = [
        "S&P 500",
        "NASDAQ Composite",
        "Dow Jones Industrial Average",
        "Financial Times Stock Exchange 100 Index",
    ]

    if index not in available_indices:
        return "Invalid index. Please choose from 'S&P 500', 'NASDAQ Composite', 'Dow Jones Industrial Average', 'Financial Times Stock Exchange 100 Index'."

    # Read the CSV file
    data = pd.read_csv("./data/stock_data.csv")

    # Filter data for the given index
    data_filtered = data[data["Index"] == index]

    # Remove 'Index' column
    data_filtered = data_filtered.drop(columns=["Index"])

    # Convert the DataFrame into a dictionary
    hist_dict = data_filtered.to_dict()

    for key, value_dict in hist_dict.items():
        hist_dict[key] = {k: v for k, v in value_dict.items()}

    return json.dumps(hist_dict)

def calculator(num1, num2, operator):
    if operator == "+":
        return str(num1 + num2)
    elif operator == "-":
        return str(num1 - num2)
    elif operator == "*":
        return str(num1 * num2)
    elif operator == "/":
        return str(num1 / num2)
    elif operator == "**":
        return str(num1**num2)
    elif operator == "sqrt":
        return str(math.sqrt(num1))
    else:
        return "Invalid operator"

"""
    Get tools
    - Returns the tools available to the model. 
    - In this case, it's a single function to get the current weather
"""
def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location name. The pytz is used to get the timezone for that location. Location names should be in a format like America/New_York, Asia/Bangkok, Europe/London",
                        }
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_market_data",
                "description": "Get the stock market data for a given index",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "string",
                            "enum": [
                                "S&P 500",
                                "NASDAQ Composite",
                                "Dow Jones Industrial Average",
                                "Financial Times Stock Exchange 100 Index",
                            ],
                        },
                    },
                    "required": ["index"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "A simple calculator used to perform basic arithmetic operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {"type": "number"},
                        "num2": {"type": "number"},
                        "operator": {
                            "type": "string",
                            "enum": ["+", "-", "*", "/", "**", "sqrt"],
                        },
                    },
                    "required": ["num1", "num2", "operator"],
                },
            },
        },
    ]

"""
    Get available functions
    - This function returns a dictionary of available functions
"""
def get_available_functions():
    return {
        "get_current_time": get_current_time,
        "get_stock_market_data": get_stock_market_data,
        "calculator": calculator,
    }

def run_multiturn_conversation(messages, tools, available_functions):
    # Step 1: send the conversation and available functions to GPT
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
    )

    # Step 2: check if GPT wanted to call a function
    while response.choices[0].finish_reason == "tool_calls":
        response_message = response.choices[0].message
        print("Recommended Function call:")
        print(response_message.tool_calls[0])
        print()

        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        function_name = response_message.tool_calls[0].function.name

        # verify function exists
        if function_name not in available_functions:
            return "Function " + function_name + " does not exist"
        function_to_call = available_functions[function_name]

        # verify function has correct number of arguments
        function_args = json.loads(response_message.tool_calls[0].function.arguments)
        if check_args(function_to_call, function_args) is False:
            return "Invalid number of arguments for function: " + function_name
        
        # call the function
        function_response = function_to_call(**function_args)

        print("Output of function call:")
        print(function_response)
        print()

        # Step 4: send the info on the function call and function response to GPT

        # adding assistant response to messages
        messages.append(
            {
                "role": response_message.role,
                "function_call": {
                    "name": response_message.tool_calls[0].function.name,
                    "arguments": response_message.tool_calls[0].function.arguments,
                },
                "content": None,
            }
        )

        # adding function response to messages
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        print("Messages in next request:")
        for message in messages:
            print(message)
        print()

        response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
        )  # get a new response from GPT where it can see the function response

    return response


# Can add system prompting to guide the model to call functions and perform in specific ways
next_messages = [
    {
        "role": "system",
        "content": "Assistant is a helpful assistant that helps users get answers to questions. Assistant has access to several tools and sometimes you may need to call multiple tools in sequence to get answers for your users.",
    }
]
next_messages.append(
    {
        "role": "user",
        "content": "How much did S&P 500 change between July 12 and July 13? Use the calculator.",
    }
)

assistant_response = run_multiturn_conversation(
    next_messages, get_tools(), get_available_functions()
)
print("Final Response:")
print(assistant_response.choices[0].message)
print("Conversation complete!")
