# Lesson 6: Local Vector Database for Knowledge Management

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Introduction to Vector Databases](#introduction-to-vector-databases)
4. [Setting up a Local Vector Database (FAISS)](#setting-up-a-local-vector-database)
5. [Implementing Document Indexing and Retrieval](#implementing-document-indexing-and-retrieval)
6. [Creating a Caching System for Faster Lookups](#creating-a-caching-system)
7. [Developing a Query System for Context-Aware Searches](#developing-a-query-system)
8. [Practical Exercise](#practical-exercise)
9. [Conclusion](#conclusion)

## 1. Introduction <a name="introduction"></a>

In this lesson, we'll focus on enhancing our AI-assisted coding tool with a local vector database for efficient knowledge management. This will allow our tool to store, retrieve, and utilize relevant information more effectively, leading to more accurate and contextually appropriate assistance.

By the end of this lesson, you'll be able to:
- Understand the concept and benefits of vector databases
- Set up and use FAISS, a popular local vector database
- Implement document indexing and retrieval mechanisms
- Create a caching system for faster lookups
- Develop a query system for context-aware searches

Let's dive in!

## 2. Project Structure <a name="project-structure"></a>

Before we start, let's update our project structure to accommodate the new features:

```
aider/
│
├── aider/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── config.py
│   ├── utils.py
│   ├── git_manager.py
│   ├── context_manager.py
│   ├── session_manager.py
│   ├── chat_history.py
│   ├── prompt_templates.py
│   ├── completions.py
│   ├── vector_store/             # New directory for vector database related files
│   │   ├── __init__.py
│   │   ├── faiss_store.py        # FAISS implementation
│   │   ├── document_processor.py # Document processing utilities
│   │   ├── cache_manager.py      # Caching system
│   │   └── query_engine.py       # Query system for context-aware searches
│   └── knowledge_base.py         # High-level knowledge management interface
│
├── tests/
│   ├── test_vector_store/
│   │   ├── test_faiss_store.py
│   │   ├── test_document_processor.py
│   │   ├── test_cache_manager.py
│   │   └── test_query_engine.py
│   └── test_knowledge_base.py
│
├── .env
├── .gitignore
├── requirements.txt
└── setup.py
```

We'll be working primarily with the new files in the `aider/vector_store/` directory and the `knowledge_base.py` file.

## 3. Introduction to Vector Databases <a name="introduction-to-vector-databases"></a>

Vector databases are specialized systems designed to store and retrieve high-dimensional vectors efficiently. In the context of our AI-assisted coding tool, we'll use vector databases to store embeddings of code snippets, documentation, and other relevant information.

Key benefits of vector databases include:
1. Efficient similarity search
2. Scalability for large datasets
3. Support for high-dimensional data
4. Fast retrieval times

For our implementation, we'll use FAISS (Facebook AI Similarity Search), an open-source library that provides efficient similarity search and clustering of dense vectors.

Let's start by installing the required dependencies. Update your `requirements.txt` file:

```
faiss-cpu==1.7.2
numpy==1.21.0
scipy==1.7.0
```

Then install the new dependencies:

```bash
pip install -r requirements.txt
```

## 4. Setting up a Local Vector Database (FAISS) <a name="setting-up-a-local-vector-database"></a>

Now, let's create a wrapper class for FAISS to handle our vector storage and retrieval operations.

Create a new file `faiss_store.py` in the `vector_store` directory:

```python
# aider/vector_store/faiss_store.py

import numpy as np
import faiss

class FAISSStore:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.id_to_metadata = {}

    def add_vectors(self, vectors, metadata):
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors and metadata items must match")

        start_id = self.index.ntotal
        self.index.add(np.array(vectors).astype('float32'))

        for i, meta in enumerate(metadata):
            self.id_to_metadata[start_id + i] = meta

    def search(self, query_vector, k=5):
        query_vector = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # -1 indicates no match found
                results.append((self.id_to_metadata[idx], float(distances[0][i])))
        
        return results

    def save(self, filename):
        faiss.write_index(self.index, filename)

    def load(self, filename):
        self.index = faiss.read_index(filename)
```

This `FAISSStore` class provides methods to add vectors, search for similar vectors, and save/load the index to/from a file.

## 5. Implementing Document Indexing and Retrieval <a name="implementing-document-indexing-and-retrieval"></a>

Next, let's create a document processor to handle the conversion of text documents into vector embeddings. We'll use a simple TF-IDF vectorizer for this example, but in a production environment, you might want to use more advanced embedding techniques like word2vec or BERT.

Create a new file `document_processor.py` in the `vector_store` directory:

```python
# aider/vector_store/document_processor.py

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class DocumentProcessor:
    def __init__(self, max_features=1000):
        self.vectorizer = TfidfVectorizer(max_features=max_features)
        self.fitted = False

    def fit(self, documents):
        self.vectorizer.fit(documents)
        self.fitted = True

    def transform(self, documents):
        if not self.fitted:
            raise ValueError("Vectorizer must be fitted before transform")
        return self.vectorizer.transform(documents).toarray()

    def fit_transform(self, documents):
        vectors = self.vectorizer.fit_transform(documents).toarray()
        self.fitted = True
        return vectors

    def get_dimension(self):
        return self.vectorizer.max_features
```

This `DocumentProcessor` class uses TF-IDF vectorization to convert text documents into numerical vectors.

## 6. Creating a Caching System for Faster Lookups <a name="creating-a-caching-system"></a>

To improve performance, let's implement a simple caching system using Python's `lru_cache` decorator.

Create a new file `cache_manager.py` in the `vector_store` directory:

```python
# aider/vector_store/cache_manager.py

from functools import lru_cache
import hashlib

class CacheManager:
    def __init__(self, maxsize=128):
        self.maxsize = maxsize

    @lru_cache(maxsize=None)
    def cached_search(self, query_hash, k):
        # This method will be implemented in the KnowledgeBase class
        pass

    def get_query_hash(self, query):
        return hashlib.md5(query.encode()).hexdigest()

    def clear_cache(self):
        self.cached_search.cache_clear()
```

This `CacheManager` class provides a method to cache search results based on the query hash and the number of results requested.

## 7. Developing a Query System for Context-Aware Searches <a name="developing-a-query-system"></a>

Now, let's create a query engine that combines the vector store, document processor, and cache manager to provide context-aware searches.

Create a new file `query_engine.py` in the `vector_store` directory:

```python
# aider/vector_store/query_engine.py

class QueryEngine:
    def __init__(self, vector_store, document_processor, cache_manager):
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.cache_manager = cache_manager

    def search(self, query, k=5):
        query_hash = self.cache_manager.get_query_hash(query)
        cached_result = self.cache_manager.cached_search(query_hash, k)
        
        if cached_result is not None:
            return cached_result

        query_vector = self.document_processor.transform([query])[0]
        results = self.vector_store.search(query_vector, k)

        self.cache_manager.cached_search(query_hash, k, results)
        return results

    def add_document(self, document, metadata):
        vector = self.document_processor.transform([document])[0]
        self.vector_store.add_vectors([vector], [metadata])

    def update_document(self, document, metadata):
        # For simplicity, we'll just add the updated document
        # In a real-world scenario, you might want to remove the old version first
        self.add_document(document, metadata)
```

This `QueryEngine` class provides methods to search for similar documents and add/update documents in the vector store.

Now, let's create a high-level `KnowledgeBase` class that will serve as the main interface for our knowledge management system.

Create a new file `knowledge_base.py` in the `aider` directory:

```python
# aider/knowledge_base.py

from .vector_store.faiss_store import FAISSStore
from .vector_store.document_processor import DocumentProcessor
from .vector_store.cache_manager import CacheManager
from .vector_store.query_engine import QueryEngine

class KnowledgeBase:
    def __init__(self, dimension=1000, cache_size=128):
        self.document_processor = DocumentProcessor(max_features=dimension)
        self.vector_store = FAISSStore(dimension)
        self.cache_manager = CacheManager(maxsize=cache_size)
        self.query_engine = QueryEngine(self.vector_store, self.document_processor, self.cache_manager)

    def add_documents(self, documents, metadata_list):
        vectors = self.document_processor.fit_transform(documents)
        self.vector_store.add_vectors(vectors, metadata_list)

    def search(self, query, k=5):
        return self.query_engine.search(query, k)

    def save(self, filename):
        self.vector_store.save(filename)

    def load(self, filename):
        self.vector_store.load(filename)

    def clear_cache(self):
        self.cache_manager.clear_cache()
```

This `KnowledgeBase` class serves as a facade for our entire knowledge management system, providing a simple interface for adding documents, searching, and managing the vector store and cache.

## 8. Practical Exercise <a name="practical-exercise"></a>

Now that we have implemented our local vector database for knowledge management, let's create a practical exercise to reinforce what we've learned.

Exercise: Create a simple code snippet search engine

1. Initialize the knowledge base
2. Add sample code snippets to the knowledge base
3. Perform searches based on natural language queries
4. Implement a simple CLI interface for interacting with the knowledge base

Here's a step-by-step solution using our newly implemented classes:

```python
# exercise.py

import click
from aider.knowledge_base import KnowledgeBase

kb = KnowledgeBase(dimension=100, cache_size=64)

# Sample code snippets
snippets = [
    ("def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)", 
     {"language": "python", "topic": "recursion"}),
    ("for i in range(10):\n    print(i)", 
     {"language": "python", "topic": "loops"}),
    ("import re\n\npattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'\n\ndef is_valid_email(email):\n    return re.match(pattern, email) is not None", 
     {"language": "python", "topic": "regex"}),
    ("def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)", 
     {"language": "python", "topic": "sorting"}),
]

# Add snippets to the knowledge base
kb.add_documents([s[0] for s in snippets], [s[1] for s in snippets])

@click.group()
def cli():
    pass

@cli.command()
@click.argument('query')
@click.option('--limit', default=3, help='Number of results to return')
def search(query, limit):
    results = kb.search(query, k=limit)
    click.echo(f"Search results for: {query}")
    for i, (metadata, score) in enumerate(results, 1):
        click.echo(f"\n{i}. Score: {score:.4f}")
        click.echo(f"Language: {metadata['language']}")
        click.echo(f"Topic: {metadata['topic']}")
        click.echo("Snippet:")
        click.echo("---")
        click.echo(metadata['snippet'])
        click.echo("---")

@cli.command()
@click.argument('filename')
def save(filename):
    kb.save(filename)
    click.echo(f"Knowledge base saved to {filename}")

@cli.command()
@click.argument('filename')
def load(filename):
    kb.load(filename)
    click.echo(f"Knowledge base loaded from {filename}")

if __name__ == '__main__':
    cli()
```

To run this exercise, save the code to a file named `exercise.py` and use the following commands:

```bash
# Search for code snippets
python exercise.py search "fibonacci sequence"

# Save the knowledge base
python exercise.py save kb.faiss

# Load the knowledge base
python exercise.py load kb.faiss
```

This exercise demonstrates how to use our newly implemented knowledge management system to create a simple code snippet search engine.

## 9. Conclusion <a name="conclusion"></a>

In this lesson, we've successfully implemented a local vector database for knowledge management in our AI-assisted coding tool. We've created:

1. A vector store using FAISS for efficient similarity search
2. A document processor to convert text into vector embeddings
3. A caching system for faster lookups
4. A query engine for context-aware searches
5. A high-level knowledge base interface that combines all these components

These features provide a solid foundation for managing and utilizing a large knowledge base in our AI-assisted coding tool. As you continue to develop your tool, consider adding more advanced features, such as:

- Implementing more sophisticated embedding techniques (e.g., using pre-trained models like BERT or CodeBERT)
- Adding support for incremental updates to the vector store
- Implementing a distributed vector store for handling larger datasets
- Integrating the knowledge base with the context management system from the previous lesson
- Developing a relevance feedback mechanism to improve search results over time

Remember that while our implementation provides a good starting point, it's essential to continually refine and optimize these systems based on the specific needs of your AI-assisted coding tool and user feedback.

## 10. Further Reading and Resources

To deepen your understanding of vector databases, knowledge management, and related topics, consider exploring the following resources:

1. [FAISS documentation](https://github.com/facebookresearch/faiss/wiki) - Official documentation for the FAISS library
2. [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/) - A comprehensive book on information retrieval techniques
3. [Embeddings in Natural Language Processing](https://arxiv.org/abs/1301.3781) - An overview of word embeddings and their applications
4. [Practical Machine Learning for Similarity Search](https://www.pinecone.io/learn/similarity-search/) - A series of articles on similarity search and vector databases
5. [Semantic Code Search Using Deep Learning](https://github.blog/2018-09-18-towards-natural-language-semantic-code-search/) - GitHub's approach to semantic code search

## 11. Next Steps

In the next lesson, we'll focus on "AI Integration: OpenAI API and Prompt Engineering." We'll build upon our knowledge management system to create more sophisticated AI-powered features for our coding tool. This will include:

1. Setting up OpenAI API integration
2. Designing effective prompts for code generation
3. Implementing streaming responses
4. Handling rate limits and API errors
5. Creating a fallback system for offline mode

By the end of the next lesson, you'll have an even more powerful AI-assisted coding tool that can leverage advanced language models to provide intelligent code suggestions, explanations, and more.

As you move forward, continue to practice and expand upon the knowledge management system we've built in this lesson. Experiment with different types of code snippets, documentation, and other relevant information to see how it impacts the quality of search results and overall usefulness of your tool. Happy coding!

## 12. Exercises for Practice

To reinforce your understanding of the concepts covered in this lesson, try the following exercises:

1. Extend the `DocumentProcessor` class to support multiple embedding techniques (e.g., TF-IDF, Word2Vec, BERT) and allow users to choose between them.

2. Implement a method in the `KnowledgeBase` class to remove documents from the vector store and update the index accordingly.

3. Create a simple web interface using Flask or FastAPI to interact with the knowledge base, allowing users to add documents and perform searches through a browser.

4. Implement a relevance feedback mechanism that allows users to rate search results and use this information to improve future searches.

5. Extend the `KnowledgeBase` class to support multiple vector stores (e.g., FAISS, Annoy, Elasticsearch) and allow users to switch between them.

6. Implement a simple versioning system for the knowledge base, allowing users to revert to previous states of the index.

7. Create a method to export the knowledge base contents (including metadata) to a human-readable format like JSON or YAML.

8. Implement a simple plugin system that allows users to add custom document processors or query preprocessors to the knowledge base.

9. Develop a method to automatically extract code snippets from GitHub repositories and add them to the knowledge base.

10. Create a simple recommendation system that suggests related code snippets based on the user's current context (e.g., open files, recent searches).

These exercises will help you gain a deeper understanding of vector databases and knowledge management systems. As you work through these exercises, you'll likely encounter new challenges and opportunities for optimization, which will further enhance your skills in developing AI-assisted coding tools.

Remember to test your implementations thoroughly and consider edge cases as you work on these exercises. Pay special attention to performance and scalability, as these are critical factors when working with large knowledge bases.

## 13. Integration with Existing Codebase

To fully leverage the power of our new knowledge management system, we need to integrate it with the existing components of our AI-assisted coding tool. Here are some ideas for integration:

1. Context-aware code completion:
   Enhance the `ContextAwareCompletions` class from the previous lesson to use the knowledge base for more accurate code suggestions.

```python
# aider/completions.py

class ContextAwareCompletions:
    def __init__(self, context_manager, chat_history, prompt_library, knowledge_base):
        # ... (previous initialization code)
        self.knowledge_base = knowledge_base

    def generate_completion(self, prompt_name, **kwargs):
        # ... (previous code)

        # Fetch relevant snippets from the knowledge base
        relevant_snippets = self.knowledge_base.search(prompt, k=3)
        context_snippets = "\n".join([f"Relevant snippet:\n{snippet['metadata']['snippet']}" for snippet, _ in relevant_snippets])

        # Add relevant snippets to the prompt
        prompt += f"\n\nHere are some relevant code snippets:\n{context_snippets}"

        # ... (rest of the method)
```

2. Intelligent file suggestions:
   Use the knowledge base to suggest relevant files or code snippets based on the user's current task.

```python
# aider/context_manager.py

class ContextManager:
    def __init__(self, project_root, knowledge_base):
        # ... (previous initialization code)
        self.knowledge_base = knowledge_base

    def suggest_relevant_files(self, current_file, current_content):
        relevant_snippets = self.knowledge_base.search(current_content, k=5)
        suggested_files = set()
        for snippet, _ in relevant_snippets:
            if snippet['metadata']['file'] != current_file:
                suggested_files.add(snippet['metadata']['file'])
        return list(suggested_files)
```

3. Enhanced commit message generation:
   Use the knowledge base to provide more context when generating commit messages.

```python
# aider/git_manager.py

class GitManager:
    def __init__(self, repo_path, knowledge_base):
        # ... (previous initialization code)
        self.knowledge_base = knowledge_base

    def generate_commit_message(self, diff):
        relevant_snippets = self.knowledge_base.search(diff, k=3)
        context = "\n".join([f"Related change:\n{snippet['metadata']['snippet']}" for snippet, _ in relevant_snippets])
        
        prompt = f"""
        Generate a commit message for the following changes:
        {diff}

        Consider these related changes for context:
        {context}

        Commit message:
        """
        
        # Use your preferred method to generate the commit message (e.g., OpenAI API)
        return generate_message_with_ai(prompt)
```

4. Documentation assistant:
   Create a new feature that helps users write documentation by suggesting relevant examples from the knowledge base.

```python
# aider/documentation_assistant.py

class DocumentationAssistant:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def suggest_documentation(self, code_snippet):
        relevant_snippets = self.knowledge_base.search(code_snippet, k=5)
        suggestions = []
        for snippet, score in relevant_snippets:
            if 'docstring' in snippet['metadata']:
                suggestions.append({
                    'score': score,
                    'docstring': snippet['metadata']['docstring'],
                    'snippet': snippet['metadata']['snippet']
                })
        return suggestions

    def generate_docstring(self, code_snippet):
        suggestions = self.suggest_documentation(code_snippet)
        context = "\n".join([f"Similar code:\n{s['snippet']}\nDocstring:\n{s['docstring']}" for s in suggestions[:3]])
        
        prompt = f"""
        Generate a docstring for the following code snippet:
        {code_snippet}

        Consider these similar snippets and their docstrings:
        {context}

        Generated docstring:
        """
        
        # Use your preferred method to generate the docstring (e.g., OpenAI API)
        return generate_docstring_with_ai(prompt)
```

By integrating the knowledge base with these existing components, you can significantly enhance the capabilities of your AI-assisted coding tool. The tool will be able to provide more relevant suggestions, generate more accurate commit messages, and assist with documentation writing, all while leveraging the power of the local vector database.

As you continue to develop your tool, look for more opportunities to integrate the knowledge base with other features and components. This will help create a more cohesive and powerful AI-assisted coding experience for your users.