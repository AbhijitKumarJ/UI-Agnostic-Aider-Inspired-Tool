# Lesson 11: Language Support and Extensibility

## Introduction

Welcome to Lesson 11 of our AI-assisted coding tool development series. In this lesson, we'll focus on enhancing our tool's language support and extensibility. By the end of this lesson, you'll be able to add support for multiple programming languages and create a flexible plugin system for easy expansion of your tool's capabilities.

## Project Structure

Before we dive into the implementation details, let's take a look at our project structure:

```
aider/
│
├── aider/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── language/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── python.py
│   │   ├── javascript.py
│   │   └── ruby.py
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── syntax_highlighter.py
│   │   └── code_formatter.py
│   ├── lsp/
│   │   ├── __init__.py
│   │   └── server.py
│   └── utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_language.py
│   └── test_plugins.py
│
├── setup.py
├── requirements.txt
└── README.md
```

This structure provides a solid foundation for implementing language support and extensibility in our AI-assisted coding tool.

## 1. Designing a Plugin System for Language Support

To create a flexible and extensible system for language support, we'll implement a plugin architecture. This will allow us to easily add support for new languages and features without modifying the core codebase.

Let's start by creating a base class for language support:

```python
# aider/language/base.py

from abc import ABC, abstractmethod

class LanguageSupport(ABC):
    @abstractmethod
    def get_file_extensions(self):
        """Return a list of file extensions for this language."""
        pass

    @abstractmethod
    def parse_code(self, code):
        """Parse the given code and return an AST."""
        pass

    @abstractmethod
    def generate_code(self, ast):
        """Generate code from the given AST."""
        pass

    @abstractmethod
    def get_syntax_highlighting_rules(self):
        """Return syntax highlighting rules for this language."""
        pass
```

Now, let's implement language support for Python as an example:

```python
# aider/language/python.py

import ast
from .base import LanguageSupport

class PythonSupport(LanguageSupport):
    def get_file_extensions(self):
        return ['.py']

    def parse_code(self, code):
        return ast.parse(code)

    def generate_code(self, ast_node):
        return ast.unparse(ast_node)

    def get_syntax_highlighting_rules(self):
        return {
            'keywords': ['def', 'class', 'if', 'else', 'for', 'while', 'import', 'from'],
            'builtin_functions': ['print', 'len', 'range', 'str', 'int', 'float'],
            'string_prefix': ['r', 'f', 'b'],
        }
```

## 2. Implementing Language-Specific Features

With our base language support in place, we can now implement language-specific features. Let's create a plugin system to handle these features:

```python
# aider/plugins/base.py

from abc import ABC, abstractmethod

class Plugin(ABC):
    @abstractmethod
    def activate(self):
        """Activate the plugin."""
        pass

    @abstractmethod
    def deactivate(self):
        """Deactivate the plugin."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the plugin's main functionality."""
        pass
```

Now, let's implement a syntax highlighting plugin:

```python
# aider/plugins/syntax_highlighter.py

from .base import Plugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

class SyntaxHighlighter(Plugin):
    def __init__(self, language):
        self.language = language
        self.lexer = get_lexer_by_name(language)
        self.formatter = TerminalFormatter()

    def activate(self):
        print(f"Syntax highlighter for {self.language} activated.")

    def deactivate(self):
        print(f"Syntax highlighter for {self.language} deactivated.")

    def execute(self, code):
        return highlight(code, self.lexer, self.formatter)
```

## 3. Creating a Custom Language Server Protocol

To provide advanced IDE-like features, we'll implement a basic Language Server Protocol (LSP) for our tool. This will allow IDEs and text editors to communicate with our tool for features like code completion and error checking.

```python
# aider/lsp/server.py

import json
from jsonrpc import JSONRPCResponseManager, dispatcher

class AiderLanguageServer:
    def __init__(self):
        self.workspace = {}

    @dispatcher.add_method
    def initialize(self, rootUri, **kwargs):
        self.workspace['root_uri'] = rootUri
        return {
            "capabilities": {
                "textDocumentSync": 1,
                "completionProvider": {
                    "triggerCharacters": ["."]
                },
                "hoverProvider": True
            }
        }

    @dispatcher.add_method
    def textDocument_didOpen(self, textDocument, **kwargs):
        self.workspace[textDocument['uri']] = textDocument['text']

    @dispatcher.add_method
    def textDocument_didChange(self, textDocument, contentChanges, **kwargs):
        self.workspace[textDocument['uri']] = contentChanges[0]['text']

    @dispatcher.add_method
    def textDocument_completion(self, textDocument, position, **kwargs):
        # Implement completion logic here
        return {
            "isIncomplete": False,
            "items": [
                {
                    "label": "example_completion",
                    "kind": 1,
                    "detail": "Example completion item",
                    "documentation": "This is an example completion item."
                }
            ]
        }

    @dispatcher.add_method
    def textDocument_hover(self, textDocument, position, **kwargs):
        # Implement hover logic here
        return {
            "contents": {
                "kind": "markdown",
                "value": "This is an example hover message."
            }
        }

    def start(self):
        while True:
            request = input()
            response = JSONRPCResponseManager.handle(request, dispatcher)
            if response:
                print(json.dumps(response.data))
```

