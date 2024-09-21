# Lesson 25: Predictive Coding and Intelligent Suggestions

## 1. Introduction (10 minutes)

Welcome to Lesson 25 of our advanced AI-assisted coding tool development series. In this lesson, we'll dive deep into predictive coding and intelligent suggestions, which are crucial features for enhancing developer productivity and code quality.

### Topics we'll cover:
1. Implementing a predictive coding system
2. Developing an intelligent code completion engine
3. Creating a system for suggesting design patterns
4. Implementing an automated code optimization system
5. Developing a bug prediction and prevention tool

Let's start by looking at our project structure:

```
aider/
├── __init__.py
├── main.py
├── config.py
├── cli/
│   ├── __init__.py
│   └── commands.py
├── core/
│   ├── __init__.py
│   ├── file_manager.py
│   ├── git_manager.py
│   └── context_manager.py
├── ai/
│   ├── __init__.py
│   ├── openai_integration.py
│   ├── prompt_engineering.py
│   └── model_manager.py
├── predictive_coding/
│   ├── __init__.py
│   ├── predictor.py
│   ├── code_completer.py
│   ├── pattern_suggester.py
│   ├── code_optimizer.py
│   └── bug_predictor.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

In this lesson, we'll be primarily working within the `predictive_coding` directory, adding new files and implementing various predictive coding and intelligent suggestion features.

## 2. Implementing a Predictive Coding System (30 minutes)

Predictive coding is a technique that anticipates what a developer is likely to type next based on the current context and historical data. Let's implement a basic predictive coding system.

First, let's create a new file `predictor.py` in the `predictive_coding` directory:

```python
# aider/predictive_coding/predictor.py

import re
from collections import defaultdict

class Predictor:
    def __init__(self):
        self.n_gram_model = defaultdict(lambda: defaultdict(int))
        self.n = 3  # We'll use trigrams

    def train(self, code):
        tokens = self._tokenize(code)
        for i in range(len(tokens) - self.n):
            context = tuple(tokens[i:i+self.n-1])
            next_token = tokens[i+self.n-1]
            self.n_gram_model[context][next_token] += 1

    def predict(self, context):
        context = tuple(self._tokenize(context)[-self.n+1:])
        if context in self.n_gram_model:
            predictions = self.n_gram_model[context]
            return max(predictions, key=predictions.get)
        return None

    def _tokenize(self, code):
        return re.findall(r'\w+|[^\w\s]', code)
```

Now, let's update `main.py` to include our new predictive coding feature:

```python
# aider/main.py

import click
from .predictive_coding.predictor import Predictor

predictor = Predictor()

@click.group()
def cli():
    pass

@cli.command()
@click.argument('file', type=click.File('r'))
def train(file):
    """Train the predictor on a file."""
    code = file.read()
    predictor.train(code)
    click.echo("Predictor trained successfully.")

@cli.command()
@click.argument('context')
def predict(context):
    """Predict the next token given a context."""
    prediction = predictor.predict(context)
    if prediction:
        click.echo(f"Predicted next token: {prediction}")
    else:
        click.echo("Unable to make a prediction.")

if __name__ == '__main__':
    cli()
```

This implementation creates a simple n-gram model for predicting the next token based on the previous tokens. It can be trained on existing code and then used to make predictions.

## 3. Developing an Intelligent Code Completion Engine (40 minutes)

Next, let's create a more advanced code completion engine that uses our predictor along with some heuristics and AI capabilities. We'll create a new file `code_completer.py`:

```python
# aider/predictive_coding/code_completer.py

import re
from .predictor import Predictor
from ..ai.openai_integration import get_completion

class CodeCompleter:
    def __init__(self):
        self.predictor = Predictor()
        self.common_patterns = {
            'for': 'for {} in {}:\n    ',
            'if': 'if {}:\n    ',
            'def': 'def {}():\n    ',
            'class': 'class {}:\n    ',
        }

    def complete(self, code, cursor_position):
        context = code[:cursor_position]
        last_word = re.findall(r'\w+', context)[-1] if re.findall(r'\w+', context) else ''

        # Check for common patterns
        if last_word in self.common_patterns:
            return self.common_patterns[last_word]

        # Use the n-gram predictor
        prediction = self.predictor.predict(context)
        if prediction:
            return prediction

        # If all else fails, use AI to generate a completion
        prompt = f"Complete the following Python code:\n\n{context}"
        ai_completion = get_completion(prompt)
        return ai_completion.split('\n')[0]  # Return only the first line of the AI completion

