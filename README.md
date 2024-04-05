# Function Calling Examples using the Chat Completions API

### Description

This repository contains simple examples of using function calling with the Chat Completions API. If you are unfamiliar with function calling here are some docs to get acquainted:
- OpenAI | https://platform.openai.com/docs/guides/function-calling
- Azure OpenAI | https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling?tabs=python

The samples support multiple clients including OpenAI, AzureOpenAI, and Ollama. Please change the client using the `env.sample` to your needs.

## Files

- `func_get_weather`: (**Start here!**) This is a simple program that has a single function 'get_current_weather' defined. The model says to call the function/tool multiple times(parellel <u>function calling</u>). Our code invokes our functions and then we send the function/tool's response back to the model supplying it with additional context provided by the 'tool'. It responds with a user-facing message which tells the user the temperature in San Francisco, Tokyo, and Paris.
- `func_get_weather_streaming`: This is an example of how to <u>stream</u> the response from the model while also checking if the model wanted to make a function/tool call. It extends the 'func_get_weather' example.
- `func_timing_count`: This example shows how to Do 'X' every 'frequency'. Shows how to <u>manage state</u> outside the conversation. There is a function that increments a counter using <u>function calling</u>, counting user inputs before the assistant says something specific to a user. Also shows how to do something once every week by checking if it has been a week and then editing system prompt.
- `func_conversation_history`: This is a simple program that showcases some <u>semantic functionality</u> for doing two things: 1) summarizing conversation history, 2) providing prompt suggestions based on conversation history.
- `func_async_streaming_chat`: an example script that demonstrates handling of <u>asynchronous</u> client calls and <u>streaming</u> responses within a <u>chat loop</u>. It supports <u>function calling</u>, enabling dynamic and interactive conversations. This script is designed to provide a practical example of managing complex interactions in a chat-based interface.
- `func_async_streaming_chat_server`: (**Most complicated**) an extension of the 'func_async_streaming_chat' script. It not only handles <u>asynchronous</u> client calls, <u>function calling</u>, and <u>streaming</u> responses within a <u>chat loop</u>, but also demonstrates an example of how to <u>format and handle server-client</u> payloads effectively. This script provides a practical example of managing complex interactions in a chat-based interface while ensuring proper communication between the server and client.


## Usage

To use this project, follow these steps:

1. Clone the repository: `git clone <repository-url>`
2. Navigate to the project directory: `cd <project-directory>`
3. Copy `.env.sample` to a new file called `.env` and configure the settings: `copy .env.sample .env`
4. Run the project: `python <program.py>`

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
