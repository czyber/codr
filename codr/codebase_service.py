import shutil
from abc import ABC, abstractmethod

from github.Repository import Repository

from codr.application.entities import Codebase, Document, Repo
from codr.github_client import GitHubClient, RepoInfo
from codr.llm.clients import (
    invoke_coding_assistant,
    invoke_query_assistant,
    invoke_verify_agent,
)
from codr.logger import logger
from codr.models import new_uuid
from codr.storage.codebase_storage import CodebaseStorage
from codr.storage.repo_repository import RepoRepository
from codr.storage.vector_db import VectorDb
from codr.utils import Id


def get_unique_file_paths(query_results) -> set[str]:
    unique_file_paths = set()
    for result in query_results:
        for document in result:
            unique_file_paths.add(document["source"])
    return unique_file_paths


def get_first_chunk(chunks, overlap_size=100):
    # The first chunk is the chunk where no other chunk ends with the overlap
    for chunk in chunks:
        overlap = chunk[:overlap_size]
        for other_chunk in chunks:
            if chunk == other_chunk:
                continue
            if other_chunk.endswith(overlap):
                break
        else:
            return chunk
    return None


def merge_documents_with_overlap(chunks, overlap_size=100):
    # Find the first chunk
    logger.info(f"Merging {len(chunks)} chunks")
    first_chunk = get_first_chunk(chunks, overlap_size=overlap_size)
    if first_chunk is None:
        raise ValueError("Unable to find the first chunk")

    # Initialize the merged document with the first chunk
    merged_document = first_chunk
    used_chunks = {first_chunk}

    while len(used_chunks) < len(chunks):
        for chunk in chunks:
            logger.info(f"Checking chunk")
            if chunk in used_chunks:
                continue
            end_overlap = merged_document[-overlap_size:]
            if chunk.startswith(end_overlap):
                # Merge the chunk
                logger.info(f"Merging chunk")
                merged_document += chunk[overlap_size:]
                used_chunks.add(chunk)
                break
        else:
            logger.info(f"Unable to merge chunks. Used chunks: {used_chunks}")
            break

    return merged_document


def cleanup_dir(tmp_repo_dir):
    logger.info(f"Cleaning up directory {tmp_repo_dir}")
    shutil.rmtree(tmp_repo_dir)


class AbstractCodebaseService(ABC):
    @abstractmethod
    def create_index(self, codebase: Repository):
        raise NotImplementedError


