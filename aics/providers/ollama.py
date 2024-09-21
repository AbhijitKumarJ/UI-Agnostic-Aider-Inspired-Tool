# providers/ollama.py

import httpx
from typing import List, Dict, Any
from .base import BaseProvider
from langchain.llms import Ollama

class OllamaProvider(BaseProvider):
    def __init__(self):
        self.base_url = "http://localhost:11434"

    # ... (other methods remain the same)

    def get_llm(self, model_name: str = None) -> Any:
        if model_name is None:
            model_name = self.default_model
        return Ollama(model=model_name, base_url=self.base_url)

    @property
    def available_models(self) -> List[str]:
        return ["Replete-Coder-Qwen-1.5b-Q6_K:latest", "qwen2-1_5b-instruct-q8_0:latest"]

    @property
    def default_model(self) -> str:
        return "Replete-Coder-Qwen-1.5b-Q6_K:latest"

    def generate_code(self, model_name: str, prompt: str) -> str:
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/api/generate", json=data)
            response.raise_for_status()
            return response.json()["response"]

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        configs = {
            "Replete-Coder-Qwen-1.5b-Q6_K:latest": {"max_tokens": 2048, "temperature": 0.3},
            "qwen2-1_5b-instruct-q8_0:latest": {"max_tokens": 2048, "temperature": 0.3}
        }
        return configs.get(model_name, {})