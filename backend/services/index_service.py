import hashlib
import os
from services.file_service import (
    get_source_files,
    read_file
)

from services.chunk_service import chunk_code

from services.embedding_service import (
    EmbeddingService
)

from services.vector_service import (
    VectorService
)
from services.sparse_embedding_service import (
    SparseEmbeddingService
)


class IndexService:

    def __init__(self):

        self.embedding_service = (
    EmbeddingService()
)

        self.sparse_embedding_service = (
            SparseEmbeddingService()
        )

        self.vector_service = (
            VectorService()
        )

    def index_repository(
        self,
        repo_path: str
    ):

        self.vector_service.create_collection()
        repo_id = self.get_repo_id(
            repo_path
        )
        files = get_source_files(
            repo_path
        )

        all_chunks = []
        all_metadata = []

        for file_path in files:

            content = read_file(
                file_path
            )

            if not content:
                continue

            chunks = chunk_code(
                content
            )

            for chunk in chunks:

                chunk_content = chunk["content"]

                all_chunks.append(
                    chunk_content
                )

                all_metadata.append({

                    "repo_id": repo_id,

                    "file": file_path,

                    "language": get_language(
                        file_path
                    ),

                    "start_line": chunk[
                        "start_line"
                    ],

                    "end_line": chunk[
                        "end_line"
                    ],

                    "chunk_type": chunk[
                        "chunk_type"
                    ],

                    "symbol": chunk[
                        "symbol"
                    ],

                    "content": chunk_content
                })

        # Generate embeddings in one batch
        embeddings = (
            self.embedding_service
            .generate_embeddings(
                all_chunks
            )
        )

        sparse_embeddings = (
            self.sparse_embedding_service
            .generate_embeddings(
                all_chunks
            )
        )

        # Store everything in Qdrant
        for (
            embedding,
            sparse_embedding,
            metadata
        ) in zip(
            embeddings,
            sparse_embeddings,
            all_metadata
        ):

            self.vector_service.add_chunk(
                embedding,
                sparse_embedding,
                metadata
            )

        return {
            "repo_id": repo_id,
            "files": len(files),
            "chunks": len(all_chunks)
        }

    def get_repo_id(self, repo_path):

        absolute_path = os.path.abspath(
            repo_path
        )

        return hashlib.sha256(
            absolute_path.encode()
        ).hexdigest()[:16]

def get_language(
    file_path: str
):

    extension = (
        file_path
        .split(".")[-1]
        .lower()
    )

    mapping = {

        "py": "python",

        "js": "javascript",

        "jsx": "javascript",

        "ts": "typescript",

        "tsx": "typescript",

        "java": "java",

        "cpp": "cpp",

        "c": "c",

        "cs": "csharp",

        "go": "go",

        "rs": "rust"
    }

    return mapping.get(
        extension,
        "unknown"
    )