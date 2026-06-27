from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.matcher import GraphMatcher
from src.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager: Runs once when the server starts.
    We load the Model/Graph weights into RAM here so API calls are lightning fast.
    """
    print("[*] Starting up API Server...")
    # Attach the graph and matcher to the application state
    app.state.matcher = GraphMatcher()
    
    print("[*] System Ready. Accepting connections.")
    yield
    

# Initialize FastAPI App
app = FastAPI(
    title="Smart CV Matcher API",
    description="Production API for Graph-based CV Evaluation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (Crucial for connecting to your Tailwind/HTML Frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the endpoints
app.include_router(router)

@app.get("/health", tags=["System"])
def health_check():
    """Simple endpoint to check if the server is alive."""
    return {"status": "ok", "message": "Smart CV Matcher is running!"}