from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.carrito_service import CarritoService
from app.domain.carrito_model import CarritoCreate, CarritoResponse, CarritoItemCreate

router = APIRouter(prefix="/carritos", tags=["Carritos"])

# [API-CARRITO-001] Endpoints para gestionar carrito
@router.post("/", response_model=CarritoResponse, status_code=201)
def create_carrito(carrito: CarritoCreate, db: Session = Depends(get_db)):
    """Crear carrito"""
    service = CarritoService(db)
    return service.create_carrito(carrito)

@router.post("/{carrito_id}/items", response_model=CarritoResponse)
def add_item(carrito_id: int, item: CarritoItemCreate, db: Session = Depends(get_db)):
    """Añadir item al carrito"""
    service = CarritoService(db)
    return service.add_item(carrito_id, item)

@router.get("/{carrito_id}", response_model=CarritoResponse)
def get_carrito(carrito_id: int, db: Session = Depends(get_db)):
    """Obtener carrito con items"""
    service = CarritoService(db)
    carrito = service.get_carrito(carrito_id)
    if not carrito:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return carrito

@router.delete("/{carrito_id}/items/{item_id}", status_code=204)
def remove_item(carrito_id: int, item_id: int, db: Session = Depends(get_db)):
    """Eliminar item del carrito"""
    service = CarritoService(db)
    service.remove_item(carrito_id, item_id)
    return None