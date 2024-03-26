import os
import asyncio
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from enum import Enum
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# User type and User class
class UserType(Enum):
    FREE = 0
    BASIC = 1
    PREMIUM = 2

class User:
    def __init__(self, user_type):
        self.type = user_type


# Function to increment the question counter
def increment_question_counter():
    global question_counter
    question_counter += 1
    return str(question_counter)


# List of tools available to the model
def getTools():
    return [
        {
            "type": "function",
            "function": {
                "name": "increment_question_counter",
                "description": "This function increments the number of times a user has asked a question. It returns the current count for the question_counter.",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]


async def chat(messages, tools) -> bool:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return False
    except EOFError:
        print("\n\nExiting chat...")
        return False

    if user_input == "exit":
        print("\n\nExiting chat...")
        return False

    messages.append({"role": "user", "content": user_input})

    # Step 1: send the conversation and available functions to the model
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=1,
        max_tokens=400,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: check if the model wanted to call a function/tool
    if not tool_calls:
        bot_response = response_message.content
        messages.append({"role": "assistant", "content": bot_response})
        print(f"Assistant:> {bot_response}")

    else:
        messages.append(response_message)  # extend conversation with assistant's reply
        available_functions = { "increment_question_counter": increment_question_counter }
        
        for tool_call in tool_calls:

            # Note: the JSON response may not always be valid; be sure to handle errors
            function_name = tool_call.function.name
            if function_name not in available_functions:
                return "Function " + function_name + " does not exist"
        
            # Step 3: call the function with arguments if any
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            # Step 4: send the info for each tool call and its response to the model
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
        second_response_message = second_response.choices[0].message
        second_bot_response = second_response_message.content
        messages.append({"role": "assistant", "content": second_bot_response})
        print(f"Assistant:> {second_bot_response}")

    return True

question_counter = 0

async def main() -> None:
    # Set up prior to chat
    global question_counter
    user = User(UserType.PREMIUM)
    today = datetime.now() # is the current date
    last_suggestion_date = datetime(2022, 1, 1)  # Replace with actual date from database or backend

    # Initial messages to start the conversation
    messages = []
    messages.append(
        {
            "role": "system",
            "content": """
                You are a helpful assistant.
                When the user explicitly asks a question [three times] meaning the question_counter has reached 3, tell the user: "You are awesome!".

                # Tools available:
                - increment_question_counter,
                  This function increments the times a user has asked a question. It returns the current count for the question_counter.
            """
        }
    )

    # Augment the system prompt if meeting frequency criteria
    if user.type == UserType.PREMIUM and today - last_suggestion_date >= timedelta(weeks=1):
        # update the last_suggestion_date in the db to today, then augment the system prompt:
        messages[0]["content"] += "Tell the user at the start of chat: You are super awesome!"

    tools = getTools()

    chatting = True
    while chatting:
        chatting = await chat(messages, tools)


if __name__ == "__main__":
    asyncio.run(main())