# Simple Chatbot Example

This example demonstrates how to create a simple chatbot agent using PEAK-MAS and Ollama Python Library.

## What the code does:

- The chatbot is a simple agent that can respond to a predefined prompt.
- The chatbot is implemented as a PEAK-MAS agent.
- The chatbot agent implements a simple One-Shot Behaviour that defines the LLM, for this example we use the phi3-mini model, to be used by the agent and a message that would be the prompt to be send to the LLM.
- The chatbot agent sends the prompt to the LLM model and receives the response.
- The chatbot agent prints the response to the console.

## How to run the code:

1. Install the required dependencies:

```bash
pip install ollama 
```

2. Run the chatbot example:

```bash
peak run -j bot@localhost bot.py
```
or
```bash
peak start mas.yaml
```
## Expected output:

The chatbot will print the response in the log file on the logs folder.

## How can I use this code?

If you want to use this code as a base for your project, you can copy the `bot.py` file and the `mas.yaml` file to your project and modify the `bot.py` file to implement your own logic. 

Also, with changing the prompt message and the LLM model by other model available on Ollama you can obtain different performance results.

With the PEAK-MAS and Ollama library you can create complex agents that can interact with the environment and other agents. If you want to know more about the PEAK-MAS and Ollama library you can check the documentation on the [PEAK-MAS](https://peak-project.github.io/peak-mas/) and [Ollama](https://ollama.readthedocs.io/en/latest/) websites.
