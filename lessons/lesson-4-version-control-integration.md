# Lesson 4: Version Control Integration: Git Basics

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Integrating with GitPython](#integrating-with-gitpython)
4. [Implementing Basic Git Operations](#implementing-basic-git-operations)
5. [Creating a Commit Message Generator](#creating-a-commit-message-generator)
6. [Handling Merge Conflicts](#handling-merge-conflicts)
7. [Implementing a Simple Branching Strategy](#implementing-a-simple-branching-strategy)
8. [Practical Exercise](#practical-exercise)
9. [Conclusion](#conclusion)

## 1. Introduction <a name="introduction"></a>

In this lesson, we'll focus on integrating version control capabilities into our AI-assisted coding tool using Git. Version control is crucial for managing code changes, collaborating with others, and maintaining a history of project evolution. We'll use the GitPython library to interact with Git repositories programmatically.

By the end of this lesson, you'll be able to:
- Integrate GitPython into your project
- Implement basic Git operations (status, add, commit)
- Create an AI-powered commit message generator
- Handle merge conflicts programmatically
- Implement a simple branching strategy

Let's dive in!

## 2. Project Structure <a name="project-structure"></a>

Before we start, let's look at our project structure:

```
aider/
│
├── aider/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── config.py
│   ├── utils.py
│   └── git_manager.py  # New file for Git operations
│
├── tests/
│   └── test_git_manager.py
│
├── .env
├── .gitignore
├── requirements.txt
└── setup.py
```

We'll be working primarily in the `git_manager.py` file, which will contain our Git-related functionality.

## 3. Integrating with GitPython <a name="integrating-with-gitpython"></a>

First, let's install GitPython:

```bash
pip install GitPython
```

Add it to your `requirements.txt`:

```
GitPython==3.1.30
```

Now, let's create the `git_manager.py` file:

```python
# aider/git_manager.py

import os
from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError

class GitManager:
    def __init__(self, repo_path='.'):
        self.repo_path = repo_path
        try:
            self.repo = Repo(self.repo_path)
        except InvalidGitRepositoryError:
            self.repo = None

    def is_git_repo(self):
        return self.repo is not None

    def initialize_repo(self):
        if not self.is_git_repo():
            self.repo = Repo.init(self.repo_path)
            return True
        return False
```

This `GitManager` class will be the foundation for our Git operations. It initializes a connection to an existing Git repository or creates a new one if needed.

## 4. Implementing Basic Git Operations <a name="implementing-basic-git-operations"></a>

Let's implement the basic Git operations: status, add, and commit.

```python
# aider/git_manager.py

class GitManager:
    # ... (previous code)

    def get_status(self):
        if not self.is_git_repo():
            return None
        return self.repo.git.status()

    def stage_file(self, file_path):
        if not self.is_git_repo():
            return False
        try:
            self.repo.git.add(file_path)
            return True
        except GitCommandError:
            return False

    def commit(self, message):
        if not self.is_git_repo():
            return False
        try:
            self.repo.git.commit('-m', message)
            return True
        except GitCommandError:
            return False
```

Now we can use these methods to perform basic Git operations. Let's update our `cli.py` to include these new Git commands:

```python
# aider/cli.py

import click
from .git_manager import GitManager

@click.group()
@click.option('--repo-path', default='.', help='Path to the Git repository')
@click.pass_context
def cli(ctx, repo_path):
    ctx.obj = GitManager(repo_path)

@cli.command()
@click.pass_obj
def status(git_manager):
    """Show the working tree status"""
    status_output = git_manager.get_status()
    if status_output:
        click.echo(status_output)
    else:
        click.echo("Not a Git repository")

@cli.command()
@click.argument('file_path')
@click.pass_obj
def add(git_manager, file_path):
    """Add file contents to the index"""
    if git_manager.stage_file(file_path):
        click.echo(f"Successfully staged {file_path}")
    else:
        click.echo(f"Failed to stage {file_path}")

@cli.command()
@click.option('--message', '-m', required=True, help='Commit message')
@click.pass_obj
def commit(git_manager, message):
    """Record changes to the repository"""
    if git_manager.commit(message):
        click.echo(f"Successfully committed with message: {message}")
    else:
        click.echo("Failed to commit changes")

if __name__ == '__main__':
    cli()
```

## 5. Creating a Commit Message Generator <a name="creating-a-commit-message-generator"></a>

Now, let's create an AI-powered commit message generator using OpenAI's GPT model. First, make sure you have the OpenAI library installed:

```bash
pip install openai
```

Add it to your `requirements.txt`:

```
openai==0.27.0
```

Now, let's create a new file called `ai_commit.py`:

```python
# aider/ai_commit.py

import openai
from .config import get_openai_api_key

openai.api_key = get_openai_api_key()

def generate_commit_message(diff):
    prompt = f"""
    Based on the following Git diff, generate a concise and descriptive commit message:

    {diff}

    The commit message should:
    1. Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update")
    2. Be no longer than 50 characters
    3. Provide a brief summary of the changes

    Commit message:
    """

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].text.strip()
```

Now, let's update our `GitManager` class to use this AI-generated commit message:

```python
# aider/git_manager.py

from .ai_commit import generate_commit_message

class GitManager:
    # ... (previous code)

    def get_diff(self):
        if not self.is_git_repo():
            return None
        return self.repo.git.diff('--staged')

    def commit_with_ai_message(self):
        if not self.is_git_repo():
            return False
        diff = self.get_diff()
        if not diff:
            return False
        commit_message = generate_commit_message(diff)
        return self.commit(commit_message)
```

Update the `cli.py` file to include this new AI-powered commit command:

```python
# aider/cli.py

@cli.command()
@click.pass_obj
def commit_ai(git_manager):
    """Commit changes with an AI-generated commit message"""
    if git_manager.commit_with_ai_message():
        click.echo("Successfully committed with an AI-generated message")
    else:
        click.echo("Failed to commit changes")
```

## 6. Handling Merge Conflicts <a name="handling-merge-conflicts"></a>

Handling merge conflicts programmatically can be challenging, but we can provide a simple interface to help users resolve conflicts. Let's add some methods to our `GitManager` class:

```python
# aider/git_manager.py

class GitManager:
    # ... (previous code)

    def get_conflicted_files(self):
        if not self.is_git_repo():
            return None
        return [item.a_path for item in self.repo.index.unmerged_blobs()]

    def resolve_conflict(self, file_path, content):
        if not self.is_git_repo():
            return False
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            self.repo.git.add(file_path)
            return True
        except Exception:
            return False

    def abort_merge(self):
        if not self.is_git_repo():
            return False
        try:
            self.repo.git.merge('--abort')
            return True
        except GitCommandError:
            return False
```

Now, let's add CLI commands to handle merge conflicts:

```python
# aider/cli.py

@cli.command()
@click.pass_obj
def show_conflicts(git_manager):
    """Show files with merge conflicts"""
    conflicts = git_manager.get_conflicted_files()
    if conflicts:
        click.echo("Files with merge conflicts:")
        for file in conflicts:
            click.echo(f"- {file}")
    else:
        click.echo("No merge conflicts found")

@cli.command()
@click.argument('file_path')
@click.argument('content')
@click.pass_obj
def resolve_conflict(git_manager, file_path, content):
    """Resolve a merge conflict for a specific file"""
    if git_manager.resolve_conflict(file_path, content):
        click.echo(f"Successfully resolved conflict in {file_path}")
    else:
        click.echo(f"Failed to resolve conflict in {file_path}")

@cli.command()
@click.pass_obj
def abort_merge(git_manager):
    """Abort the current merge operation"""
    if git_manager.abort_merge():
        click.echo("Successfully aborted the merge")
    else:
        click.echo("Failed to abort the merge")
```

## 7. Implementing a Simple Branching Strategy <a name="implementing-a-simple-branching-strategy"></a>

Let's implement a simple branching strategy that includes creating, switching, and merging branches. Add the following methods to the `GitManager` class:

```python
# aider/git_manager.py

class GitManager:
    # ... (previous code)

    def create_branch(self, branch_name):
        if not self.is_git_repo():
            return False
        try:
            self.repo.git.branch(branch_name)
            return True
        except GitCommandError:
            return False

    def switch_branch(self, branch_name):
        if not self.is_git_repo():
            return False
        try:
            self.repo.git.checkout(branch_name)
            return True
        except GitCommandError:
            return False

    def merge_branch(self, branch_name):
        if not self.is_git_repo():
            return False
        try:
            self.repo.git.merge(branch_name)
            return True
        except GitCommandError:
            return False

    def list_branches(self):
        if not self.is_git_repo():
            return None
        return [str(branch) for branch in self.repo.branches]
```

Now, let's add the corresponding CLI commands:

```python
# aider/cli.py

@cli.command()
@click.argument('branch_name')
@click.pass_obj
def create_branch(git_manager, branch_name):
    """Create a new branch"""
    if git_manager.create_branch(branch_name):
        click.echo(f"Successfully created branch: {branch_name}")
    else:
        click.echo(f"Failed to create branch: {branch_name}")

@cli.command()
@click.argument('branch_name')
@click.pass_obj
def switch_branch(git_manager, branch_name):
    """Switch to a different branch"""
    if git_manager.switch_branch(branch_name):
        click.echo(f"Successfully switched to branch: {branch_name}")
    else:
        click.echo(f"Failed to switch to branch: {branch_name}")

@cli.command()
@click.argument('branch_name')
@click.pass_obj
def merge_branch(git_manager, branch_name):
    """Merge a branch into the current branch"""
    if git_manager.merge_branch(branch_name):
        click.echo(f"Successfully merged branch: {branch_name}")
    else:
        click.echo(f"Failed to merge branch: {branch_name}")

@cli.command()
@click.pass_obj
def list_branches(git_manager):
    """List all branches in the repository"""
    branches = git_manager.list_branches()
    if branches:
        click.echo("Branches:")
        for branch in branches:
            click.echo(f"- {branch}")
    else:
        click.echo("No branches found or not a Git repository")
```

## 8. Practical Exercise <a name="practical-exercise"></a>

Now that we have implemented various Git functionalities, let's create a practical exercise to reinforce what we've learned.

Exercise: Implement a feature using our Git-integrated CLI tool

1. Initialize a new Git repository
2. Create a new file called `feature.py` with some initial content
3. Stage and commit the file using our AI-generated commit message
4. Create a new branch called `new-feature`
5. Switch to the `new-feature` branch
6. Modify the `feature.py` file
7. Stage and commit the changes
8. Switch back to the `main` branch
9. Merge the `new-feature` branch into `main`
10. List all branches and display the final status

Here's a step-by-step solution using our CLI commands:

```bash
# 1. Initialize a new Git repository
mkdir git-exercise
cd git-exercise
python -m aider.cli init

# 2. Create a new file called feature.py
echo "def greet():\n    print('Hello, World!')" > feature.py

# 3. Stage and commit the file using AI-generated commit message
python -m aider.cli add feature.py
python -m aider.cli commit-ai

# 4. Create a new branch called new-feature
python -m aider.cli create-branch new-feature

# 5. Switch to the new-feature branch
python -m aider.cli switch-branch new-feature

# 6. Modify the feature.py file
echo "def greet(name):\n    print(f'Hello, {name}!')" > feature.py

# 7. Stage and commit the changes
python -m aider.cli add feature.py
python -m aider.cli commit-ai

# 8. Switch back to the main branch
python -m aider.cli switch-branch main

# 9. Merge the new-feature branch into main
python -m aider.cli merge-branch new-feature

# 10. List all branches and display the final status
python -m aider.cli list-branches
python -m aider.cli status
```

This exercise demonstrates how to use our newly implemented Git functionality in a typical development workflow.

## 9. Conclusion <a name="conclusion"></a>

In this lesson, we've successfully integrated Git functionality into our AI-assisted coding tool. We've implemented basic Git operations, created an AI-powered commit message generator, added support for handling merge conflicts, and implemented a simple branching strategy. Here's a summary of what we've accomplished:

1. Integrated GitPython into our project
2. Implemented basic Git operations (status, add, commit)
3. Created an AI-powered commit message generator using OpenAI's GPT model
4. Added functionality to handle merge conflicts
5. Implemented a simple branching strategy (create, switch, merge, list branches)
6. Created a practical exercise to reinforce the concepts learned

These features provide a solid foundation for version control integration in our AI-assisted coding tool. As you continue to develop your tool, consider adding more advanced Git features, such as:

- Pull and push operations for remote repositories
- Stash management
- Interactive rebasing
- Git hooks integration
- Visualization of commit history and branch structure

Remember that while our implementation provides programmatic access to Git operations, it's essential to understand Git concepts and best practices. Encourage users of your tool to familiarize themselves with Git to make the most of these features.

## 10. Further Reading and Resources

To deepen your understanding of Git and version control integration, consider exploring the following resources:

1. [Pro Git Book](https://git-scm.com/book/en/v2) - A comprehensive guide to Git
2. [GitPython Documentation](https://gitpython.readthedocs.io/) - Official documentation for the GitPython library
3. [Conventional Commits](https://www.conventionalcommits.org/) - A specification for adding human and machine-readable meaning to commit messages
4. [Git Branching Strategies](https://www.atlassian.com/git/tutorials/comparing-workflows) - An overview of different Git branching workflows
5. [OpenAI API Documentation](https://beta.openai.com/docs/) - Official documentation for the OpenAI API used in our commit message generator

## 11. Next Steps

In the next lesson, we'll focus on "Context Management and Session Handling." We'll build upon our Git integration to create a more robust system for managing project context and user sessions. This will include:

1. Designing a context management system
2. Implementing session persistence
3. Creating a chat history manager
4. Developing a prompt template system
5. Implementing context-aware completions

By the end of the next lesson, you'll have a more sophisticated AI-assisted coding tool that can maintain context across multiple sessions and provide more accurate and relevant assistance to users.

As you move forward, continue to practice and expand upon the Git integration we've built in this lesson. Experiment with different branching strategies and try to incorporate version control seamlessly into your development workflow. Happy coding!