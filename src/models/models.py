from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LicenseBase(BaseModel):
    name: str
    type: str
    valid_until: datetime
    active: bool

class LicenseCreate(LicenseBase):
    pass

class License(LicenseBase):
    id: str

    class Config:
        from_attributes = True

class LicenseUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    valid_until: Optional[str] = None
    active: Optional[bool] = None

class LicenseValidationResponse(BaseModel):
    valid: bool