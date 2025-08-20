from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import select
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schemas.ProjectRead])
async def list_projects():
	with get_session() as session:
		result = session.execute(select(models.Project).order_by(models.Project.created_at.desc()))
		return result.scalars().all()


@router.post("/", response_model=schemas.ProjectRead)
async def create_project(payload: schemas.ProjectCreate):
	with get_session() as session:
		project = models.Project(**payload.model_dump())
		session.add(project)
		session.flush()
		return project


@router.get("/{project_id}", response_model=schemas.ProjectRead)
async def get_project(project_id: int):
	with get_session() as session:
		project = session.get(models.Project, project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")
		return project


@router.put("/{project_id}", response_model=schemas.ProjectRead)
async def update_project(project_id: int, payload: schemas.ProjectCreate):
	with get_session() as session:
		project = session.get(models.Project, project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")
		for key, value in payload.model_dump().items():
			setattr(project, key, value)
		session.flush()
		return project


@router.delete("/{project_id}")
async def delete_project(project_id: int):
	with get_session() as session:
		project = session.get(models.Project, project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")
		session.delete(project)
		return {"status": "deleted"}