from dataclasses import dataclass
import json

from ollama import AsyncClient

from config import settings


@dataclass
class ClassificationResult:
    topics: list[str]
    departments: list[str]
    confidence: float
    needs_clarification: bool


class QueryClassifier:

    def __init__(self):
        self.client = AsyncClient(
            host=settings.OLLAMA_HOST
        )

    async def classify(self, message: str) -> ClassificationResult:
        message = message.strip()

        if not message:
            return ClassificationResult(
                topics=[],
                departments=[],
                confidence=0.0,
                needs_clarification=True,
            )

        prompt = f"""
/no_think

You are the query classification component of a university
campus support system.

Your ONLY job is to classify the user's message.

Available departments:
- IT
- HR
- Finance
- Facilities
- Administration
- Other

Rules:

1. Identify every distinct topic in the user's message.
2. Identify the department responsible for each topic.
3. If multiple unrelated issues exist, return multiple departments.
4. Only use departments from the available department list.
5. Confidence must be a number between 0.0 and 1.0.
6. Use low confidence when the message is ambiguous.
7. Set needs_clarification=true when the query cannot be
   reliably classified.
8. Do not answer the user's question.
9. Do not explain your reasoning.
10. Return ONLY valid JSON.

Required JSON format:

{{
    "topics": ["topic1", "topic2"],
    "departments": ["IT"],
    "confidence": 0.94,
    "needs_clarification": false
}}

User message:
{message}
"""

        response = await self.client.chat(
            model=settings.OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise classification system. Return only JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format={
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "departments": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "needs_clarification": {
                        "type": "boolean",
                    },
                },
                "required": [
                    "topics",
                    "departments",
                    "confidence",
                    "needs_clarification",
                ],
            },
        )

        raw_content = response["message"]["content"]

        result = json.loads(raw_content)

        allowed_departments = {
            "IT",
            "HR",
            "Finance",
            "Facilities",
            "Administration",
            "Other",
        }

        departments = [
            department
            for department in result["departments"]
            if department in allowed_departments
        ]

        confidence = max(
            0.0,
            min(1.0, float(result["confidence"]))
        )

        needs_clarification = (
            bool(result["needs_clarification"])
            or not departments
            or confidence < 0.60
        )

        return ClassificationResult(
            topics=result["topics"],
            departments=departments,
            confidence=confidence,
            needs_clarification=needs_clarification,
        )