# Lesson 7: AI Integration: OpenAI API and Prompt Engineering

## 1. Introduction to AI Integration (10 minutes)

In this lesson, we'll dive into integrating artificial intelligence into our coding assistant tool. We'll focus on using OpenAI's GPT models, which are powerful language models capable of understanding and generating human-like text, including code.

### Overview of OpenAI's GPT models

GPT (Generative Pre-trained Transformer) models are a family of large language models developed by OpenAI. These models have been trained on vast amounts of text data and can perform a wide range of natural language processing tasks, including code generation and understanding.

Key points about GPT models:
- They use transformer architecture, which allows them to handle long-range dependencies in text.
- They can be fine-tuned for specific tasks, such as code completion or bug fixing.
- The latest models (as of this writing) include GPT-3.5 and GPT-4, with GPT-4 being the most advanced.

### Explanation of prompt engineering

Prompt engineering is the practice of designing and refining input prompts to get the best possible output from language models. In the context of our coding assistant, this means crafting prompts that will result in accurate and helpful code suggestions or completions.

Key aspects of prompt engineering:
- Clear and specific instructions
- Providing relevant context
- Using examples (few-shot learning)
- Structuring prompts for consistent outputs

### Goals of this lesson

By the end of this lesson, you will be able to:
1. Set up and use the OpenAI API in your Python project
2. Design effective prompts for code-related tasks
3. Implement streaming responses for better user experience
4. Handle API rate limits and errors gracefully
5. Create a fallback system for offline use

Let's start by looking at our project structure:

```
aider/
│
├── src/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── openai_integration.py
│   │   ├── prompt_engineering.py
│   │   └── fallback_system.py
│   │
│   ├── cli/
│   │   └── main.py
│   │
│   └── utils/
│       └── config.py
│
├── tests/
│   └── test_ai_integration.py
│
├── .env
├── requirements.txt
└── README.md
```

## 2. Setting up OpenAI API Integration (15 minutes)

Let's start by setting up the OpenAI API integration in our project.

First, we need to install the required libraries. Add the following to your `requirements.txt` file:

```
openai==0.27.0
python-dotenv==0.19.2
```

Now, let's create the `openai_integration.py` file:

```python
# src/ai/openai_integration.py

import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_completion(prompt, model="gpt-3.5-turbo"):
    """
    Get a completion from the OpenAI API.
    
    Args:
        prompt (str): The input prompt for the API.
        model (str): The model to use for completion.
    
    Returns:
        str: The generated completion.
    """
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # Use 0 for more deterministic outputs
    )
    return response.choices[0].message["content"]

# Example usage
if __name__ == "__main__":
    prompt = "Write a Python function to calculate the factorial of a number."
    result = get_completion(prompt)
    print(result)
```

To use this integration, create a `.env` file in your project root and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

Make sure to add `.env` to your `.gitignore` file to keep your API key secure.

## 3. Designing Effective Prompts for Code Generation (30 minutes)

Now that we have basic API integration, let's focus on designing effective prompts for code-related tasks. We'll create a `PromptTemplate` class to help us structure our prompts consistently.

Create the `prompt_engineering.py` file:

```python
# src/ai/prompt_engineering.py

class PromptTemplate:
    def __init__(self, template):
        self.template = template
    
    def format(self, **kwargs):
        return self.template.format(**kwargs)

# Prompt templates for various coding tasks
code_generation_prompt = PromptTemplate("""
You are an AI programming assistant. Your task is to generate Python code based on the following request:

Request: {user_request}

Current code context:
```python
{current_code}
```

Please provide only the Python code as your response, without any additional explanation.
""")

code_explanation_prompt = PromptTemplate("""
Explain the following Python code in simple terms:

```python
{code_to_explain}
```

Provide a brief overview followed by a step-by-step explanation.
""")

bug_fixing_prompt = PromptTemplate("""
The following Python code has a bug. Identify and fix the bug:

```python
{buggy_code}
```

Explain the bug and provide the corrected code.
""")

# Example usage
if __name__ == "__main__":
    from openai_integration import get_completion
    
    user_request = "Create a function to find the nth Fibonacci number"
    current_code = "# No existing code"
    
    prompt = code_generation_prompt.format(
        user_request=user_request,
        current_code=current_code
    )
    
    result = get_completion(prompt)
    print(result)
```

This setup allows us to create structured prompts for different coding tasks. The `PromptTemplate` class makes it easy to reuse and modify prompts as needed.

