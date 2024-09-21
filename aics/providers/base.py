# providers/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    @abstractmethod
    def generate_code(self, model_name: str, prompt: str) -> str:
        pass

    @abstractmethod
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_llm(self, model_name: str = None) -> Any:
        pass