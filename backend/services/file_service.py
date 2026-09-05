import os


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
}


def get_source_files(repo_path: str):
    files = []

    for root, dirs, filenames in os.walk(repo_path):

        # Ignore unnecessary directories
        dirs[:] = [
            d for d in dirs
            if d not in {
                ".git",
                "node_modules",
                "venv",
                "__pycache__",
                "dist",
                "build"
            }
        ]

        for filename in filenames:

            extension = os.path.splitext(filename)[1].lower()

            if extension in ALLOWED_EXTENSIONS:

                file_path = os.path.join(root, filename)

                files.append(file_path)

    return files

def read_file(file_path: str):

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except UnicodeDecodeError:
        return None