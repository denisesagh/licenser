from datetime import datetime

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request

from src.db.database import DatabaseManager
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.models import License, LicenseCreate, LicenseUpdate

db = DatabaseManager()
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)




@router.get("/validate", response_model=bool, status_code=status.HTTP_200_OK)
def check_license( request: Request):
    """
    Get a license by its ID.
    """
    license_id = request.headers.get("License-Id")
    if not license_id:
        raise HTTPException(status_code=400, detail="License ID not provided")
    try:
        current_license: License = db.get_license_by_id(license_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="License not found")
    if not current_license:
        raise HTTPException(status_code=404, detail="License not found")
    if current_license.valid_until < datetime.now():
        raise HTTPException(status_code=403, detail="License expired")
    if not current_license.active:
        raise HTTPException(status_code=403, detail="License inactive")
    return True

@router.post("/create", response_model=License, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_license(request: Request, license_to_create: LicenseCreate):
    """
    Create a new license.
    """
    license_id = db.create_license(license_to_create.model_dump())
    if not license_id:
        raise HTTPException(status_code=400, detail="License creation failed")
    return {**license_to_create.model_dump(), "id": license_id}

@router.post("/update", response_model=License, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def update_license(request: Request, license_to_update: LicenseUpdate):
    """
    Update an existing license.
    """
    license_id = request.headers.get("License-Id")
    if not license_id:
        raise HTTPException(status_code=400, detail="License ID not provided")
    if not db.update_license(license_id, license_to_update):
        raise HTTPException(status_code=400, detail="License update failed")
    return {**license_to_update.model_dump(), "id": license_id}
