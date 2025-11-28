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


# [API-USUARIO-02] Endpoint para verificación de correo
@router.get("/verificar/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verificar email de usuario"""
    service = UserService(db)
    result = service.verify_email(token)
    if not result:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    return {"message": "Email verificado correctamente"}