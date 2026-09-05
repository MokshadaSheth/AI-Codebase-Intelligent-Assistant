from fastembed import SparseTextEmbedding


class SparseEmbeddingService:

    def __init__(self):

        self.model = SparseTextEmbedding(
            model_name="Qdrant/bm25"
        )

    def generate_embedding(
        self,
        text: str
    ):

        embedding = next(
            self.model.embed([text])
        )

        return {
            "indices": embedding.indices.tolist(),
            "values": embedding.values.tolist()
        }

    def generate_embeddings(
        self,
        texts
    ):

        embeddings = []

        for embedding in self.model.embed(
            texts
        ):

            embeddings.append({

                "indices":
                    embedding.indices.tolist(),

                "values":
                    embedding.values.tolist()

            })

        return embeddings