from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class WorkCreate(BaseModel):
	name: str
	description: Optional[str] = None
	unit: str
	base_rate: float
	currency: str = "EUR"
	is_active: bool = True


class WorkRead(WorkCreate):
	id: int

	class Config:
		from_attributes = True


class MaterialCreate(BaseModel):
	name: str
	unit: str
	price_per_unit: float
	currency: str = "EUR"
	supplier: Optional[str] = None
	is_active: bool = True


class MaterialRead(MaterialCreate):
	id: int

	class Config:
		from_attributes = True


class ProjectCreate(BaseModel):
	name: str
	client_name: Optional[str] = None
	address: Optional[str] = None
	currency: str = "EUR"


class ProjectRead(ProjectCreate):
	id: int

	class Config:
		from_attributes = True


class EstimateLineCreate(BaseModel):
	line_type: Literal["work", "material"]
	ref_id: int
	name: Optional[str] = None
	unit: Optional[str] = None
	quantity: float
	unit_price: Optional[float] = None
	currency: Optional[str] = None


class EstimateCreate(BaseModel):
	project_id: int
	title: str
	currency: str = "EUR"
	coefficient_complexity: float = 1.0
	coefficient_urgency: float = 1.0
	coefficient_floor: float = 1.0
	discount_percent: float = 0.0
	markup_percent: float = 0.0
	lines: List[EstimateLineCreate] = Field(default_factory=list)


class EstimateLineRead(BaseModel):
	id: int
	line_type: str
	ref_id: int
	name: str
	unit: str
	quantity: float
	unit_price: float
	currency: str
	subtotal: float

	class Config:
		from_attributes = True


class EstimateRead(BaseModel):
	id: int
	project_id: int
	title: str
	currency: str
	coefficient_complexity: float
	coefficient_urgency: float
	coefficient_floor: float
	discount_percent: float
	markup_percent: float
	lines: List[EstimateLineRead]

	class Config:
		from_attributes = True