from google.generativeai.types import GenerationConfig
from app.config import settings
import google.generativeai as genai

# Configure with debugging
api_key = settings.GEMINI_API_KEY
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in .env file")

genai.configure(api_key=api_key)
story_model = genai.GenerativeModel(settings.GEMINI_MODEL)

async def generate_family_narrative(
    dna_snps_count: int,
    ethnicity_estimate: str = "unknown",  # you can add simple inference later
    gedcom_summary: dict = None,
    documents: list[dict] = None
) -> dict:
    docs_text = "\n".join([d.get("summary", "") + "\n" + d.get("extracted_text", "")[:500] for d in (documents or [])])

    prompt = f"""
    Create a compelling, accurate family history narrative.
    Inputs:
    - DNA: {dna_snps_count} SNPs parsed, ethnicity approx {ethnicity_estimate}
    - Family tree: {gedcom_summary or 'No tree uploaded'}
    - Documents/Photos: {docs_text}

    Rules:
    - Do NOT invent names, dates, places not in input
    - No repeating historical events (e.g. famine only once)
    - Structure: 1. Ethnicity overview 2. Timeline (unique events) 3. 3-5 ancestor bios 4. Migration story 5. Conclusion
    - Engaging but factual tone
    Output JSON: {{"overview": str, "timeline": list[dict], "ancestors": list[dict], "story": str}}
    """

    try:
        response = story_model.generate_content(
            prompt,
            generation_config=GenerationConfig(
                response_mime_type="application/json"
            )
        )

        import json
        try:
            return json.loads(response.text)
        except:
            return {"error": "Generation failed", "raw": response.text}
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "not valid" in error_msg:
            raise ValueError(
                f"Gemini API key is invalid or API not enabled. "
                f"Check: 1) .env GEMINI_API_KEY is correct, "
                f"2) Generative Language API is enabled in Google Cloud Console, "
                f"3) API key has proper restrictions/permissions. Error: {error_msg}"
            )
        raise