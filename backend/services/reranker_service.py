from sentence_transformers import CrossEncoder


class RerankerService:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, query, results, limit=5):
        pairs = [
            (query, result.payload["content"])
            for result in results
        ]

        scores = self.model.predict(pairs)

        ranked_results = sorted(
            zip(scores, results),
            key=lambda item: item[0],
            reverse=True
        )

        return [
            result
            for _, result in ranked_results[:limit]
        ]
