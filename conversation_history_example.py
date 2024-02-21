import os
from openai import AzureOpenAI
import json

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)


# Example function hard coded to return the expected response from a db call
# In production, this could be your backend API or an external API
def get_conversation_history():
    """Get the conversation history from a data source"""
    # Assume the conversation history is retrieved from a data source such as CosmosDB or a storage account
    # Possibly all parameters for user id from the user input, api/query requirements, etc. could be passed here.
    # In this example, we'll use a demo conversation history JSON
    with open("conversation_history.json", "r") as file:
        conversation_history = json.load(file)
    return json.dumps(conversation_history)

def summarize_conversation_history():
    """Summarize the conversation history"""
    # Possibly all parameters for user id from the user input, api/query requirements, etc. could be passed here.
    return get_conversation_history()

def generate_prompt_suggestions():
    """Provide chat suggestions based on our conversation history"""

    # Possibly all parameters for user id from the user input, api/query requirements, etc. could be passed here.
    return get_conversation_history()



def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
        { 
            "role": "system", 
            "content": """
                You are a helpful assistant designed to output JSON.
                Only use the functions you have been provided with.
                Adhere to the descriptions for the functions/tools provided.

                # Tools available:
                - summarize_conversation_history, 
                    This function retrieves the conversation history from a data source. 
                    Summarize the conversation history into a concise paragraph. Limit to 100 words. 
                    At most 5 sentences; if you use bullets, at most 5 bullets. 
                    Begin the summary with "In the conversation history, we discussed...".
                - generate_prompt_suggestions, 
                    Provides prompt suggestions based on the conversation history, return a json array, with one to 5 word suggestions. 
                    Limit the suggestions to 6 total.
                    Always include these first: ["Review academic dashboard" , "Apply for classes", "Practice an exam question"]
            """
        },
        {
            "role": "user",
            "content": "Summarize our chat history. And also provide chat suggestions based on our chat history.",
        },
        # {
        #     "role": "user",
        #     "content": "Summarize our chat history."
        # },
        # {
        #     "role": "user",
        #     "content": "Provide chat suggestions based on our chat history.",
        # },
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "summarize_conversation_history",
                "description": "Summarizes the conversation history.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_prompt_suggestions",
                "description": "Provides prompt suggestions based on the conversation history.",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        response_format={ "type": "json_object" },
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "summarize_conversation_history": summarize_conversation_history,
            "generate_prompt_suggestions": generate_prompt_suggestions,
        } 
        messages.append(response_message)  # extend conversation with assistant's reply
        
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_response = function_to_call()
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
            response_format={ "type": "json_object" },
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
    

# print(run_conversation())
result = run_conversation()

# from pprint import pprint
# pprint(vars(result))

message_content = result.choices[0].message.content
print(message_content)
