from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import openpyxl
from ..db import get_session
from .. import models

router = APIRouter(prefix="/export", tags=["export"])


def _load_estimate(session, estimate_id: int) -> models.Estimate:
	estimate = session.get(models.Estimate, estimate_id)
	if not estimate:
		raise HTTPException(status_code=404, detail="Estimate not found")
	_ = estimate.lines
	return estimate


@router.get("/estimate/{estimate_id}/pdf")
async def export_estimate_pdf(estimate_id: int):
	with get_session() as session:
		estimate = _load_estimate(session, estimate_id)
		buffer = BytesIO()
		p = canvas.Canvas(buffer, pagesize=A4)
		width, height = A4
		y = height - 40
		p.setFont("Helvetica-Bold", 14)
		p.drawString(40, y, f"Estimate: {estimate.title}")
		y -= 20
		p.setFont("Helvetica", 10)
		p.drawString(40, y, f"Project ID: {estimate.project_id}  Currency: {estimate.currency}")
		y -= 20
		p.drawString(40, y, "Items:")
		y -= 16
		for line in estimate.lines:
			if y < 50:
				p.showPage()
				y = height - 40
			p.drawString(50, y, f"- {line.name} ({line.unit}): {line.quantity} x {line.unit_price} = {line.subtotal} {line.currency}")
			y -= 14
		p.showPage()
		p.save()
		pdf = buffer.getvalue()
		buffer.close()
		return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=estimate_{estimate_id}.pdf"})


@router.get("/estimate/{estimate_id}/xlsx")
async def export_estimate_xlsx(estimate_id: int):
	with get_session() as session:
		estimate = _load_estimate(session, estimate_id)
		wb = openpyxl.Workbook()
		ws = wb.active
		ws.title = "Estimate"
		ws.append(["Name", "Unit", "Quantity", "Unit price", "Subtotal", "Currency"])
		for line in estimate.lines:
			ws.append([line.name, line.unit, line.quantity, line.unit_price, line.subtotal, line.currency])
		bio = BytesIO()
		wb.save(bio)
		bio.seek(0)
		return Response(content=bio.read(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=estimate_{estimate_id}.xlsx"})