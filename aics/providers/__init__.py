# providers/__init__.py

from .groq import GroqProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider

PROVIDERS = {
    'groq': GroqProvider,
    'ollama': OllamaProvider,
    'openrouter': OpenRouterProvider
}

def get_provider(name):
    provider_class = PROVIDERS.get(name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}")
    return provider_class()