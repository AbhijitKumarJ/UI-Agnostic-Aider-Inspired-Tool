# Lesson 8: Advanced Code Analysis and Refactoring

## 1. Introduction to Advanced Code Analysis and Refactoring (10 minutes)

In this lesson, we'll dive deep into advanced code analysis and refactoring techniques to enhance our AI-powered coding assistant. These features will allow our tool to provide more insightful suggestions and automate complex code improvements.

### Key Concepts

1. Abstract Syntax Tree (AST) parsing
2. Code complexity analysis
3. Automated refactoring
4. Code style enforcement
5. Code smell detection

### Goals of this lesson

By the end of this lesson, you will be able to:

1. Implement AST parsing for Python code
2. Develop a code complexity analyzer
3. Create an automated refactoring system
4. Implement code style enforcement
5. Develop a code smell detector

Let's start by looking at our updated project structure:

```
aider/
│
├── src/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── openai_integration.py
│   │   └── prompt_engineering.py
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── ast_parser.py
│   │   ├── complexity_analyzer.py
│   │   ├── code_style.py
│   │   └── smell_detector.py
│   │
│   ├── refactoring/
│   │   ├── __init__.py
│   │   └── automated_refactor.py
│   │
│   ├── cli/
│   │   └── main.py
│   │
│   └── utils/
│       └── config.py
│
├── tests/
│   ├── test_ast_parser.py
│   ├── test_complexity_analyzer.py
│   ├── test_code_style.py
│   ├── test_smell_detector.py
│   └── test_automated_refactor.py
│
├── requirements.txt
└── README.md
```

## 2. Implementing Abstract Syntax Tree (AST) Parsing (30 minutes)

Abstract Syntax Tree (AST) parsing is a powerful technique for analyzing and manipulating code. We'll use Python's built-in `ast` module to implement our AST parser.

Let's create the `ast_parser.py` file:

```python
# src/analysis/ast_parser.py

import ast
from typing import Dict, List, Any

class ASTParser:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)

    def get_function_names(self) -> List[str]:
        return [node.name for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]

    def get_class_names(self) -> List[str]:
        return [node.name for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)]

    def get_imported_modules(self) -> List[str]:
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        return imports

    def get_function_complexity(self) -> Dict[str, int]:
        complexity = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                complexity[node.name] = self._calculate_complexity(node)
        return complexity

    def _calculate_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            complexity += self._calculate_complexity(child)
        return complexity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "functions": self.get_function_names(),
            "classes": self.get_class_names(),
            "imports": self.get_imported_modules(),
            "complexity": self.get_function_complexity()
        }

# Example usage
if __name__ == "__main__":
    sample_code = """
import math

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

class MathOperations:
    def __init__(self):
        self.pi = math.pi

    def circle_area(self, radius):
        return self.pi * radius ** 2
    """

    parser = ASTParser(sample_code)
    print(parser.to_dict())
```

This `ASTParser` class provides basic functionality for analyzing Python code structure. It can extract function and class names, imported modules, and calculate a simple complexity metric for functions.

## 3. Developing a Code Complexity Analyzer (25 minutes)

Now that we have our AST parser, let's create a more comprehensive code complexity analyzer. We'll implement the Cyclomatic Complexity metric and provide detailed analysis for each function.

Create the `complexity_analyzer.py` file:

