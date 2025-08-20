from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import works, materials, projects, estimates, export

app = FastAPI(title="Construction Estimate API", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(works.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(estimates.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/")
async def root():
	return {"status": "ok"}