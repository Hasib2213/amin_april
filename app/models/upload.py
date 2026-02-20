from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class DNASNP(BaseModel):
    rsid: str
    chromosome: str
    position: str | int
    genotype: str

class UploadBase(BaseModel):
    user_id: str = "demo_user"
    filename: str
    type: str  # "dna", "gedcom", "document", "photo"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class DNAUpload(UploadBase):
    type: str = "dna"
    snps: List[DNASNP] = []

class GEDCOMUpload(UploadBase):
    type: str = "gedcom"
    individuals: List[Dict] = []   # basic parsed
    families: List[Dict] = []

class DocumentUpload(UploadBase):
    type: str = "document"
    extracted_text: str = ""
    summary: str = ""
    key_entities: List[Dict] = []   # name/date/place etc.

class PhotoUpload(UploadBase):
    type: str = "photo"
    extracted_text: str = ""
    summary: str = ""
    key_entities: List[Dict] = []   # name/date/place etc.