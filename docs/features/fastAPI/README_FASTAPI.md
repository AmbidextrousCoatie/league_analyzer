# FastAPI Development Setup

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn[standard]
```

### 2. Run Development Server

**Option A: Using Python script (like Flask)**
```bash
python main.py
```

**Option B: Using Uvicorn directly**
```bash
uvicorn main:app --reload --port 5000
```

### 3. Test the API

- **Hello World:** http://127.0.0.1:5000/
- **Health Check:** http://127.0.0.1:5000/health
- **Test Endpoint:** http://127.0.0.1:5000/api/v1/test
- **API Documentation:** http://127.0.0.1:5000/docs (Swagger UI)
- **Alternative Docs:** http://127.0.0.1:5000/redoc (ReDoc)

## Comparison with Flask

| Flask | FastAPI |
|-------|---------|
| `python wsgi.py` | `python main.py` |
| `app.run(debug=True)` | `uvicorn.run("main:app", reload=True)` |
| Port 5000 | Port 5000 |
| No auto docs | Auto docs at `/docs` |

## Features

- ✅ Auto-reload on code changes (`reload=True`)
- ✅ Automatic API documentation (Swagger UI)
- ✅ Type hints and validation
- ✅ Same port as Flask (5000)
- ✅ Same workflow in Cursor

## Next Steps

1. Add your routes to `main.py` or create route modules
2. Add domain models
3. Add application layer (commands/queries)
4. Migrate existing Flask routes

