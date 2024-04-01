import os
import json
import asyncio
from typing import Any, Tuple
from openai import AsyncAzureOpenAI
from typing import Tuple


azure_openai_client = AsyncAzureOpenAI(
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

def init_messages():
    messages = [
        { 
            "role": "system", 
            "content": """
                You are a helpful assistant.
                You have access to a function that can get the current weather in a given location.
                Determine a reasonable Unit of Measurement (Celsius or Fahrenheit) for the temperature based on the location.
            """
        },
        # {
        #     "role": "user",
        #     "content": "What's the weather like in San Francisco, Tokyo, and Paris?",
        # }
    ]
    
    return messages

def get_tools():
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
    
    return tools

def get_available_functions():
    available_functions = {
        "get_current_weather": get_current_weather,
    }
    
    return available_functions


def get_user_input() -> str:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return ""
    except EOFError:
        print("\n\nExiting chat...")
        return ""

    if user_input == "exit":
        print("\n\nExiting chat...")
        return ""

    return user_input

async def chat(messages, tools) -> Tuple[Any, bool]:
    # User's input
    user_input = get_user_input()
    if not user_input:
        return False
    messages.append({"role": "user", "content": user_input})

    # Step 1: send the conversation and available functions to the model
    stream_response = await azure_openai_client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
        stream=True
    )

    print("Assistant:> ", end="")
    
    tool_calls = [] # Accumulator for tool calls to process later
    full_delta_content = "" # Accumulator for the full assistant's content

    async for chunk in stream_response:
        delta = chunk.choices[0].delta if chunk.choices and chunk.choices[0].delta is not None else None

        if delta and delta.content:
            full_delta_content += delta.content
            await asyncio.sleep(0.1)
            print(delta.content, end="", flush=True)
            
        elif delta and delta.tool_calls:
            tc_chunk_list = delta.tool_calls
            for tc_chunk in tc_chunk_list:
                if len(tool_calls) <= tc_chunk.index:
                    tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                tc = tool_calls[tc_chunk.index]

                if tc_chunk.id:
                    tc["id"] += tc_chunk.id
                if tc_chunk.function.name:
                    tc["function"]["name"] += tc_chunk.function.name
                if tc_chunk.function.arguments:
                    tc["function"]["arguments"] += tc_chunk.function.arguments


    # Step 2: check if the model wanted to call a function
    if tool_calls:
        messages.append({ "role": "assistant", "tool_calls": tool_calls })
        available_functions = get_available_functions() 

        for tool_call in tool_calls:

            # Note: the JSON response may not always be valid; be sure to handle errors
            function_name = tool_call['function']['name']
            if function_name not in available_functions:
                return "Function " + function_name + " does not exist"
        
            # Step 3: call the function with arguments if any
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call['function']['arguments'])
            function_response = function_to_call(**function_args)

            # Step 4: send the info for each function call and function response to the model
            messages.append(
                {
                    "tool_call_id": tool_call['id'],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response

        stream_response2 = await azure_openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            messages=messages,
            temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
            stream=True,
        )

        async def print_stream_chunks(stream):
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    await asyncio.sleep(0.1)

        await print_stream_chunks(stream_response2)

        print("")
        return True

    print("")
    messages.append({ "role": "assistant", "content": full_delta_content })
    return True
    

async def main() -> None:

    messages = init_messages()
    tools = get_tools()

    chatting = True
    while chatting:
        chatting = await chat(messages, tools)

if __name__ == "__main__":
    asyncio.run(main())