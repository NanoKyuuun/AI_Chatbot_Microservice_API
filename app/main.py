from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.deps import validate_api_key
from app.core.logging import setup_logging
from app.core.errors import global_exception_handler
from app.api.v1 import routes_collections, routes_documents, routes_search, routes_chat
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Initialize logging
setup_logging()

app = FastAPI(
    title="AI Chatbot Microservice API",
    description="REST API mandiri untuk chatbot AI, pencarian semantik, dan tanya jawab berbasis dokumen",
    version="1.0.0",
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, global_exception_handler)
app.add_exception_handler(RequestValidationError, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(routes_collections.router, prefix="/v1")
app.include_router(routes_documents.router, prefix="/v1")
app.include_router(routes_search.router, prefix="/v1")
app.include_router(routes_chat.router, prefix="/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Chatbot Microservice API",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/v1/secure-test")
async def secure_test(auth_data: dict = Depends(validate_api_key)):
    return {
        "message": "You are authenticated",
        "tenant_id": auth_data["tenant_id"]
    }