## 4. Developing a Syntax-Aware Editing System

To make our AI-assisted coding tool more intelligent, let's implement a syntax-aware editing system that understands the structure of the code:

```python
# aider/utils.py

import ast

def get_node_at_position(tree, position):
    """Find the AST node at the given position."""
    for node in ast.walk(tree):
        if hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
            if node.lineno == position['line'] + 1 and node.col_offset <= position['character']:
                return node
    return None

def get_context_for_completion(code, position):
    """Get the context for code completion at the given position."""
    tree = ast.parse(code)
    node = get_node_at_position(tree, position)
    
    if isinstance(node, ast.Name):
        return {'type': 'variable', 'name': node.id}
    elif isinstance(node, ast.Call):
        return {'type': 'function_call', 'name': node.func.id if isinstance(node.func, ast.Name) else None}
    elif isinstance(node, ast.Attribute):
        return {'type': 'attribute', 'object': node.value.id if isinstance(node.value, ast.Name) else None}
    
    return {'type': 'unknown'}
```

## 5. Implementing Multi-Language Project Support

To support projects with multiple programming languages, we need to create a system that can detect and handle different file types:

```python
# aider/language/__init__.py

from .python import PythonSupport
from .javascript import JavaScriptSupport
from .ruby import RubySupport

language_supports = {
    'python': PythonSupport(),
    'javascript': JavaScriptSupport(),
    'ruby': RubySupport(),
}

def get_language_support(file_extension):
    for lang, support in language_supports.items():
        if file_extension in support.get_file_extensions():
            return support
    raise ValueError(f"Unsupported file extension: {file_extension}")
```

Now, let's update our CLI to handle multi-language projects:

```python
# aider/cli.py

import click
import os
from .language import get_language_support
from .plugins.syntax_highlighter import SyntaxHighlighter

@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def main(files):
    for file in files:
        _, extension = os.path.splitext(file)
        try:
            language_support = get_language_support(extension)
            highlighter = SyntaxHighlighter(language_support.__class__.__name__.lower())
            highlighter.activate()

            with open(file, 'r') as f:
                code = f.read()
                
            highlighted_code = highlighter.execute(code)
            print(f"File: {file}")
            print(highlighted_code)
            
            ast = language_support.parse_code(code)
            print(f"AST: {ast}")

            highlighter.deactivate()
        except ValueError as e:
            print(f"Error processing {file}: {str(e)}")

if __name__ == '__main__':
    main()
```

## Conclusion

In this lesson, we've implemented a flexible and extensible system for language support in our AI-assisted coding tool. We've created a plugin architecture for easy addition of new languages and features, implemented a basic Language Server Protocol for IDE integration, and developed a syntax-aware editing system.

Here's a summary of what we've accomplished:

1. Designed a plugin system for language support
2. Implemented language-specific features
3. Created a custom Language Server Protocol
4. Developed a syntax-aware editing system
5. Implemented multi-language project support

By following these steps, you've significantly enhanced the capabilities of your AI-assisted coding tool, making it more versatile and powerful for developers working with multiple programming languages.

## Exercises

1. Implement language support for a new programming language (e.g., Java, C++, or Go).
2. Create a new plugin for code formatting that integrates with popular formatting tools like Black (Python) or Prettier (JavaScript).
3. Extend the Language Server Protocol implementation to support more advanced features like "go to definition" or "find all references".
4. Implement a code complexity analyzer that works across multiple languages.
5. Create a plugin for generating unit tests based on the code structure and language-specific testing frameworks.

By completing these exercises, you'll gain a deeper understanding of language support and extensibility in AI-assisted coding tools, and be well-prepared to tackle more advanced topics in the upcoming lessons.

