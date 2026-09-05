import os
import re
import subprocess


class GitHubService:

    def __init__(self):
        self.base_path = "../repositories"

        os.makedirs(
            self.base_path,
            exist_ok=True
        )

    def validate_url(self, url: str):

        pattern = (
            r"^https://github\.com/"
            r"[\w.-]+/"
            r"[\w.-]+"
            r"(?:\.git)?/?$"
        )

        return re.match(
            pattern,
            url
        ) is not None

    def get_repo_name(self, url: str):

        url = url.rstrip("/")

        name = url.split("/")[-1]

        if name.endswith(".git"):
            name = name[:-4]

        return name

    def clone_repository(self, url: str):

        if not self.validate_url(url):
            raise ValueError(
                "Only valid GitHub repository URLs are allowed."
            )

        repo_name = self.get_repo_name(url)

        repo_path = os.path.join(
            self.base_path,
            repo_name
        )

        # Already cloned
        if os.path.exists(repo_path):
            return repo_path

        subprocess.run(
            [
                "git",
                "clone",
                url,
                repo_path
            ],
            check=True
        )

        return repo_path