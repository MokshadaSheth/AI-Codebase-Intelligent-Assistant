from services.vector_service import VectorService


service = VectorService()

service.create_collection()

print("Qdrant collection created successfully.")