import os
import json
import asyncio
import openai
from typing import Any, Tuple
from dotenv import load_dotenv

"""
    Initialize the client
    - Setup the client to use either Azure, OpenAI or Ollama API
    - Uses the Async client to handle asynchronous requests
    - Uses the environment variables
"""
load_dotenv()
API_HOST = os.getenv("API_HOST")

if API_HOST == "azure":
    client = openai.AsyncAzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
elif API_HOST == "openai":
    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
    DEPLOYMENT_NAME = os.getenv("OPENAI_MODEL")
elif API_HOST == "ollama":
    client = openai.AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="nokeyneeded",
    )
    DEPLOYMENT_NAME = os.getenv("OLLAMA_MODEL")

"""
    Get the current weather
    - This function is hard coded weather values
    - In production, this could be from your backend data or external API
"""
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

"""
    Initialize messages
    - Returns the initial messages to start the conversation
    - In this case, it's a single message to introduce the assistant
"""
def init_messages():
    return [
        { 
            "role": "system", 
            "content": """
                You are a helpful assistant.
                You have access to a function that can get the current weather in a given location.
                Determine a reasonable Unit of Measurement (Celsius or Fahrenheit) for the temperature based on the location.
            """
        }
    ]

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

"""
    Get available functions
    - This function returns a dictionary of available functions
"""
def get_available_functions():
    return { "get_current_weather": get_current_weather }

"""
    Get user input
    - Handle 'exit' command and exceptions
"""
def get_user_input() -> str:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return ""
    except EOFError:
        print("\n\nExiting chat...")
        return ""

    # Handle exit command
    if user_input == "exit":
        print("\n\nExiting chat...")
        return ""

    return user_input

"""
    Send the chat request to the model
    - Handle asynchronous responses
    - Handle streaming responses
    - Handle tool calls
"""
async def send_chat_request(messages):
    
    # Step 1: send the conversation and available functions to the model
    stream_response1 = await client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        tools=get_tools(),
        tool_choice="auto",
        temperature=0.1,
        top_p=0.95,
        max_tokens=4096,
        stream=True
    )

    # Convert the stream response to a list
    stream_response1_list = [item async for item in stream_response1]
    
    tool_calls = [] # Accumulator for tool calls to process later; 
    full_delta_content = "" # Accumulator for delta content to process later

    # Process the stream response for tool calls and delta content
    for chunk in stream_response1_list:
        delta = chunk.choices[0].delta if chunk.choices and chunk.choices[0].delta is not None else None

        if delta and delta.content:
            full_delta_content += delta.content
            
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
    if not tool_calls and full_delta_content:
        messages.append({ "role": "assistant", "content": full_delta_content })

        # Convert the list to a stream to return as a response
        async def list_to_stream():
            for item in stream_response1_list:
                yield item

        return list_to_stream()
    elif tool_calls:
        # Extend conversation by appending the tool calls to the messages
        messages.append({ "role": "assistant", "tool_calls": tool_calls })
        
        # Map of function names to the actual functions
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

        stream_response2 = await client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
            top_p=0.95,
            max_tokens=4096,
            stream=True,
        )
        return stream_response2

"""
    Format the response for the stream
    - Use case: Fit an expected response payload format to send to a web client chat UI
"""
def format_stream_response(chatCompletionChunk):
    response_obj = {
        "id": chatCompletionChunk.id,
        "model": chatCompletionChunk.model,
        "created": chatCompletionChunk.created,
        "object": chatCompletionChunk.object,
        "choices": [{
            "messages": []
        }]
    }

    if len(chatCompletionChunk.choices) > 0:
        delta = chatCompletionChunk.choices[0].delta
        if delta:
            if hasattr(delta, "context"):
                messageObj = {
                    "role": "tool",
                    "content": json.dumps(delta.context)
                }
                response_obj["choices"][0]["messages"].append(messageObj)
                return response_obj
            if delta.role == "assistant" and hasattr(delta, "context"):
                messageObj = {
                    "role": "assistant",
                    "context": delta.context,
                }
                response_obj["choices"][0]["messages"].append(messageObj)
                return response_obj
            else:
                if delta.content:
                    messageObj = {
                        "role": "assistant",
                        "content": delta.content,
                    }
                    response_obj["choices"][0]["messages"].append(messageObj)
                    return response_obj
    return {}

"""
    Stream the chat request
    - Sends the chat request to the model and waits for the response
    - Returns an async generator to stream the response
"""
async def stream_chat_request(messages):
    response = await send_chat_request(messages)
    
    async def generate():
        async for completionChunk in response:
            await asyncio.sleep(0.1) # smooth out the stream
            yield format_stream_response(completionChunk)

    return generate()

"""
    Process the chat response
    - If in a Client/Server environment, this function would be on the client and receive the response from the server
    - It would then need to parse the payload and display the response in the chat UI
    - In this example, we simply print the response to the console instead as this is a standalone script
"""
async def process_chat_response(async_generator):
    async for result in async_generator:
        content = result.get('choices', [{}])[0].get('messages', [{}])[0].get('content')
        if content:
            print(content, end="")
    print()


"""
    Chat
    - The main chat loop
    - Handles the user input, sends the chat request, and processes the chat response
"""
async def chat(messages) -> Tuple[Any, bool]:

    # User's input
    user_input = get_user_input()
    if not user_input:
        return False
    messages.append({"role": "user", "content": user_input})

    # Send the chat request
    async_generator = await stream_chat_request(messages)
    
    # Assistant's response
    print("Assistant:> ", end="")
    await process_chat_response(async_generator) # Process the chat response

    return True

# Initialize the messages
messages = init_messages()

async def main() -> None:

    chatting = True
    while chatting:
        chatting = await chat(messages)

if __name__ == "__main__":
    asyncio.run(main())