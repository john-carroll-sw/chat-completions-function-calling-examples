# Function Calling Examples using the Chat Completions API

### Description

This repository contains simple examples of using function calling with the Chat Completions API.

These basic examples in Python are designed to help those interested in learning about function calling. These examples serve as an introduction to the concept and its applications.

The repository includes examples of parallel and sequential function calling, generating prompt suggestions, conversation summarization, and timed activation of assistant behavior. These examples aim to provide a practical understanding of function calling.

For those seeking something more advanced, the repository also contains a more complex example that involves the integration of function calling, asynchronous programming, and streaming responses within a chat loop. It also covers the formatting and handling of server-client payloads, which is a crucial aspect of creating a chatbot experience.

If you are unfamiliar with function calling here are some docs to get acquainted:

- [Prompting Guide / function_calling](https://www.promptingguide.ai/applications/function_calling)
- [OpenAI / function-calling](https://platform.openai.com/docs/guides/function-calling)
- [Azure OpenAI / function-calling](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling?tabs=python)
- [Ollama / functions](https://js.langchain.com/docs/integrations/chat/ollama_functions)

Fundamental Steps for Function Calling: 

1. Call the model with the user query and a set of functions defined in the functions parameter.
2. The model can choose to call a function; if so, the content will be a stringified JSON object adhering to your custom schema (note: the model may generate invalid JSON or hallucinate parameters).
3. Parse the string into JSON in your code, and call your function with the provided arguments if they exist.
4. Call the model again by appending the function response as a new message, and let the model summarize the results back to the user.

## Files

- [`func_get_weather.py`](./func_get_weather.py): (**Start here!**) This is a simple program that has a single native function 'get_current_weather' defined. The model is made aware of this function. Given the user's input, it tells us to call the function/tool. Our code invokes our function and then we add the function's response back to the model, supplying it with additional context. Finally, the assistant responds to the user with the temperature in San Francisco, Tokyo, and Paris. This also utilizes **parallel** <u>function calling</u>.
- [`func_get_weather_streaming.py`](./func_get_weather_streaming.py): This is an example of how to <u>**stream**</u> the response from the model while also checking if the model wanted to make a function/tool call. It extends the 'func_get_weather' example.
- [`func_conversation_history.py`](./func_conversation_history.py): This is a simple program that showcases some <u>semantic functionality</u> for: 1) **summarizing conversation history**, 2) providing **prompt suggestions** based on conversation history. This also shows how to utilize using **JSON Mode**.
- [`funct_sequential_calls`](./func_sequential_calls.py): This serves as an example of **sequential** function calling. In certain scenarios, achieving the desired output requires calling multiple functions in a specific order, where the output of one function becomes the input for another function. By giving the model adequate tools, context and instructions, it can achieve complex operations by breaking them down into smaller, more manageable steps.
- [`func_timing_count_chat.py`](./func_timing_count_chat.py): This example shows how to Do 'X' every 'frequency'. Shows how to <u>**manage state**</u> outside the conversation. There is a function that increments a counter using <u>function calling</u>, counting user inputs before the assistant says something specific to a user. Also shows how to do something once every week by checking if it has been a week and then editing system prompt.
- [`func_async_streaming_chat.py`](./func_async_streaming_chat.py): an example script that demonstrates handling of <u>asynchronous</u> client calls and <u>streaming</u> responses within a <u>chat loop</u>. It supports <u>function calling</u>, enabling dynamic and interactive conversations. This script is designed to provide a practical example of managing complex interactions in a chat-based interface.
- [`func_async_streaming_chat_server.py`](./func_async_streaming_chat_server.py): (**Most complicated**) an extension of the 'func_async_streaming_chat' script. It not only handles <u>asynchronous</u> client calls, <u>function calling</u>, and <u>streaming</u> responses within a <u>chat loop</u>, but also demonstrates an example of how to <u>format and handle server-client</u> payloads effectively. This script provides a practical example of managing complex interactions in a chat-based interface while ensuring proper communication between the server and client.


## Usage

To use this project, follow these steps:

1. Clone the repository: `git clone <repository-url>`
2. Navigate to the project directory: `cd <project-directory>`
3. Set up a Python virtual environment and activate it:

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

4. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

5. Copy the `.env.sample` file to a new file called `.env`:

    ```bash
    cp .env.sample .env
    ```

6. Configure the environment settings per your usage:

   - For Azure OpenAI, create an Azure OpenAI gpt-3.5 or gpt-4 deployment, and customize the `.env` file with your Azure OpenAI endpoint and deployment id.

        ```bash
        API_HOST=azure
        AZURE_OPENAI_ENDPOINT=https://<YOUR-AZURE-OPENAI-SERVICE-NAME>.openai.azure.com
        AZURE_OPENAI_API_KEY=<YOUR-AZURE-OPENAI-API-KEY>
        AZURE_OPENAI_API_VERSION=2024-03-01-preview
        AZURE_OPENAI_DEPLOYMENT_NAME=<YOUR-AZURE-DEPLOYMENT-NAME>
        AZURE_OPENAI_MODEL=gpt-4
        ```

   - For OpenAI.com, customize the `.env` file with your OpenAI API key and desired model name.

        ```bash
        API_HOST=openai
        OPENAI_KEY=<YOUR-OPENAI-API-KEY>
        OPENAI_MODEL=gpt-3.5-turbo
        ```

   - For Ollama, customize the `.env` file with your Ollama endpoint and model name (any model you've pulled).

        ```bash
        API_HOST=ollama
        OLLAMA_ENDPOINT=http://localhost:11434/v1
        OLLAMA_MODEL=llama2
        ```

7. Run the project: `python <program.py>`

To open this project in VS Code:

1. Navigate to the parent of the project directory: `cd ..\<project-directory>`
2. Open in VS Code: `code <project-folder-name>`

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these guidelines:

1. Fork the repository
2. Create a new branch: `git checkout -b <branch-name>`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin <branch-name>`
5. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).
