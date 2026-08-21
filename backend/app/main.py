import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import routes, auth, explore

# Initialize PostgreSQL / SQLite tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Travel Copilot API", 
    description="Multi-agent travel routing, pricing, delay forecasting, and AI Smart Explore engine.",
    version="2.0.0"
)

# Configure CORS Middleware for cross-origin Flutter Web calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")
app.include_router(auth.router)
app.include_router(explore.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI Travel Copilot Master Service Engine",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
