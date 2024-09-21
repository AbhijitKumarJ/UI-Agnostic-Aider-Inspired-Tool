# features/ai_integration/__init__.py

import httpx
import os
from config import PROJECT_ROOT, RAG_STORAGE_PATH
from core.feature_registry import FeatureRegistry
from providers import get_provider
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import pandas as pd

@FeatureRegistry.register('ai_integration')
class AIIntegration:
    def __init__(self, provider_name, model_name=None):
        try:
            self.provider = get_provider(provider_name)
            self.model_name = model_name if model_name is not None else self.provider.default_model
            self.vectorstore = None
            self.dataset = None
            self.rag_path = RAG_STORAGE_PATH
            self._load_rag()
        except Exception as e:
            raise ValueError(f"Failed to initialize provider '{provider_name}': {str(e)}")

    def _load_rag(self):
        if os.path.exists(self.rag_path):
            embeddings = HuggingFaceEmbeddings()
            self.vectorstore = Chroma(persist_directory=self.rag_path, embedding_function=embeddings)

    def create_rag(self, file_path):
        try:
            # Read the file content
            with open(file_path, 'r') as file:
                content = file.read()

            # Split the content into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(content)

            # Create embeddings
            embeddings = HuggingFaceEmbeddings()

            # Store embeddings in a vector database
            self.vectorstore = Chroma.from_texts(chunks, embeddings, persist_directory=self.rag_path)
            self.vectorstore.persist()

            return "RAG created successfully and persisted to disk"
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to create RAG: {str(e)}")

    def query_rag(self, query):
        if not self.vectorstore:
            raise ValueError("RAG has not been created yet. Please create a RAG first.")

        # Create a retrieval chain using the provider's model
        qa_chain = RetrievalQA.from_chain_type(
            llm = self.provider.get_llm(self.model_name),  # Assuming the provider has a get_llm method
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )

        # Query the RAG
        result = qa_chain({"query": query})

        return result["result"]

    def generate_code(self, prompt):
        try:
            return self.provider.generate_code(self.model_name, prompt)
        except httpx.HTTPStatusError as e:
            error_detail = self._parse_error_response(e.response)
            raise ValueError(f"API request failed: {error_detail}")
        except Exception as e:
            raise ValueError(f"Code generation failed: {str(e)}")

    def explain_code(self, code):
        prompt = f"Explain the following code:\n\n{code}"
        return self.generate_code(prompt)

    def _parse_error_response(self, response):
        try:
            error_data = response.json()
            return error_data.get('error', {}).get('message', 'Unknown error occurred')
        except ValueError:
            return f"HTTP {response.status_code}: {response.text}"

    def create_ragold(self, file_path):
        try:
            # Read the file content
            with open(file_path, 'r') as file:
                content = file.read()

            # Split the content into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(content)

            # Create embeddings
            embeddings = HuggingFaceEmbeddings()

            # Store embeddings in a vector database
            self.vectorstore = Chroma.from_texts(chunks, embeddings, collection_name="my_rag")

            return "RAG created successfully"
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to create RAG: {str(e)}")

    def query_ragold(self, query):
        if not self.vectorstore:
            raise ValueError("RAG has not been created yet. Please create a RAG first.")

        # Create a retrieval chain using the provider's model
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.provider.get_llm(self.model_name),  # Assuming the provider has a get_llm method
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )

        # Query the RAG
        result = qa_chain({"query": query})

        return result["result"]

    def load_dataset(self, dataset_path):
        try:
            _, file_extension = os.path.splitext(dataset_path)
            if file_extension.lower() == '.csv':
                self.dataset = pd.read_csv(dataset_path)
            elif file_extension.lower() == '.json':
                self.dataset = pd.read_json(dataset_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            return f"Dataset loaded successfully. Shape: {self.dataset.shape}"
        except Exception as e:
            raise ValueError(f"Failed to load dataset: {str(e)}")

    def analyze_row(self, row, iterations):
        if self.dataset is None:
            raise ValueError("No dataset loaded. Please load a dataset first.")

        if isinstance(row, int):
            if row < 0 or row >= len(self.dataset):
                raise ValueError(f"Row index {row} is out of bounds.")
            row_data = self.dataset.iloc[row]
        else:
            row_data = row

        analysis = []
        for _ in range(iterations):
            prompt = f"Analyze the following data:\n\n{row_data.to_dict()}\n\nProvide insights and potential next steps."
            analysis.append(self.generate_code(prompt))

        return "\n\n".join(analysis)