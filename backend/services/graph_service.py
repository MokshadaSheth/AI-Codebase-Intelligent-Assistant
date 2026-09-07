from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    question: str
    repo_id: str
    history: list
    limit: int
    retrieved_results: list[Any]
    reranked_results: list[Any]
    context: str
    answer: str
    sources: list


class GraphService:

    def __init__(
        self,
        embedding_service,
        sparse_embedding_service,
        vector_service,
        reranker_service,
        llm_service,
        mcp_tools=None
    ):
        self.embedding_service = embedding_service
        self.sparse_embedding_service = sparse_embedding_service
        self.vector_service = vector_service
        self.reranker_service = reranker_service
        self.llm_service = llm_service
        self.mcp_tools = mcp_tools

        graph = StateGraph(GraphState)
        graph.add_node("retrieve_node", self.retrieve_node)
        graph.add_node("rerank_node", self.rerank_node)
        graph.add_node("generate_node", self.generate_node)
        graph.add_edge(START, "retrieve_node")
        graph.add_edge("retrieve_node", "rerank_node")
        graph.add_edge("rerank_node", "generate_node")
        graph.add_edge("generate_node", END)

        self.compiled_graph = graph.compile()

    def retrieve_node(self, state: GraphState):
        question_embedding = self.embedding_service.generate_embedding(
            state["question"]
        )
        sparse_question_embedding = (
            self.sparse_embedding_service.generate_embedding(
                state["question"]
            )
        )

        retrieved_results = self.vector_service.search(
            question_embedding,
            sparse_question_embedding,
            state["repo_id"],
            limit=20
        )

        retrieved_results = self.reranker_service.boost_code_matches(
            state["question"],
            retrieved_results
        )

        return {"retrieved_results": retrieved_results}

    def rerank_node(self, state: GraphState):
        reranked_results = self.reranker_service.rerank(
            state["question"],
            state["retrieved_results"],
            limit=state["limit"]
        )

        return {"reranked_results": reranked_results}

    def generate_node(self, state: GraphState):
        context_parts = []

        for result in state["reranked_results"]:
            file_path = result.payload.get("file", "unknown")
            content = result.payload.get("content", "")
            context_parts.append(
                f"""
FILE: {file_path}

CODE:
{content}
"""
            )

        context = "\n".join(context_parts)
        tools = []
        if self.mcp_tools is not None:
            tools = self.mcp_tools.tools_for_results(
                state["reranked_results"]
            )

        try:
            answer = self.llm_service.generate_answer(
                state["question"],
                context,
                state["history"],
                tools=tools
            )
        except Exception:
            if not tools:
                raise
            answer = self.llm_service.generate_answer(
                state["question"],
                context,
                state["history"]
            )

        sources = []
        for result in state["reranked_results"]:
            payload = result.payload
            sources.append({
                "file": payload.get("file", "unknown"),
                "start_line": payload.get("start_line"),
                "end_line": payload.get("end_line"),
                "symbol": payload.get("symbol"),
                "chunk_type": payload.get("chunk_type", "code")
            })

        return {
            "context": context,
            "answer": answer,
            "sources": sources
        }

    def run(
        self,
        question: str,
        repo_id: str,
        history=None,
        limit: int = 5
    ):
        return self.compiled_graph.invoke({
            "question": question,
            "repo_id": repo_id,
            "history": [] if history is None else history,
            "limit": limit,
            "retrieved_results": [],
            "reranked_results": [],
            "context": "",
            "answer": "",
            "sources": []
        })