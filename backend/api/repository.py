import subprocess

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.index_service import IndexService
from services.github_service import GitHubService


router = APIRouter(
    prefix="/repository",
    tags=["Repository"]
)


class RepositoryRequest(BaseModel):
    repo_path: str


class GitHubRequest(BaseModel):
    github_url: str


@router.post("/index")
def index_repository(
    request: RepositoryRequest
):

    try:

        service = IndexService()

        result = service.index_repository(
            request.repo_path
        )

        return {
            "message": "Repository indexed successfully",
            "files": result["files"],
            "chunks": result["chunks"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/clone")
def clone_repository(
    request: GitHubRequest
):

    try:

        service = GitHubService()

        repo_path = service.clone_repository(
            request.github_url
        )

        return {
            "message": "Repository cloned successfully",
            "repo_path": repo_path
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except subprocess.CalledProcessError:

        raise HTTPException(
            status_code=500,
            detail="Failed to clone repository."
        )

@router.post("/connect")
def connect_repository(
    request: GitHubRequest
):

    try:

        github_service = GitHubService()

        repo_path = (
            github_service
            .clone_repository(
                request.github_url
            )
        )

        index_service = IndexService()

        result = (
            index_service
            .index_repository(
                repo_path
            )
        )

        return {
            "message": "Repository connected and indexed successfully",
            "repo_path": repo_path,
            "repo_id": result["repo_id"],
            "files": result["files"],
            "chunks": result["chunks"]
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )