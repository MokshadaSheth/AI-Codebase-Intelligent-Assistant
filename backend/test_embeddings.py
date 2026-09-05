from services.embedding_service import EmbeddingService


service = EmbeddingService()

text = "Where is user authentication implemented?"

embedding = service.generate_embedding(text)

print("Embedding size:", len(embedding))

print("First 10 values:")
print(embedding[:10])