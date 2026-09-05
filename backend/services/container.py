from services.embedding_service import EmbeddingService
from services.sparse_embedding_service import SparseEmbeddingService
from services.vector_service import VectorService
from services.llm_service import LLMService
from services.reranker_service import RerankerService
from services.mcp_tools import MCPTools
from services.graph_service import GraphService
from services.rag_service import RAGService


embedding_service = EmbeddingService()

sparse_embedding_service = SparseEmbeddingService()

vector_service = VectorService()

llm_service = LLMService()

reranker_service = RerankerService()

mcp_tools = MCPTools()

graph_service = GraphService(
    embedding_service=embedding_service,
    sparse_embedding_service=sparse_embedding_service,
    vector_service=vector_service,
    reranker_service=reranker_service,
    llm_service=llm_service,
    mcp_tools=mcp_tools
)


rag_service = RAGService(graph_service=graph_service)