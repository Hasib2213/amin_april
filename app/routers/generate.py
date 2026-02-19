from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.services.narrative_generator import generate_family_narrative
from bson import ObjectId

router = APIRouter(prefix="/api/v1", tags=["generate"])

@router.post("/report")
async def create_report(user_id: str = "demo_user", db = Depends(get_db)):
    uploads = await db.uploads.find({"user_id": user_id}).to_list(50)

    dna = next((u for u in uploads if u["type"] == "dna"), {})
    gedcom = next((u for u in uploads if u["type"] == "gedcom"), {})
    docs = [u for u in uploads if u["type"] in ("document", "photo")]

    narrative = await generate_family_narrative(
        dna_snps_count=len(dna.get("snps", [])),
        gedcom_summary=gedcom,
        documents=docs
    )

    report = {
        "user_id": user_id,
        "generated_at": datetime.utcnow(),
        "narrative": narrative,
        "sources": [str(u["_id"]) for u in uploads]
    }

    result = await db.reports.insert_one(report)
    return {"report_id": str(result.inserted_id), "narrative": narrative}