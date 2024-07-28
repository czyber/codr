from dataclasses import dataclass


@dataclass
class CreateCodebaseIndexRequest:
    pass


@dataclass
class CreateCodebaseIndexResponse:
    pass


class CreateCodebaseIndex:
    def execute(self, request: CreateCodebaseIndexRequest) -> CreateCodebaseIndexResponse:
        pass
