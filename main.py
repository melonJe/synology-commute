import uvicorn
from fastapi import FastAPI

from app.routers import synology

app = FastAPI(debug=True)

app.include_router(synology.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
