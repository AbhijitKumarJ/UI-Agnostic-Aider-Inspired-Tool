# Lesson 3: File Handling and Code Manipulation

## Table of Contents
1. [Introduction](#introduction)
2. [Implementing File Reading and Writing Operations](#implementing-file-reading-and-writing-operations)
3. [Developing a File Tracking System](#developing-a-file-tracking-system)
4. [Creating a Simple Diff Utility](#creating-a-simple-diff-utility)
5. [Implementing Syntax Highlighting for Code Display](#implementing-syntax-highlighting-for-code-display)
6. [Handling Multiple File Types](#handling-multiple-file-types)
7. [Project Structure Update](#project-structure-update)
8. [Conclusion and Next Steps](#conclusion-and-next-steps)

## 1. Introduction

In this lesson, we'll focus on enhancing our AICoder tool with robust file handling and code manipulation capabilities. We'll implement file reading and writing operations, develop a file tracking system, create a simple diff utility, add syntax highlighting for code display, and implement support for multiple file types. These features will form the foundation for more advanced AI-assisted coding functionalities in future lessons.

## 2. Implementing File Reading and Writing Operations

Let's start by implementing basic file reading and writing operations. We'll create a new file called `file_utils.py` to contain these functions.

```python
# aicoder/aicoder/file_utils.py

import os
import click

def read_file(file_path):
    """Read the contents of a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        click.echo(f"Error reading file {file_path}: {e}", err=True)
        return None

def write_file(file_path, content):
    """Write content to a file."""
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        click.echo(f"File {file_path} written successfully.")
    except IOError as e:
        click.echo(f"Error writing to file {file_path}: {e}", err=True)

def ensure_directory(directory):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        click.echo(f"Created directory: {directory}")
```

Now, let's update our `files.py` command to use these new utilities:

```python
# aicoder/aicoder/commands/files.py

import click
import os
from ..file_utils import read_file, write_file, ensure_directory

@click.group()
def files():
    """Manage files in the project."""
    pass

@files.command()
@click.argument('filename', type=click.Path())
@click.option('--content', '-c', help='Content to write to the file')
def add(filename, content):
    """Add a file to the project."""
    if os.path.exists(filename):
        click.echo(f"File {filename} already exists.")
        return

    if content:
        write_file(filename, content)
    else:
        click.echo(f"Created empty file: {filename}")
        write_file(filename, '')

@files.command()
@click.argument('filename', type=click.Path(exists=True))
def remove(filename):
    """Remove a file from the project."""
    try:
        os.remove(filename)
        click.echo(f"Removed file: {filename}")
    except OSError as e:
        click.echo(f"Error removing file {filename}: {e}", err=True)

@files.command()
@click.argument('directory', type=click.Path(exists=True), default='.')
def list(directory):
    """List all files in the project."""
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * level
        click.echo(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            click.echo(f"{sub_indent}{file}")

@files.command()
@click.argument('filename', type=click.Path(exists=True))
def show(filename):
    """Display the contents of a file."""
    content = read_file(filename)
    if content is not None:
        click.echo(f"Contents of {filename}:")
        click.echo(content)
```

## 3. Developing a File Tracking System

To keep track of files in our project, we'll implement a simple file tracking system using a JSON file. Let's create a new file called `file_tracker.py`:

```python
# aicoder/aicoder/file_tracker.py

import json
import os
import click
from .file_utils import ensure_directory

class FileTracker:
    def __init__(self, track_file='.aicoder_track.json'):
        self.track_file = track_file
        self.tracked_files = self._load_tracked_files()

    def _load_tracked_files(self):
        if os.path.exists(self.track_file):
            with open(self.track_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_tracked_files(self):
        ensure_directory(os.path.dirname(self.track_file))
        with open(self.track_file, 'w') as f:
            json.dump(self.tracked_files, f, indent=2)

    def add_file(self, filename):
        abs_path = os.path.abspath(filename)
        self.tracked_files[abs_path] = {
            'last_modified': os.path.getmtime(abs_path)
        }
        self._save_tracked_files()
        click.echo(f"Added {filename} to tracked files.")

    def remove_file(self, filename):
        abs_path = os.path.abspath(filename)
        if abs_path in self.tracked_files:
            del self.tracked_files[abs_path]
            self._save_tracked_files()
            click.echo(f"Removed {filename} from tracked files.")
        else:
            click.echo(f"{filename} is not in tracked files.")

    def get_tracked_files(self):
        return list(self.tracked_files.keys())

    def check_for_changes(self):
        changed_files = []
        for abs_path, info in self.tracked_files.items():
            if os.path.exists(abs_path):
                current_mtime = os.path.getmtime(abs_path)
                if current_mtime != info['last_modified']:
                    changed_files.append(abs_path)
                    info['last_modified'] = current_mtime
            else:
                changed_files.append(abs_path)
        
        self._save_tracked_files()
        return changed_files
```

Now, let's update our `files.py` command to use the `FileTracker`:

```python
# aicoder/aicoder/commands/files.py

import click
import os
from ..file_utils import read_file, write_file, ensure_directory
from ..file_tracker import FileTracker

@click.group()
@click.pass_context
def files(ctx):
    """Manage files in the project."""
    ctx.ensure_object(dict)
    ctx.obj['tracker'] = FileTracker()

@files.command()
@click.argument('filename', type=click.Path())
@click.option('--content', '-c', help='Content to write to the file')
@click.pass_context
def add(ctx, filename, content):
    """Add a file to the project."""
    if os.path.exists(filename):
        click.echo(f"File {filename} already exists.")
        return

    if content:
        write_file(filename, content)
    else:
        click.echo(f"Created empty file: {filename}")
        write_file(filename, '')

    ctx.obj['tracker'].add_file(filename)

@files.command()
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def remove(ctx, filename):
    """Remove a file from the project."""
    try:
        os.remove(filename)
        click.echo(f"Removed file: {filename}")
        ctx.obj['tracker'].remove_file(filename)
    except OSError as e:
        click.echo(f"Error removing file {filename}: {e}", err=True)

@files.command()
@click.pass_context
def list(ctx):
    """List all tracked files in the project."""
    tracked_files = ctx.obj['tracker'].get_tracked_files()
    for file in tracked_files:
        click.echo(file)

@files.command()
@click.pass_context
def check_changes(ctx):
    """Check for changes in tracked files."""
    changed_files = ctx.obj['tracker'].check_for_changes()
    if changed_files:
        click.echo("The following files have changed:")
        for file in changed_files:
            click.echo(file)
    else:
        click.echo("No changes detected in tracked files.")
```

## 4. Creating a Simple Diff Utility

To help users visualize changes in their code, let's implement a simple diff utility. We'll use the `difflib` module from Python's standard library. Create a new file called `diff_utils.py`:

```python
# aicoder/aicoder/diff_utils.py

import difflib
import click

def create_diff(old_content, new_content, filename):
    """Create a unified diff between old and new content."""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3
    )
    return ''.join(diff)

def display_diff(old_content, new_content, filename):
    """Display a colored diff between old and new content."""
    diff = create_diff(old_content, new_content, filename)
    for line in diff.splitlines():
        if line.startswith('+'):
            click.secho(line, fg='green')
        elif line.startswith('-'):
            click.secho(line, fg='red')
        elif line.startswith('^'):
            click.secho(line, fg='blue')
        else:
            click.echo(line)
```

Now, let's add a new command to our `files.py` to use this diff utility:

```python
# aicoder/aicoder/commands/files.py

# ... (previous code)

from ..diff_utils import display_diff

@files.command()
@click.argument('filename', type=click.Path(exists=True))
@click.argument('new_content', required=False)
@click.option('--file2', type=click.Path(exists=True), help='Compare with another file')
def diff(filename, new_content, file2):
    """Show differences between current file content and new content or another file."""
    old_content = read_file(filename)
    if old_content is None:
        return

    if file2:
        new_content = read_file(file2)
        if new_content is None:
            return
    elif new_content is None:
        click.echo("Please provide new content or a second file to compare.")
        return

    display_diff(old_content, new_content, filename)
```

## 5. Implementing Syntax Highlighting for Code Display

To improve code readability, let's add syntax highlighting using the `pygments` library. First, add `pygments` to your `requirements.txt` file and install it:

```
pip install pygments
```

Now, let's create a new file called `syntax_highlighter.py`:

```python
# aicoder/aicoder/syntax_highlighter.py

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, PythonLexer
from pygments.formatters import TerminalFormatter
import click

def highlight_code(code, filename):
    """Highlight code based on the file extension."""
    try:
        lexer = get_lexer_for_filename(filename)
    except:
        lexer = PythonLexer()
    
    highlighted_code = highlight(code, lexer, TerminalFormatter())
    return highlighted_code

def display_highlighted_code(code, filename):
    """Display syntax-highlighted code."""
    highlighted_code = highlight_code(code, filename)
    click.echo(highlighted_code)
```

Let's update our `show` command in `files.py` to use syntax highlighting:

```python
# aicoder/aicoder/commands/files.py

# ... (previous code)

from ..syntax_highlighter import display_highlighted_code

@files.command()
@click.argument('filename', type=click.Path(exists=True))
def show(filename):
    """Display the contents of a file with syntax highlighting."""
    content = read_file(filename)
    if content is not None:
        click.echo(f"Contents of {filename}:")
        display_highlighted_code(content, filename)
```

## 6. Handling Multiple File Types

To support multiple file types, we'll create a simple factory pattern to handle different file types. Create a new file called `file_handlers.py`:

```python
# aicoder/aicoder/file_handlers.py

import os

class BaseFileHandler:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, 'r') as f:
            return f.read()

    def write(self, content):
        with open(self.filename, 'w') as f:
            f.write(content)

class PythonFileHandler(BaseFileHandler):
    def analyze(self):
        # Implement Python-specific analysis
        return "Python file analysis not yet implemented"

class JavaScriptFileHandler(BaseFileHandler):
    def analyze(self):
        # Implement JavaScript-specific analysis
        return "JavaScript file analysis not yet implemented"

def get_file_handler(filename):
    _, ext = os.path.splitext(filename)
    if ext == '.py':
        return PythonFileHandler(filename)
    elif ext == '.js':
        return JavaScriptFileHandler(filename)
    else:
        return BaseFileHandler(filename)
```

Now, let's update our `files.py` to use these file handlers:

```python
# aicoder/aicoder/commands/files.py

# ... (previous code)

from ..file_handlers import get_file_handler

@files.command()
@click.argument('filename', type=click.Path(exists=True))
def analyze(filename):
    """Analyze a file based on its type."""
    handler = get_file_handler(filename)
    analysis_result = handler.analyze()
    click.echo(f"Analysis of {filename}:")
    click.echo(analysis_result)
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
│   ├── file_utils.py
│   ├── file_tracker.py
│   ├── diff_utils.py
│   ├── syntax_highlighter.py
│   └── file_handlers.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_commands/
│   │   ├── __init__.py
│   │   ├── test_analyze.py
│   │   ├── test_generate.py
│   │   └── test_files.py
│   ├── test_file_utils.py
│   ├── test_file_tracker.py
│   ├── test_diff_utils.py
│   └── test_file_handlers.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

## 8. Conclusion and Next Steps

In this lesson, we've significantly enhanced our AICoder tool with robust file handling and code manipulation capabilities. We've:

1. Implemented file reading and writing operations
2. Developed a file tracking system
3. Created a simple diff utility
4. Implemented syntax highlighting for code display
5. Added support for handling multiple file types

These enhancements provide a solid foundation for more advanced AI-assisted coding features. Here's a summary of what we've accomplished:

- **File Operations**: We can now read, write, and manage files efficiently.
- **File Tracking**: Our tool can keep track of files and detect changes.
- **Diff Utility**: Users can easily visualize differences between file versions.
- **Syntax Highlighting**: Code is now displayed with syntax highlighting for better readability.
- **Multiple File Types**: We've laid the groundwork for supporting various programming languages.

For the next steps, consider the following:

1. **Implement Unit Tests**: Write comprehensive unit tests for all the new functionality we've added.

2. **Enhance File Analysis**: Expand the `analyze` command to provide more insightful code analysis based on file types.

3. **AI Integration**: Start integrating AI capabilities to suggest improvements or generate code based on file content.

4. **Version Control Integration**: Begin integrating with Git for better project management.

5. **Performance Optimization**: As the tool grows, look for opportunities to optimize performance, especially for large files or projects.

Remember to update your `requirements.txt` file with any new dependencies:

```bash
pip freeze > requirements.txt
```

And commit your changes to version control:

```bash
git add .
git commit -m "Lesson 3: Implemented file handling, diff utility, syntax highlighting, and multi-file type support"
```

In the next lesson, we'll focus on version control integration, where we'll dive deeper into working with Git repositories, handling commits, and managing branches within our AICoder tool.

## 9. Exercises

To reinforce your understanding of the concepts covered in this lesson, try the following exercises:

1. Implement a `search` command that allows users to search for specific text across all tracked files.

2. Extend the `diff` command to support comparing the current version of a file with a specific Git commit.

3. Create a `refactor` command that uses the AI integration to suggest code refactoring for a given file.

4. Implement a `stats` command that provides statistics about the project, such as total lines of code, number of functions, etc.

5. Add support for more file types in the `file_handlers.py` module, such as Ruby, Java, or C++.

These exercises will help you practice and extend the functionality of the AICoder tool while reinforcing the concepts learned in this lesson.

Stay tuned for the next lesson, where we'll dive into version control integration and further enhance our AI-assisted coding tool!