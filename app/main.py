from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.deps import validate_api_key

app = FastAPI(
    title="AI Chatbot Microservice API",
    description="REST API mandiri untuk chatbot AI, pencarian semantik, dan tanya jawab berbasis dokumen",
    version="1.0.0",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
