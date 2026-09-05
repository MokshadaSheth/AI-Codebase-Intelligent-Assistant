from services.llm_service import LLMService


service = LLMService()


answer = service.generate_answer(
    "What does a function do?",
    """
    def add(a, b):
        return a + b
    """
)


print(answer)