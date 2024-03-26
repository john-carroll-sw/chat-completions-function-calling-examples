# Project Name
Function Calling Examples

## Description

This repository contains the basic examples of function calling using the Chat Completions API.

## Files

- `counter_example`: This example shows how to Do 'X' every 'frequency'. Shows how to increment a counter using function calling, counting user inputs before the assistant says something specific to a user. Also shows how to do something once every week by checking if it has been a week and then editing system prompt.
- `weather_example`: This is a simple program that has a single function get_current_weather is defined. The model calls the function multiple times, and after sending the function response back to the model, it decides the next step. It responds with a user-facing message which was telling the user the temperature in San Francisco, Tokyo, and Paris. Depending on the query, it may choose to call a function again.
- `conversation_history_example`: This is a simple program that showcases some functionality for doing two things: 1) summarizing conversation history, 2) providing prompt suggestions based on conversation history.


## Usage

To use this project, follow these steps:

1. Clone the repository: `git clone <repository-url>`
2. Navigate to the project directory: `cd <project-directory>`
3. Run the project: `<command-to-run-the-project>`

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these guidelines:

1. Fork the repository
2. Create a new branch: `git checkout -b <branch-name>`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin <branch-name>`
5. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).
