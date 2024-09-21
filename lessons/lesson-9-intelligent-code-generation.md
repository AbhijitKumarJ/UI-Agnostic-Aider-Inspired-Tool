# Lesson 9: Intelligent Code Generation and Completion

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Context-Aware Code Completion](#context-aware-code-completion)
4. [Code Snippet Generator](#code-snippet-generator)
5. [Function Docstring Generator](#function-docstring-generator)
6. [Intelligent Variable Naming System](#intelligent-variable-naming-system)
7. [Code Optimization Suggester](#code-optimization-suggester)
8. [Practical Exercise](#practical-exercise)
9. [Conclusion and Next Steps](#conclusion-and-next-steps)

## Introduction

In this lesson, we'll dive deep into intelligent code generation and completion techniques for our AI-assisted coding tool. We'll build upon the foundations we've established in previous lessons, particularly our work with the OpenAI API and prompt engineering. The goal is to create a sophisticated system that can understand context, generate relevant code snippets, and provide intelligent suggestions to improve code quality and developer productivity.

## Project Structure

Before we begin, let's take a look at our updated project structure:

```
aider/
│
├── cli/
│   ├── __init__.py
│   └── main.py
│
├── core/
│   ├── __init__.py
│   ├── file_manager.py
│   ├── git_manager.py
│   └── context_manager.py
│
├── ai/
│   ├── __init__.py
│   ├── openai_integration.py
│   ├── prompt_templates.py
│   ├── code_completion.py        # New file
│   ├── snippet_generator.py      # New file
│   ├── docstring_generator.py    # New file
│   ├── variable_namer.py         # New file
│   └── optimization_suggester.py # New file
│
├── utils/
│   ├── __init__.py
│   └── code_parser.py
│
├── config/
│   └── settings.py
│
├── tests/
│   ├── test_code_completion.py
│   ├── test_snippet_generator.py
│   ├── test_docstring_generator.py
│   ├── test_variable_namer.py
│   └── test_optimization_suggester.py
│
├── .env
├── requirements.txt
└── main.py
```

We've added several new files in the `ai/` directory to handle the various aspects of intelligent code generation and completion that we'll be implementing in this lesson.

## Context-Aware Code Completion

Let's start by implementing context-aware code completion. This feature will analyze the current code context and provide relevant suggestions for completing code.

First, let's create the `code_completion.py` file:

```python
# ai/code_completion.py

import openai
from typing import List
from aider.core.context_manager import ContextManager
from aider.ai.prompt_templates import CodeCompletionPrompt

class CodeCompleter:
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def get_completion(self, current_line: str, n_suggestions: int = 3) -> List[str]:
        context = self.context_manager.get_current_context()
        prompt = CodeCompletionPrompt.format(
            context=context,
            current_line=current_line
        )

        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=50,
            n=n_suggestions,
            stop=["\n"],
            temperature=0.5,
        )

        return [choice.text.strip() for choice in response.choices]

# Usage example:
# completer = CodeCompleter(context_manager)
# suggestions = completer.get_completion("def calculate_")
# print(suggestions)
```

In this implementation, we're using the OpenAI Codex model to generate code completion suggestions based on the current context and the line being typed. The `ContextManager` class (which we assumed was implemented in a previous lesson) provides the necessary context for more accurate suggestions.

Next, let's update our `prompt_templates.py` file to include the new prompt for code completion:

```python
# ai/prompt_templates.py

class CodeCompletionPrompt:
    template = """
    You are an AI programming assistant. Given the following code context and the current line being typed, suggest {n_suggestions} possible completions.

    Code context:
    {context}

    Current line:
    {current_line}

    Completions:
    """

    @classmethod
    def format(cls, context: str, current_line: str, n_suggestions: int = 3) -> str:
        return cls.template.format(
            context=context,
            current_line=current_line,
            n_suggestions=n_suggestions
        )
```

## Code Snippet Generator

Now, let's implement a code snippet generator that can create common code patterns or structures based on user input.

```python
# ai/snippet_generator.py

import openai
from aider.ai.prompt_templates import SnippetGeneratorPrompt

class SnippetGenerator:
    @staticmethod
    def generate_snippet(snippet_type: str, parameters: dict) -> str:
        prompt = SnippetGeneratorPrompt.format(
            snippet_type=snippet_type,
            parameters=parameters
        )

        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=200,
            temperature=0.2,
        )

        return response.choices[0].text.strip()

# Usage example:
# snippet = SnippetGenerator.generate_snippet("for_loop", {"iterable": "items", "variable": "item"})
# print(snippet)
```

And the corresponding prompt template:

```python
# ai/prompt_templates.py

class SnippetGeneratorPrompt:
    template = """
    Generate a Python code snippet for a {snippet_type} with the following parameters:
    {parameters}

    Code snippet:
    """

    @classmethod
    def format(cls, snippet_type: str, parameters: dict) -> str:
        param_str = "\n".join(f"{k}: {v}" for k, v in parameters.items())
        return cls.template.format(snippet_type=snippet_type, parameters=param_str)
```

## Function Docstring Generator

Next, let's create a function docstring generator that can automatically create informative docstrings for Python functions.

```python
# ai/docstring_generator.py

import ast
import openai
from aider.ai.prompt_templates import DocstringGeneratorPrompt

class DocstringGenerator:
    @staticmethod
    def generate_docstring(function_code: str) -> str:
        tree = ast.parse(function_code)
        function_def = tree.body[0]

        prompt = DocstringGeneratorPrompt.format(
            function_name=function_def.name,
            args=", ".join(arg.arg for arg in function_def.args.args),
            function_body=ast.unparse(function_def)
        )

        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=150,
            temperature=0.3,
        )

        return response.choices[0].text.strip()

# Usage example:
# function_code = """
# def calculate_average(numbers):
#     return sum(numbers) / len(numbers)
# """
# docstring = DocstringGenerator.generate_docstring(function_code)
# print(docstring)
```

And the corresponding prompt template:

```python
# ai/prompt_templates.py

class DocstringGeneratorPrompt:
    template = """
    Generate a comprehensive Python docstring for the following function:

    Function name: {function_name}
    Arguments: {args}

    Function body:
    {function_body}

    Docstring:
    """

    @classmethod
    def format(cls, function_name: str, args: str, function_body: str) -> str:
        return cls.template.format(
            function_name=function_name,
            args=args,
            function_body=function_body
        )
```

## Intelligent Variable Naming System

Now, let's implement an intelligent variable naming system that suggests meaningful names based on the context and purpose of the variable.

```python
# ai/variable_namer.py

import openai
from aider.ai.prompt_templates import VariableNamingPrompt

class VariableNamer:
    @staticmethod
    def suggest_name(variable_type: str, context: str, n_suggestions: int = 3) -> list:
        prompt = VariableNamingPrompt.format(
            variable_type=variable_type,
            context=context,
            n_suggestions=n_suggestions
        )

        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=50,
            n=n_suggestions,
            temperature=0.6,
        )

        return [choice.text.strip() for choice in response.choices]

# Usage example:
# names = VariableNamer.suggest_name("list", "storing user ages")
# print(names)
```

And the corresponding prompt template:

```python
# ai/prompt_templates.py

class VariableNamingPrompt:
    template = """
    Suggest {n_suggestions} meaningful and descriptive variable names for a {variable_type} that will be used for {context}.

    Variable names:
    """

    @classmethod
    def format(cls, variable_type: str, context: str, n_suggestions: int = 3) -> str:
        return cls.template.format(
            variable_type=variable_type,
            context=context,
            n_suggestions=n_suggestions
        )
```

## Code Optimization Suggester

Finally, let's implement a code optimization suggester that can analyze code and provide suggestions for improvements.

```python
# ai/optimization_suggester.py

import ast
import openai
from aider.ai.prompt_templates import OptimizationSuggesterPrompt

class OptimizationSuggester:
    @staticmethod
    def suggest_optimizations(code: str) -> list:
        tree = ast.parse(code)
        
        prompt = OptimizationSuggesterPrompt.format(code=code)

        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=200,
            temperature=0.2,
        )

        suggestions = response.choices[0].text.strip().split("\n")
        return [suggestion.strip() for suggestion in suggestions if suggestion.strip()]

# Usage example:
# code = """
# def factorial(n):
#     if n == 0:
#         return 1
#     else:
#         return n * factorial(n - 1)
# """
# optimizations = OptimizationSuggester.suggest_optimizations(code)
# print(optimizations)
```

And the corresponding prompt template:

```python
# ai/prompt_templates.py

class OptimizationSuggesterPrompt:
    template = """
    Analyze the following Python code and suggest optimizations or improvements. Focus on performance, readability, and best practices. Provide each suggestion on a new line.

    Code:
    {code}

    Optimization suggestions:
    """

    @classmethod
    def format(cls, code: str) -> str:
        return cls.template.format(code=code)
```

## Practical Exercise

Now that we have implemented these intelligent code generation and completion features, let's create a practical exercise to tie everything together. We'll create a simple command-line interface that demonstrates the use of these features.

```python
# main.py

import click
from aider.core.context_manager import ContextManager
from aider.ai.code_completion import CodeCompleter
from aider.ai.snippet_generator import SnippetGenerator
from aider.ai.docstring_generator import DocstringGenerator
from aider.ai.variable_namer import VariableNamer
from aider.ai.optimization_suggester import OptimizationSuggester

@click.group()
def cli():
    pass

@cli.command()
@click.option('--context', default='', help='Current code context')
@click.option('--line', prompt='Enter the current line', help='Current line being typed')
def complete(context, line):
    context_manager = ContextManager()
    context_manager.set_context(context)
    completer = CodeCompleter(context_manager)
    suggestions = completer.get_completion(line)
    click.echo("Completion suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        click.echo(f"{i}. {suggestion}")

@cli.command()
@click.option('--type', prompt='Enter snippet type', help='Type of snippet to generate')
@click.option('--params', prompt='Enter parameters (key1:value1,key2:value2)', help='Snippet parameters')
def snippet(type, params):
    parameters = dict(param.split(':') for param in params.split(','))
    snippet = SnippetGenerator.generate_snippet(type, parameters)
    click.echo("Generated snippet:")
    click.echo(snippet)

@cli.command()
@click.option('--function', prompt='Enter function code', help='Function to generate docstring for')
def docstring(function):
    docstring = DocstringGenerator.generate_docstring(function)
    click.echo("Generated docstring:")
    click.echo(docstring)

@cli.command()
@click.option('--type', prompt='Enter variable type', help='Type of variable')
@click.option('--context', prompt='Enter variable context', help='Context of variable usage')
def name_variable(type, context):
    names = VariableNamer.suggest_name(type, context)
    click.echo("Suggested variable names:")
    for i, name in enumerate(names, 1):
        click.echo(f"{i}. {name}")

@cli.command()
@click.option('--code', prompt='Enter code to optimize', help='Code to suggest optimizations for')
def optimize(code):
    suggestions = OptimizationSuggester.suggest_optimizations(code)
    click.echo("Optimization suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        click.echo(f"{i}. {suggestion}")

if __name__ == '__main__':
    cli()
```

This CLI allows users to interact with all the intelligent code generation and completion features we've implemented. You can run it using:

```
python main.py [command]
```

Where `[command]` is one of `complete`, `snippet`, `docstring`, `name-variable`, or `optimize`.

## Conclusion and Next Steps

In this lesson, we've implemented a comprehensive set of intelligent code generation and completion features for our AI-assisted coding tool. We've created context-aware code completion, a code snippet generator, a function docstring generator, an intelligent variable naming system, and a code optimization suggester.

These features demonstrate the power of combining AI with static code analysis to provide developers with intelligent assistance throughout the coding process. By leveraging the OpenAI Codex model and carefully crafted prompts, we've created a system that can understand code context and provide relevant suggestions.

In the next lesson, we'll focus on test generation and code quality assurance, building upon the foundations we've established here. We'll explore how to use AI to generate test cases, analyze code coverage, and predict potential bugs.

As an exercise, try to extend the current implementation by:

1. Adding more snippet types to the SnippetGenerator
2. Improving the OptimizationSuggester to provide more detailed explanations for each suggestion
3. Implementing a caching system to reduce API calls and improve performance
4. Adding support for different programming languages

Remember to always consider the ethical implications of AI-assisted coding and ensure that the tool enhances developer skills rather than replacing them.
