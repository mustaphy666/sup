from fastapi import APIRouter, HTTPException, status
from sqlite3 import IntegrityError

from app.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)

from app.auth.models import find_customer_by_email

from app.database import (
    create_user,
    get_user_by_email,
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):

    email = request.email.lower().strip()

    if "@" not in email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address.",
        )

    customer = find_customer_by_email(email)

    if not customer:
        raise HTTPException(
            status_code=403,
            detail="No matching customer account found.",
        )

    existing_user = get_user_by_email(email)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Account already exists.",
        )

    password_hash = hash_password(request.password)

    try:
        user = create_user(
            email=email,
            customer_id=customer["customer_id"],
            password_hash=password_hash,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Account already exists.",
        )

    token = create_access_token(user["user_id"])

    return AuthResponse(
        access_token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):

    email = request.email.lower().strip()

    user = get_user_by_email(email)

    if not user or not verify_password(
        request.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user["user_id"])

    return AuthResponse(
        access_token=token,
    )