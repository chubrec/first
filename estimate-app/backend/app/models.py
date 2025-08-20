from sqlalchemy import Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .db import Base


class Work(Base):
	__tablename__ = "works"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	unit: Mapped[str] = mapped_column(String(16), nullable=False)
	base_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
	currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Material(Base):
	__tablename__ = "materials"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	unit: Mapped[str] = mapped_column(String(16), nullable=False)
	price_per_unit: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
	currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")
	supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Project(Base):
	__tablename__ = "projects"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(255), nullable=False)
	client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
	address: Mapped[str | None] = mapped_column(String(255), nullable=True)
	currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	estimates: Mapped[list["Estimate"]] = relationship("Estimate", back_populates="project")


class Estimate(Base):
	__tablename__ = "estimates"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")

	coefficient_complexity: Mapped[float] = mapped_column(Float, default=1.0)
	coefficient_urgency: Mapped[float] = mapped_column(Float, default=1.0)
	coefficient_floor: Mapped[float] = mapped_column(Float, default=1.0)
	discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
	markup_percent: Mapped[float] = mapped_column(Float, default=0.0)

	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	project: Mapped[Project] = relationship("Project", back_populates="estimates")
	lines: Mapped[list["EstimateLine"]] = relationship("EstimateLine", back_populates="estimate", cascade="all, delete-orphan")


class EstimateLine(Base):
	__tablename__ = "estimate_lines"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	estimate_id: Mapped[int] = mapped_column(ForeignKey("estimates.id"), nullable=False)

	line_type: Mapped[str] = mapped_column(String(16), nullable=False)
	ref_id: Mapped[int] = mapped_column(Integer, nullable=False)

	name: Mapped[str] = mapped_column(String(255), nullable=False)
	unit: Mapped[str] = mapped_column(String(16), nullable=False)
	quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
	unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
	currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")

	subtotal: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

	estimate: Mapped[Estimate] = relationship("Estimate", back_populates="lines")