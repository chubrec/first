from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import select
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/works", tags=["works"])


@router.get("/", response_model=List[schemas.WorkRead])
async def list_works():
	with get_session() as session:
		result = session.execute(select(models.Work).order_by(models.Work.name))
		return result.scalars().all()


@router.post("/", response_model=schemas.WorkRead)
async def create_work(payload: schemas.WorkCreate):
	with get_session() as session:
		existing = session.execute(select(models.Work).where(models.Work.name == payload.name)).scalar_one_or_none()
		if existing:
			raise HTTPException(status_code=400, detail="Work with this name already exists")
		work = models.Work(**payload.model_dump())
		session.add(work)
		session.flush()
		return work


@router.get("/{work_id}", response_model=schemas.WorkRead)
async def get_work(work_id: int):
	with get_session() as session:
		work = session.get(models.Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")
		return work


@router.put("/{work_id}", response_model=schemas.WorkRead)
async def update_work(work_id: int, payload: schemas.WorkCreate):
	with get_session() as session:
		work = session.get(models.Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")
		for key, value in payload.model_dump().items():
			setattr(work, key, value)
		session.flush()
		return work


@router.delete("/{work_id}")
async def delete_work(work_id: int):
	with get_session() as session:
		work = session.get(models.Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")
		session.delete(work)
		return {"status": "deleted"}