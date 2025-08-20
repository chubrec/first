## Backend (FastAPI)

### Setup

1. Create venv (optional)
2. Install deps

```bash
pip install -r requirements.txt
```

3. Initialize DB tables

```bash
python -c "from app.db import engine; from app import models; models.Base.metadata.create_all(engine)"
```

4. Run server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for Swagger.