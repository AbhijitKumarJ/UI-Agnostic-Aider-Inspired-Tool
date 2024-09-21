# Lesson 2: Building the Core CLI Framework

## Table of Contents
1. [Introduction](#introduction)
2. [Designing a Modular CLI Architecture](#designing-a-modular-cli-architecture)
3. [Implementing Subcommands](#implementing-subcommands)
4. [Adding Global Options](#adding-global-options)
5. [Creating a Configuration Management System](#creating-a-configuration-management-system)
6. [Handling Environment Variables](#handling-environment-variables)
7. [Project Structure Update](#project-structure-update)
8. [Conclusion and Next Steps](#conclusion-and-next-steps)

## 1. Introduction

In this lesson, we'll expand on the basic CLI structure we created in Lesson 1 to build a more robust and feature-rich command-line interface for our AI-assisted coding tool, AICoder. We'll focus on creating a modular architecture, implementing subcommands, handling global options, managing configurations, and working with environment variables.

## 2. Designing a Modular CLI Architecture

To create a scalable and maintainable CLI tool, we'll design a modular architecture. This approach will allow us to easily add new features and commands as our tool grows.

Let's update our project structure to reflect this modular design:

```
aicoder/
│
├── aicoder/
│   ├── __init__.py
│   ├── cli.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── analyze.py
│   │   ├── generate.py
│   │   └── files.py
│   ├── config.py
│   ├── ai_integration.py
│   └── file_utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_commands/
│       ├── __init__.py
│       ├── test_analyze.py
│       ├── test_generate.py
│       └── test_files.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

Let's create the new directories and files:

```bash
mkdir -p aicoder/aicoder/commands aicoder/tests/test_commands
touch aicoder/aicoder/commands/{__init__.py,analyze.py,generate.py,files.py}
touch aicoder/aicoder/config.py
touch aicoder/tests/test_commands/{__init__.py,test_analyze.py,test_generate.py,test_files.py}
```

## 3. Implementing Subcommands

We'll implement three main subcommands: `analyze`, `generate`, and `files`. Each subcommand will be in its own file within the `commands` directory.

### 3.1 Analyze Command

Let's implement the `analyze` command in `aicoder/aicoder/commands/analyze.py`:

```python
# aicoder/aicoder/commands/analyze.py

import click

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def analyze(filename, verbose):
    """Analyze a file and suggest improvements."""
    click.echo(f"Analyzing {filename}...")
    if verbose:
        click.echo("Verbose mode enabled")
    # TODO: Implement file analysis logic
```

### 3.2 Generate Command

Now, let's implement the `generate` command in `aicoder/aicoder/commands/generate.py`:

```python
# aicoder/aicoder/commands/generate.py

import click

@click.command()
@click.argument('prompt')
@click.option('--language', '-l', default='python', help='Programming language for code generation')
def generate(prompt, language):
    """Generate code based on a natural language prompt."""
    click.echo(f"Generating {language} code for: {prompt}")
    # TODO: Implement code generation logic
```

### 3.3 Files Command

Let's implement the `files` command with subcommands in `aicoder/aicoder/commands/files.py`:

```python
# aicoder/aicoder/commands/files.py

import click

@click.group()
def files():
    """Manage files in the project."""
    pass

@files.command()
@click.argument('filename', type=click.Path())
def add(filename):
    """Add a file to the project."""
    click.echo(f"Adding file: {filename}")
    # TODO: Implement file addition logic

@files.command()
@click.argument('filename', type=click.Path(exists=True))
def remove(filename):
    """Remove a file from the project."""
    click.echo(f"Removing file: {filename}")
    # TODO: Implement file removal logic

@files.command()
def list():
    """List all files in the project."""
    click.echo("Listing all files:")
    # TODO: Implement file listing logic
```

### 3.4 Updating the Main CLI File

Now, let's update our main `cli.py` file to include these new commands:

```python
# aicoder/aicoder/cli.py

import click
from .commands.analyze import analyze
from .commands.generate import generate
from .commands.files import files

@click.group()
def cli():
    """AICoder: Your AI-powered coding assistant."""
    pass

cli.add_command(analyze)
cli.add_command(generate)
cli.add_command(files)

if __name__ == '__main__':
    cli()
```

## 4. Adding Global Options

To add global options that apply to all commands, we can use Click's `pass_context` decorator and define options on the main `cli` group. Let's update our `cli.py` file:

```python
# aicoder/aicoder/cli.py

import click
from .commands.analyze import analyze
from .commands.generate import generate
from .commands.files import files

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.option('--config', type=click.Path(), help='Path to config file')
@click.pass_context
def cli(ctx, debug, config):
    """AICoder: Your AI-powered coding assistant."""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['CONFIG'] = config

cli.add_command(analyze)
cli.add_command(generate)
cli.add_command(files)

if __name__ == '__main__':
    cli()
```

Now, you can access these global options in your subcommands using the `click.pass_context` decorator:

```python
# Example usage in a subcommand

@click.command()
@click.pass_context
def some_command(ctx):
    if ctx.obj['DEBUG']:
        click.echo("Debug mode is on")
    # Rest of the command logic
```

## 5. Creating a Configuration Management System

To manage configurations for our CLI tool, we'll create a simple configuration system using Python's `configparser` module. Let's implement this in the `config.py` file:

```python
# aicoder/aicoder/config.py

import configparser
import os
import click

DEFAULT_CONFIG_PATH = os.path.expanduser('~/.aicoder.ini')

def load_config(config_path=None):
    config = configparser.ConfigParser()
    
    # Load default configuration
    config['DEFAULT'] = {
        'ai_model': 'gpt-3.5-turbo',
        'language': 'python',
        'max_tokens': '150'
    }
    
    # Load user configuration
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        click.echo(f"Config file not found. Using default configuration.")
    
    return config

def save_config(config, config_path=None):
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
    click.echo(f"Configuration saved to {config_path}")
```

Now, let's update our `cli.py` to use this configuration system:

```python
# aicoder/aicoder/cli.py

import click
from .commands.analyze import analyze
from .commands.generate import generate
from .commands.files import files
from .config import load_config

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.option('--config', type=click.Path(), help='Path to config file')
@click.pass_context
def cli(ctx, debug, config):
    """AICoder: Your AI-powered coding assistant."""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['CONFIG'] = load_config(config)

cli.add_command(analyze)
cli.add_command(generate)
cli.add_command(files)

if __name__ == '__main__':
    cli()
```

## 6. Handling Environment Variables

To make our CLI tool more flexible, we'll add support for environment variables. We can use Click's built-in support for environment variables in command options.

Let's update our `generate` command to use an environment variable for the AI model:

```python
# aicoder/aicoder/commands/generate.py

import click
import os

@click.command()
@click.argument('prompt')
@click.option('--language', '-l', default='python', help='Programming language for code generation')
@click.option('--model', envvar='AICODER_MODEL', default='gpt-3.5-turbo', help='AI model to use for code generation')
@click.pass_context
def generate(ctx, prompt, language, model):
    """Generate code based on a natural language prompt."""
    click.echo(f"Generating {language} code using {model} for: {prompt}")
    # TODO: Implement code generation logic
    
    if ctx.obj['DEBUG']:
        click.echo(f"Debug: Config loaded from {ctx.obj['CONFIG'].get('DEFAULT', 'language')}")
```

Now, users can set the `AICODER_MODEL` environment variable to change the default AI model:

```bash
export AICODER_MODEL=gpt-4
aicoder generate "Create a function to calculate prime numbers"
```

## 7. Project Structure Update

After implementing these features, our project structure now looks like this:

```
aicoder/
│
├── aicoder/
│   ├── __init__.py
│   ├── cli.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── analyze.py
│   │   ├── generate.py
│   │   └── files.py
│   ├── config.py
│   ├── ai_integration.py
│   └── file_utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_commands/
│       ├── __init__.py
│       ├── test_analyze.py
│       ├── test_generate.py
│       └── test_files.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

## 8. Conclusion and Next Steps

In this lesson, we've significantly expanded our CLI framework for the AICoder tool. We've:

1. Designed a modular CLI architecture
2. Implemented subcommands (analyze, generate, files)
3. Added global options (debug mode, config file path)
4. Created a configuration management system
5. Implemented environment variable handling

These enhancements provide a solid foundation for building more advanced features in our AI-assisted coding tool.

In the next lesson, we'll focus on file handling and code manipulation, where we'll implement file reading and writing operations, develop a file tracking system, and create a simple diff utility.

Remember to update your `requirements.txt` file with any new dependencies and commit your changes to version control:

```bash
pip freeze > requirements.txt
git add .
git commit -m "Lesson 2: Implemented core CLI framework with subcommands, configuration, and environment variable support"
```

Stay tuned for more advanced features and AI integration in upcoming lessons!
