from codr.application.entities import Repo, RepoInfo
from codr.storage.dao.abstract_dao import DAO
from codr.storage.repository import E, Factory, Repository


class RepoRepository(Repository[Repo]):
    def __init__(self, dao: DAO, factory: Factory[E]) -> None:
        super().__init__(dao=dao, factory=factory)

    def get_by_identifier_and_sha(self, info: RepoInfo, sha: str) -> Repo:
        return self._dao.get_by(name=info.name, owner=info.owner, sha=sha)
