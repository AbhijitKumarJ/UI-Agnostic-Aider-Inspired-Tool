
import json
import random
import csv
from typing import List, Dict, Any

from core.feature_registry import FeatureRegistry

@FeatureRegistry.register_feature('dataset_handling')   
class DatasetHandler:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = self.load_dataset()

    def load_dataset(self) -> List[Dict[str, Any]]:
        extension = self.dataset_path.split('.')[-1].lower()
        if extension == 'json':
            with open(self.dataset_path, 'r') as f:
                return json.load(f)
        elif extension == 'jsonl':
            with open(self.dataset_path, 'r') as f:
                return [json.loads(line) for line in f]
        elif extension in ['csv', 'tsv']:
            delimiter = ',' if extension == 'csv' else '\t'
            with open(self.dataset_path, 'r', newline='') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                return list(reader)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def get_random_row(self) -> Dict[str, Any]:
        return random.choice(self.data)

    def get_row_by_index(self, index: int) -> Dict[str, Any]:
        if 0 <= index < len(self.data):
            return self.data[index]
        raise IndexError("Row index out of range")

    def get_total_rows(self) -> int:
        return len(self.data)