```

Now, let's update `main.py` to include our new code completion feature:

```python
# aider/main.py

import click
from .predictive_coding.predictor import Predictor
from .predictive_coding.code_completer import CodeCompleter

predictor = Predictor()
code_completer = CodeCompleter()

# ... (previous code remains the same)

@cli.command()
@click.argument('file', type=click.File('r'))
@click.argument('cursor_position', type=int)
def complete(file, cursor_position):
    """Complete code at the given cursor position."""
    code = file.read()
    completion = code_completer.complete(code, cursor_position)
    click.echo(f"Suggested completion: {completion}")

# ... (rest of the file remains the same)
```

This implementation combines n-gram prediction, common coding patterns, and AI-generated completions to provide intelligent code suggestions.

## 4. Creating a System for Suggesting Design Patterns (30 minutes)

Design patterns are reusable solutions to common problems in software design. Let's create a system that suggests appropriate design patterns based on the current code context. We'll create a new file `pattern_suggester.py`:

```python
# aider/predictive_coding/pattern_suggester.py

import re
from ..ai.openai_integration import get_completion

class PatternSuggester:
    def __init__(self):
        self.patterns = {
            'Singleton': r'class.*\n.*@classmethod\n.*def instance\(',
            'Factory': r'class.*Factory:',
            'Observer': r'class.*Observer:.*\n.*def update\(',
            'Strategy': r'class.*Strategy:.*\n.*def execute\(',
        }

    def suggest(self, code):
        suggestions = []
        for pattern, regex in self.patterns.items():
            if re.search(regex, code):
                suggestions.append(pattern)

        if not suggestions:
            # Use AI to suggest a pattern
            prompt = f"""
            Analyze the following Python code and suggest an appropriate design pattern:

            {code}

            Respond with only the name of the suggested design pattern.
            """
            ai_suggestion = get_completion(prompt).strip()
            suggestions.append(ai_suggestion)

        return suggestions
```

Now, let's update `main.py` to include our new design pattern suggestion feature:

```python
# aider/main.py

import click
from .predictive_coding.predictor import Predictor
from .predictive_coding.code_completer import CodeCompleter
from .predictive_coding.pattern_suggester import PatternSuggester

predictor = Predictor()
code_completer = CodeCompleter()
pattern_suggester = PatternSuggester()

# ... (previous code remains the same)

@cli.command()
@click.argument('file', type=click.File('r'))
def suggest_pattern(file):
    """Suggest design patterns for the given file."""
    code = file.read()
    suggestions = pattern_suggester.suggest(code)
    if suggestions:
        click.echo(f"Suggested design patterns: {', '.join(suggestions)}")
    else:
        click.echo("No specific design pattern suggested for this code.")

# ... (rest of the file remains the same)
```

This implementation uses both predefined regex patterns and AI suggestions to recommend appropriate design patterns for the given code.

## 5. Implementing an Automated Code Optimization System (40 minutes)

Now, let's create a system that can automatically suggest optimizations for the given code. We'll create a new file `code_optimizer.py`:

```python
# aider/predictive_coding/code_optimizer.py

import ast
from ..ai.openai_integration import get_completion

class CodeOptimizer:
    def __init__(self):
        self.optimizations = {
            'list_comprehension': self._optimize_list_comprehension,
            'remove_unused_variables': self._remove_unused_variables,
            'use_set_operations': self._use_set_operations,
        }

    def optimize(self, code):
        tree = ast.parse(code)
        optimized = False
        for optimization in self.optimizations.values():
            new_tree, changed = optimization(tree)
            if changed:
                tree = new_tree
                optimized = True

        if optimized:
            return ast.unparse(tree)
        else:
            # If no built-in optimizations were applied, use AI
            return self._ai_optimize(code)

    def _optimize_list_comprehension(self, tree):
        class ListComprehensionTransformer(ast.NodeTransformer):
            def visit_For(self, node):
                if (isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Call) and 
                    isinstance(node.body[0].value.func, ast.Attribute) and 
                    node.body[0].value.func.attr == 'append'):
                    
                    new_node = ast.List(
                        elts=[ast.ListComp(
                            elt=node.body[0].value.args[0],
                            generators=[
                                ast.comprehension(
                                    target=node.target,
                                    iter=node.iter,
                                    ifs=[],
                                    is_async=0
                                )
                            ]
                        )],
                        ctx=ast.Load()
                    )
                    return new_node
                return node

        transformer = ListComprehensionTransformer()
        new_tree = transformer.visit(tree)
        return new_tree, new_tree != tree

    def _remove_unused_variables(self, tree):
        # Implementation of unused variable removal
        # This is a complex task and might require a full static analysis
        # For simplicity, we'll just return the original tree
        return tree, False

    def _use_set_operations(self, tree):
        class SetOperationTransformer(ast.NodeTransformer):
            def visit_Call(self, node):
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr in ['intersection', 'union', 'difference'] and 
                    isinstance(node.func.value, ast.Call) and 
                    isinstance(node.func.value.func, ast.Name) and 
                    node.func.value.func.id == 'set'):
                    
                    new_node = ast.BinOp(
                        left=node.func.value,
                        op=ast.BitAnd() if node.func.attr == 'intersection' else
                           ast.BitOr() if node.func.attr == 'union' else
                           ast.Sub(),
                        right=node.args[0]
                    )
                    return new_node
                return node

        transformer = SetOperationTransformer()
        new_tree = transformer.visit(tree)
        return new_tree, new_tree != tree

    def _ai_optimize(self, code):
        prompt = f"""
        Optimize the following Python code:

        {code}

        Provide only the optimized code without any explanations.
        """
        return get_completion(prompt)
