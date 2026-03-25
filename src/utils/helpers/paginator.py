from typing import Union

from github.PaginatedList import PaginatedList
from github.File import File
from github.Repository import Repository


def to_list(paginator: PaginatedList[Union[Repository, File]]):
    return [obj for obj in paginator]
