# Lesson 5: Context Management and Session Handling

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Designing a Context Management System](#designing-a-context-management-system)
4. [Implementing Session Persistence](#implementing-session-persistence)
5. [Creating a Chat History Manager](#creating-a-chat-history-manager)
6. [Developing a Prompt Template System](#developing-a-prompt-template-system)
7. [Implementing Context-Aware Completions](#implementing-context-aware-completions)
8. [Practical Exercise](#practical-exercise)
9. [Conclusion](#conclusion)

## 1. Introduction <a name="introduction"></a>

In this lesson, we'll focus on enhancing our AI-assisted coding tool with robust context management and session handling capabilities. These features are crucial for providing a seamless and personalized experience to users, allowing the tool to maintain context across multiple interactions and sessions.

By the end of this lesson, you'll be able to:
- Design and implement a context management system
- Create a session persistence mechanism
- Develop a chat history manager
- Create a flexible prompt template system
- Implement context-aware completions

Let's dive in!

## 2. Project Structure <a name="project-structure"></a>

Before we start, let's update our project structure to accommodate the new features:

```
aider/
│
├── aider/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── config.py
│   ├── utils.py
│   ├── git_manager.py
│   ├── context_manager.py    # New file for context management
│   ├── session_manager.py    # New file for session persistence
│   ├── chat_history.py       # New file for chat history management
│   ├── prompt_templates.py   # New file for prompt templates
│   └── completions.py        # New file for context-aware completions
│
├── tests/
│   ├── test_context_manager.py
│   ├── test_session_manager.py
│   ├── test_chat_history.py
│   ├── test_prompt_templates.py
│   └── test_completions.py
│
├── .env
├── .gitignore
├── requirements.txt
└── setup.py
```

We'll be working primarily with the new files in the `aider/` directory.

## 3. Designing a Context Management System <a name="designing-a-context-management-system"></a>

Let's start by creating a context management system that will keep track of the current project state, active files, and other relevant information.

Create a new file `context_manager.py`:

```python
# aider/context_manager.py

import os
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class FileContext:
    path: str
    content: str
    last_modified: float

@dataclass
class ProjectContext:
    root_path: str
    active_files: List[FileContext] = field(default_factory=list)
    git_branch: str = "main"
    environment_vars: Dict[str, str] = field(default_factory=dict)

class ContextManager:
    def __init__(self, project_root: str):
        self.context = ProjectContext(root_path=project_root)

    def add_file(self, file_path: str):
        abs_path = os.path.join(self.context.root_path, file_path)
        if os.path.exists(abs_path):
            with open(abs_path, 'r') as f:
                content = f.read()
            last_modified = os.path.getmtime(abs_path)
            file_context = FileContext(file_path, content, last_modified)
            self.context.active_files.append(file_context)

    def remove_file(self, file_path: str):
        self.context.active_files = [f for f in self.context.active_files if f.path != file_path]

    def update_git_branch(self, branch_name: str):
        self.context.git_branch = branch_name

    def set_environment_var(self, key: str, value: str):
        self.context.environment_vars[key] = value

    def get_context_summary(self) -> str:
        summary = f"Project Root: {self.context.root_path}\n"
        summary += f"Git Branch: {self.context.git_branch}\n"
        summary += f"Active Files:\n"
        for file in self.context.active_files:
            summary += f"- {file.path}\n"
        summary += "Environment Variables:\n"
        for key, value in self.context.environment_vars.items():
            summary += f"- {key}: {value}\n"
        return summary
```

This `ContextManager` class provides methods to manage the project context, including adding and removing files, updating the Git branch, and setting environment variables.

## 4. Implementing Session Persistence <a name="implementing-session-persistence"></a>

Now, let's implement session persistence to allow users to resume their work from where they left off. We'll use JSON for serialization and deserialization of session data.

Create a new file `session_manager.py`:

```python
# aider/session_manager.py

import json
import os
from dataclasses import asdict
from .context_manager import ContextManager, ProjectContext, FileContext

class SessionManager:
    def __init__(self, session_file: str):
        self.session_file = session_file

    def save_session(self, context_manager: ContextManager):
        session_data = asdict(context_manager.context)
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self) -> ContextManager:
        if not os.path.exists(self.session_file):
            return None

        with open(self.session_file, 'r') as f:
            session_data = json.load(f)

        context = ProjectContext(**session_data)
        context.active_files = [FileContext(**f) for f in session_data['active_files']]
        
        context_manager = ContextManager(context.root_path)
        context_manager.context = context
        return context_manager

    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
```

This `SessionManager` class provides methods to save, load, and clear sessions, allowing users to resume their work across multiple sessions.

## 5. Creating a Chat History Manager <a name="creating-a-chat-history-manager"></a>

To provide context-aware assistance, we need to keep track of the conversation history. Let's create a chat history manager that stores and retrieves past interactions.

Create a new file `chat_history.py`:

```python
# aider/chat_history.py

from dataclasses import dataclass, field
from typing import List
import json

@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass
class ChatHistory:
    messages: List[ChatMessage] = field(default_factory=list)

class ChatHistoryManager:
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.chat_history = ChatHistory()

    def add_message(self, role: str, content: str):
        message = ChatMessage(role, content)
        self.chat_history.messages.append(message)

    def get_recent_messages(self, n: int) -> List[ChatMessage]:
        return self.chat_history.messages[-n:]

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump([asdict(msg) for msg in self.chat_history.messages], f, indent=2)

    def load_history(self):
        if not os.path.exists(self.history_file):
            return

        with open(self.history_file, 'r') as f:
            messages = json.load(f)
        self.chat_history.messages = [ChatMessage(**msg) for msg in messages]

    def clear_history(self):
        self.chat_history.messages.clear()
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
```

This `ChatHistoryManager` class allows us to add messages, retrieve recent messages, and save/load the chat history to/from a file.

## 6. Developing a Prompt Template System <a name="developing-a-prompt-template-system"></a>

To generate consistent and customizable prompts for our AI model, let's create a prompt template system.

Create a new file `prompt_templates.py`:

```python
# aider/prompt_templates.py

from string import Template

class PromptTemplate:
    def __init__(self, template: str):
        self.template = Template(template)

    def format(self, **kwargs):
        return self.template.safe_substitute(**kwargs)

class PromptLibrary:
    def __init__(self):
        self.templates = {
            "code_completion": PromptTemplate(
                "Complete the following code:\n"
                "```$language\n$code\n```\n"
                "Context: $context"
            ),
            "code_explanation": PromptTemplate(
                "Explain the following code:\n"
                "```$language\n$code\n```"
            ),
            "git_commit": PromptTemplate(
                "Generate a commit message for the following changes:\n"
                "```\n$diff\n```"
            ),
            "error_resolution": PromptTemplate(
                "Resolve the following error:\n"
                "```\n$error_message\n```\n"
                "In the context of:\n"
                "```$language\n$code\n```"
            )
        }

    def get_template(self, template_name: str) -> PromptTemplate:
        return self.templates.get(template_name)

    def add_template(self, template_name: str, template: str):
        self.templates[template_name] = PromptTemplate(template)
```

This `PromptLibrary` class provides a collection of customizable prompt templates that can be easily extended and modified.

## 7. Implementing Context-Aware Completions <a name="implementing-context-aware-completions"></a>

Now, let's tie everything together by implementing context-aware completions using the OpenAI API. We'll use the context, chat history, and prompt templates to generate more accurate and relevant completions.

Create a new file `completions.py`:

```python
# aider/completions.py

import openai
from .context_manager import ContextManager
from .chat_history import ChatHistoryManager
from .prompt_templates import PromptLibrary

class ContextAwareCompletions:
    def __init__(self, context_manager: ContextManager, 
                 chat_history: ChatHistoryManager, 
                 prompt_library: PromptLibrary):
        self.context_manager = context_manager
        self.chat_history = chat_history
        self.prompt_library = prompt_library

    def generate_completion(self, prompt_name: str, **kwargs):
        template = self.prompt_library.get_template(prompt_name)
        if not template:
            raise ValueError(f"Unknown prompt template: {prompt_name}")

        context_summary = self.context_manager.get_context_summary()
        recent_messages = self.chat_history.get_recent_messages(5)
        
        prompt = template.format(**kwargs, context=context_summary)
        
        messages = [{"role": "system", "content": "You are an AI programming assistant."}]
        for msg in recent_messages:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        completion = response.choices[0].message['content'].strip()
        self.chat_history.add_message("assistant", completion)
        return completion
```

This `ContextAwareCompletions` class uses the context manager, chat history, and prompt templates to generate context-aware completions using the OpenAI API.

## 8. Practical Exercise <a name="practical-exercise"></a>

Now that we have implemented our context management and session handling systems, let's create a practical exercise to reinforce what we've learned.

Exercise: Implement a simple coding assistant that maintains context across multiple interactions

1. Initialize the project context and session
2. Add a file to the context
3. Generate a code completion
4. Update the Git branch
5. Generate a commit message
6. Save the session and chat history
7. Load the session in a new instance and continue the conversation

Here's a step-by-step solution using our newly implemented classes:

```python
# exercise.py

import os
from aider.context_manager import ContextManager
from aider.session_manager import SessionManager
from aider.chat_history import ChatHistoryManager
from aider.prompt_templates import PromptLibrary
from aider.completions import ContextAwareCompletions

# Initialize managers
context_manager = ContextManager("/path/to/your/project")
session_manager = SessionManager("session.json")
chat_history = ChatHistoryManager("chat_history.json")
prompt_library = PromptLibrary()
completions = ContextAwareCompletions(context_manager, chat_history, prompt_library)

# Add a file to the context
context_manager.add_file("main.py")

# Generate a code completion
completion = completions.generate_completion(
    "code_completion",
    language="python",
    code="def greet(name):\n    "
)
print("Code completion:", completion)

# Update the Git branch
context_manager.update_git_branch("feature/new-greeting")

# Generate a commit message
diff = "diff --git a/main.py b/main.py\n...\n+def greet(name):\n+    print(f'Hello, {name}!')"
commit_message = completions.generate_completion(
    "git_commit",
    diff=diff
)
print("Commit message:", commit_message)

# Save the session and chat history
session_manager.save_session(context_manager)
chat_history.save_history()

# Simulate closing and reopening the tool
del context_manager
del chat_history

# Load the session in a new instance
loaded_context_manager = session_manager.load_session()
loaded_chat_history = ChatHistoryManager("chat_history.json")
loaded_chat_history.load_history()

# Continue the conversation with the loaded context
loaded_completions = ContextAwareCompletions(loaded_context_manager, loaded_chat_history, prompt_library)
new_completion = loaded_completions.generate_completion(
    "code_explanation",
    language="python",
    code="def greet(name):\n    print(f'Hello, {name}!')"
)
print("Code explanation:", new_completion)
```

This exercise demonstrates how to use our newly implemented context management and session handling features in a typical workflow of an AI-assisted coding tool.

## 9. Conclusion <a name="conclusion"></a>

In this lesson, we've successfully implemented a robust context management and session handling system for our AI-assisted coding tool. We've created:

1. A context management system to track project state and active files
2. A session persistence mechanism to save and load user sessions
3. A chat history manager to maintain conversation context
4. A flexible prompt template system for generating consistent prompts
5. A context-aware completion system that leverages all the above components to provide more accurate and relevant assistance

These features provide a solid foundation for maintaining context and handling sessions in our AI-assisted coding tool. As you continue to develop your tool, consider adding more advanced features, such as:

- Intelligent context pruning to manage large projects
- Multi-user support with separate contexts and histories
- Integration with version control systems to track changes across commits
- Natural language understanding to improve context-awareness in user queries
- Customizable prompt templates that users can modify or extend

Remember that while our implementation provides a good starting point, it's essential to continually refine and optimize these systems based on user feedback and real-world usage patterns.

## 10. Further Reading and Resources

To deepen your understanding of context management, session handling, and AI-assisted coding, consider exploring the following resources:

1. [OpenAI API Documentation](https://beta.openai.com/docs/) - Official documentation for the OpenAI API used in our completions
2. [Python dataclasses](https://docs.python.org/3/library/dataclasses.html) - Used for creating simple yet powerful data structures
3. [JSON in Python](https://docs.python.org/3/library/json.html) - Used for serialization and deserialization of session data
4. [Python string Templates](https://docs.python.org/3/library/string.html#template-strings) - Used in our prompt template system
5. [Design Patterns](https://refactoring.guru/design-patterns) - Useful patterns for structuring complex systems

## 11. Next Steps

In the next lesson, we'll focus on "Local Vector Database for Knowledge Management." We'll build upon our context management system to create a more sophisticated knowledge base that can efficiently store and retrieve relevant information. This will include:

1. Introduction to vector databases
2. Setting up a local vector database (e.g., FAISS)
3. Implementing document indexing and retrieval
4. Creating a caching system for faster lookups
5. Developing a query system for context-aware searches

By the end of the next lesson, you'll have an even more powerful AI-assisted coding tool that can efficiently manage and utilize a large knowledge base to provide more accurate and contextually relevant assistance to users.

As you move forward, continue to practice and expand upon the context management and session handling systems we've built in this lesson. Experiment with different ways to utilize context in your AI completions and try to create more sophisticated prompt templates that take advantage of the rich context information available. Happy coding!

## 12. Exercises for Practice

To reinforce your understanding of the concepts covered in this lesson, try the following exercises:

1. Extend the `ContextManager` to include a method for tracking open files in the user's IDE or editor.

2. Implement a method in the `SessionManager` to merge two different sessions, resolving conflicts if necessary.

3. Create a new prompt template that utilizes the git branch information to provide branch-specific completions.

4. Extend the `ChatHistoryManager` to include a method for summarizing the conversation history using the OpenAI API.

5. Implement a simple command-line interface (CLI) that allows users to interact with the context-aware completions system, save/load sessions, and manage chat history.

6. Create a method in the `ContextAwareCompletions` class that can generate unit tests based on the current context and a given function implementation.

7. Implement a simple caching mechanism for the `ContextAwareCompletions` class to avoid redundant API calls for similar queries.

8. Extend the `PromptLibrary` to allow loading custom prompt templates from a configuration file.

9. Create a method in the `ContextManager` that can generate a visual representation (e.g., ASCII art or simple graph) of the current project structure.

10. Implement a simple plugin system that allows users to extend the functionality of the context management system with custom modules.

These exercises will help you gain a deeper understanding of the systems we've built and encourage you to think creatively about how to extend and improve them. As you work through these exercises, you'll likely encounter new challenges and opportunities for optimization, which will further enhance your skills in developing AI-assisted coding tools.

Remember to test your implementations thoroughly and consider edge cases as you work on these exercises. Good luck, and enjoy the process of building your AI-assisted coding tool!
