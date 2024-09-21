# Lesson 12: User Interaction and CLI UX Design

## Introduction

Welcome to Lesson 12 of our AI-assisted coding tool development series. In this lesson, we'll focus on enhancing the user experience of our Command Line Interface (CLI) tool. We'll cover techniques to make our tool more interactive, user-friendly, and efficient. By the end of this lesson, you'll be able to create a polished and professional CLI interface for your AI-assisted coding tool.

## Project Structure

Before we dive into the implementation details, let's take a look at our updated project structure:

```
aider/
│
├── aider/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── interactive/
│   │   ├── __init__.py
│   │   ├── prompt.py
│   │   ├── suggestions.py
│   │   └── editor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── colors.py
│   │   ├── spinner.py
│   │   └── progress.py
│   ├── language/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── python.py
│   │   ├── javascript.py
│   │   └── ruby.py
│   └── plugins/
│       ├── __init__.py
│       ├── base.py
│       ├── syntax_highlighter.py
│       └── code_formatter.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_interactive.py
│   └── test_utils.py
│
├── setup.py
├── requirements.txt
└── README.md
```

This structure builds upon our previous lesson and introduces new modules for handling user interaction and CLI UX design.

## 1. Designing an Interactive Prompt System

Let's start by creating an interactive prompt system that will make our CLI more engaging and user-friendly. We'll use the `prompt_toolkit` library for this purpose.

First, install the required library:

```bash
pip install prompt_toolkit
```

Now, let's create our interactive prompt system:

```python
# aider/interactive/prompt.py

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

class InteractivePrompt:
    def __init__(self, history_file='.aider_history'):
        self.session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory(),
            lexer=PygmentsLexer(PythonLexer)
        )

    def prompt(self, message=">>> "):
        return self.session.prompt(message)

    def multiline_prompt(self, message="Enter your code (Ctrl+D to finish):\n"):
        print(message)
        lines = []
        while True:
            try:
                line = self.session.prompt('... ')
                lines.append(line)
            except EOFError:
                break
        return '\n'.join(lines)
```

## 2. Implementing Auto-suggestions and Command Completion

To make our CLI more efficient, let's implement auto-suggestions and command completion. We'll create a custom completer for our AI-assisted coding commands:

```python
# aider/interactive/suggestions.py

from prompt_toolkit.completion import Completer, Completion

class AiderCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for command in self.commands:
            if command.startswith(word):
                yield Completion(command, start_position=-len(word))

# Usage in prompt.py
from .suggestions import AiderCompleter

# In the InteractivePrompt class constructor
self.session = PromptSession(
    history=FileHistory(history_file),
    auto_suggest=AutoSuggestFromHistory(),
    lexer=PygmentsLexer(PythonLexer),
    completer=AiderCompleter(['analyze', 'refactor', 'test', 'explain', 'commit'])
)
```

## 3. Creating a Progress Bar and Spinner for Long-running Tasks

For tasks that take a while to complete, it's important to provide visual feedback to the user. Let's implement a progress bar and spinner:

```python
# aider/utils/progress.py

import time
from tqdm import tqdm

def progress_bar(iterable, desc="Processing"):
    return tqdm(iterable, desc=desc, unit="item")

# aider/utils/spinner.py

import itertools
import threading
import time
import sys

class Spinner:
    def __init__(self, message="Working", delay=0.1):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.delay = delay
        self.message = message
        self.running = False
        self.spinner_thread = None

    def spin(self):
        while self.running:
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(self.delay)

    def start(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()

    def stop(self):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.flush()

# Usage example
from aider.utils.progress import progress_bar
from aider.utils.spinner import Spinner

def long_running_task():
    with Spinner("Analyzing code"):
        # Simulate a long-running task
        time.sleep(5)

    for i in progress_bar(range(100), desc="Refactoring"):
        # Simulate a task with measurable progress
        time.sleep(0.1)
```

## 4. Developing a Color-coded Output System

To make our CLI output more readable and visually appealing, let's implement a color-coded output system:

