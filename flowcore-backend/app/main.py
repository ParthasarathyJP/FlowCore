from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import users
# உங்கள் புராஜெக்ட்டுக்கு ஏற்ப supabase_admin-ஐ இங்கு இம்போர்ட் செய்யவும்
# from app.database import supabase_admin 

app = FastAPI(
    title="FlowCore API",
    description="Modular Business & Operations Engine (Manufacturing, Retail, Wholesale, D2C)",
    version="1.0.0"
)

# CORS Middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Integration
app.include_router(auth.router)
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.get("/api/users/business/{business_id}")
def get_business_users(business_id: str):
    try:
        # 1. profiles டேபிளிலிருந்து குறிப்பிட்ட பிசினஸ் ஐடி கொண்டவர்களின் ID-க்களைப் பெறுகிறோம்
        profiles_res = supabase_admin.table("profiles").select("*").eq("business_id", business_id).execute()
        profiles = profiles_res.data

        # 2. auth.users-லிருந்து அனைத்து யூசர்களின் மெயில் ஐடியை எடுத்து, profiles உடன் இணைக்கிறோம்
        users_res = supabase_admin.auth.admin.list_users()
        
        # A dictionary-ஆக மாற்றி எளிதாக மேப் செய்ய:
        email_map = {user.id: user.email for user in users_res}

        # இரண்டையும் இணைத்து அனுப்பவும்:
        combined_users = []
        for profile in profiles:
            user_id = profile.get("id")
            profile["email"] = email_map.get(user_id, "N/A")
            combined_users.append(profile)

        return {"users": combined_users}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/")
def read_root():
    return {"message": "Welcome to FlowCore API Engine", "status": "active"}