```python
# src/analysis/complexity_analyzer.py

from src.analysis.ast_parser import ASTParser
import ast
from typing import Dict, Any

class ComplexityAnalyzer:
    def __init__(self, code: str):
        self.parser = ASTParser(code)

    def analyze(self) -> Dict[str, Any]:
        return {
            "overall_complexity": self._calculate_overall_complexity(),
            "function_complexity": self._analyze_functions(),
            "class_complexity": self._analyze_classes()
        }

    def _calculate_overall_complexity(self) -> int:
        return sum(self.parser.get_function_complexity().values())

    def _analyze_functions(self) -> Dict[str, Dict[str, Any]]:
        function_analysis = {}
        for node in ast.walk(self.parser.tree):
            if isinstance(node, ast.FunctionDef):
                function_analysis[node.name] = self._analyze_function(node)
        return function_analysis

    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        return {
            "complexity": self.parser._calculate_complexity(node),
            "num_parameters": len(node.args.args),
            "num_local_vars": len([n for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)]),
            "num_return_statements": len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
        }

    def _analyze_classes(self) -> Dict[str, Dict[str, Any]]:
        class_analysis = {}
        for node in ast.walk(self.parser.tree):
            if isinstance(node, ast.ClassDef):
                class_analysis[node.name] = self._analyze_class(node)
        return class_analysis

    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        return {
            "num_methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
            "num_class_variables": len([n for n in node.body if isinstance(n, ast.Assign)]),
            "inheritance": [base.id for base in node.bases if isinstance(base, ast.Name)]
        }

# Example usage
if __name__ == "__main__":
    sample_code = """
class ComplexClass:
    class_var = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def complex_method(self, a, b, c):
        result = 0
        for i in range(a):
            if i % 2 == 0:
                result += i * b
            else:
                result += i * c
        return result

def simple_function():
    return "Hello, World!"
    """

    analyzer = ComplexityAnalyzer(sample_code)
    print(analyzer.analyze())
```

This `ComplexityAnalyzer` class provides a more detailed analysis of the code, including overall complexity, function-level metrics, and class-level metrics.

## 4. Creating an Automated Refactoring System (35 minutes)

Now let's implement an automated refactoring system that can suggest and apply code improvements based on our analysis.

Create the `automated_refactor.py` file:

```python
# src/refactoring/automated_refactor.py

import ast
import astor
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from typing import List, Tuple

class AutomatedRefactorer:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)
        self.analyzer = ComplexityAnalyzer(code)

    def suggest_refactorings(self) -> List[Tuple[str, str, str]]:
        suggestions = []
        analysis = self.analyzer.analyze()

        for func_name, func_analysis in analysis["function_complexity"].items():
            if func_analysis["complexity"] > 10:
                suggestions.append((
                    func_name,
                    "high_complexity",
                    f"Function '{func_name}' has high complexity ({func_analysis['complexity']}). Consider breaking it down into smaller functions."
                ))
            if func_analysis["num_parameters"] > 5:
                suggestions.append((
                    func_name,
                    "too_many_parameters",
                    f"Function '{func_name}' has too many parameters ({func_analysis['num_parameters']}). Consider using a data class or dictionary."
                ))

        for class_name, class_analysis in analysis["class_complexity"].items():
            if class_analysis["num_methods"] > 10:
                suggestions.append((
                    class_name,
                    "too_many_methods",
                    f"Class '{class_name}' has too many methods ({class_analysis['num_methods']}). Consider splitting it into smaller classes."
                ))

        return suggestions

    def apply_refactoring(self, refactoring_type: str, target: str) -> str:
        if refactoring_type == "extract_method":
            return self._extract_method(target)
        elif refactoring_type == "rename":
            return self._rename(target)
        else:
            raise ValueError(f"Unsupported refactoring type: {refactoring_type}")

    def _extract_method(self, function_name: str) -> str:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # This is a simplified extraction. In a real-world scenario,
                # you'd need to analyze the function body and extract a meaningful subset.
                new_func_name = f"extracted_from_{function_name}"
                new_func = ast.FunctionDef(
                    name=new_func_name,
                    args=ast.arguments(args=[], vararg=None, kwarg=None, defaults=[]),
                    body=node.body[:len(node.body)//2],  # Extract first half of the function
                    decorator_list=[]
                )
                ast.fix_missing_locations(new_func)
                
                # Update the original function to call the new function
                call = ast.Expr(ast.Call(func=ast.Name(id=new_func_name, ctx=ast.Load()), args=[], keywords=[]))
                node.body = [call] + node.body[len(node.body)//2:]
                
                # Insert the new function before the original one
                self.tree.body.insert(self.tree.body.index(node), new_func)
                
                return astor.to_source(self.tree)

    def _rename(self, old_name: str) -> str:
        new_name = f"renamed_{old_name}"
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == old_name:
                node.name = new_name
            elif isinstance(node, ast.Name) and node.id == old_name:
                node.id = new_name
        return astor.to_source(self.tree)

# Example usage
if __name__ == "__main__":
    sample_code = """
def complex_function(a, b, c, d, e, f):
    result = 0
    for i in range(a):
        if i % 2 == 0:
            result += i * b
        else:
            result += i * c
    for j in range(d):
        if j % 2 == 0:
            result -= j * e
        else:
            result -= j * f
    return result

class LargeClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    """

    refactorer = AutomatedRefactorer(sample_code)
    print("Refactoring suggestions:")
    for suggestion in refactorer.suggest_refactorings():
        print(f"- {suggestion[2]}")

    print("\nApplying 'extract_method' refactoring to 'complex_function':")
    refactored_code = refactorer.apply_refactoring("extract_method", "complex_function")
    print(refactored_code)
```