## 4. Implementing Streaming Responses (20 minutes)

For a better user experience, especially with longer responses, we can implement streaming. This allows us to display the AI's response as it's being generated, rather than waiting for the entire response to complete.

Let's update our `openai_integration.py` file to include a streaming function:

```python
# src/ai/openai_integration.py

# ... (previous code remains the same)

def stream_completion(prompt, model="gpt-3.5-turbo"):
    """
    Stream a completion from the OpenAI API.
    
    Args:
        prompt (str): The input prompt for the API.
        model (str): The model to use for completion.
    
    Yields:
        str: Chunks of the generated completion.
    """
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        stream=True
    )
    
    collected_messages = []
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        collected_messages.append(chunk_message)
        content = chunk_message.get('content', '')
        if content:
            yield content

# Example usage
if __name__ == "__main__":
    prompt = "Write a Python function to calculate the sum of squares from 1 to n."
    for part in stream_completion(prompt):
        print(part, end='', flush=True)
```

This streaming implementation allows us to display the response in real-time, which can be particularly useful for longer code generations or explanations.

## 5. Handling Rate Limits and API Errors (15 minutes)

When working with external APIs, it's crucial to handle rate limits and other potential errors gracefully. Let's implement a retry mechanism with exponential backoff for our API calls.

Update the `openai_integration.py` file:

```python
# src/ai/openai_integration.py

import time
import random
import openai

# ... (previous code remains the same)

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

def api_call_with_retry(func, max_retries=5):
    """
    Execute an API call with retry logic.
    
    Args:
        func (callable): The API call function to execute.
        max_retries (int): Maximum number of retries.
    
    Returns:
        The result of the API call.
    
    Raises:
        APIError: If max retries are exceeded.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except openai.error.RateLimitError as e:
            if attempt == max_retries - 1:
                raise APIError(f"Rate limit exceeded: {str(e)}")
            sleep_time = (2 ** attempt) + random.random()
            print(f"Rate limit hit. Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        except openai.error.APIError as e:
            raise APIError(f"OpenAI API error: {str(e)}")

# Update get_completion and stream_completion to use api_call_with_retry

def get_completion(prompt, model="gpt-3.5-turbo"):
    def api_call():
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        return response.choices[0].message["content"]
    
    return api_call_with_retry(api_call)

def stream_completion(prompt, model="gpt-3.5-turbo"):
    def api_call():
        messages = [{"role": "user", "content": prompt}]
        return openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
            stream=True
        )
    
    response = api_call_with_retry(api_call)
    
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        content = chunk_message.get('content', '')
        if content:
            yield content

# Example usage
if __name__ == "__main__":
    try:
        prompt = "Write a Python function to find the greatest common divisor of two numbers."
        result = get_completion(prompt)
        print(result)
    except APIError as e:
        print(f"An error occurred: {str(e)}")
```

This implementation adds error handling and retry logic to our API calls, making our integration more robust and resilient to temporary issues.

## 6. Creating a Fallback System for Offline Mode (20 minutes)

To ensure our coding assistant can still provide some functionality when offline or when API calls fail, let's implement a fallback system with caching.

Create the `fallback_system.py` file:

```python
# src/ai/fallback_system.py

import json
import os
from .openai_integration import get_completion, APIError

class AICompletionSystem:
    def __init__(self, cache_file="completion_cache.json"):
        self.online = True
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        if self.online:
            try:
                response = get_completion(prompt, model)
                self.cache[prompt] = response
                self.save_cache()
                return response
            except APIError:
                self.online = False
                print("Switching to offline mode due to API error.")
        
        if prompt in self.cache:
            print("Using cached response.")
            return self.cache[prompt]
        else:
            return "Sorry, I'm offline and don't have a cached response for this prompt."

# Example usage
if __name__ == "__main__":
    ai_system = AICompletionSystem()
    
    prompts = [
        "Write a Python function to check if a number is prime.",
        "Explain the concept of recursion in programming.",
        "Write a Python function to check if a number is prime.",  # Repeated to test caching
    ]
    
    for prompt in prompts:
        print(f"Prompt: {prompt}")
        result = ai_system.get_completion(prompt)
        print(f"Response: {result}\n")
```

This fallback system allows our coding assistant to work offline by caching responses and falling back to cached results when the API is unavailable.

## 7. Practical Exercise (30 minutes)

Now that we have all the components in place, let's create a simple CLI interface for our coding assistant that incorporates all these features.

Update the `main.py` file:

