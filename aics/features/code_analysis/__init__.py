
import ast
from core.feature_registry import FeatureRegistry

@FeatureRegistry.register('code_analysis', dependencies=['ai_integration'])
class CodeAnalyzer:
    def analyze_python(self, code):
        tree = ast.parse(code)
        return {
            'functions': self._get_functions(tree),
            'classes': self._get_classes(tree),
            'imports': self._get_imports(tree),
        }

    def _get_functions(self, tree):
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    def _get_classes(self, tree):
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def _get_imports(self, tree):
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.{node.names[0].name}")
        return imports
