# Lesson 14: Error Handling and Debugging

## Introduction

In this lesson, we'll focus on implementing robust error handling and debugging features for our AI-assisted coding tool. Proper error handling is crucial for maintaining a stable and user-friendly application, while effective debugging tools can significantly speed up development and troubleshooting processes. We'll cover various techniques including a comprehensive error handling system, debug mode with detailed logging, AI-assisted error resolution, crash report generation, and a self-diagnostic tool.

## Project Structure

Before we dive into the error handling and debugging techniques, let's review our project structure:

```
aider/
│
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── commands.py
│
├── core/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── git_manager.py
│   ├── context_manager.py
│   └── ai_integration.py
│
├── utils/
│   ├── __init__.py
│   ├── error_handler.py
│   ├── logger.py
│   ├── crash_reporter.py
│   └── diagnostics.py
│
├── ai/
│   ├── __init__.py
│   └── error_resolver.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_core.py
│   └── test_utils.py
│
├── config.py
├── main.py
└── requirements.txt
```

Now, let's go through each error handling and debugging technique in detail.

## 1. Designing a Comprehensive Error Handling System

A comprehensive error handling system helps in capturing, logging, and properly responding to various types of errors that may occur during the execution of our tool. Let's create a custom error handling system in `utils/error_handler.py`:

```python
# utils/error_handler.py

import sys
import traceback
from utils.logger import Logger

class AiderError(Exception):
    """Base class for Aider-specific errors"""
    pass

class FileNotFoundError(AiderError):
    """Raised when a file is not found"""
    pass

class GitError(AiderError):
    """Raised when a Git operation fails"""
    pass

class AIError(AiderError):
    """Raised when an AI-related operation fails"""
    pass

class ErrorHandler:
    def __init__(self):
        self.logger = Logger()

    def handle_error(self, error, exit_program=False):
        error_type = type(error).__name__
        error_message = str(error)
        traceback_str = traceback.format_exc()

        self.logger.error(f"{error_type}: {error_message}")
        self.logger.debug(traceback_str)

        if isinstance(error, AiderError):
            print(f"Aider Error: {error_message}")
        else:
            print(f"An unexpected error occurred: {error_message}")

        if exit_program:
            sys.exit(1)

error_handler = ErrorHandler()

def safe_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_handler.handle_error(e)
    return wrapper
```

Now we can use this error handling system throughout our application:

```python
# cli/main.py

from utils.error_handler import safe_operation, FileNotFoundError

class AiderCLI:
    @safe_operation
    def process_file(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        # Process the file...
```

## 2. Implementing a Debug Mode with Detailed Logging

To assist in troubleshooting issues, let's implement a debug mode with detailed logging. We'll create a `Logger` class in `utils/logger.py`:

```python
# utils/logger.py

import logging
import os

class Logger:
    def __init__(self, log_file='aider.log', debug_mode=False):
        self.logger = logging.getLogger('aider')
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if debug_mode:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
```

Update the main CLI to use this logger:

```python
# cli/main.py

from utils.logger import Logger

class AiderCLI:
    def __init__(self, debug_mode=False):
        self.logger = Logger(debug_mode=debug_mode)

    def process_file(self, filename):
        self.logger.info(f"Processing file: {filename}")
        # Process the file...
        self.logger.debug(f"File processing complete: {filename}")
```

## 3. Creating an AI-Assisted Error Resolution System

Let's create an AI-assisted error resolution system that can provide suggestions for fixing common errors. We'll implement this in `ai/error_resolver.py`:

```python
# ai/error_resolver.py

from core.ai_integration import AIIntegration

class ErrorResolver:
    def __init__(self):
        self.ai = AIIntegration()

    def get_error_resolution(self, error_message, context):
        prompt = f"""
        Given the following error message and context, suggest a possible solution:

        Error: {error_message}

        Context:
        {context}

        Suggested solution:
        """
        return self.ai.get_completion(prompt)

error_resolver = ErrorResolver()
```

Now, let's update our error handler to use this AI-assisted error resolution:

```python
# utils/error_handler.py

from ai.error_resolver import error_resolver

class ErrorHandler:
    # ... previous code ...

    def handle_error(self, error, exit_program=False):
        # ... previous error handling code ...

        if not exit_program:
            context = self.get_error_context()
            suggested_solution = error_resolver.get_error_resolution(str(error), context)
            print(f"\nAI-suggested solution:\n{suggested_solution}")

    def get_error_context(self):
        # Get relevant context information
        return "Current file being processed, recent operations, etc."
```

