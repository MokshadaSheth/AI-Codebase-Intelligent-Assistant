class RAGService:

    def __init__(self, graph_service):
        self.graph_service = graph_service

    def ask(
        self,
        question: str,
        repo_id: str,
        history=None,
        limit: int = 5
    ):

        result = self.graph_service.run(
            question,
            repo_id,
            [] if history is None else history,
            limit
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"]
        }