import inspect
import json
import os
from dotenv import load_dotenv
import openai

def check_args(function, args):
    """
    Check if the correct arguments are provided to a function.
    - Uses the inspect module to get the function signature
    - Compares the function signature with the provided arguments

    Args:
        function (callable): The function to check the arguments for.
        args (list): The arguments provided to the function.

    Returns:
        bool: True if the correct arguments are provided, False otherwise.

    """
    sig = inspect.signature(function)
    params = sig.parameters

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True


def get_function_and_args(tool_call, available_functions):
    """
    Retrieves the function and its arguments based on the tool call.
    Verifies if the function exists and has the correct number of arguments.

    Args:
        tool_call (ToolCall): The tool call object containing the function name and arguments.
        available_functions (dict): A dictionary of available functions.

    Returns:
        tuple: A tuple containing the function to call and its arguments.
            If the function or arguments are invalid, returns an error message and None.
    """
    # verify function exists
    if tool_call.function.name not in available_functions:
        return "Function " + tool_call.function.name + " does not exist", None
    function_to_call = available_functions[tool_call.function.name]

    # verify function has correct number of arguments
    function_args = json.loads(tool_call.function.arguments)
    if check_args(function_to_call, function_args) is False:
        return "Invalid number of arguments for function: " + tool_call.function.name, None

    return function_to_call, function_args

def setup_client():
    """
    Sets up the client based on the API_HOST environment variable.
    - Setup the client to use either Azure, OpenAI or Ollama API
    - Uses the environment variables
    - Returns the client and deployment name

    Returns:
        client: The OpenAI client object.
        DEPLOYMENT_NAME: The name of the deployment.
    """
    load_dotenv()
    API_HOST = os.getenv("API_HOST")

    if API_HOST == "azure":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
        DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    elif API_HOST == "openai":
        client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))
        DEPLOYMENT_NAME = os.getenv("OPENAI_MODEL")
    elif API_HOST == "ollama":
        client = openai.AsyncOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="nokeyneeded",
        )
        DEPLOYMENT_NAME = os.getenv("OLLAMA_MODEL")
    
    return client, DEPLOYMENT_NAME

def setup_async_client():
    """
    Sets up the async client based on the API_HOST environment variable.
    - Setup the client to use either Azure, OpenAI or Ollama API
    - Uses the Async client to handle asynchronous requests
    - Uses the environment variables
    - Returns the client and deployment name

    Returns:
        client: The OpenAI client object.
        DEPLOYMENT_NAME: The name of the deployment.
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
    return client, DEPLOYMENT_NAME
