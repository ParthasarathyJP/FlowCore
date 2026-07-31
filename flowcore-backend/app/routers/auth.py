from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# .env ஃபைலை லோட் செய்தல்
load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["Auth & Business Registration"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Supabase கிளைண்ட் உருவாக்கம்
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class BusinessSignupSchema(BaseModel):
    business_name: str
    business_type: str  # 'manufacturing', 'retail', 'wholesale', 'd2c'
    admin_name: str
    email: str
    password: str

@router.post("/signup-business")
def signup_business(data: BusinessSignupSchema):
    try:
        # 1. Supabase Auth-ல் யூசரை உருவாக்குதல்
        auth_response = supabase.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create auth user")
            
        user_id = auth_response.user.id

        # 2. பிசினஸ் விவரங்களை 'businesses' டேபிளில் சேமித்தல்
        biz_res = supabase.table("businesses").insert({
            "business_name": data.business_name,
            "business_type": data.business_type
        }).execute()
        
        if not biz_res.data:
            raise HTTPException(status_code=400, detail="Failed to create business record")

        business_id = biz_res.data[0]["id"]

        # 3. யூசரை பிசினஸுடன் இணைக்க 'profiles' டேபிளில் பதிவு செய்தல்
        supabase.table("profiles").insert({
            "id": user_id,
            "business_id": business_id,
            "full_name": data.admin_name,
            "role": "admin"
        }).execute()

        return {
            "status": "success", 
            "message": "Business & Admin registered successfully!", 
            "business_id": business_id
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class LoginSchema(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(data: LoginSchema):
    try:
        # Supabase மூலம் யூசரை லாகின் செய்தல்
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        if not response.user:
            raise HTTPException(status_code=400, detail="Invalid login credentials")
            
        return {
            "status": "success",
            "message": "Login successful",
            "user": response.user,
            "session": response.session
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))