This `AutomatedRefactorer` class suggests refactorings based on code analysis and can apply simple refactorings like method extraction and renaming.

## 5. Implementing Code Style Enforcement (20 minutes)

To ensure consistent code style, let's implement a simple code style checker using Python's `ast` module and some predefined rules.

Create the `code_style.py` file:

```python
# src/analysis/code_style.py

import ast
from typing import List, Tuple

class CodeStyleChecker:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)

    def check_style(self) -> List[Tuple[int, str]]:
        issues = []
        issues.extend(self._check_function_names())
        issues.extend(self._check_class_names())
        issues.extend(self._check_variable_names())
        issues.extend(self._check_import_style())
        return sorted(issues, key=lambda x: x[0])

    def _check_function_names(self) -> List[Tuple[int, str]]:
        issues = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower() or not node.name.replace('_', '').isalnum():
                    issues.append((node.lineno, f"Function name '{node.name}' should be lowercase with underscores"))
        return issues

    def _check_class_names(self) -> List[Tuple[int, str]]:
        issues = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper() or not node.name.replace('_', '').isalnum():
                    issues.append((node.lineno, f"Class name '{node.name}' should be CamelCase"))
        return issues

    def _check_variable_names(self) -> List[Tuple[int, str]]:
        issues = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if not node.id.islower() or not node.id.replace('_', '').isalnum():
                    issues.append((node.lineno, f"Variable name '{node.id}' should be lowercase with underscores"))
        return issues

    def _check_import_style(self) -> List[Tuple[int, str]]:
        issues = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if '.' in alias.name:
                        issues.append((node.lineno, f"Use 'from ... import ...' for importing specific modules"))
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    issues.append((node.lineno, f"Avoid relative imports"))
        return issues

# Example usage
if __name__ == "__main__":
    sample_code = """
import os.path
from . import module

def badFunctionName():
    pass

class lowercase_class:
    pass

CONSTANT = 10
badVariableName = 20
    """

    checker = CodeStyleChecker(sample_code)
    for line, issue in checker.check_style():
        print(f"Line {line}: {issue}")
```

This `CodeStyleChecker` class implements basic style checks for function names, class names, variable names, and import styles based on common Python conventions.

## 6. Developing a Code Smell Detector (25 minutes)

Now, let's create a code smell detector that can identify potential issues in the code structure and design.

Create the `smell_detector.py` file:

