import google.generativeai as genai
from app.config import settings
from pydantic import BaseModel, Field
from typing import List

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")  # or latest

class ExtractedInfo(BaseModel):
    full_text: str = Field(description="Exact transcribed text")
    summary: str = Field(description="2-4 sentence family history summary")
    key_entities: List[dict] = Field(description="List of {'type': 'name/date/place/event', 'value': str}")

async def extract_from_file(file_bytes: bytes, mime_type: str = "image/jpeg") -> ExtractedInfo:
    prompt = """
    Analyze this historical family document/photo/letter/certificate.
    Transcribe ALL text exactly (preserve spelling, dates, names).
    For handwritten: be as accurate as possible, use [?] for uncertain parts.
    Then extract:
    - summary: brief family-relevant insight
    - key_entities: important names, dates, places, events
    Output ONLY valid JSON matching the schema.
    """

    response = model.generate_content(
        [prompt, {"mime_type": mime_type, "data": file_bytes}],
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": ExtractedInfo.model_json_schema(),
        }
    )

    return ExtractedInfo.model_validate_json(response.text)