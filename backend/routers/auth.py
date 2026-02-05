"""
Authentication Router - Login & Registration
"""
from fastapi import APIRouter, HTTPException, status, Depends
from database import get_db
from schemas import UserCreate, UserLogin, UserResponse, Token
from utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    # Import logger from database (or set up new one)
    import logging
    logger = logging.getLogger("api.auth")
    
    logger.info(f"Attempting registration for email: {user.email}")
    
    try:
        db = get_db()
        
        # Check if user already exists
        logger.info("Checking for existing user...")
        existing = db.table("users").select("id").eq("email", user.email).execute()
        
        if existing.data:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        logger.info("Creating new user...")
        hashed_pw = hash_password(user.password)
        
        user_data = {
            "email": user.email,
            "name": user.name,
            "password_hash": hashed_pw,
            "role": user.role.value
        }
        
        result = db.table("users").insert(user_data).execute()
        
        logger.info(f"Insert result: {result}")
        
        if not result.data:
            logger.error("Database returned no data after insert")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user - no data returned from database"
            )
        
        logger.info("User created successfully")
        return result.data[0]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        # Check for common Supabase errors
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
             detail = "Database table 'users' does not exist. Please run the schema.sql in Supabase."
        else:
             detail = f"Registration failed: {str(e)}"
             
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token"""
    db = get_db()
    
    # Find user
    result = db.table("users").select("*").eq("email", credentials.email).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user = result.data[0]
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    token = create_access_token(user["id"], user["role"])
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current user profile"""
    db = get_db()
    result = db.table("users").select("*").eq("id", current_user.user_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return result.data[0]
