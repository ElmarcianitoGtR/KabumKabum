from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.models import User, UserRole
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user,
)
from app.services.solana_service import store_credentials_on_chain, verify_credentials_on_chain

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ─────────────────────────────────────────────────
#  SCHEMAS
# ─────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name:     str
    email:    EmailStr
    password: str
    role:     UserRole = UserRole.READER


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    role:          str


class RefreshRequest(BaseModel):
    refresh_token: str


# ─────────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────────
@router.post("/register", status_code=201)
async def register(data: RegisterRequest):
    # Verificar que el email no exista
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed = hash_password(data.password)

    # Guardar hash + rol en Solana (on-chain)
    solana_pubkey = await store_credentials_on_chain(
        email=data.email,
        hashed_password=hashed,
        role=data.role.value,
    )

    # Guardar perfil completo en MongoDB
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hashed,
        role=data.role,
        solana_public_key=solana_pubkey,
    )
    await user.insert()

    return {
        "message": "Usuario registrado correctamente",
        "email":   user.email,
        "role":    user.role,
        "solana":  solana_pubkey,
    }


# ─────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.email == form.username)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # 1) Verificar password localmente con bcrypt
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # 2) Verificar on-chain en Solana que el hash coincide
    valid_on_chain = await verify_credentials_on_chain(
        email=user.email,
        hashed_password=user.hashed_password,
    )
    if not valid_on_chain:
        raise HTTPException(status_code=401, detail="Verificación blockchain fallida")

    # 3) Actualizar último login
    user.last_login = datetime.utcnow()
    await user.save()

    # 4) Emitir tokens JWT con el rol embebido
    token_data = {"sub": user.email, "role": user.role.value}
    return TokenResponse(
        access_token  = create_access_token(token_data),
        refresh_token = create_refresh_token(token_data),
        role          = user.role.value,
    )


# ─────────────────────────────────────────────────
#  REFRESH TOKEN
# ─────────────────────────────────────────────────
@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token de refresco inválido")

    user = await User.find_one(User.email == payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    token_data = {"sub": user.email, "role": user.role.value}
    return TokenResponse(
        access_token  = create_access_token(token_data),
        refresh_token = create_refresh_token(token_data),
        role          = user.role.value,
    )


# ─────────────────────────────────────────────────
#  PERFIL ACTUAL
# ─────────────────────────────────────────────────
@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id":         str(current_user.id),
        "name":       current_user.name,
        "email":      current_user.email,
        "role":       current_user.role,
        "solana":     current_user.solana_public_key,
        "last_login": current_user.last_login,
    }
