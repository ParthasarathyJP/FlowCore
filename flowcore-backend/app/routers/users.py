import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv

# .env ஃபைலில் உள்ள மாறிகளை லோட் செய்ய
load_dotenv()

router = APIRouter()

# .env ஃபைலில் இருந்து Supabase URL மற்றும் Service Role Key-ஐ பெறுதல்
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Supabase URL and Service Role Key must be set in environment variables.")

# Supabase Admin Client உருவாக்கம்
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    business_id: str
    role: str

@router.post("/create", summary="Create a new team user under a business")
def create_team_user(payload: CreateUserRequest):
    try:
        # Supabase Admin API மூலம் யூசரை உருவாக்குதல் மற்றும் metadata-ஐச் சேர்த்தல்
        response = supabase_admin.auth.admin.create_user({
            "email": payload.email,
            "password": payload.password,
            "email_confirm": True, # ஆட்டோமேட்டிக்காக ஈமெயில் வெரிஃபை செய்ய
            "user_metadata": {
                "full_name": payload.full_name,
                "business_id": payload.business_id,
                "role": payload.role
            }
        })
        
        return {
            "success": True,
            "message": "User profile created successfully",
            "user": response.user
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# புதியதாக இணைக்கப்பட்ட Get Business Users எண்ட்பாயிண்ட்
@router.get("/business/{business_id}", summary="Get all team members with email for a business")
def get_business_users(business_id: str):
    try:
        # 1. profiles டேபிளிலிருந்து குறிப்பிட்ட பிசினஸ் ஐடி கொண்டவர்களின் விபரங்களைப் பெறுதல்
        profiles_res = supabase_admin.table("profiles").select("*").eq("business_id", business_id).execute()
        profiles = profiles_res.data or []

        # 2. auth.users-லிருந்து அனைத்து யூசர்களின் மெயில் ஐடியைப் பெறுதல்
        users_res = supabase_admin.auth.admin.list_users()
        
        # Safe mapping for emails
        email_map = {}
        if hasattr(users_res, 'users') and users_res.users:
            email_map = {u.id: u.email for u in users_res.users}
        elif isinstance(users_res, list):
            email_map = {u.id: u.email for u in users_res}

        # 3. profiles மற்றும் emails இரண்டையும் இணைத்தல்
        combined_users = []
        for profile in profiles:
            user_id = profile.get("id")
            profile["email"] = email_map.get(user_id, "N/A")
            combined_users.append(profile)

        return {"users": combined_users}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class UpdateUserRequest(BaseModel):
    full_name: str
    role: str

@router.put("/{user_id}", summary="Update team user profile details")
def update_team_user(user_id: str, payload: UpdateUserRequest):
    try:
        # Supabase profiles டேபிளில் பெயர் மற்றும் ரோலை மாற்றுதல்
        response = supabase_admin.table("profiles").update({
            "full_name": payload.full_name,
            "role": payload.role
        }).eq("id", user_id).execute()

        return {
            "success": True,
            "message": "User updated successfully",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class UpdatePasswordRequest(BaseModel):
    user_id: str
    new_password: str

@router.put("/password/update", summary="Update user password")
def update_user_password(payload: UpdatePasswordRequest):
    try:
        # Supabase Admin API மூலம் குறிப்பிட்ட யூசரின் பாஸ்வேர்டை மாற்றுதல்
        response = supabase_admin.auth.admin.update_user_by_id(
            payload.user_id,
            {"password": payload.new_password}
        )
        return {
            "success": True,
            "message": "Password updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))