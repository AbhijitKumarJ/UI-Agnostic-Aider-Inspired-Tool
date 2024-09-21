# providers/openrouter.py

import os
import httpx
from typing import List, Dict, Any
from .base import BaseProvider
from langchain.llms import OpenAI

class OpenRouterProvider(BaseProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    # ... (other methods remain the same)

    def get_llm(self, model_name: str = None) -> Any:
        if model_name is None:
            model_name = self.default_model
        return OpenAI(model_name=model_name, openai_api_key=self.api_key, openai_api_base=self.base_url)

    @property
    def available_models(self) -> List[str]:
        return ["nousresearch/hermes-3-llama-3.1-405b:free","mistralai/mistral-7b-instruct:free", "meta-llama/llama-3.1-8b-instruct:free", "microsoft/phi-3-mini-128k-instruct:free", "qwen/qwen2-7b-instruct:free"]

    @property
    def default_model(self) -> str:
        return "qwen/qwen2-7b-instruct:free"

    def generate_code(self, model_name: str, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048
        }
        
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/chat/completions", json=data, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        configs = {
            "nousresearch/hermes-3-llama-3.1-405b:free": {"max_tokens": 4096, "temperature": 0.0},
            "meta-llama/llama-3.1-8b-instruct:free": {"max_tokens": 4096, "temperature": 0.3},
            "mistralai/mistral-7b-instruct:free": {"max_tokens": 4096, "temperature": 0.3},
            "microsoft/phi-3-mini-128k-instruct:free": {"max_tokens": 4096, "temperature": 0.3},
            "qwen/qwen2-7b-instruct:free": {"max_tokens": 4096, "temperature": 0.3}
        }
        return configs.get(model_name, {})