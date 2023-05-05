import uvicorn
from fastapi import FastAPI

from app.routers import employee, synology

app = FastAPI(debug=True)

app.include_router(employee.router)
app.include_router(synology.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
