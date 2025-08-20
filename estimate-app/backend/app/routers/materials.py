from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import select
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/", response_model=List[schemas.MaterialRead])
async def list_materials():
	with get_session() as session:
		result = session.execute(select(models.Material).order_by(models.Material.name))
		return result.scalars().all()


@router.post("/", response_model=schemas.MaterialRead)
async def create_material(payload: schemas.MaterialCreate):
	with get_session() as session:
		existing = session.execute(select(models.Material).where(models.Material.name == payload.name)).scalar_one_or_none()
		if existing:
			raise HTTPException(status_code=400, detail="Material with this name already exists")
		material = models.Material(**payload.model_dump())
		session.add(material)
		session.flush()
		return material


@router.get("/{material_id}", response_model=schemas.MaterialRead)
async def get_material(material_id: int):
	with get_session() as session:
		material = session.get(models.Material, material_id)
		if not material:
			raise HTTPException(status_code=404, detail="Material not found")
		return material


@router.put("/{material_id}", response_model=schemas.MaterialRead)
async def update_material(material_id: int, payload: schemas.MaterialCreate):
	with get_session() as session:
		material = session.get(models.Material, material_id)
		if not material:
			raise HTTPException(status_code=404, detail="Material not found")
		for key, value in payload.model_dump().items():
			setattr(material, key, value)
		session.flush()
		return material


@router.delete("/{material_id}")
async def delete_material(material_id: int):
	with get_session() as session:
		material = session.get(models.Material, material_id)
		if not material:
			raise HTTPException(status_code=404, detail="Material not found")
		session.delete(material)
		return {"status": "deleted"}