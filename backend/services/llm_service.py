import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    def generate_answer(
        self,
        question,
        context,
        history=None,
        tools=None
    ):

        if history is None:
            history = []

        # Build conversation history
        history_text = ""

        for message in history:

            role = message.get(
                "role",
                "user"
            )

            content = message.get(
                "content",
                ""
            )

            history_text += (
                f"{role.upper()}: "
                f"{content}\n"
            )

        prompt = f"""
You are an AI Codebase Assistant.

Your job is to answer questions about
the provided software repository.

Use the conversation history and
retrieved code context to answer the
current question.

IMPORTANT RULES:

1. Answer using the provided code context.
2. Do not invent files or code.
3. If the answer cannot be determined
   from the context, say so.
4. Use conversation history to understand
   references such as "that file", "it",
   "this function", etc.
5. Give a clear technical explanation.

CONVERSATION HISTORY:

{history_text}

CURRENT QUESTION:

{question}

RETRIEVED CODE CONTEXT:

{context}

ANSWER:
"""

        request = {
            "model": self.model,
            "contents": prompt
        }
        if tools:
            request["tools"] = tools

        response = self.client.models.generate_content(
            **request
        )

        return response.text