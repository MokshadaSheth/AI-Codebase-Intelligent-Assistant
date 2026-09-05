import re


def chunk_code(
    content: str,
    chunk_size: int = 40
):

    lines = content.splitlines()

    chunks = []

    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size,
            len(lines)
        )

        chunk_lines = lines[start:end]

        chunk_text = "\n".join(
            chunk_lines
        )

        if chunk_text.strip():

            chunks.append({
                "content": chunk_text,
                "start_line": start + 1,
                "end_line": end,
                "chunk_type": detect_chunk_type(
                    chunk_text
                ),
                "symbol": detect_symbol(
                    chunk_text
                )
            })

        start = end

    return chunks


def detect_chunk_type(
    code: str
):

    if re.search(
        r"\bclass\s+\w+",
        code
    ):
        return "class"

    if re.search(
        r"\bfunction\s+\w+",
        code
    ):
        return "function"

    if re.search(
        r"\bdef\s+\w+",
        code
    ):
        return "function"

    return "code"


def detect_symbol(
    code: str
):

    patterns = [

        r"\bclass\s+(\w+)",

        r"\bfunction\s+(\w+)",

        r"\bdef\s+(\w+)",

        r"const\s+(\w+)\s*=",

        r"let\s+(\w+)\s*=",

        r"var\s+(\w+)\s*="
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            code
        )

        if match:

            return match.group(1)

    return None