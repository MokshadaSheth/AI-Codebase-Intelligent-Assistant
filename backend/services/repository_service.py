import os
from git import Repo


def clone_repository(url: str, path: str):
    if os.path.exists(path):
        return False

    Repo.clone_from(url, path)

    return True