```python
# src/analysis/smell_detector.py

import ast
from typing import List, Tuple
from src.analysis.complexity_analyzer import ComplexityAnalyzer

class CodeSmellDetector:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)
        self.analyzer = ComplexityAnalyzer(code)

    def detect_smells(self) -> List[Tuple[str, str, int]]:
        smells = []
        smells.extend(self._detect_long_method())
        smells.extend(self._detect_large_class())
        smells.extend(self._detect_long_parameter_list())
        smells.extend(self._detect_duplicate_code())
        smells.extend(self._detect_god_object())
        return smells

    def _detect_long_method(self) -> List[Tuple[str, str, int]]:
        smells = []
        analysis = self.analyzer.analyze()
        for func_name, func_analysis in analysis["function_complexity"].items():
            if func_analysis["complexity"] > 10:
                smells.append(("Long Method", func_name, func_analysis["complexity"]))
        return smells

    def _detect_large_class(self) -> List[Tuple[str, str, int]]:
        smells = []
        analysis = self.analyzer.analyze()
        for class_name, class_analysis in analysis["class_complexity"].items():
            if class_analysis["num_methods"] > 10:
                smells.append(("Large Class", class_name, class_analysis["num_methods"]))
        return smells

    def _detect_long_parameter_list(self) -> List[Tuple[str, str, int]]:
        smells = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                num_params = len(node.args.args)
                if num_params > 5:
                    smells.append(("Long Parameter List", node.name, num_params))
        return smells

    def _detect_duplicate_code(self) -> List[Tuple[str, str, int]]:
        # This is a simplified detection of duplicate code
        # In a real-world scenario, you'd use more sophisticated algorithms
        smells = []
        code_blocks = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                code = ast.dump(node)
                if code in code_blocks:
                    smells.append(("Duplicate Code", node.name, node.lineno))
                else:
                    code_blocks[code] = node.name
        return smells

    def _detect_god_object(self) -> List[Tuple[str, str, int]]:
        smells = []
        analysis = self.analyzer.analyze()
        for class_name, class_analysis in analysis["class_complexity"].items():
            if class_analysis["num_methods"] > 15 and class_analysis["num_class_variables"] > 10:
                smells.append(("God Object", class_name, class_analysis["num_methods"]))
        return smells

# Example usage
if __name__ == "__main__":
    sample_code = """
class GodObject:
    def __init__(self):
        self.var1 = 1
        self.var2 = 2
        # ... (imagine 10 more variables)

    def method1(self): pass
    def method2(self): pass
    # ... (imagine 15 more methods)

def long_method(a, b, c, d, e, f):
    result = 0
    for i in range(100):
        if i % 2 == 0:
            result += i * a
        else:
            result += i * b
    for j in range(100):
        if j % 2 == 0:
            result -= j * c
        else:
            result -= j * d
    return result

def duplicate_code1():
    for i in range(10):
        print(i)
        if i % 2 == 0:
            print("Even")

def duplicate_code2():
    for i in range(10):
        print(i)
        if i % 2 == 0:
            print("Even")
    """

    detector = CodeSmellDetector(sample_code)
    for smell, name, value in detector.detect_smells():
        print(f"{smell} detected in {name} (value: {value})")
```

This `CodeSmellDetector` class identifies common code smells such as long methods, large classes, long parameter lists, duplicate code, and god objects.

## 7. Integrating Advanced Analysis into the CLI (20 minutes)

Now that we have implemented various code analysis and refactoring tools, let's integrate them into our CLI. We'll update the `main.py` file to include new commands for these features.

Update the `main.py` file:

```python
# src/cli/main.py

import click
from src.ai.openai_integration import get_completion
from src.analysis.ast_parser import ASTParser
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from src.analysis.code_style import CodeStyleChecker
from src.analysis.smell_detector import CodeSmellDetector
from src.refactoring.automated_refactor import AutomatedRefactorer

@click.group()
def cli():
    """Advanced code analysis and refactoring CLI"""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def analyze(file_path):
    """Analyze the given Python file"""
    with open(file_path, 'r') as file:
        code = file.read()

    ast_parser = ASTParser(code)
    click.echo("AST Analysis:")
    click.echo(ast_parser.to_dict())

    complexity_analyzer = ComplexityAnalyzer(code)
    click.echo("\nComplexity Analysis:")
    click.echo(complexity_analyzer.analyze())

    style_checker = CodeStyleChecker(code)
    click.echo("\nStyle Issues:")
    for line, issue in style_checker.check_style():
        click.echo(f"Line {line}: {issue}")

    smell_detector = CodeSmellDetector(code)
    click.echo("\nCode Smells:")
    for smell, name, value in smell_detector.detect_smells():
        click.echo(f"{smell} detected in {name} (value: {value})")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def suggest_refactoring(file_path):
    """Suggest refactorings for the given Python file"""
    with open(file_path, 'r') as file:
        code = file.read()

    refactorer = AutomatedRefactorer(code)
    click.echo("Refactoring Suggestions:")
    for suggestion in refactorer.suggest_refactorings():
        click.echo(f"- {suggestion[2]}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--refactoring-type', type=click.Choice(['extract_method', 'rename']), required=True)
@click.option('--target', required=True, help="Function or class name to refactor")
def apply_refactoring(file_path, refactoring_type, target):
    """Apply a specific refactoring to the given Python file"""
    with open(file_path, 'r') as file:
        code = file.read()

    refactorer = AutomatedRefactorer(code)
    refactored_code = refactorer.apply_refactoring(refactoring_type, target)
    
    click.echo("Refactored code:")
    click.echo(refactored_code)

    if click.confirm("Do you want to save the refactored code?"):
        with open(file_path, 'w') as file:
            file.write(refactored_code)
        click.echo(f"Refactored code saved to {file_path}")

if __name__ == '__main__':
    cli()
```

