# Let's start with defining the tools.
from typing import Any, List, TypedDict

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from codr.llm.documents import document_storage


class CodeChange(BaseModel):
    file_path: str
    line_number: int
    original_text: str
    new_text: str


class DocumentInspectionInput(BaseModel):
    path: str


class DocumentInspectionTool(BaseTool):
    """Tool that inspects a document"""

    name: str = "document-inspection-tool"
    description: str = "useful for looking at files and making decisions about them"
    args_schema: type[BaseModel] = DocumentInspectionInput
    verbose = True

    def _run(self, path: str) -> Any:
        """This function inspects the document, it returns the python file"""
        return document_storage.documents.get(path, None)

    async def _arun(self, path: str) -> Any:
        return await self._run(path)


class CodeEditInput(BaseModel):
    file_path: str
    line_number: int
    original_text: str
    new_text: str


class CodeEditTool(BaseTool):
    """Tool that edits code"""

    name: str = "code-edit-tool"
    description: str = "useful for editing code"
    args_schema: type[BaseModel] = CodeEditInput
    verbose = True

    def _run(
        self, file_path: str, line_number: int, original_text: str, new_text: str
    ) -> Any:
        # Check if the file content is in the document_storage.documents dictionary
        if file_path not in document_storage.documents:
            # If the file is not in document_storage.documents, initialize it with an empty string
            document_storage.documents[file_path] = ""

        # Read the contents from the document_storage.documents dictionary
        content = document_storage.documents[file_path]

        # Replace the original text with the new text
        new_content = content.replace(original_text, new_text)

        # Update the document_storage.documents dictionary with the modified content
        document_storage.documents[file_path] = new_content

        # Write the modified content back to the file
        with open("hihi.py", "w") as f:
            f.write(new_content)

        return {
            "file_path": file_path,
            "original_text": original_text,
            "new_text": new_text,
        }


class LineNumberSearchInput(BaseModel):
    file_path: str
    text: str


class LineNumberSearchTool(BaseTool):
    """Tool that is useful for finding the line numbers of the start and the end of a specific text in a file"""

    name: str = "line-number-search-tool"
    description: str = "useful for finding the line numbers of the start and the end of a specific text in a file"
    args_schema: type[BaseModel] = LineNumberSearchInput
    verbose = True

    def _run(self, file_path: str, text: str) -> Any:
        # Check if the file content is in the document_storage.documents dictionary
        if file_path not in document_storage.documents:
            # If the file is not in document_storage.documents, initialize it with an empty string
            document_storage.documents[file_path] = ""

        # Read the contents from the document_storage.documents dictionary
        content = document_storage.documents[file_path]

        # Split the content into lines
        lines = content.split("\n")

        # Initialize the start and end line numbers
        start_line_number = -1
        end_line_number = -1

        # Iterate over the lines to find the start and end line numbers
        for i, line in enumerate(lines):
            if text in line:
                if start_line_number == -1:
                    start_line_number = i
                end_line_number = i

        return {
            "file_path": file_path,
            "line_start": start_line_number,
            "line_end": end_line_number,
        }
