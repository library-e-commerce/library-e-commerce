from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import UserService
from app.domain.user_model import UserCreate, UserResponse

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# [API-USUARIO-01] Endpoint para registro de nuevos usuarios
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    service = UserService(db)
    return service.create_user(user)