class CodebaseService(AbstractCodebaseService):
    def __init__(self, storage: RepoRepository, vector_db: VectorDb) -> None:
        self.__storage = storage
        self.__vector_db = vector_db
        self.__codebase = None

    def create_index(self, codebase: Repository):
        self.__codebase = codebase
        slug = self.__codebase.full_name
        sha = self.__codebase.get_branch(self.__codebase.default_branch).commit.sha
        repo_info = RepoInfo.from_slug(slug)

        repo = self.__storage.get_by_identifier_and_sha(info=repo_info, sha=sha)

        if repo.embeddings_created:
            return self._get_embeddings(sha=sha)

        embeddings = self._create_embeddings(repo=self.__codebase, repo_id=repo.id)
        return embeddings

    def create_embeddings(self, slug: str, sha: str):
        # Use GitHub API to get the codebase
        repo = self.__codebase.repo

        # Check if we already have indexed the codebase
        codebase = self.__storage.get_by_identifier_and_sha(
            info=RepoInfo.from_slug(slug), sha=sha
        )

        if codebase.embeddings_created:
            return self._get_embeddings(sha=codebase.sha)

        # Create embeddings
        embeddings = self._create_embeddings(repo=repo, repo_id=codebase.id)
        return embeddings

    def _create_embeddings(
        self, repo: Repository, repo_id: Id, chunk_size=1000, overlap_size=100
    ) -> list[Document]:
        sha = self.__codebase.get_branch(self.__codebase.default_branch).commit.sha
        logger.info(f"Creating embeddings for {repo.full_name} at {sha}")
        codebase = repo.get_contents("")
        documents = []

        while codebase:
            file_content = codebase.pop(0)
            if file_content.type == "dir":
                codebase.extend(repo.get_contents(file_content.path))
            elif file_content.type == "file" and file_content.name.endswith(".py"):
                # Split file content in chunks of 1000 chars
                content = file_content.decoded_content.decode("utf-8")
                if len(content) < chunk_size:
                    if len(content) == 0:
                        continue
                    documents.append(
                        Document(
                            id=new_uuid(),
                            content=content,
                            source=file_content.path,
                            sha=sha,
                        )
                    )
                else:
                    start = 0
                    while start < len(content):
                        end = start + chunk_size
                        chunk = content[start:end]
                        documents.append(
                            Document(
                                id=new_uuid(),
                                content=chunk,
                                source=file_content.path,
                                sha=sha,
                            )
                        )
                        start += chunk_size - overlap_size

        # Create embeddings
        embedding_id = new_uuid()
        self.__storage.update(
            # TODO: Fix this and decide on datastructures for handling codebases/repositories
            Repo(
                id=repo_id,
                name=repo.name,
                owner=repo.owner.login,
                sha=sha,
                embeddings_created=True,
            )
        )
        self.__vector_db.create(documents=documents)
        logger.info(f"Created embeddings for {repo.full_name} at {sha}")
        return documents

    def _get_embeddings(self, sha: str) -> list:
        return self.__vector_db.get(sha=sha)

    def get_embeddings(self) -> list:
        slug = self.__codebase.full_name
        sha = self.__codebase.get_branch(self.__codebase.default_branch).commit.sha
        logger.info(f"Getting embeddings for {slug} at {sha}")
        codebase = self.__storage.get_by_identifier_and_sha(
            info=RepoInfo.from_slug(slug), sha=sha
        )
        if codebase is None:
            logger.info(
                f"No embeddings found for {slug} at {sha}. Creating embeddings."
            )
            return self.create_embeddings(slug=slug, sha=sha)
        logger.info(f"Embeddings found for {slug} at {sha}. Getting embeddings.")
        return self.__vector_db.get(sha=sha)

    """

    def get_relevant_files(self, task: str):
        queries = invoke_query_assistant(task).queries
        relevant_documents = self.query_multiple(queries)
        unique_file_paths = get_unique_file_paths(relevant_documents)

        relevant_files = []
        for file_path in unique_file_paths:
            logger.info(f"Getting relevant files for {file_path}")
            relevant_files.append(
                (
                    file_path,
                    merge_documents_with_overlap(
                        self.get_by_source(file_path)["documents"]
                    ),
                )
            )  # Todo: resolve typing issue

        return relevant_files
        """

    """
    def get_code_changes(self, task: str, relevant_files: list):
        code_changes = invoke_coding_assistant(task, relevant_files)
        verify_code_changes = invoke_verify_agent(task, code_changes)
        logger.info(f"Code changes: {verify_code_changes.code_changes}")
        return verify_code_changes.code_changes

    def apply_code_changes(self, code_changes: list):
        tmp_dir, tmp_repo_dir = self.__repo_client.download()
        self.__repo_client.initialize_git_repo(tmp_repo_dir)
        self._apply_code_changes(tmp_repo_dir, code_changes)
        self.__repo_client.commit_changes(tmp_repo_dir)
        self.__repo_client.create_pull_request(tmp_repo_dir)
        cleanup_dir(tmp_dir)

    def _apply_code_changes(self, tmp_repo_dir, code_changes):
        for code_change in code_changes:
            file_path = code_change["file_path"]
            new_text = code_change["new_text"]
            with open(f"{tmp_repo_dir}/{file_path}", "r") as file:
                content = file.read().replace(code_change["original_text"], new_text)
            with open(f"{tmp_repo_dir}/{file_path}", "w") as file:
                file.write(content)

    def query(self, query: str) -> list:
        return self.__vector_db.query(query, sha=self.__repo_client.sha)

    def query_multiple(self, queries: list[str]) -> list:
        return self.__vector_db.query_texts(queries, sha=self.__repo_client.sha)

    def get_by_source(self, source: str) -> list:
        return self.__vector_db.get_by_metadata(
            "source", source, sha=self.__repo_client.sha
        )
    """
