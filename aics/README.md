
# AI Coding Assistant

This project implements a UI-agnostic AI-assisted coding tool with support for multiple AI providers and models. It includes features such as code analysis, generation, explanation, RAG (Retrieval-Augmented Generation), and dataset analysis.

## Features

- Code analysis
- Code generation
- Code explanation
- RAG creation and querying
- Dataset loading and analysis
- Support for multiple AI providers (Groq, OpenRouter, Ollama)
- CLI, API, and Web interfaces

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `AI_PROVIDER`: The AI provider to use (groq, openrouter, ollama)
   - `AI_MODEL`: The model to use for the selected provider

## Usage

### CLI

- Analyze code: `python main.py cli analyze <file_path>`
- Generate code: `python main.py cli generate "<prompt>"`
- Explain code: `python main.py cli explain <file_path>`
- Create RAG: `python main.py cli create-rag <file_path>`
- Query RAG: `python main.py cli query-rag "<query>"`
- Load dataset: `python main.py cli load-dataset <dataset_path>`
- Analyze dataset row: `python main.py cli analyze-dataset-row --iterations <num> --row-index <index>`

### API

Run the API server: `python main.py api`

### Web Interface

Run the web server: `python main.py web`

## Testing

Run unit tests: `python -m unittest discover tests`

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
