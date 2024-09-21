import os
import json
from typing import List, Dict, Any

from core.feature_registry import FeatureRegistry

@FeatureRegistry.register('file_management')   
class FileManager:
    def __init__(self, project_root: str):
        self.project_root = project_root

    def read_file(self, file_path: str) -> str:
        with open(os.path.join(self.project_root, file_path), 'r') as file:
            return file.read()

    def write_file(self, file_path: str, content: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(content)

    def list_files(self) -> List[str]:
        file_list = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                file_list.append(os.path.relpath(os.path.join(root, file), self.project_root))
        return file_list

    def save_json(self, file_path: str, data: Dict[str, Any]):
        with open(os.path.join(self.project_root, file_path), 'w') as file:
            json.dump(data, file, indent=2)

    def load_json(self, file_path: str) -> Dict[str, Any]:
        with open(os.path.join(self.project_root, file_path), 'r') as file:
            return json.load(file)
