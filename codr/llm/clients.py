from typing import List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from codr.llm.documents import document_storage
from codr.llm.tools import DocumentInspectionTool, LineNumberSearchTool

load_dotenv()


class Queries(BaseModel):
    queries: list[str]


query_assistant = ChatOpenAI(model="gpt-4o").with_structured_output(Queries)

query_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an exceptional Senior Software Engineer. For the given task, come up with queries that will help locate the files that need changes. \
        Here is an example

        Example:
        Task: Add a new field to the homework model

        Queries:
        ['def homework_router()', 'class Homework', 'path/to/homework_model.py', 'Homework()']


        This is the task:
        {task}

        Queries:
        """,
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def invoke_query_assistant(task: str) -> Queries:
    query_prompt = query_prompt_template.invoke({"task": task, "agent_scratchpad": []})
    return query_assistant.invoke(query_prompt)


class CodeChange(TypedDict):
    file_path: str
    line_start: int
    line_end: int
    original_text: str
    new_text: str


class CodeChanges(BaseModel):
    code_changes: List[CodeChange] = Field(
        ..., description="List of code changes to be made"
    )


parser = PydanticOutputParser(pydantic_object=CodeChanges)

tools = [DocumentInspectionTool(), LineNumberSearchTool()]

llm = ChatOpenAI(model="gpt-4o")
code_change_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an exceptional Principal Software Engineer. For the given task and code snippet, come up with necessary code changes. \
        It might be the case that the snippet does not need any changes. \
        Think step by step if a code change you would do actually is necessary for achieving the task. \
        Focus solely on the task, do not reformat the code or make any other changes. Only touch the code that is totally necessary to complete the task. \
        Make ALL necessary changes and do not skip any, since your code changes will be used to update the codebase.
        The code changes should be in the form of a list of code changes. If you dont want to make any changes, return an empty list.
        Use the LineNumberSearchTool to find the line numbers where the changes should be made.

        This is the task:
        {task}

        This is the file with the file_path: {file_path}

        This is the code snippet:
        {snippet}

        Return a list of code changes with the following fields:
        - file_path: The path to the file where the change is necessary \
        - line_start: The line number where the change starts \
        - line_end: The line number where the change ends \
        - original_text: The original text that needs to be changed \
        - new_text: The new text that should replace the original text. Wrap the output in `json` tags\n{format_instructions}. Just write the json, do NOT include ```json```""",
        ),
        ("placeholder", "{messages}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
).partial(format_instructions=parser.get_format_instructions())


code_edit_system_message = SystemMessage(
    content="""You are an exceptional Principal Software Engineer. For the given task and code snippet, come up with necessary code changes. \
        It might be the case that the snippet does not need any changes. \
        Think step by step if a code change you would do actually is necessary for achieving the task. \
        Focus solely on the task, do not reformat the code or make any other changes. Only touch the code that is totally necessary to complete the task. \
        Make ALL necessary changes and do not skip any, since your code changes will be used to update the codebase.
        The code changes should be in the form of a list of code changes. If you dont want to make any changes, return an empty list.
        Use the LineNumberSearchTool to find the line numbers where the changes should be made."""
)


def invoke_coding_assistant(task: str, relevant_files: list) -> CodeChanges:

    document_storage.documents = {doc[0]: doc[1] for doc in relevant_files}
    llm.bind_tools(tools)

    code_changes = []
    for fp, doc in document_storage.documents.items():
        chain = code_change_prompt | llm | parser
        resp = chain.invoke(
            {
                "input": f"{task}, These are the possible files: {', '.join(document_storage.documents.keys())}",
                "task": task,
                "file_path": fp,
                "snippet": doc,
                "agent_scratchpad": [],
            },
        )

        code_changes.extend(resp.code_changes)

    return CodeChanges(code_changes=code_changes)


verify_agent = ChatOpenAI(model="gpt-4o")

verify_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an exceptional Senior Software Engineer. For the given task and code snippet, verify the code changes that the Principal Software Engineer has made. \
        You should check if the code changes are correct and if they are in line with the task. \

        I will show you proposed code changes in json Format, you should check if they fulfill the following criteria:
        - The change is necessary for the task to be completed
        - The change is not only a refactoring or reformatting of the code
        - The change is in line with the task and does not introduce any new bugs
        - The change does not alter functionality of the code that is not necessary for the task

        You will return a list of code changes. Only add the code changes that fulfill the criteria. If a certain change is not necessary, do not include it in the list.

        This is the task:
        {task}

        These are the code changes:
        {code_changes}

        Return a list of code changes with the following fields:
        - file_path: The path to the file where the change is necessary \
        - line_start: The line number where the change starts \
        - line_end: The line number where the change ends \
        - original_text: The original text that needs to be changed \
        - new_text: The new text that should replace the original text. Wrap the output in `json` tags\n{format_instructions}. Just write the json, do NOT include ```json```
        """,
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
).partial(format_instructions=parser.get_format_instructions())


def invoke_verify_agent(task: str, code_changes: CodeChanges) -> CodeChanges:
    verify_prompt = verify_prompt_template.invoke(
        {
            "task": task,
            "code_changes": code_changes.code_changes,
            "agent_scratchpad": [],
        }
    )

    chain = verify_agent | parser
    return chain.invoke(verify_prompt)