```python
# aider/utils/colors.py

from colorama import init, Fore, Back, Style

init(autoreset=True)

class ColorPrinter:
    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}{message}")

    @staticmethod
    def error(message):
        print(f"{Fore.RED}{message}")

    @staticmethod
    def warning(message):
        print(f"{Fore.YELLOW}{message}")

    @staticmethod
    def info(message):
        print(f"{Fore.CYAN}{message}")

    @staticmethod
    def code(message):
        print(f"{Fore.MAGENTA}{message}")

# Usage example
from aider.utils.colors import ColorPrinter

ColorPrinter.success("Task completed successfully!")
ColorPrinter.error("An error occurred.")
ColorPrinter.warning("Warning: This action is irreversible.")
ColorPrinter.info("Tip: Use 'aider --help' for more information.")
ColorPrinter.code("print('Hello, World!')")
```

## 5. Implementing a CLI-based Code Editor

To provide a seamless coding experience within our CLI, let's implement a basic code editor:

```python
# aider/interactive/editor.py

import tempfile
import os
import subprocess

class CLIEditor:
    def __init__(self, preferred_editor=None):
        self.editor = preferred_editor or os.environ.get('EDITOR', 'nano')

    def edit_code(self, initial_content=""):
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tf:
            tf.write(initial_content)
            tf.flush()
            tf_name = tf.name

        try:
            subprocess.call([self.editor, tf_name])
            with open(tf_name, 'r') as tf:
                edited_content = tf.read()
        finally:
            os.unlink(tf_name)

        return edited_content

# Usage example
from aider.interactive.editor import CLIEditor

editor = CLIEditor()
new_code = editor.edit_code("def hello_world():\n    print('Hello, World!')\n")
print("Edited code:")
print(new_code)
```

## 6. Putting It All Together

Now that we have implemented various components to enhance our CLI UX, let's update our main CLI interface to incorporate these features:

```python
# aider/cli.py

import click
from aider.interactive.prompt import InteractivePrompt
from aider.interactive.editor import CLIEditor
from aider.utils.colors import ColorPrinter
from aider.utils.spinner import Spinner
from aider.utils.progress import progress_bar

@click.group()
def cli():
    pass

@cli.command()
@click.option('--interactive', '-i', is_flag=True, help="Start interactive mode")
def main(interactive):
    if interactive:
        prompt = InteractivePrompt()
        editor = CLIEditor()
        
        while True:
            command = prompt.prompt("aider> ")
            if command == "exit":
                break
            elif command == "edit":
                code = editor.edit_code()
                ColorPrinter.code(code)
            elif command == "analyze":
                with Spinner("Analyzing code"):
                    # Simulate code analysis
                    import time
                    time.sleep(3)
                ColorPrinter.success("Analysis complete!")
            elif command == "refactor":
                for i in progress_bar(range(100), desc="Refactoring"):
                    # Simulate refactoring process
                    import time
                    time.sleep(0.05)
                ColorPrinter.success("Refactoring complete!")
            else:
                ColorPrinter.error(f"Unknown command: {command}")
    else:
        ColorPrinter.info("Running in non-interactive mode. Use --interactive or -i for interactive mode.")

if __name__ == '__main__':
    cli()
```

## Conclusion

In this lesson, we've significantly improved the user experience of our AI-assisted coding tool's CLI. We've implemented:

1. An interactive prompt system with history and syntax highlighting
2. Auto-suggestions and command completion
3. Progress bars and spinners for long-running tasks
4. A color-coded output system for better readability
5. A CLI-based code editor for seamless code editing

These enhancements make our tool more user-friendly, efficient, and professional. Users can now interact with the AI-assisted coding tool more intuitively, with visual feedback and helpful suggestions throughout the process.

## Exercises

To further reinforce your understanding and skills, try the following exercises:

1. Implement a help system that displays available commands and their descriptions when the user types "help" or "?".
2. Add support for custom themes, allowing users to choose their preferred color scheme for the CLI output.
3. Implement a command history browser that allows users to search and reuse previous commands.
4. Create a configuration wizard that guides new users through setting up their preferences for the AI-assisted coding tool.
5. Implement a simple plugin system that allows users to add custom commands to the interactive prompt.

By completing these exercises, you'll gain a deeper understanding of CLI UX design and be well-prepared to create highly interactive and user-friendly command-line tools.

