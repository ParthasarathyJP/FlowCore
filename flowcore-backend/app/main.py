from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(
    title="FlowCore API",
    description="Modular Business & Operations Engine (Manufacturing, Retail, Wholesale, D2C)",
    version="1.0.0"
)

# CORS Middleware (Next.js ஃப்ரெண்ட்எண்டுடன் இணைக்க அனுமதித்தல்)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production-ல் குறிப்பிட்ட ஃப்ரெண்ட்எண்ட் URL-ஐ மட்டும் அனுமதிக்கலாம்
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Integration
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FlowCore API Engine", "status": "active"}