```

Now, let's update `main.py` to include our new code optimization feature:

```python
# aider/main.py

import click
from .predictive_coding.predictor import Predictor
from .predictive_coding.code_completer import CodeCompleter
from .predictive_coding.pattern_suggester import PatternSuggester
from .predictive_coding.code_optimizer import CodeOptimizer

predictor = Predictor()
code_completer = CodeCompleter()
pattern_suggester = PatternSuggester()
code_optimizer = CodeOptimizer()

# ... (previous code remains the same)

@cli.command()
@click.argument('file', type=click.File('r'))
def optimize(file):
    """Optimize the code in the given file."""
    code = file.read()
    optimized_code = code_optimizer.optimize(code)
    click.echo("Optimized code:")
    click.echo(optimized_code)

# ... (rest of the file remains the same)
```

This implementation includes both rule-based optimizations (like converting loops to list comprehensions and using set operations) and AI-based optimization for more complex cases.

## 6. Developing a Bug Prediction and Prevention Tool (30 minutes)

Lastly, let's create a tool that can predict potential bugs in the code and suggest preventive measures. We'll create a new file `bug_predictor.py`:

```python
# aider/predictive_coding/bug_predictor.py

import ast
from ..ai.openai_integration import get_completion

class BugPredictor:
    def __init__(self):
        self.common_bugs = {
            'division_by_zero': self._check_division_by_zero,
            'unused_variables': self._check_unused_variables,
            'undefined_variables': self._check_undefined_variables,
        }

    def predict(self, code):
        tree = ast.parse(code)
        predictions = []
        for bug_type, checker in self.common_bugs.items():
            bugs = checker(tree)
            predictions.extend(bugs)

        if not predictions:
            # Use AI to predict potential bugs
            ai_predictions = self._ai_predict_bugs(code)
            predictions.extend(ai_predictions)

        return predictions

    def _check_division_by_zero(self, tree):
        class DivisionByZeroChecker(ast.NodeVisitor):
            def __init__(self):
                self.bugs = []

            def visit_BinOp(self, node):
                if isinstance(node.op, ast.Div) and isinstance(node.right, ast.Num) and node.right.n == 0:
                    self.bugs.append(f"Potential division by zero at line {node.lineno}")
                self.generic_visit(node)

        checker = DivisionByZeroChecker()
        checker.visit(tree)
        return checker.bugs

    def _check_unused_variables(self, tree):
        # This is a simplified check and might have false positives
        class UnusedVariableChecker(ast.NodeVisitor):
            def __init__(self):
                self.defined = set()
                self.used = set()
                self.bugs = []

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.defined.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    self.used.add(node.id)

            def report(self):
                unused = self.defined - self.used
                for var in unused:
                    self.bugs.append(f"Unused variable: {var}")

        checker = UnusedVariableChecker()
        checker.visit(tree)
        checker.report()
        return checker.bugs

    def _check_undefined_variables(self, tree):
        class UndefinedVariableChecker(ast.NodeVisitor):
            def __init__(self):
                self.defined = set()
                self.used = set()
                self.bugs = []

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.defined.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    self.used.add(node.id)

            def report(self):
                undefined = self.used - self.defined
                for var in undefined:
                    self.bugs.append(f"Potentially undefined variable: {var}")

        checker = UndefinedVariableChecker()
        checker.visit(tree)
        checker.report()
        return checker.bugs

    def _ai_predict_bugs(self, code):
        prompt = f"""
        Analyze the following Python code for potential bugs:

        {code}

        List only the potential bugs, one per line, without any additional explanation.
        """
        ai_predictions = get_completion(prompt).strip().split('\n')
        return [pred for pred in ai_predictions if pred]