```python
# src/cli/main.py

import click
from src.ai.fallback_system import AICompletionSystem
from src.ai.prompt_engineering import (
    code_generation_prompt,
    code_explanation_prompt,
    bug_fixing_prompt
)

ai_system = AICompletionSystem()

@click.group()
def cli():
    """AI-powered coding assistant CLI"""
    pass

@cli.command()
@click.argument('task')
@click.option('--code', help='Existing code context')
def generate(task, code):
    """Generate code based on a given task"""
    prompt = code_generation_prompt.format(
        user_request=task,
        current_code=code or "# No existing code"
    )
    result = ai_system.get_completion(prompt)
    click.echo(result)

@cli.command()
@click.argument('code')
def explain(code):
    """Explain the given code"""
    prompt = code_explanation_prompt.format(code_to_explain=code)
    result = ai_system.get_completion(prompt)
    click.echo(result)

@cli.command()
@click.argument('code')
def fix(code):
    """Fix bugs in the given code"""
    prompt = bug_fixing_prompt.format(buggy_code=code)
    result = ai_system.get_completion(prompt)
    click.echo(result)

if __name__ == '__main__':
    cli()
```

To run this CLI, you can use commands like:

```bash
python src/cli/main.py generate "Create a function to find the nth Fibonacci number"
python src/cli/main.py explain "def factorial(n): return 1 if n == 0 else n * factorial(n-1)"
python src/cli/main.py fix "def divide(a, b): return a / b"
```

This exercise brings together all the components we've created in this lesson, demonstrating how they can be used in a practical application.

## 8. Discussion and Q&A (10 minutes)

Let's review the key concepts we've covered in this lesson:

1. Setting up OpenAI API integration
2. Designing effective prompts for code-related tasks
3. Implementing streaming responses for better user experience
4. Handling API rate limits and errors
5. Creating a fallback system for offline use

Some potential improvements and extensions to consider:

- Implement more sophisticated caching mechanisms (e.g., using a database instead of a JSON file)
- Add support for multiple AI models and create a model selection algorithm
- Improve prompt engineering by fine-tuning prompts based on user feedback
- Implement a local fallback model for offline use (e.g., a smaller model that can run on the user's machine)

Questions for discussion:
1. How might we adapt this system to work with other AI APIs (e.g., Google's PaLM, Anthropic's Claude, or Hugging Face's models)?
2. What are some potential ethical considerations when using AI for code generation and assistance?
3. How can we ensure the security and privacy of code snippets sent to the AI API?
4. What strategies could we employ to make our prompts more effective for code-related tasks?
5. How might we extend this system to handle more complex coding tasks, such as refactoring or test generation?

## 9. Additional Concepts and Advanced Topics

While we've covered the basics of AI integration for our coding assistant, there are several advanced topics we could explore in future lessons:

### 9.1 Context-Aware Code Completion

Implement a system that maintains a context of the user's current coding session, allowing for more accurate and relevant code completions.

```python
# src/ai/context_aware_completion.py

class CodingContext:
    def __init__(self):
        self.current_file = None
        self.open_files = {}
        self.recent_completions = []

    def update_file(self, filename, content):
        self.current_file = filename
        self.open_files[filename] = content

    def add_completion(self, completion):
        self.recent_completions.append(completion)
        if len(self.recent_completions) > 5:
            self.recent_completions.pop(0)

    def get_context_prompt(self):
        context = f"Current file: {self.current_file}\n\n"
        context += "Recent completions:\n"
        for comp in self.recent_completions:
            context += f"- {comp}\n"
        context += f"\nCurrent file content:\n{self.open_files[self.current_file]}"
        return context

# Usage in main.py
coding_context = CodingContext()

@cli.command()
@click.argument('filename')
@click.argument('content')
def update_context(filename, content):
    """Update the current coding context"""
    coding_context.update_file(filename, content)
    click.echo(f"Updated context for {filename}")

@cli.command()
@click.argument('task')
def complete(task):
    """Get a context-aware code completion"""
    context = coding_context.get_context_prompt()
    prompt = f"{context}\n\nTask: {task}\n\nComplete the code:"
    result = ai_system.get_completion(prompt)
    coding_context.add_completion(result)
    click.echo(result)
```

### 9.2 Fine-tuning for Specific Coding Tasks

Explore the process of fine-tuning a model on a dataset of coding tasks to improve its performance for specific languages or frameworks.

```python
# src/ai/fine_tuning.py

import openai

def prepare_fine_tuning_data(data_file):
    # Process your dataset and convert it to the required format
    # This is a simplified example
    with open(data_file, 'r') as f:
        data = f.readlines()
    
    formatted_data = []
    for line in data:
        task, code = line.strip().split('|')
        formatted_data.append({
            "prompt": f"Task: {task}\n\nCode:",
            "completion": f" {code}"
        })
    
    return formatted_data

def start_fine_tuning(base_model, training_file):
    response = openai.FineTune.create(
        training_file=training_file,
        model=base_model,
        n_epochs=3,
        batch_size=4,
        learning_rate_multiplier=0.1
    )
    return response

# Usage
data = prepare_fine_tuning_data("coding_tasks.txt")
training_file = openai.File.create(
    file=open("formatted_data.jsonl", "rb"),
    purpose='fine-tune'
)
fine_tuning_job = start_fine_tuning("gpt-3.5-turbo", training_file.id)
print(f"Fine-tuning job started: {fine_tuning_job.id}")
```

### 9.3 Implementing a Local Fallback Model

For improved offline capabilities, we could implement a local, smaller model that can run on the user's machine when the main API is unavailable.

```python
# src/ai/local_fallback_model.py

from transformers import AutoTokenizer, AutoModelForCausalLM

class LocalModel:
    def __init__(self, model_name="codegen-350M-mono"):
        self.tokenizer = AutoTokenizer.from_pretrained(f"Salesforce/{model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(f"Salesforce/{model_name}")

    def generate(self, prompt, max_length=100):
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        output = self.model.generate(input_ids, max_length=max_length)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

# Update AICompletionSystem in fallback_system.py
class AICompletionSystem:
    def __init__(self, cache_file="completion_cache.json"):
        # ... (previous init code) ...
        self.local_model = LocalModel()

    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        if self.online:
            # ... (previous online code) ...
        
        if prompt in self.cache:
            print("Using cached response.")
            return self.cache[prompt]
        else:
            print("Using local fallback model.")
            return self.local_model.generate(prompt)
```

### 9.4 Implementing a Plugin System

To make our coding assistant more extensible, we could implement a plugin system that allows users to add custom functionality or integrate with specific tools or frameworks.

```python
# src/plugins/plugin_manager.py

import importlib
import os

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module = importlib.import_module(f"{self.plugin_dir}.{module_name}")
                if hasattr(module, "register_plugin"):
                    plugin_info = module.register_plugin()
                    self.plugins[plugin_info["name"]] = plugin_info["func"]

    def execute_plugin(self, plugin_name, *args, **kwargs):
        if plugin_name in self.plugins:
            return self.plugins[plugin_name](*args, **kwargs)
        else:
            raise ValueError(f"Plugin '{plugin_name}' not found")

# Example plugin file: plugins/git_integration.py
def git_status():
    # Implementation of git status
    pass

def register_plugin():
    return {
        "name": "git_status",
        "func": git_status
    }

# Usage in main.py
plugin_manager = PluginManager()

@cli.command()
@click.argument('plugin_name')
@click.argument('args', nargs=-1)
def run_plugin(plugin_name, args):
    """Run a plugin command"""
    result = plugin_manager.execute_plugin(plugin_name, *args)
    click.echo(result)
```

## 10. Conclusion

In this lesson, we've explored the integration of AI into our coding assistant tool, focusing on the OpenAI API and effective prompt engineering. We've implemented key features such as:

1. Basic API integration
2. Structured prompt templates
3. Streaming responses
4. Error handling and retries
5. Offline fallback with caching

We've also discussed several advanced topics that could be explored in future lessons to enhance our coding assistant further.

As you continue to develop your AI-powered coding assistant, remember to consider the ethical implications of AI in software development, prioritize user privacy and data security, and continually refine your prompts and models based on user feedback and real-world usage.

## 11. Further Reading and Resources

1. [OpenAI API Documentation](https://platform.openai.com/docs/introduction)
2. [Prompt Engineering Guide](https://www.promptingguide.ai/)
3. [Hugging Face Transformers Library](https://huggingface.co/transformers/)
4. [Ethics in AI-Assisted Coding](https://www.acm.org/binaries/content/assets/public-policy/2020_usacm_statement_ai_se.pdf)
5. [Fine-tuning GPT models](https://platform.openai.com/docs/guides/fine-tuning)

In the next lesson, we'll explore advanced code analysis and refactoring techniques, building upon the AI integration we've implemented here.