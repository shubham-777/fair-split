"""
FairSplit FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, balances, expense, group, users, group_members  # , expenses
from app.config import settings
from app.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Expense sharing and group management API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "app": settings.APP_NAME
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(groups.router, prefix="/api/v1")
app.include_router(group_members.router, prefix="/api/v1")
app.include_router(expense.router, prefix="/api/v1")
app.include_router(balances.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )