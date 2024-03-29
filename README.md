# Function Calling Examples in Azure Open AI

## Description

This repository contains simple examples of using function calling using the Chat Completions API for AOAI. If using the OAI client, change the client accordingly.

## Files

- `weather_example`: This is a simple program that has a single function `get_current_weather` defined. The model says to call the function multiple times(parellel funciton calling), and after sending the function response back to the model, it decides the next step. It responds with a user-facing message which tells the user the temperature in San Francisco, Tokyo, and Paris.
- `weather_example_streaming.py`: This is an example of how to stream the response from the model while also checking if the model wanted to make a function/tool call. It extends the `weather_example`.
- `counter_example`: This example shows how to Do 'X' every 'frequency'. Shows how to increment a counter using function calling, counting user inputs before the assistant says something specific to a user. Also shows how to do something once every week by checking if it has been a week and then editing system prompt.
- `conversation_history_example`: This is a simple program that showcases some functionality for doing two things: 1) summarizing conversation history, 2) providing prompt suggestions based on conversation history.


## Usage

To use this project, follow these steps:

1. Clone the repository: `git clone <repository-url>`
2. Navigate to the project directory: `cd <project-directory>`
3. Run the project: `python <program.py>`

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
