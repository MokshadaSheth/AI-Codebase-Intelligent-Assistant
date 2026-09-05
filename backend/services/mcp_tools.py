import os
from pathlib import Path


class MCPTools:

    def tools_for_results(self, results):
        repo_path = self._repo_path_from_results(results)
        if repo_path is None:
            return []

        try:
            from services.mcp_server import get_file, list_files, search_code
        except Exception:
            return []

        def search_code_tool(query: str):
            """Search source files in the current repository."""
            try:
                return search_code(repo_path, query)
            except Exception as error:
                return f"MCP search unavailable: {error}"

        def get_file_tool(file_path: str):
            """Read an allowed source file in the current repository."""
            try:
                return get_file(repo_path, file_path)
            except Exception as error:
                return f"MCP file read unavailable: {error}"

        def list_files_tool():
            """List allowed source files in the current repository."""
            try:
                return list_files(repo_path)
            except Exception as error:
                return f"MCP file listing unavailable: {error}"

        search_code_tool.__name__ = "search_code"
        get_file_tool.__name__ = "get_file"
        list_files_tool.__name__ = "list_files"

        return [
            search_code_tool,
            get_file_tool,
            list_files_tool,
        ]

    def _repo_path_from_results(self, results):
        file_paths = []
        for result in results:
            file_path = result.payload.get("file")
            if file_path:
                file_paths.append(os.path.abspath(file_path))

        if not file_paths:
            return None

        try:
            common_path = Path(os.path.commonpath(file_paths))
        except ValueError:
            return None
        if common_path.is_file():
            common_path = common_path.parent
        return str(common_path)
