from sentence_transformers import CrossEncoder
import re


class RerankerService:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def boost_code_matches(self, query, results):
        """Apply a lightweight code-aware boost before CrossEncoder reranking."""
        query_tokens = self._query_tokens(query)
        scored_results = []

        for position, result in enumerate(results):
            payload = result.payload or {}
            file_value = str(payload.get("file") or "").lower()
            symbol_value = str(payload.get("symbol") or "").lower()
            content_value = str(payload.get("content") or "").lower()
            file_name = file_value.replace("\\", "/").rsplit("/", 1)[-1]

            boost = 0.0
            for token in query_tokens:
                # Exact metadata matches are more reliable than content matches.
                if token == file_name or token == symbol_value:
                    boost += 6.0
                elif token in file_name or token in symbol_value:
                    boost += 1.5
                elif re.search(rf"(?<![a-z0-9_]){re.escape(token)}(?![a-z0-9_])", content_value):
                    boost += 0.25

            # Keep the original Qdrant order for candidates with equal boosts.
            scored_results.append((boost, -position, result))

        scored_results.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [result for _, _, result in scored_results]

    @staticmethod
    def _query_tokens(query):
        stop_words = {
            "a", "an", "and", "are", "contains", "does", "file", "for",
            "how", "in", "is", "of", "the", "to", "what", "where", "which"
        }
        tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_.-]*", query.lower())
        query_tokens = [
            token for token in tokens
            if len(token) >= 3 and token not in stop_words
        ]

        # Normalize common natural-language forms without altering explicit code tokens.
        for token in query_tokens.copy():
            if "_" not in token and "." not in token and "-" not in token:
                if token.endswith("ing") and len(token) > 5:
                    query_tokens.append(token[:-3])
                elif token.endswith("ed") and len(token) > 4:
                    query_tokens.append(token[:-2])

        return query_tokens

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
