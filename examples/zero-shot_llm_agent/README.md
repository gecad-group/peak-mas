# Zero-shot LLM Agent Example

This example demonstrates how to create a simple agent using PEAK-MAS and Ollama Python Library.

## What the code does:

The PEAK-MAS framework allows interaction with other systems and frameworks, for this example we demonstrate a basic scenario where a agent is designed to answer a specific question using a generative text model as a tool through the use of the Ollama library.  The agent's behaviour is defined by a simple one-shot behaviour that describes which model and how the agent will interact with the large language model (LLM).

When the agent is executed it uses the phi3-mini model and generates with a predefined instruction a message to be printed in the log file of the agent. The prompt is essentially a request to generate a unique and creative Hello World message. The agent then receives the response from the LLM and prints it to the console for display.

The agent acts as a simple interface between the user and the LLM, this could allow, in more complex scenarios, users or other agents to have a better and more human-like communication.

## How to run the code:

1. Install the required dependencies:

Go to official ollama web page and follow the instructions to install the software.

https://ollama.com/

then install the ollama python library:

```bash
pip install ollama 
```

2. Run the agent example:

```bash
peak run -j agent@localhost agent.py
```
or
```bash
peak start mas.yaml
```
## Expected output:

The chatbot will print the response in the log file on the logs folder.

## How can I use this code?

If you want to use this code as a base for your project, you can copy the `agent.py` file and the `mas.yaml` file to your project and modify the `agent.py` file to implement your own logic. 

Also, with changing the prompt message and the LLM model by other model available on Ollama you can obtain different performance results.

With the PEAK-MAS and Ollama library you can create complex agents that can interact with the environment and other agents. If you want to know more about the PEAK-MAS and Ollama library you can check the documentation on the [PEAK-MAS](https://peak-project.github.io/peak-mas/) and [Ollama](https://ollama.readthedocs.io/en/latest/) websites.
