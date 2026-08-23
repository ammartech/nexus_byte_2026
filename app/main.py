from fastapi import FastAPI
from app.routers import auth, users, documents, optimizations, templates, exports

app = FastAPI(title="Resume Optimizer API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(optimizations.router)
app.include_router(templates.router)
app.include_router(exports.router)

@app.get("/health")
def health():
    return {"status": "ok"}