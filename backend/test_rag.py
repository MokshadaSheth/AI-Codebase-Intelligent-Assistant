from services.rag_service import RAGService


service = RAGService()


result = service.ask(
    "Where is authentication implemented?"
)


print("\nANSWER:")
print(result["answer"])


print("\nSOURCES:")

for source in result["sources"]:
    print(source)