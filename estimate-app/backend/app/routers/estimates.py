from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import select
from ..db import get_session
from .. import models, schemas
from ..services.calculator import compute_line_subtotal

router = APIRouter(prefix="/estimates", tags=["estimates"])


@router.post("/", response_model=schemas.EstimateRead)
async def create_estimate(payload: schemas.EstimateCreate):
	with get_session() as session:
		project = session.get(models.Project, payload.project_id)
		if not project:
			raise HTTPException(status_code=404, detail="Project not found")
		estimate = models.Estimate(
			project_id=payload.project_id,
			title=payload.title,
			currency=payload.currency or project.currency,
			coefficient_complexity=payload.coefficient_complexity,
			coefficient_urgency=payload.coefficient_urgency,
			coefficient_floor=payload.coefficient_floor,
			discount_percent=payload.discount_percent,
			markup_percent=payload.markup_percent,
		)
		session.add(estimate)
		session.flush()

		for line in payload.lines:
			if line.line_type == "work":
				work = session.get(models.Work, line.ref_id)
				if not work:
					raise HTTPException(status_code=400, detail=f"Work {line.ref_id} not found")
				unit_price = line.unit_price if line.unit_price is not None else work.base_rate
				name = line.name or work.name
				unit = line.unit or work.unit
				currency = line.currency or work.currency
			elif line.line_type == "material":
				material = session.get(models.Material, line.ref_id)
				if not material:
					raise HTTPException(status_code=400, detail=f"Material {line.ref_id} not found")
				unit_price = line.unit_price if line.unit_price is not None else material.price_per_unit
				name = line.name or material.name
				unit = line.unit or material.unit
				currency = line.currency or material.currency
			else:
				raise HTTPException(status_code=400, detail="Invalid line_type")

			subtotal = compute_line_subtotal(line.quantity, unit_price)
			line_model = models.EstimateLine(
				estimate_id=estimate.id,
				line_type=line.line_type,
				ref_id=line.ref_id,
				name=name,
				unit=unit,
				quantity=line.quantity,
				unit_price=unit_price,
				currency=currency,
				subtotal=subtotal,
			)
			session.add(line_model)
		session.flush()
		session.refresh(estimate)
		return estimate


@router.get("/{estimate_id}", response_model=schemas.EstimateRead)
async def get_estimate(estimate_id: int):
	with get_session() as session:
		estimate = session.get(models.Estimate, estimate_id)
		if not estimate:
			raise HTTPException(status_code=404, detail="Estimate not found")
		_ = estimate.lines
		return estimate


@router.get("/project/{project_id}", response_model=List[schemas.EstimateRead])
async def list_estimates_for_project(project_id: int):
	with get_session() as session:
		result = session.execute(select(models.Estimate).where(models.Estimate.project_id == project_id).order_by(models.Estimate.created_at.desc()))
		return result.scalars().unique().all()