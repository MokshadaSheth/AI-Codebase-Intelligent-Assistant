from pathlib import Path

from mcp.server.mcpserver import MCPServer

from services.file_service import get_source_files, read_file


mcp = MCPServer("codebase-assistant")

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    "dist",
    "build",
}

SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
}


def _repository_root(repo_path: str) -> Path:
    root = Path(repo_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Repository does not exist: {repo_path}")
    return root


def _is_allowed_file(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False

    if any(part in IGNORED_DIRECTORIES for part in path.parts):
        return False

    return path.name not in SECRET_NAMES and not path.name.startswith(".env.")


def _source_files(root: Path) -> list[Path]:
    return [
        Path(file_path).resolve()
        for file_path in get_source_files(str(root))
        if _is_allowed_file(Path(file_path).resolve(), root)
    ]


@mcp.tool()
def list_files(repo_path: str) -> list[str]:
    """List source files in a repository without exposing secret files."""
    root = _repository_root(repo_path)
    return [
        str(path.relative_to(root))
        for path in _source_files(root)
    ]


@mcp.tool()
def get_file(repo_path: str, file_path: str) -> str:
    """Read one source file within a repository."""
    root = _repository_root(repo_path)
    requested = (root / file_path).resolve()

    if not _is_allowed_file(requested, root):
        return "Error: file is outside the repository or is not an allowed source file."

    if not requested.is_file():
        return f"Error: file does not exist: {file_path}"

    content = read_file(str(requested))
    if content is None:
        return "Error: file is not valid UTF-8 text."
    return content


@mcp.tool()
def search_code(repo_path: str, query: str) -> list[dict[str, object]]:
    """Search source files and return matching lines with file locations."""
    root = _repository_root(repo_path)
    matches = []
    search_query = query.casefold()

    for path in _source_files(root):
        content = read_file(str(path))
        if content is None:
            continue

        lines = content.splitlines()
        for line_number, line in enumerate(lines, start=1):
            if search_query in line.casefold():
                matches.append({
                    "file": str(path.relative_to(root)),
                    "line": line_number,
                    "snippet": line.strip(),
                })

    return matches


if __name__ == "__main__":
    mcp.run()