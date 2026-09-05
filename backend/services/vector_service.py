from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    PointStruct,
    Prefetch,
    FusionQuery,
    Fusion,
    Filter,
    FieldCondition,
    MatchValue
)

import uuid


class VectorService:

    def __init__(self):

        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

        self.collection_name = (
            "code_chunks_hybrid"
        )

    def create_collection(self):

        collections = (
            self.client.get_collections()
        )

        exists = any(
            collection.name ==
            self.collection_name
            for collection
            in collections.collections
        )

        if exists:
            return

        self.client.create_collection(

            collection_name=(
                self.collection_name
            ),

            vectors_config={

                "dense": VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )

            },

            sparse_vectors_config={

                "sparse": SparseVectorParams(
                    index=SparseIndexParams()
                )

            }
        )

    def add_chunk(
        self,
        embedding,
        sparse_embedding,
        payload
    ):

        point = PointStruct(

            id=str(
                uuid.uuid4()
            ),

            vector={

                "dense": embedding,

                "sparse": sparse_embedding

            },

            payload=payload
        )

        self.client.upsert(

            collection_name=(
                self.collection_name
            ),

            points=[point]
        )

    def search(
        self,
        embedding,
        sparse_embedding,
        repo_id,
        limit=5
    ):

        repo_filter = Filter(
            must=[
                FieldCondition(
                    key="repo_id",
                    match=MatchValue(value=repo_id)
                )
            ]
        )

        results = self.client.query_points(

            collection_name=(
                self.collection_name
            ),

            prefetch=[

                Prefetch(

                    query=embedding,

                    using="dense",

                    limit=limit * 4,

                    filter=repo_filter
                ),

                Prefetch(

                    query=sparse_embedding,

                    using="sparse",

                    limit=limit * 4,

                    filter=repo_filter
                )
            ],

            query=FusionQuery(
                fusion=Fusion.RRF
            ),

            limit=limit,

            with_payload=True
        )

        return results.points