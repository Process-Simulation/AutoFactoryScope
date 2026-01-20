from fastapi import FastAPI
from autofactoryscope_api.config import settings

app = FastAPI(title="AutoFactoryScope API")

@app.get("/health")
async def health_check():
    return {"status": "ok", "app_name": "AutoFactoryScope API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
