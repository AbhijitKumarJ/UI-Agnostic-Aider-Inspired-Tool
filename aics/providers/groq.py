# providers/groq.py

import os
from typing import Any, Dict, List
import httpx
from .base import BaseProvider
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

class GroqLLM(LLM):
    api_key: str
    model_name: str
    base_url: str = "https://api.groq.com/openai/v1"

    def _call(self, prompt: str, stop: List[str] | None = None, run_manager: CallbackManagerForLLMRun | None = None, **kwargs: Any) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048
        }
        
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/chat/completions", json=data, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    @property
    def _llm_type(self) -> str:
        return "groq"

class GroqProvider(BaseProvider):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.base_url = "https://api.groq.com/openai/v1"

    @property
    def available_models(self) -> List[str]:
        return ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it"]

    @property
    def default_model(self) -> str:
        return "llama-3.1-8b-instant"

    def generate_code(self, model_name: str, prompt: str) -> str:
        llm = self.get_llm(model_name)
        return llm(prompt)

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        configs = {
            "llama-3.1-70b-versatile": {"max_tokens": 4096, "temperature": 0.2},
            "llama-3.1-8b-instant": {"max_tokens": 4096, "temperature": 0.7},
            "mixtral-8x7b-32768": {"max_tokens": 32768, "temperature": 0.8},
            "gemma-7b-it": {"max_tokens": 8192, "temperature": 0.7}
        }
        return configs.get(model_name, {})

    def get_llm(self, model_name: str = None) -> Any:
        if model_name is None:
            model_name = self.default_model
        return GroqLLM(api_key=self.api_key, model_name=model_name, base_url=self.base_url)