import google.generativeai as genai
from app.config import settings
from pydantic import BaseModel, Field, ConfigDict
from typing import List

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

class ExtractedInfo(BaseModel):
    model_config = ConfigDict(extra='ignore')  # Ignore extra fields from Gemini
    
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
    
    Return ONLY valid JSON in this exact format:
    {
        "full_text": "exact transcribed text here",
        "summary": "2-4 sentence family history summary",
        "key_entities": [
            {"type": "name", "value": "John Doe"},
            {"type": "date", "value": "1892-05-15"},
            {"type": "place", "value": "Boston, MA"}
        ]
    }
    """

    try:
        response = model.generate_content(
            [prompt, {"mime_type": mime_type, "data": file_bytes}],
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        import json
        data = json.loads(response.text)
        return ExtractedInfo(**data)
    except Exception as e:
        # Fallback if JSON parsing fails
        return ExtractedInfo(
            full_text=f"Error extracting: {str(e)}",
            summary="Could not process document",
            key_entities=[]
        )