# config.py

import os
from decouple import config, Csv

PROJECT_ROOT = config('PROJECT_ROOT', default='.')
RAG_STORAGE_PATH = os.path.join(PROJECT_ROOT, 'rag_storage')
AI_PROVIDER = config('AI_PROVIDER', default='groq')
AI_MODEL = config('AI_MODEL', default="llama-3.1-8b-instant")
MAX_ITERATIONS = config('MAX_ITERATIONS', default=5, cast=int)
IMPROVEMENT_THRESHOLD = config('IMPROVEMENT_THRESHOLD', default=0.1, cast=float)

GROQ_API_KEY = config('GROQ_API_KEY')
OPENROUTER_API_KEY = config('OPENROUTER_API_KEY')

PROVIDERS = {
    "groq": {
        "class": "providers.groq.GroqProvider",
        "api_key": GROQ_API_KEY,
    },
    "ollama": {
        "class": "providers.ollama.OllamaProvider",
    },
    "openrouter": {
        "class": "providers.openrouter.OpenRouterProvider",
        "api_key": OPENROUTER_API_KEY,
    },
}