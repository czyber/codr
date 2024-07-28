from abc import ABC, abstractmethod

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from codr.application.entities import Document
from codr.models import new_uuid

load_dotenv()

client = OpenAI()


class EmbeddingCreator:
    def get_embedding(self, input):
        # Cast from list of bytes to list of strings
        embeddings = client.embeddings.create(
            input=input, model="text-embedding-3-large"
        )
        # return all embeddings
        return [d.embedding for d in embeddings.data]

    def __call__(self, input):
        return self.get_embedding(input)


embedding_creator = EmbeddingCreator()


class VectorDb(ABC):
    @abstractmethod
    def create(self, documents: list[Document]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, sha: str) -> list:
        raise NotImplementedError

    @abstractmethod
    def query(self, query: str, sha: str | None = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def query_texts(self, query_texts: list[str], sha: str | None = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_by_metadata(self, key: str, value: str, sha: str | None = None) -> list:
        raise NotImplementedError


class ChromaDb(VectorDb):
    def __init__(self):
        self.__client = chromadb.HttpClient()
        self.__collection = self.__client.get_or_create_collection(
            "codebase_embeddings_newnew", embedding_function=embedding_creator
        )

    def create(self, documents: list[Document]) -> None:
        return self.__collection.add(
            documents=[d.content for d in documents],
            ids=[new_uuid() for _ in range(len(documents))],
            metadatas=[{"source": d.source, "sha": d.sha} for d in documents],
        )

    def get(self, sha: str) -> list:
        results = self.__collection.get(where={"sha": {"$eq": sha}})
        return results["embeddings"]

    def query(self, query: str, sha: str | None = None) -> list:
        if sha is not None:
            results = self.__collection.query(
                query_texts=[query], n_results=10, where={"sha": {"$eq": sha}}
            )
        else:
            results = self.__collection.query(query_texts=[query], n_results=10)
        return results

    def query_texts(self, query_texts: list[str], sha: str | None = None) -> list:
        if sha is not None:
            results = self.__collection.query(
                query_texts=query_texts, n_results=10, where={"sha": {"$eq": sha}}
            )
        else:
            results = self.__collection.query(query_texts=query_texts, n_results=10)
        sources = [result for result in results.get("metadatas")]
        return sources

    def get_by_metadata(self, key: str, value: str, sha: str | None = None) -> list:
        query = {key: value}

        # If sha is provided, add it to the query with and operation
        if sha is not None:
            query = {"$and": [query, {"sha": {"$eq": sha}}]}

        results = self.__collection.get(where=query)
        return results

    def delete(self, identifier: str) -> None:
        self.__client.delete_collection(identifier)