## 4. Developing a Crash Report Generator

To help with diagnosing issues that lead to crashes, let's implement a crash report generator in `utils/crash_reporter.py`:

```python
# utils/crash_reporter.py

import sys
import os
import platform
import datetime
import traceback
import json

class CrashReporter:
    def __init__(self, report_dir='crash_reports'):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)

    def generate_report(self, error):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.report_dir, f"crash_report_{timestamp}.json")

        report = {
            "timestamp": timestamp,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "aider_version": "1.0.0",  # Replace with actual version
            },
            "environment_variables": dict(os.environ),
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Crash report generated: {report_file}")

crash_reporter = CrashReporter()
```

Update the error handler to use the crash reporter:

```python
# utils/error_handler.py

from utils.crash_reporter import crash_reporter

class ErrorHandler:
    # ... previous code ...

    def handle_error(self, error, exit_program=False):
        # ... previous error handling code ...

        if exit_program:
            crash_reporter.generate_report(error)
            sys.exit(1)
```

## 5. Implementing a Self-Diagnostic Tool

Finally, let's create a self-diagnostic tool that can check various aspects of the Aider system and report any issues. We'll implement this in `utils/diagnostics.py`:

```python
# utils/diagnostics.py

import os
import sys
import shutil
import subprocess
from utils.logger import Logger

class Diagnostics:
    def __init__(self):
        self.logger = Logger()

    def run_diagnostics(self):
        print("Running Aider self-diagnostics...")
        
        checks = [
            self.check_python_version,
            self.check_dependencies,
            self.check_git_installation,
            self.check_ai_api_key,
            self.check_disk_space,
        ]

        all_passed = True
        for check in checks:
            if not check():
                all_passed = False

        if all_passed:
            print("All diagnostic checks passed.")
        else:
            print("Some diagnostic checks failed. Please review the output above.")

    def check_python_version(self):
        required_version = (3, 7)
        current_version = sys.version_info[:2]
        
        if current_version >= required_version:
            print(f"✅ Python version: {sys.version}")
            return True
        else:
            print(f"❌ Python version: {sys.version}")
            print(f"   Required version: {required_version[0]}.{required_version[1]} or higher")
            return False

    def check_dependencies(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "check"], check=True, capture_output=True)
            print("✅ All dependencies are satisfied")
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Dependency check failed:")
            print(e.stdout.decode())
            return False

    def check_git_installation(self):
        if shutil.which("git"):
            print("✅ Git is installed")
            return True
        else:
            print("❌ Git is not installed or not in PATH")
            return False

    def check_ai_api_key(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            print("✅ AI API key is set")
            return True
        else:
            print("❌ AI API key is not set")
            return False

    def check_disk_space(self):
        _, _, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        if free_gb > 1:
            print(f"✅ Available disk space: {free_gb} GB")
            return True
        else:
            print(f"❌ Low disk space: {free_gb} GB")
            return False

diagnostics = Diagnostics()
```

Now we can add a command to run diagnostics in our CLI:

```python
# cli/main.py

from utils.diagnostics import diagnostics

class AiderCLI:
    # ... other methods ...

    def run_diagnostics(self):
        diagnostics.run_diagnostics()
```

## Conclusion

In this lesson, we've covered several crucial aspects of error handling and debugging for our AI-assisted coding tool:

1. Designing a comprehensive error handling system
2. Implementing a debug mode with detailed logging
3. Creating an AI-assisted error resolution system
4. Developing a crash report generator
5. Implementing a self-diagnostic tool

These features will greatly improve the reliability and maintainability of our tool, making it easier to identify and resolve issues quickly.

## Exercises

1. Implement custom exceptions for at least three specific error scenarios in your AI-assisted coding tool.
2. Add debug logging statements to a complex function in your tool, and use the debug mode to track its execution.
3. Extend the AI-assisted error resolution system to handle a specific type of error (e.g., syntax errors in user-provided code).
4. Modify the crash report generator to include additional relevant information about the tool's state at the time of the crash.
5. Add two more checks to the self-diagnostic tool that are specific to your AI-assisted coding tool's functionality.

## Further Reading

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Python Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Traceback Module](https://docs.python.org/3/library/traceback.html)
- [Python Debugging Techniques](https://realpython.com/python-debugging-pdb/)
- [Best Practices for Exception Handling](https://docs.python-guide.org/writing/gotchas/#exceptions)

By implementing these error handling and debugging features, you'll create a more robust and maintainable AI-assisted coding tool that can better handle unexpected situations and provide valuable information for troubleshooting and improving the application.