```

Now, let's update `main.py` to include our new bug prediction feature:

```python
# aider/main.py

import click
from .predictive_coding.predictor import Predictor
from .predictive_coding.code_completer import CodeCompleter
from .predictive_coding.pattern_suggester import PatternSuggester
from .predictive_coding.code_optimizer import CodeOptimizer
from .predictive_coding.bug_predictor import BugPredictor

predictor = Predictor()
code_completer = CodeCompleter()
pattern_suggester = PatternSuggester()
code_optimizer = CodeOptimizer()
bug_predictor = BugPredictor()

# ... (previous code remains the same)

@cli.command()
@click.argument('file', type=click.File('r'))
def predict_bugs(file):
    """Predict potential bugs in the given file."""
    code = file.read()
    predictions = bug_predictor.predict(code)
    if predictions:
        click.echo("Potential bugs detected:")
        for prediction in predictions:
            click.echo(f"- {prediction}")
    else:
        click.echo("No potential bugs detected.")

# ... (rest of the file remains the same)
```

This implementation includes both static analysis-based bug prediction (checking for division by zero, unused variables, and undefined variables) and AI-based bug prediction for more complex cases.

## 7. Practical Exercise (30 minutes)

Now that we have implemented all these features, let's create a practical exercise to tie everything together. Create a new Python file in your project directory called `exercise.py` with the following content:

```python
# exercise.py

def process_data(data):
    result = []
    for item in data:
        if item % 2 == 0:
            result.append(item * 2)
    return result

def main():
    numbers = [1, 2, 3, 4, 5]
    processed = process_data(numbers)
    print(f"Processed data: {processed}")

    set1 = set([1, 2, 3, 4, 5])
    set2 = set([4, 5, 6, 7, 8])
    intersection = set1.intersection(set2)
    print(f"Intersection: {intersection}")

    x = 10
    y = 0
    z = x / y

if __name__ == "__main__":
    main()
```

Now, use the Aider tool to analyze, optimize, and improve this code. Run the following commands:

1. Train the predictor:
   ```
   python -m aider train exercise.py
   ```

2. Get code completion suggestions:
   ```
   python -m aider complete exercise.py 50
   ```

3. Suggest design patterns:
   ```
   python -m aider suggest_pattern exercise.py
   ```

4. Optimize the code:
   ```
   python -m aider optimize exercise.py
   ```

5. Predict potential bugs:
   ```
   python -m aider predict_bugs exercise.py
   ```

Analyze the output of each command and see how the Aider tool helps improve the code.

## 8. Discussion and Q&A (10 minutes)

Let's review the key concepts we've covered in this lesson:

1. We implemented a predictive coding system using n-grams and AI assistance.
2. We developed an intelligent code completion engine that combines multiple techniques.
3. We created a system for suggesting appropriate design patterns.
4. We implemented an automated code optimization system using both rule-based and AI-based approaches.
5. We developed a bug prediction and prevention tool using static analysis and AI.

These features significantly enhance the capabilities of our AI-assisted coding tool, making it more powerful and useful for developers.

### Potential improvements and extensions:

1. Integrate these features more tightly with popular IDEs and text editors.
2. Implement a learning system that improves predictions based on user feedback.
3. Extend the bug prediction system to include more complex static analysis techniques.
4. Develop a more sophisticated AI model specifically trained on code patterns and common bugs.
5. Implement a feature to explain the reasoning behind code optimizations and bug predictions.

### Q&A

Feel free to ask any questions about the concepts we've covered or the implementation details. Here are some questions to consider:

1. How might we improve the accuracy of our predictive coding system?
2. What are some potential limitations of our current code optimization approach?
3. How can we ensure that the AI-generated suggestions are always safe and appropriate?
4. What additional features would you like to see in an AI-assisted coding tool?

## Conclusion

In this lesson, we've built a comprehensive set of predictive coding and intelligent suggestion features for our AI-assisted coding tool. These features demonstrate the power of combining traditional software engineering techniques with modern AI capabilities. As you continue to develop and use this tool, consider how you can further refine and expand its capabilities to best suit your development needs.

Remember that while AI assistance can greatly enhance productivity, it's crucial to always review and understand the suggestions provided by the tool. Happy coding!