import os
from dotenv import load_dotenv
from typing import Type, TypeVar, List, Dict, Any
from pydantic import BaseModel
from openai import OpenAI
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1")

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-5-nano")
EMBEDDINGS_MODEL = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-large")

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """
    שכבת תקשורת עם LLM.

    אחראית על:
    - קריאות ל-OpenAI
    - תמיכה ב-messages (system/user)
    - structured output עם Pydantic
    """

    def __init__(self, model_name: str = OPENROUTER_MODEL):
        self.model_name = model_name

    # ------------------------------------------------------------
    # Structured output
    # ------------------------------------------------------------

    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        temperature: float = 0.2
        ) ->     T:

        schema = response_model.model_json_schema()

        messages = [
            {
                "role": "system",
                "content": (
                    "Return valid JSON only. "
                    "No markdown, no explanation. "
                    "Match this schema exactly:\n"
                    f"{json.dumps(schema)}"
                )
            },
            *messages
        ]

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=4000,
            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        try:
            data = json.loads(content)

            return response_model.model_validate(data)

        except Exception as e:
            raise ValueError(
                f"Failed parsing OpenRouter response into "
                f"{response_model.__name__}: {e}"
            )
    # ------------------------------------------------------------
    # free text
    # ------------------------------------------------------------

    def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2
    ) -> str:


        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=4000
        )

        return response.choices[0].message.content

    # ------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------

    def embed_texts(
        self,
        texts: list[str],
        model_name: str | None = None,
    ) -> list[list[float]]:
        """Embed a list of texts using the OpenAI embeddings API."""

        model = model_name or EMBEDDINGS_MODEL
        
        response = client.embeddings.create(
            model=model,
            input=texts,
        )

        return [item.embedding for item in response.data]