This updated CLI now includes commands for analyzing code, suggesting refactorings, and applying specific refactorings.

## 8. Practical Exercise (25 minutes)

Let's create a practical exercise that combines all the concepts we've covered in this lesson. We'll analyze a Python file, detect code smells, suggest refactorings, and apply them.

Create a new file called `example_code.py` in your project root:

```python
# example_code.py

import math, os, sys

class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, x):
        self.value += x

    def subtract(self, x):
        self.value -= x

    def multiply(self, x):
        self.value *= x

    def divide(self, x):
        if x != 0:
            self.value /= x
        else:
            print("Error: Division by zero")

    def SQRT(self, x):
        return math.sqrt(x)

    def complex_calculation(self, a, b, c, d, e, f, g):
        result = 0
        for i in range(100):
            if i % 2 == 0:
                result += i * a * b
            else:
                result += i * c * d
        for j in range(100):
            if j % 2 == 0:
                result -= j * e * f
            else:
                result -= j * g
        return result

calc = Calculator()
calc.add(5)
calc.subtract(3)
calc.multiply(2)
calc.divide(2)
print(calc.value)
print(calc.SQRT(16))
print(calc.complex_calculation(1, 2, 3, 4, 5, 6, 7))
```

Now, let's use our CLI to analyze this code, suggest refactorings, and apply them:

1. Analyze the code:
   ```
   python src/cli/main.py analyze example_code.py
   ```

2. Suggest refactorings:
   ```
   python src/cli/main.py suggest_refactoring example_code.py
   ```

3. Apply a refactoring (e.g., extract method for complex_calculation):
   ```
   python src/cli/main.py apply_refactoring example_code.py --refactoring-type extract_method --target complex_calculation
   ```

4. Analyze the code again to see the improvements:
   ```
   python src/cli/main.py analyze example_code.py
   ```

This exercise demonstrates how to use the advanced code analysis and refactoring tools we've built to improve code quality.

## 9. Discussion and Q&A (15 minutes)

Let's review the key concepts we've covered in this lesson:

1. AST parsing for code analysis
2. Complexity analysis using Cyclomatic Complexity
3. Automated refactoring suggestions and applications
4. Code style enforcement
5. Code smell detection

Some potential improvements and extensions to consider:

- Implement more sophisticated code smell detection algorithms
- Add support for other programming languages
- Integrate machine learning models for more accurate refactoring suggestions
- Implement a GUI for easier visualization of code analysis results
- Add unit tests for each component to ensure reliability

Questions for discussion:
1. How might we adapt these tools to work with larger codebases or different programming languages?
2. What are some potential challenges in implementing automated refactoring for more complex code structures?
3. How can we balance between strict code style enforcement and allowing for necessary exceptions?
4. What other code quality metrics could we incorporate into our analysis tools?
5. How might we integrate these analysis and refactoring tools with popular IDEs or code editors?

## 10. Conclusion

In this lesson, we've explored advanced code analysis and refactoring techniques, implementing tools for AST parsing, complexity analysis, automated refactoring, code style enforcement, and code smell detection. These tools can significantly improve code quality and maintainability in software projects.

By integrating these features into our AI-powered coding assistant, we've enhanced its ability to provide valuable insights and suggestions for code improvement. As you continue to develop your coding assistant, consider how you can further refine and expand these capabilities to meet the specific needs of your users and target programming languages.

## 11. Further Reading and Resources

1. [Python AST module documentation](https://docs.python.org/3/library/ast.html)
2. [Refactoring: Improving the Design of Existing Code](https://martinfowler.com/books/refactoring.html) by Martin Fowler
3. [Code Complete: A Practical Handbook of Software Construction](https://www.oreilly.com/library/view/code-complete-2nd/0735619670/) by Steve McConnell
4. [Cyclomatic Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)
5. [PyLint - Python static code analysis tool](https://www.pylint.org/)

In the next lesson, we'll explore intelligent code generation and completion techniques, building upon the analysis and refactoring capabilities we've developed here.